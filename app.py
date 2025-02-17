import requests
from bs4 import BeautifulSoup
import cv2
import numpy as np
from PIL import Image
from io import BytesIO
from ultralytics import YOLO
from flask import Flask, render_template, url_for
from threading import Thread
import time
import datetime
import os
import sys
from pyngrok import ngrok

# Load YOLO model and define vehicle classes
model = YOLO('models/yolov8n.pt')  # Corrected model path
vehicle_classes = ['car', 'motorcycle', 'bus', 'truck']

# Function to get locations from the website
def get_locations(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    map_div = soup.find('div', class_='image-showcase map')
    buttons = map_div.find_all('button')
    return [{'id': btn.get('id'),
             'name': btn.get_text(strip=True)}
            for btn in buttons]

# Function to get camera data for a location
def get_cameras(location_id):
    base_url = 'https://onemotoring.lta.gov.sg'
    url = f'{base_url}/content/onemotoring/home/driving/traffic_information/traffic-cameras/{location_id}.html'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    snapshots_div = soup.find('div', class_='snapshots')

    if not snapshots_div:
        return []

    cameras = []
    for card in snapshots_div.find_all('div', class_='card'):
        desc = card.find('div', class_='trf-desc')
        time_elem = card.find('div', class_='timestamp')
        img = card.find('img')

        if img and img.get('src'):
            img_src = img.get('src')
            if img_src.startswith('//'):
                img_src = 'https:' + img_src

            cameras.append({
                'description': desc.get_text(strip=True) if desc else 'No description',
                'timestamp': time_elem.get_text(strip=True) if time_elem else 'No timestamp',
                'image_url': img_src
            })

    return cameras

# Function to process image from URL
def process_image(image_url):
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

# Function to detect vehicles and annotate image
def detect_vehicles_and_annotate(image, image_path):
    results = model(image)
    detections = []
    annotated_image = image.copy()

    for result in results:
        boxes = result.boxes
        for box in boxes:
            cls = int(box.cls[0])
            conf = float(box.conf[0])
            class_name = result.names[cls]
            if class_name in vehicle_classes:
                detections.append({
                    'class': class_name,
                    'confidence': conf,
                    'box': box.xyxy[0].cpu().numpy()
                })
                x1, y1, x2, y2 = map(int, box.xyxy[0])  # Draw bounding box and label
                label = f"{class_name} {conf:.2f}"
                cv2.rectangle(annotated_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(annotated_image, label, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    cv2.imwrite(image_path, annotated_image)  # Save annotated image

    return detections

# Function to count vehicles
def get_vehicle_counts(detections):
    counts = {cls: 0 for cls in vehicle_classes}
    for det in detections:
        counts[det['class']] += 1
    counts['total'] = sum(counts.values())
    return counts


# Create 'templates' and 'static' directories
if not os.path.exists('templates'):
    os.makedirs('templates')

if not os.path.exists('static'):
    os.makedirs('static')


# Global variables
url = 'https://onemotoring.lta.gov.sg/content/onemotoring/home/driving/traffic_information/traffic-cameras/cte.html'
all_locations = get_locations(url)
current_data = {}
last_update = None

# Function to fetch data (called once)
def fetch_data():
    global current_data, last_update
    new_data = {}
    for loc in all_locations:
        cameras = get_cameras(loc['id'])
        for idx, cam in enumerate(cameras):
            img = process_image(cam['image_url'])
            image_filename = f"{loc['id']}_{idx}.jpg"
            image_path = os.path.join('static', image_filename)
            detections = detect_vehicles_and_annotate(img, image_path)
            counts = get_vehicle_counts(detections)
            cam['vehicle_counts'] = counts
            cam['image_filename'] = image_filename
        new_data[loc['id']] = cameras
    current_data = new_data
    last_update = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Function to update data periodically
def update_data():
    while True:
        fetch_data()
        time.sleep(300)

# Flask app setup
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('traffic.html',
                           locations=all_locations,
                           camera_data=current_data,
                           last_update=last_update)

fetch_data()  # Initial data fetch

update_thread = Thread(target=update_data) # Start background update thread
update_thread.daemon = True
update_thread.start()

def is_colab():
    return 'google.colab' in sys.modules

if __name__ == '__main__':
    if is_colab():
        # ngrok setup for Colab.  REPLACE WITH YOUR TOKEN.
        ngrok.set_auth_token('your_ngrok_auth_token')
        public_url = ngrok.connect(5000).public_url
        print(f"Open the following URL in your browser: {public_url}")
    else:
        print("App is running locally on http://127.0.0.1:5000")

    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.run(port=5000) # Run the app

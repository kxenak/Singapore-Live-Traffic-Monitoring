# Singapore Live Traffic Monitoring

This project uses YOLOv8 (specifically a pre-trained `yolov8n.pt` model) to analyze live traffic camera feeds from the Singapore Land Transport Authority (LTA) website, detect vehicles, and display the counts on a simple web interface.  It's built with Flask and can be deployed locally or using ngrok for public access (primarily useful in Colab environments).

## Features

*   **Live Camera Data:**  Fetches image data from the LTA OneMotoring traffic camera website.
*   **Vehicle Detection:**  Uses YOLOv8 to detect cars, motorcycles, buses, and trucks.
*   **Vehicle Counting:**  Counts the number of each vehicle type in each camera feed.
*   **Web Interface:**  Displays the annotated images and vehicle counts in a simple, auto-refreshing web page.
*   **Colab and Local Deployment:**  Supports running in Google Colab (with ngrok) or locally.
*   **Periodic Updates:**  Automatically updates the camera feeds and vehicle counts every 5 minutes.

## Prerequisites

*   Python 3.7+
*   The required Python packages (listed in `requirements.txt`).
*   The YOLOv8 model file (`yolov8n.pt`).  You can download `yolov8n.pt` from this [link](https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt). Place the downloaded file in the `models/` directory.  *It's crucial to get the correct pre-trained model;  results will be inaccurate or the application may fail if the model is missing or incorrect.*

## Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/kxenak/singapore-live-traffic-monitoring.git
    cd traffic-camera-analyzer
    ```

2.  **Create and activate a virtual environment (recommended):**

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Download the YOLOv8 model:**  Download `yolov8n.pt` from the link provided in the "Prerequisites" section and place it in the `models/` directory.

## Usage

### Running Locally

1.  **Start the Flask app:**

    ```bash
    python app.py
    ```

2.  **Access the web interface:** Open your web browser and go to `http://127.0.0.1:5000`.

### Running in Google Colab

1.  **Upload the project files:** Upload the `app.py`, `requirements.txt`, `templates/traffic.html`, and `models/yolov8n.pt` files to your Colab environment.  You can create the `models` and `templates` directories in Colab directly.  You can also clone the repository directly in Colab using `!git clone ...`.

2.  **Install dependencies (in a Colab cell):**

    ```python
    !pip install -r requirements.txt
    ```

3.  **Run the app (in a Colab cell):**  The `app.py` file already includes the necessary ngrok setup for Colab. Just run the `app.py` file.

    ```python
    !python app.py
    ```
    This will print a public ngrok URL that you can use to access the web interface.

**Important Notes for Colab:**

*   Colab sessions have limited runtime.  The app will stop when the session ends.
*   ngrok requires an authentication token.  You can get a free token from [ngrok.com](https://ngrok.com/). Replace `'your_ngrok_auth_token'` in `app.py` with your actual token.
* The program will create the static folder and save images there.

## Project Structure

```
traffic-camera-analyzer/
├── .gitignore          # Files and folders to ignore in Git
├── README.md           # This documentation file
├── app.py              # Main application code (Flask, YOLO, data fetching)
├── requirements.txt    # List of required Python packages
├── models/
│   └── yolov8n.pt      # YOLOv8 pre-trained model file (you need to download this)
├── static/             # Directory for storing processed images (created dynamically)
└── templates/
    └── traffic.html    # HTML template for the web interface
```

## Code Explanation

*   **`app.py`:**  This is the heart of the application. It contains:
    *   Flask app setup for serving the web interface.
    *   Functions to fetch camera data from the LTA website (`get_locations`, `get_cameras`).
    *   Image processing using OpenCV (`process_image`).
    *   Vehicle detection using YOLOv8 (`detect_vehicles_and_annotate`).
    *   Vehicle counting (`get_vehicle_counts`).
    *   A background thread to periodically update the data (`update_data`).
    *   ngrok integration for Colab deployment.
*   **`templates/traffic.html`:**  The HTML template uses Jinja2 templating to display the data fetched by the Flask app.  It shows the location, camera images, timestamps, and vehicle counts. It includes a meta refresh tag to automatically reload the page every 5 minutes.
*   **`requirements.txt`:** Lists all the Python libraries needed to run the project.
*  **`models/yolov8n.pt`:** The pre-trained YOLOv8 model.

## Contributing

Contributions are welcome!  Please feel free to submit pull requests or open issues.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details (you'll need to create a LICENSE file with the MIT license text).

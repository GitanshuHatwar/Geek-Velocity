# Install required libraries
# pip install ultralytics opencv-python pyngrok flask flask-cors

# Import libraries
from flask import Flask, request, jsonify
import cv2
import numpy as np
from ultralytics import YOLO
from pyngrok import ngrok
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load pre-trained YOLOv8 model with adjusted confidence threshold
model = YOLO('yolov8n.pt')  # Lightweight model

# Define vehicle classes to detect
vehicle_classes = ['car', 'motorbike', 'bus', 'truck']

# Define the API endpoint for image uploads
@app.route('/upload', methods=['POST', 'OPTIONS'])
def upload_images():
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'success'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response

    # Debug information
    print("Request method:", request.method)
    print("Content-Type:", request.headers.get('Content-Type'))
    print("Files keys:", list(request.files.keys()))

    # Check if images are included in the request
    if 'images' not in request.files:
        print("ERROR: No 'images' field found in request.files")
        return jsonify({'error': 'No images uploaded'}), 400

    # Get the list of uploaded images
    images = request.files.getlist('images')
    print(f"Number of images received: {len(images)}")

    if len(images) != 4:
        return jsonify({'error': 'Exactly 4 images are required'}), 400

    vehicle_data = []  # List to hold data for each image

    # Process each uploaded image
    for idx, img in enumerate(images):
        # Read image from file storage
        img_array = cv2.imdecode(np.frombuffer(img.read(), np.uint8), cv2.IMREAD_COLOR)
        if img_array is None:
            return jsonify({'error': 'Failed to decode one or more images'}), 400

        # Run YOLOv8 inference with a higher confidence threshold to reduce false positives
        results = model(img_array, conf=0.5)[0]  # conf=0.5 means 50% confidence threshold

        # Collect vehicle data
        vehicles = []
        for box in results.boxes:
            cls_id = int(box.cls)
            label = model.names[cls_id]
            if label in vehicle_classes:
                # Get bounding box coordinates
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                vehicles.append({
                    'label': label,
                    'bbox': [x1, y1, x2, y2]
                })

        count = len(vehicles)
        print(f"Lane {idx + 1} vehicle count: {count}")
        vehicle_data.append({
            'count': count,
            'vehicles': vehicles
        })

    # Calculate green signal timings
    time_per_vehicle = 5  # seconds per vehicle
    green_light_times = []
    for data in vehicle_data:
        count = data['count']
        green_time = max(15, min(count * time_per_vehicle, 60))  # min 15 sec, max 60 sec
        green_light_times.append(green_time)

    # Prepare response data
    response_data = {
        'vehicle_data': vehicle_data,
        'green_light_times': green_light_times
    }

    print("Sending response:", response_data)

    # Return the response as JSON
    return jsonify(response_data)

# Start the Flask server and expose it via ngrok
if __name__ == '__main__':
    # Set your ngrok authtoken (replace with your actual token)
    ngrok.set_auth_token("2uwRDtV6qXXovklq3iaQucvBwdb_7XSvYgk69jwP93sitaw2S")

    # Start ngrok tunnel on port 5000
    public_url = ngrok.connect(5000)
    print(f"Public URL: {public_url}")

    # Run Flask app
    app.run(host='0.0.0.0', port=5000)

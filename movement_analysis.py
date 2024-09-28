import cv2
import requests
import numpy as np
from fer.emotionsmultilanguage import emotions_dict


# Function to extract frames from the video
def extract_frames(video_path, skipping):
    cap = cv2.VideoCapture(video_path)
    frames = []
    it = 1
    while True:

        ret, frame = cap.read()

        if not ret:
            break

        if it%skipping != 0:
            it += 1
            continue
        frames.append(frame)
        it = 1
    cap.release()
    return frames

# Function to send a frame to the Luxand API for emotion detection
def detect_emotions(frame):
    # Check if the frame is None
    if frame is None:
        print("Warning: Received an empty frame.")
        return None

    # Convert the frame from BGR to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Encode the frame as JPEG
    _, buffer = cv2.imencode('.jpg', rgb_frame)

    # Prepare the files dictionary for the request
    files = {
        "photo": buffer.tobytes(),  # Use the raw bytes from the encoded frame
    }

    # Endpoint URL
    url = "https://api.luxand.cloud/photo/emotions"

    # Request headers with your API token
    headers = {
        "token": "68564b7d74fb43dbbd1794021fdffd6a",
    }

    # Making the POST request
    response = requests.post(url, headers=headers, files=files)

    # Return the JSON response if successful
    if response.status_code == 200:
        return response.json()  # Parse JSON response
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None

def analyze_movement(video_path, skipping = 15):

    # Step 1: Extract frames from the video
    frames = extract_frames(video_path, skipping)
    emotions_dict = []
    # Check if frames were extracted
    if not frames:
        print("No frames extracted. Please check the video file path or format.")

    # Step 2: Analyze each frame for emotions
    for i, frame in enumerate(frames):
        emotions = detect_emotions(frame)
        if emotions:
            emotions_dict.append(emotions)
    return emotions_dict

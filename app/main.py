from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel
import shutil
import os
import uuid
import time
from moviepy.editor import VideoFileClip
from google.cloud import speech_v1p1beta1 as speech
from pydub import AudioSegment
from fastapi.encoders import jsonable_encoder
import math

# Importing additional analysis functions
from movement_analysis import analyze_movement
from text_analysis import analyze_text
from sentiment_analysis import analyze_sentiment, summarize
from analyze_audio_quality import analyze_audio_and_speech

# Video storage to track the status and data of each query
video_storage = {}

# FastAPI app instance
app = FastAPI()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials.json"

# Directory to save uploaded videos
UPLOAD_DIR = "video"
AUDIO_DIR = "audio"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)


# Pydantic model for the response
class VideoResponse(BaseModel):
    query_id: str


def clean_data(data):
    """Recursively clean the data, replacing NaN and Infinity with None."""
    if isinstance(data, dict):
        return {key: clean_data(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [clean_data(item) for item in data]
    elif isinstance(data, float):
        # Replace NaN, inf, -inf with None
        if math.isnan(data) or math.isinf(data):
            return None
        return data
    else:
        return data


def extract_audio_from_video(video_path, output_audio_path):
    """Extracts audio from the video and saves it as a WAV file."""
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(output_audio_path)
    return output_audio_path


def convert_stereo_to_mono(input_audio_path, output_audio_path):
    """Converts stereo sound to mono."""
    audio = AudioSegment.from_wav(input_audio_path)
    mono_audio = audio.set_channels(1)
    mono_audio.export(output_audio_path, format="wav")
    return output_audio_path


def transcribe_video(audio_path):
    """Uses Google Cloud to transcribe audio to text."""
    client = speech.SpeechClient()
    with open(audio_path, "rb") as audio_file_data:
        audio_content = audio_file_data.read()

    audio = speech.RecognitionAudio(content=audio_content)

    config = speech.RecognitionConfig(
        language_code="pl-PL",
        enable_automatic_punctuation=True
    )

    response = client.recognize(config=config, audio=audio)

    transcript = ""
    for result in response.results:
        transcript += result.alternatives[0].transcript + "\n"

    return {"transcript": transcript}


async def analyze_all(video_path, query_id):
    """Function centralizing all analysis processes on the video file."""
    print("Extracting audio")
    data = {}
    audio_path = "audio/" + video_path[6:-4] + ".wav"
    extract_audio_from_video(video_path, audio_path)
    convert_stereo_to_mono(audio_path, audio_path)

    print("Transcribing")
    text = transcribe_video(audio_path)["transcript"]
    data["transcript"] = text

    print("Analyzing")
    temp = analyze_text(text)
    data["flesch"] = temp.get("flesch")
    data["gunning"] = temp.get("gunning")
    data["language_errors"] = temp.get("language_errors")
    data["foreign_words"] = temp.get("foreign_language")
    data["use_passive_voice"] = temp.get("use_passive_voice")

    data["emotions"] = analyze_movement(video_path)
    data["sentiment"] = analyze_sentiment(text)
    data["summarize"] = summarize(text)
    data["audio"] = analyze_audio_and_speech(video_path, audio_path, text)

    # Update the video storage with status and data
    video_storage[query_id]["status"] = "200"
    video_storage[query_id]["data"] = data
    print("Analysis completed")


# Endpoint to upload video and return query_id immediately
@app.post("/upload_video", response_model=VideoResponse)
async def upload_video(file: UploadFile = File(...), background_tasks: BackgroundTasks = BackgroundTasks()):
    """
    Upload a video file and start the analysis process in the background.

    **Args:**
    - file: The video file to be uploaded.

    **Returns:**
    - query_id: A unique identifier to track the video analysis process.
    - status: Initial status of the processing (100 = in progress).
    """
    # Generate a unique query ID
    query_id = str(uuid.uuid4())

    # Save the video file
    video_path = os.path.join(UPLOAD_DIR, f"{query_id}.mp4")
    with open(video_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Store initial status with query ID
    video_storage[query_id] = {
        "video_path": video_path,
        "status": "100",  # Initial status
        "data": None
    }

    # Add the analysis task to the background
    background_tasks.add_task(analyze_all, video_path, query_id)

    # Return the query ID and initial status right away
    return JSONResponse(content={"query_id": query_id, "status": "100"})


# Endpoint to get the video analysis result by query_id
@app.get("/video/{query_id}")
async def get_video(query_id: str):
    """
    Retrieve the video analysis result by its unique query ID.

    **Args:**
    - query_id: The unique identifier for the uploaded video.

    **Returns:**
    - If the analysis is completed, the data is returned.
    - If the analysis is still in progress, a status of 100 is returned.
    """
    if query_id not in video_storage:
        raise HTTPException(status_code=404, detail="Video not found")

    data = video_storage[query_id].get("data")
    cleaned_data = clean_data(data)
    safe_data = jsonable_encoder(cleaned_data)

    # Check if analysis is completed or still running
    if video_storage[query_id].get("status") == "200":
        return JSONResponse(content={"query_id": query_id, "data": safe_data})
    else:
        return JSONResponse(content={"query_id": query_id, "status": "100"})  # Still processing

@app.options("/test")
async def corsastuff():
    return Response(status_code=204)
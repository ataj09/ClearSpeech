from moviepy.editor import VideoFileClip
from google.cloud import speech_v1p1beta1 as speech
from pydub import AudioSegment
from fastapi.encoders import jsonable_encoder

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import shutil
import os
import uuid
import math
import time


from app.movement_analysis import analyze_movement
from app.text_analysis import analyze_text
from app.sentiment_analysis import analyze_sentiment, summarize
from app.analyze_audio_quality import analyze_audio_and_speech

def clean_data(data):
    """Recursively clean the data, replacing NaN and Infinity with None"""
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
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(output_audio_path)
    return output_audio_path


def convert_stereo_to_mono(input_audio_path, output_audio_path):
    # Load the stereo audio file
    audio = AudioSegment.from_wav(input_audio_path)

    # Convert to mono
    mono_audio = audio.set_channels(1)

    # Export the mono audio to the output path
    mono_audio.export(output_audio_path, format="wav")
    return output_audio_path

def transcribe_video(audio_path):
    # Transcribe audio
    client = speech.SpeechClient()
    time.sleep(12000000)

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
    print(transcript)
    return {"transcript": transcript}

async def analyze_all(video_path, query_id):

    print("exctracting audio")
    data = {}
    audio_path = "audio/" + video_path[6:-4] + ".wav"
    extract_audio_from_video(video_path, audio_path)
    convert_stereo_to_mono(audio_path, audio_path)


        #transcript using
    print("transcribing")
    text = transcribe_video(audio_path)["transcript"]
    data["transcript"] = text

    print("analyzing")
    temp = analyze_text(text)
    data["flesch"] = temp.get("flesch")
    data["gunning"] = temp.get("gunning")
    data["language_errors"] = temp.get("language_errors")

    data["emotions"] = analyze_movement(video_path)

    data["sentiment"] = analyze_sentiment(text)
    data["summarize"] = summarize(text)
    data["audio"] = analyze_audio_and_speech(video_path, audio_path, text)
    video_storage[query_id]["status"] = "200"
    video_storage[query_id]["data"] = data
    print("analysis completed")


        #video_storage[query_id]["status"] = "-1"
        #print("analysis completed")
# Example usage:



#text_subtitles = extract_subtitles(video_path, "temp.srt")
#print(compare_phonetic_text(text, text_subtitles))
video_storage = {}
app = FastAPI()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credencials.json"

# Directory to save uploaded videos
UPLOAD_DIR = "video"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Pydantic model for the response
class VideoResponse(BaseModel):
    query_id: str


@app.post("/upload_video", response_model=VideoResponse)
async def upload_video(file: UploadFile = File(...)):
    # Generate a unique query ID
    query_id = str(uuid.uuid4())

    # Save the video file
    video_path = os.path.join(UPLOAD_DIR, f"{query_id}.mp4")
    #video_path = "video/HY_2024_film_02.mp4" # FOR MOCKING
    with open(video_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Store file location with query ID
    video_storage[query_id] = {
        "video_path": video_path,
        "status": 50
    }
    await analyze_all(video_path, query_id)
    return JSONResponse(content={"query_id": query_id, "status": "50"})


@app.get("/video/{query_id}")
async def get_video(query_id: str):
    print(video_storage.keys())
    if query_id not in video_storage:
        raise HTTPException(status_code=404, detail="Video not found")

    data = video_storage[query_id].get("data")
    # Use jsonable_encoder to convert invalid float values to None (null in JSON)
    cleaned_data = clean_data(data)
    safe_data = jsonable_encoder(cleaned_data)
    if video_storage[query_id].get("status") == "200":
        return JSONResponse(content={"query_id": query_id, "data": safe_data})
    else:
        return JSONResponse(content={"query_id": query_id, "status": "100"})








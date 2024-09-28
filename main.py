from moviepy.editor import VideoFileClip
from google.cloud import speech_v1p1beta1 as speech
from pydub import AudioSegment
from text_analysis import extract_subtitles, compare_phonetic_text
import os

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import shutil
import os
import uuid
import time


from movement_analysis import analyze_movement
from text_analysis import analyze_text
from sentiment_analysis import analyze_sentiment, summarize
from analyze_audio_quality import analyze_audio_and_speech

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

def analyze_all(video_path, query_id):

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
    print("analysis completed")

    return data
        #video_storage[query_id]["status"] = "-1"
        #print("analysis completed")
# Example usage:



os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credencials.json"
#text_subtitles = extract_subtitles(video_path, "temp.srt")
#print(compare_phonetic_text(text, text_subtitles))
video_storage = {}
app = FastAPI()

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
    video_path = "video/HY_2024_film_02.mp4" # FOR MOCKING
    with open(video_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Store file location with query ID
    video_storage[query_id] = {
        "video_path": video_path,
        "status": 50
    }
    analyze_all(video_path, query_id)
    return JSONResponse(content={"query_id": query_id, "status": "50"})


@app.get("/video/{query_id}")
async def get_video(query_id: str):
    if query_id not in video_storage:
        raise HTTPException(status_code=404, detail="Video not found")

    if video_storage[query_id].get("status") == "200":
        return JSONResponse(content={"query_id": query_id, "data": video_storage["query_id"].get("Data")})
    else:
        return JSONResponse(content={"query_id": query_id, "status": "100"})








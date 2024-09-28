from moviepy.editor import VideoFileClip
from google.cloud import speech_v1p1beta1 as speech
from pydub import AudioSegment
from text_analysis import extract_subtitles, compare_phonetic_text
import os

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

def analyze_all(video_path):
    audio_path = "audio/" + video_path[6:-4] + ".wav"
    extract_audio_from_video(video_path, audio_path)
    convert_stereo_to_mono(audio_path, audio_path)
    text = transcribe_video(audio_path)["transcript"]
    analyze_text(text)
    analyze_movement(video_path)
    analyze_sentiment(text)
    summarize(text)
    analyze_audio_and_speech(video_path, audio_path, text)
# Example usage:




#text_subtitles = extract_subtitles(video_path, "temp.srt")
#print(compare_phonetic_text(text, text_subtitles))

def main():
    video_path = "video/HY_2024_film_02.mp4"
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credencials.json"
    analyze_all(video_path)

if __name__ == "__main__":
    main()


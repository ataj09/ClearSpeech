import cv2
import librosa
import numpy as np
from pydub import AudioSegment
from pydub.silence import detect_silence
import spacy

nlp = spacy.load("pl_core_news_sm")
# Function to detect silence
def detect_silence_intervals(audio_path):
    audio = AudioSegment.from_wav(audio_path)
    silence_intervals = detect_silence(audio, min_silence_len=500, silence_thresh=-50)
    silence_times = [(start / 1000, stop / 1000) for start, stop in silence_intervals]
    return silence_times


# Function to calculate average volume (dBFS)
def calculate_average_volume(audio_path):
    audio = AudioSegment.from_wav(audio_path)
    loudness_dB = audio.dBFS
    print(f"Average Volume (dBFS): {loudness_dB:.2f}")
    flag = ""
    if loudness_dB < -30:
        flag = "low"
    elif loudness_dB > -10:
        flag = "high"
    else:
        flag = "ok"

    return {"loudness": loudness_dB, "flag": flag}


# Function to calculate SNR (Signal-to-Noise Ratio)
def calculate_snr(audio_path, threshold=0.01):
    # Load audio file
    y, sr = librosa.load(audio_path, sr=None)

    # Identify non-silent sections based on the amplitude threshold
    non_silent_indices = np.where(np.abs(y) > threshold)[0]

    if non_silent_indices.size == 0:
        print("The audio is silent or below the threshold.")
        return {"snr": np.nan, "flag": "silent"}

    # Extract non-silent sections
    y_non_silent = y[non_silent_indices]

    # Calculate mean and std for non-silent sections
    signal_mean = np.mean(y_non_silent)
    signal_std = np.std(y_non_silent)

    # Calculate SNR
    if signal_std == 0:
        print("All non-silent sections have the same amplitude.")
        return {"snr": np.nan, "flag": "uniform signal"}

    snr = signal_mean / signal_std
    snr_dB = 10 * np.log10(snr)

    print(f"Signal-to-Noise Ratio (SNR): {snr_dB:.2f} dB")

    if snr_dB < 20:
        print("The audio has high background noise.")
        flag = "background noise"
    else:
        print("The audio has good clarity.")
        flag = "good clarity"

    return {"snr": snr_dB, "flag": flag}


# Function to calculate speech rate (words per minute)
def calculate_speech_rate(transcription, audio_path):
    y, sr = librosa.load(audio_path, sr=None)
    duration = librosa.get_duration(y=y, sr=sr)
    num_words = len(transcription.split())
    speech_rate = (num_words / duration) * 60
    flag = ""
    print(f"Speech Rate: {speech_rate:.2f} words per minute")

    if speech_rate < 100:
        print("The speech rate is too slow.")
        flag = "slow"
    elif speech_rate > 160:
        print("The speech rate is too fast.")
        flag = "fast"
    else:
        print("The speech rate is normal.")
        flag = "ok"
    return {"speech_rate": speech_rate, "flag": flag}

# DO THOSE
def identify_jargon(transcription, jargon_terms):
    detected_jargon = []
    for term in jargon_terms:
        if term in transcription:
            detected_jargon.append(term)
    return detected_jargon


# Step 6: Automatically detect foreign language words

# Main function to run all the analyses
def analyze_audio_and_speech(video_path, audio_path, transcription):
    jargon_terms = ["technologia", "innowacja", "efektywny"]  # Example jargon terms
    data = {}
    # Step 2: Detect silence intervals
    data["silence_intervals"] = detect_silence_intervals(audio_path)

    # Step 3: Calculate average volume
    data["average_volume"] = calculate_average_volume(audio_path)

    # Step 4: Calculate SNR (Signal-to-Noise Ratio)
    data["snr"] = calculate_snr(audio_path)

    # Step 5: Calculate speech rate based on transcription
    data["speech_rate"] = calculate_speech_rate(transcription, audio_path)




    return data


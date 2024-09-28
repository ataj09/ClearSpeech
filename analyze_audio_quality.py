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
    print("Detected silence intervals (start, stop) in seconds:")
    for start, stop in silence_times:
        print(f"Silence from {start}s to {stop}s")


# Function to calculate average volume (dBFS)
def calculate_average_volume(audio_path):
    audio = AudioSegment.from_wav(audio_path)
    loudness_dB = audio.dBFS
    print(f"Average Volume (dBFS): {loudness_dB:.2f}")

    if loudness_dB < -30:
        print("The audio is too quiet.")
    elif loudness_dB > -10:
        print("The audio is too loud.")
    else:
        print("The volume level is acceptable.")


# Function to calculate SNR (Signal-to-Noise Ratio)
def calculate_snr(audio_path):
    y, sr = librosa.load(audio_path, sr=None)
    signal_mean = np.mean(y)
    signal_std = np.std(y)
    snr = signal_mean / signal_std
    snr_dB = 10 * np.log10(snr)
    print(f"Signal-to-Noise Ratio (SNR): {snr_dB:.2f} dB")

    if snr_dB < 20:
        print("The audio has high background noise.")
    else:
        print("The audio has good clarity.")


# Function to calculate speech rate (words per minute)
def calculate_speech_rate(transcription, audio_path):
    y, sr = librosa.load(audio_path, sr=None)
    duration = librosa.get_duration(y=y, sr=sr)
    num_words = len(transcription.split())
    speech_rate = (num_words / duration) * 60
    print(f"Speech Rate: {speech_rate:.2f} words per minute")

    if speech_rate < 100:
        print("The speech rate is too slow.")
    elif speech_rate > 160:
        print("The speech rate is too fast.")
    else:
        print("The speech rate is normal.")


# Function to detect speech activity based on energy levels (RMS)
def detect_speech_activity(audio_path, threshold=0.02):
    y, sr = librosa.load(audio_path, sr=None)

    # Calculate short-time energy using RMS
    rms = librosa.feature.rms(y=y)[0]

    # Speech is detected when RMS energy exceeds the threshold
    speech_activity = rms > threshold

    # Convert frame indices to time (in seconds)
    times = librosa.frames_to_time(np.arange(len(rms)), sr=sr)

    # Identify speech and non-speech segments
    speech_times = [(times[i], speech_activity[i]) for i in range(len(speech_activity))]

    print("Detected speech activity (time, is_speech):")
    for time, is_speech in speech_times:
        print(f"Time: {time:.2f}s, Speech: {'Yes' if is_speech else 'No'}")

def identify_jargon(transcription, jargon_terms):
    detected_jargon = []
    for term in jargon_terms:
        if term in transcription:
            detected_jargon.append(term)
    return detected_jargon


# Step 6: Automatically detect foreign language words
def detect_foreign_language(transcription):
    foreign_words_detected = []
    doc = nlp(transcription)

    for token in doc:
        # Using spaCy's language model to check if the word is in the known language
        if not token.is_alpha or token.is_stop:  # Skip punctuation and stop words
            continue

        # Here, you can customize to check against a foreign language list if needed
        if token.lang_ != "pl":  # Check if the token is not Polish
            foreign_words_detected.append(token.text)

    return foreign_words_detected



# Main function to run all the analyses
def analyze_audio_and_speech(video_path, audio_path, transcription):
    jargon_terms = ["technologia", "innowacja", "efektywny"]  # Example jargon terms

    # Step 2: Detect silence intervals
    detect_silence_intervals(audio_path)

    # Step 3: Calculate average volume
    calculate_average_volume(audio_path)

    # Step 4: Calculate SNR (Signal-to-Noise Ratio)
    calculate_snr(audio_path)

    # Step 5: Calculate speech rate based on transcription
    calculate_speech_rate(transcription, audio_path)

    # Step 6: Detect speech activity based on energy levels
    detect_speech_activity(audio_path)




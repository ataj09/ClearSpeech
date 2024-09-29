import pysrt
import spacy
import textstat
import ffmpeg
import subprocess
# Load the Polish language model
nlp = spacy.load("pl_core_news_sm")
from moviepy.editor import VideoFileClip


def extract_subtitles_with_moviepy(video_file):
    video = VideoFileClip(video_file)
    if not video:
        print("Error opening video file.")
        return None

    # Attempt to extract subtitles (if available)
    for sub in video.subtitles:
        print(f"Subtitle: {sub}")

def calculate_readability(text):
    # Calculate readability scores
    flesch_score = textstat.flesch_reading_ease(text)
    gunning_fog_score = textstat.gunning_fog(text)

    return flesch_score, gunning_fog_score


def detect_language_errors(text):
    doc = nlp(text)
    errors = []

    # Check for long sentences
    for sent in doc.sents:
        if len(sent) > 20:  # Example criterion: more than 20 words
            errors.append("Long sentence: {}".format(sent.text))

    # Check for jargon or complex words
    complex_words = ['efektywny', 'przedsiębiorstwo']  # Example complex words
    for token in doc:
        if token.text in complex_words:
            errors.append("Jargon detected: {}".format(token.text))

    return errors

def analyze_text(text):
    flesch, gunning_fog = calculate_readability(text)
    language_errors = detect_language_errors(text)
    return {"flesch": flesch, "gunning": gunning_fog, "errors": language_errors}



def extract_subtitles(video_file, output_srt_file):
    command = [
        'ffmpeg',
        '-i', video_file,
        '-map', '0:s:0',
        output_srt_file,
        '-y'  # Overwrite existing file
    ]

    try:
        subprocess.run(command, check=True)
        print(f"Subtitles extracted to {output_srt_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error extracting subtitles: {e}")

    subs = pysrt.open(output_srt_file)
    subtitle_texts = [sub.text for sub in subs]
    return " ".join(subtitle_texts)

def compare_phonetic_text(text1, text2):
    doc1 = nlp(text1)
    doc2 = nlp(text2)

    # Calculate similarity between the two documents
    similarity = doc1.similarity(doc2)
    return similarity


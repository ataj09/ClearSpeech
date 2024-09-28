import cv2
from pydub import AudioSegment


def extract_audio_from_video(video_path, output_audio_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error opening video file")
        return None

    # Extract audio using moviepy or directly from the video
    video = cv2.VideoCapture(video_path)
    frame_rate = video.get(cv2.CAP_PROP_FPS)
    video.release()

    audio = AudioSegment.from_file(video_path, format="mp4")
    audio.export(output_audio_path, format="wav")
    return output_audio_path


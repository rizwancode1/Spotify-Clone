# music/utils.py
import os
from os.path import normpath
import uuid
from pydub import AudioSegment
from pydub.playback import play
from PIL import Image
from django.core.validators import FileExtensionValidator

def generate_thumbnail(image_field, thumbnail_size=(640, 360)):
    image = Image.open(image_field.path)
    image.thumbnail(thumbnail_size)
    thumbnail_path = os.path.join('thumbnails/', f"thumbnail_{image_field.name}")
    image.save(thumbnail_path)
    return thumbnail_path


def calculate_length_with_pydub(audio_field):
    audio_path = audio_field.path

    # Normalize the path
    audio_path = normpath(audio_path)

    print(f"Audio path: {audio_path}")

    try:
        audio = AudioSegment.from_file(f"{audio_path}")
        play(audio)
        length_in_seconds = len(audio) // 1000
        return length_in_seconds
    except Exception as e:
        print(f"Error while extracting length: {e}")
        return None
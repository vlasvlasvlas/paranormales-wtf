import os
import json
from dotenv import load_dotenv
from functions import (
    download_audio_from_youtube,
    transcribe_audio,
    classify_story_with_examples,
    save_stories_to_db,
    identify_story_timestamps
)

# Cargar variables de entorno
load_dotenv(".env", override=True)

# Variables de entorno
AUDIO_FILE = 'audio.mp3'
DB_FILE = 'stories.db'
PROMPT_EXAMPLES_FILE = 'prompt_examples.json'
VIDEOS_FILE = 'videos.json'

def main():
    """
    Procesa los videos de YouTube y guarda las historias en una base de datos.
    """
    try:
        # Leer URLs de videos desde el archivo JSON
        with open(VIDEOS_FILE, 'r') as f:
            videos = json.load(f)
        
        for video in videos:
            youtube_url = video['url']
            date = video['fecha']
            print(f"Procesando video: {youtube_url} del {date}")

            # Descargar y extraer audio
            download_audio_from_youtube(youtube_url, AUDIO_FILE)

            # Transcribir audio a texto
            text, timestamps = transcribe_audio(AUDIO_FILE)

            # Clasificar historias
            classified_stories = classify_story_with_examples(text, PROMPT_EXAMPLES_FILE)

            # Identificar timestamps de las historias
            identified_stories = identify_story_timestamps(classified_stories, timestamps)

            # Guardar en la base de datos
            save_stories_to_db(identified_stories, DB_FILE)
        
        print("Proceso completado exitosamente.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
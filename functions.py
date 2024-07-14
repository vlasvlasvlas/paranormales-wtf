import os
import youtube_dl
import whisper
import json
import openai
import sqlite3

def download_audio_from_youtube(youtube_url, output_file):
    """
    Descarga el audio de un video de YouTube y lo guarda en un archivo de salida.
    Parametros:
    youtube_url (str): URL del video de YouTube.
    output_file (str): Nombre del archivo de salida.
    """
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': output_file
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])

def transcribe_audio(audio_file):
    """
    Transcribe el audio a texto utilizando el modelo Whisper de OpenAI.
    Parametros:
    audio_file (str): Nombre del archivo de audio.
    
    Retorna:
    text (str): Texto transcrito.
    timestamps (list): Timestamps de los segmentos transcritos.
    """
    model = whisper.load_model("base")
    result = model.transcribe(audio_file)
    text = result['text']
    timestamps = result['segments']
    return text, timestamps

def classify_story_with_examples(text, examples_file):
    """
    Clasifica historias utilizando GPT-4 con ejemplos de few-shot learning.
    Parametros:
    text (str): Texto a clasificar.
    examples_file (str): Nombre del archivo JSON con ejemplos.

    Retorna:
    classified_stories (list): Lista de historias clasificadas.
    """
    with open(examples_file, 'r') as f:
        examples_data = json.load(f)
        examples = ""
        for example in examples_data["examples"]:
            examples += f"Historia: {example['story']}\nClasificación: {example['classification']}\n\n"

    openai.api_key = os.getenv('OPENAI_API_KEY')

    def classify_story(story_text):
        prompt = f"{examples}Historia a clasificar: {story_text}\nClasificación:"
        response = openai.Completion.create(
            model="gpt-4",
            prompt=prompt,
            max_tokens=10
        )
        return response.choices[0].text.strip()

    stories = text.split("SEPARADOR_DE_HISTORIAS")  # Define un separador adecuado
    classified_stories = [(story, classify_story(story)) for story in stories]
    return classified_stories

def identify_story_timestamps(classified_stories, timestamps):
    """
    Identifica los timestamps de las historias clasificadas.
    Parametros:
    classified_stories (list): Lista de historias clasificadas.
    timestamps (list): Timestamps de los segmentos transcritos.

    Retorna:
    identified_stories (list): Lista de historias con sus timestamps identificados.
    """
    identified_stories = []
    for story, classification in classified_stories:
        start_time = next((segment['start'] for segment in timestamps if segment['text'] in story), None)
        if start_time:
            identified_stories.append((story, classification, start_time))
    return identified_stories

def save_stories_to_db(classified_stories, db_file):
    """
    Guarda las historias clasificadas en una base de datos SQLite.
    Parametros:
    classified_stories (list): Lista de historias clasificadas con timestamps.
    db_file (str): Nombre del archivo de la base de datos.
    """
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS stories (story TEXT, classification TEXT, start_time TEXT)''')

    for story, classification, start_time in classified_stories:
        c.execute("INSERT INTO stories (story, classification, start_time) VALUES (?, ?, ?)", (story, classification, start_time))
    
    conn.commit()
    conn.close()

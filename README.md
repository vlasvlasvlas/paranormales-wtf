# Paranormales-WTF: Clasificación de Historias Paranormales Misteriosamente Absurdas y Divertidas

Este proyecto toma videos de YouTube del canal "La Noche Paranormal", extrae el audio, lo transcribe a texto y clasifica las historias en diferentes categorías usando un modelo de lenguaje LLM (en este caso, Llama 3 con few-shot learning).

![alt text](image.png)

## Para Qué Es Esto o Por Qué Hago Esto

Me encantan las historias rarísimas que cuentan en "La Noche Paranormal" y me cuesta mucho encontrarlas. Así que hice esto para poder encontrarlas más a mano, de manera más simple. Además, quiero poner en práctica el encadenamiento de modelos de diferentes tipos (video > audio > texto > identificación).

## Paso a Paso: La Cadena de Proceso

1. **Descargar Audio de YouTube**: Se utiliza `youtube-dl` para descargar el video de YouTube y extraer el audio en formato MP3.
2. **Dividir Audio en Segmentos**: Utiliza `pydub` para dividir el audio en segmentos basados en pausas largas.
3. **Transcribir Audio a Texto**: Se emplea `Whisper de OpenAI` para convertir el audio en texto, identificando los timestamps.
4. **Clasificar Historias**: Utilizando GPT-4 o Llama 3 con ejemplos de few-shot learning, se clasifican las historias en "misteriosamente absurdas y divertidas", "paranormal bizarra" o "normal".
5. **Identificar Timestamps**: Se asocian los timestamps de las transcripciones con las historias clasificadas para poder ubicarlas en el video original.
6. **Guardar en la Base de Datos**: Las historias clasificadas junto con sus timestamps se almacenan en una base de datos SQLite (`stories.db`) para un acceso y gestión fáciles.

## Requisitos

- Python 3.7+
- youtube-dl
- pydub
- Whisper de OpenAI
- OpenAI GPT-4 o Llama 3
- dotenv

## Instalación

1. Clonar el repositorio.
2. Crear un archivo `requirements.txt` con el siguiente contenido:
    ```text
    youtube-dl
    pydub
    openai-whisper
    openai
    python-dotenv
    ```
3. Instalar las dependencias:
    ```bash
    pip install -r requirements.txt
    ```
4. Crear un archivo `.env` en la raíz del proyecto con las siguientes variables:
    ```
    OPENAI_API_KEY=your_openai_api_key
    ```

## Uso

1. Colocar las URLs de los videos de YouTube en el archivo `videos.json` con el formato:
    ```json
    [
        {
            "url": "https://www.youtube.com/watch?v=9XvvBI9Zols",
            "fecha": "2024-07-11"
        },
        {
            "url": "https://www.youtube.com/watch?v=4lzhpXm3IHA",
            "fecha": "2024-07-10"
        }
    ]
    ```
2. Ejecutar el script principal:
    ```bash
    python main.py
    ```
3. Las historias clasificadas se guardarán en `stories.db`.

## Estructura del Proyecto

- `main.py`: Script principal que coordina todas las funciones.
- `functions.py`: Contiene todas las funciones compartimentadas.
- `prompt_examples.json`: Archivo JSON que contiene los ejemplos para few-shot learning.
- `videos.json`: Archivo JSON que contiene las URLs de los videos de YouTube y sus fechas.
- `.env`: Archivo para almacenar variables de entorno.
- `README.md`: Instrucciones y descripción del proyecto.

## Identificación de Timestamps

Al final, quisiera identificar los timestamps de las historias para poder escucharlas en el video original pasando el parámetro `?t=` al clip de YouTube y poder escucharlas directamente. Esto no está todavía en la agenda y podrían ayudarme con eso.

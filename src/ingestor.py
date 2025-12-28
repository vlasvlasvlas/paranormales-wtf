#!/usr/bin/env python3
"""
Ingestor de subtítulos de YouTube
Extrae subtítulos automáticos de videos de YouTube y los guarda localmente.
"""
import json
import os
from pathlib import Path
from youtube_transcript_api import YouTubeTranscriptApi


def extract_video_id(url: str) -> str:
    """Extrae el video_id de una URL de YouTube"""
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    return url


def fetch_subtitles(video_id: str, languages: list = None) -> dict | None:
    """
    Obtiene subtítulos de un video de YouTube.
    
    Args:
        video_id: ID del video de YouTube
        languages: Lista de códigos de idioma a intentar (default: español)
    
    Returns:
        Dict con video_id, language y segments, o None si falla
    """
    if languages is None:
        languages = ['es', 'es-419', 'es-ES']
    
    try:
        ytt_api = YouTubeTranscriptApi()
        data = ytt_api.fetch(video_id, languages=languages)
        
        # Convertir a lista de dicts serializables
        segments = []
        for item in data:
            segments.append({
                "start": round(item.start, 2),
                "duration": round(item.duration, 2),
                "text": item.text
            })
        
        return {
            "video_id": video_id,
            "language": "es",
            "total_segments": len(segments),
            "segments": segments
        }
    except Exception as e:
        print(f"❌ Error extrayendo subtítulos de {video_id}: {e}")
        return None


def save_subtitles(data: dict, output_dir: str = "data/subtitulos") -> str:
    """Guarda los subtítulos en un archivo JSON"""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    output_path = os.path.join(output_dir, f"{data['video_id']}.json")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return output_path


def process_videos_input(input_file: str = "data/videos_input.json") -> list:
    """
    Procesa todos los videos del archivo de entrada.
    
    Returns:
        Lista de video_ids procesados exitosamente
    """
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    processed = []
    
    for video in data.get("videos", []):
        video_id = video.get("video_id") or extract_video_id(video.get("url", ""))
        
        if not video_id:
            print(f"⚠️ No se pudo obtener video_id para: {video}")
            continue
        
        # Verificar si ya está descargado
        output_path = f"data/subtitulos/{video_id}.json"
        if os.path.exists(output_path):
            print(f"⏭️ Ya existe: {video_id}")
            processed.append(video_id)
            continue
        
        print(f"📥 Descargando subtítulos: {video_id}")
        result = fetch_subtitles(video_id)
        
        if result:
            save_subtitles(result)
            print(f"✅ Guardado: {output_path} ({result['total_segments']} segmentos)")
            processed.append(video_id)
        else:
            print(f"❌ Falló: {video_id}")
    
    return processed


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Procesar URL o video_id específico
        video_id = extract_video_id(sys.argv[1])
        print(f"📥 Descargando subtítulos: {video_id}")
        result = fetch_subtitles(video_id)
        if result:
            path = save_subtitles(result)
            print(f"✅ Guardado: {path}")
            print(f"📊 Total segmentos: {result['total_segments']}")
    else:
        # Procesar todos los videos del archivo de entrada
        processed = process_videos_input()
        print(f"\n📊 Procesados: {len(processed)} videos")

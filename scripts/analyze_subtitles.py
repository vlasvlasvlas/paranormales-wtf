#!/usr/bin/env python3
"""
Analizador de subtítulos - Genera una vista del contenido para identificar 
manualmente patrones de inicio/fin de historias.
"""
import json
import sys
from pathlib import Path


def format_timestamp(seconds: float) -> str:
    """Convierte segundos a formato HH:MM:SS"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def analyze_subtitles(video_id: str, 
                      output_format: str = "txt",
                      chunk_duration: int = 60) -> None:
    """
    Analiza subtítulos y genera un reporte legible.
    
    Args:
        video_id: ID del video
        output_format: 'txt' o 'md'
        chunk_duration: Duración en segundos para agrupar segmentos
    """
    input_path = f"data/subtitulos/{video_id}.json"
    
    if not Path(input_path).exists():
        print(f"❌ No existe: {input_path}")
        return
    
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    segments = data['segments']
    total_duration = segments[-1]['start'] + segments[-1]['duration'] if segments else 0
    
    print(f"\n{'='*70}")
    print(f"📺 Video: {video_id}")
    print(f"📊 Total segmentos: {len(segments)}")
    print(f"⏱️  Duración: {format_timestamp(total_duration)}")
    print(f"{'='*70}\n")
    
    # Generar texto combinado por chunks de tiempo
    current_chunk_start = 0
    current_chunk_text = []
    
    output_lines = []
    
    for seg in segments:
        # Si pasamos al siguiente chunk, guardar el anterior
        while seg['start'] >= current_chunk_start + chunk_duration:
            if current_chunk_text:
                chunk_text = ' '.join(current_chunk_text)
                ts = format_timestamp(current_chunk_start)
                yt_link = f"https://youtube.com/watch?v={video_id}&t={int(current_chunk_start)}s"
                
                output_lines.append(f"\n[{ts}] ({yt_link})")
                output_lines.append("-" * 50)
                output_lines.append(chunk_text)
                output_lines.append("")
                
                current_chunk_text = []
            current_chunk_start += chunk_duration
        
        current_chunk_text.append(seg['text'])
    
    # Último chunk
    if current_chunk_text:
        chunk_text = ' '.join(current_chunk_text)
        ts = format_timestamp(current_chunk_start)
        yt_link = f"https://youtube.com/watch?v={video_id}&t={int(current_chunk_start)}s"
        output_lines.append(f"\n[{ts}] ({yt_link})")
        output_lines.append("-" * 50)
        output_lines.append(chunk_text)
    
    # Guardar archivo
    output_path = f"data/subtitulos/{video_id}_analisis.txt"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"Análisis de: {video_id}\n")
        f.write(f"Duración: {format_timestamp(total_duration)}\n")
        f.write(f"Chunks de {chunk_duration} segundos\n")
        f.write("=" * 70 + "\n")
        f.write('\n'.join(output_lines))
    
    print(f"✅ Guardado: {output_path}")
    
    # Mostrar primeros chunks
    print("\n📝 Primeros 5 chunks:\n")
    for line in output_lines[:25]:
        print(line)
    print("\n... (ver archivo completo para más)")


def find_potential_story_starts(video_id: str) -> list:
    """
    Busca patrones que típicamente indican inicio de historias.
    """
    input_path = f"data/subtitulos/{video_id}.json"
    
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Patrones de inicio de historia
    patterns = [
        "me escribe",
        "nos escribe", 
        "la siguiente historia",
        "vamos con otra",
        "les cuento",
        "esta historia",
        "bueno, ahora",
        "hola,",  # Inicio de llamada
        "muy buenas noches",  # Saludo de oyente
        "¿de dónde sos",  # Pregunta típica del conductor
        "¿de dónde nos",
    ]
    
    potential_starts = []
    
    # Combinar segmentos cercanos para contexto
    window_size = 5
    for i, seg in enumerate(data['segments']):
        context = ' '.join([s['text'].lower() for s in data['segments'][max(0, i-2):i+window_size]])
        
        for pattern in patterns:
            if pattern in context.lower():
                potential_starts.append({
                    "timestamp": seg['start'],
                    "timestamp_fmt": format_timestamp(seg['start']),
                    "pattern": pattern,
                    "context": context[:200],
                    "youtube_url": f"https://youtube.com/watch?v={video_id}&t={int(seg['start'])}s"
                })
                break  # Solo un match por segmento
    
    # Eliminar duplicados cercanos (menos de 30 segundos)
    filtered = []
    last_ts = -60
    for item in potential_starts:
        if item['timestamp'] - last_ts > 30:
            filtered.append(item)
            last_ts = item['timestamp']
    
    return filtered


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 analyze_subtitles.py <video_id> [chunk_duration]")
        print("Ejemplo: python3 analyze_subtitles.py n2BkstRXbV0 60")
        sys.exit(1)
    
    video_id = sys.argv[1]
    chunk_duration = int(sys.argv[2]) if len(sys.argv) > 2 else 60
    
    # Análisis general
    analyze_subtitles(video_id, chunk_duration=chunk_duration)
    
    # Buscar inicios potenciales de historias
    print("\n" + "=" * 70)
    print("🔍 Posibles inicios de historias detectados:")
    print("=" * 70)
    
    starts = find_potential_story_starts(video_id)
    for i, s in enumerate(starts[:20], 1):
        print(f"\n{i}. [{s['timestamp_fmt']}] Pattern: '{s['pattern']}'")
        print(f"   🔗 {s['youtube_url']}")
        print(f"   📝 {s['context'][:100]}...")
    
    print(f"\n📊 Total posibles historias: {len(starts)}")

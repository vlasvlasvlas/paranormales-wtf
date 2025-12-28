#!/usr/bin/env python3
"""
Prueba de extracción de subtítulos de YouTube (API v1.2+)
"""
from youtube_transcript_api import YouTubeTranscriptApi
import json

def extract_subtitles(video_id: str) -> dict:
    """Extrae subtítulos de un video de YouTube"""
    try:
        # Nueva API v1.2+ - usar fetch directamente
        ytt_api = YouTubeTranscriptApi()
        data = ytt_api.fetch(video_id, languages=['es', 'es-419', 'es-ES'])
        
        # Convertir a lista de dicts
        segments = []
        for item in data:
            segments.append({
                "start": item.start,
                "duration": item.duration,
                "text": item.text
            })
        
        return {
            "video_id": video_id,
            "language": "es",
            "segments": segments
        }
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    video_id = "n2BkstRXbV0"
    
    print(f"Extrayendo subtítulos del video: {video_id}")
    result = extract_subtitles(video_id)
    
    if result:
        # Guardar resultado completo
        output_file = f"data/subtitulos/{video_id}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Guardado en: {output_file}")
        print(f"📊 Total segmentos: {len(result['segments'])}")
        
        # Calcular duración total
        if result['segments']:
            last_seg = result['segments'][-1]
            total_mins = int((last_seg['start'] + last_seg['duration']) // 60)
            print(f"⏱️ Duración aproximada: {total_mins} minutos")
        
        # Mostrar primeros 15 segmentos como muestra
        print("\n📝 Primeros 15 segmentos:")
        print("-" * 70)
        for seg in result['segments'][:15]:
            mins = int(seg['start'] // 60)
            secs = int(seg['start'] % 60)
            print(f"[{mins:02d}:{secs:02d}] {seg['text']}")
        
        print("\n" + "-" * 70)
        print("📝 Segmentos del medio (minuto 30):")
        print("-" * 70)
        mid_segments = [s for s in result['segments'] if 1800 <= s['start'] <= 1860]
        for seg in mid_segments[:10]:
            mins = int(seg['start'] // 60)
            secs = int(seg['start'] % 60)
            print(f"[{mins:02d}:{secs:02d}] {seg['text']}")

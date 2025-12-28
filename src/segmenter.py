#!/usr/bin/env python3
"""
Segmentador de historias - Usa heurísticas y patrones para detectar 
inicio/fin de historias en los subtítulos.
"""
import json
import re
from pathlib import Path
from datetime import datetime


def load_subtitles(video_id: str) -> dict:
    """Carga subtítulos de un video"""
    path = f"data/subtitulos/{video_id}.json"
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def format_timestamp(seconds: float) -> str:
    """Convierte segundos a formato MM:SS"""
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins:02d}:{secs:02d}"


def combine_segments_in_range(segments: list, start_time: float, end_time: float) -> str:
    """Combina el texto de segmentos en un rango de tiempo"""
    texts = []
    for seg in segments:
        seg_start = seg['start']
        seg_end = seg_start + seg.get('duration', 0)
        # Si el segmento está en el rango
        if seg_start >= start_time and seg_start < end_time:
            texts.append(seg['text'])
    return ' '.join(texts)


def detect_story_boundaries(segments: list) -> list:
    """
    Detecta inicio de historias usando patrones típicos del programa.
    
    Retorna lista de historias detectadas con timestamps.
    """
    # Patrones que típicamente indican inicio de historia
    patterns_inicio = [
        # Saludos a oyentes en vivo
        r"hola,?\s+\w+[,.]?\s*(cómo|como)\s+(te va|estás|andás)",
        r"buenas noches.*bienvenid",
        r"hola.*buenas noches",
        r"te escuchamos",
        r"contanos.*historia",
        r"escuchamos tu historia",
        
        # Historias escritas/audios
        r"me escribe\s+\w+",
        r"nos escribe\s+\w+",
        r"soy\s+\w+\s+de\s+\w+",
        r"te habla\s+\w+",
        r"mi nombre es\s+\w+",
        r"hola.*quería contar",
        r"quería compartir",
        r"te cuento.*historia",
        r"voy a contar",
        
        # Transiciones
        r"vamos con otra",
        r"la siguiente historia",
        r"hay más historias",
        r"tengo.*que está.*vivo",
        r"está.*en vivo.*nosotros",
        r"vamos a saludar",
        
        # Inicios de audios WhatsApp
        r"hola\s+héctor",
        r"buenas noches\s+héctor",
        r"hola\s+chicos",
    ]
    
    # Patrones que indican FIN de historia / transición
    patterns_fin = [
        r"gracias por (contar|compartir|llamar)",
        r"un abrazo",
        r"cuídate",
        r"chao",
        r"seguimos con",
        r"vamos a (una pausa|corte)",
        r"ya (volvemos|regresamos)",
    ]
    
    # Combinar texto en ventanas de tiempo para mejor detección
    window_seconds = 30  # Ventana de 30 segundos
    
    stories = []
    current_story_start = None
    current_context = ""
    
    # Crear índice de texto por tiempo
    text_by_time = {}
    for seg in segments:
        time_key = int(seg['start'] // window_seconds) * window_seconds
        if time_key not in text_by_time:
            text_by_time[time_key] = []
        text_by_time[time_key].append(seg)
    
    # Buscar inicios de historias
    potential_starts = []
    
    for time_key in sorted(text_by_time.keys()):
        segs = text_by_time[time_key]
        combined_text = ' '.join([s['text'] for s in segs]).lower()
        
        for pattern in patterns_inicio:
            if re.search(pattern, combined_text, re.IGNORECASE):
                # Encontrar el timestamp más preciso
                first_seg = segs[0]
                potential_starts.append({
                    'start': first_seg['start'],
                    'pattern': pattern,
                    'context': combined_text[:200]
                })
                break
    
    # Eliminar duplicados cercanos (menos de 60 segundos)
    filtered_starts = []
    last_time = -120
    for start in potential_starts:
        if start['start'] - last_time > 60:
            filtered_starts.append(start)
            last_time = start['start']
    
    # Crear historias con estimación de duración
    for i, start in enumerate(filtered_starts):
        # Fin es el inicio de la siguiente historia o +10 minutos
        if i < len(filtered_starts) - 1:
            end_time = filtered_starts[i + 1]['start']
        else:
            end_time = start['start'] + 600  # 10 minutos por defecto
        
        # Limitar duración máxima a 15 minutos
        if end_time - start['start'] > 900:
            end_time = start['start'] + 600
        
        # Extraer texto completo de la historia
        full_text = combine_segments_in_range(segments, start['start'], end_time)
        
        stories.append({
            'id': i + 1,
            'timestamp_inicio': round(start['start'], 1),
            'timestamp_fin': round(end_time, 1),
            'timestamp_fmt': format_timestamp(start['start']),
            'duracion_segundos': round(end_time - start['start'], 1),
            'patron_detectado': start['pattern'],
            'texto_completo': full_text,
            'clasificacion': None,  # Para llenar después
        })
    
    return stories


def segment_video(video_id: str) -> dict:
    """
    Procesa un video y genera su segmentación.
    """
    print(f"\n🔍 Segmentando video: {video_id}")
    
    # Cargar subtítulos
    data = load_subtitles(video_id)
    segments = data['segments']
    
    print(f"   📊 Total segmentos de subtítulos: {len(segments)}")
    
    # Detectar historias
    stories = detect_story_boundaries(segments)
    
    print(f"   📚 Historias detectadas: {len(stories)}")
    
    # Crear resultado
    result = {
        "video_id": video_id,
        "fecha_segmentacion": datetime.now().isoformat(),
        "total_historias": len(stories),
        "metodo": "heuristicas_v1",
        "historias": stories
    }
    
    # Guardar
    output_path = f"data/segmentacion/{video_id}.json"
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"   ✅ Guardado: {output_path}")
    
    # Mostrar resumen
    print(f"\n   📋 Historias encontradas:")
    for story in stories[:10]:
        print(f"      [{story['timestamp_fmt']}] {story['texto_completo'][:60]}...")
    
    if len(stories) > 10:
        print(f"      ... y {len(stories) - 10} más")
    
    return result


def update_pipeline_status(video_id: str, total_historias: int):
    """Actualiza el estado del pipeline"""
    status_path = "data/pipeline_status.json"
    
    with open(status_path, 'r', encoding='utf-8') as f:
        status = json.load(f)
    
    # Encontrar y actualizar el video
    for video in status['videos']:
        if video['video_id'] == video_id:
            video['estado']['segmentacion'] = 'completado'
            video['metricas']['historias_detectadas'] = total_historias
            video['metricas']['historias_pendientes'] = total_historias
            video['timestamps']['segmentacion_completada'] = datetime.now().isoformat()
            break
    
    # Actualizar resumen global
    status['resumen_global']['total_historias'] = sum(
        v['metricas']['historias_detectadas'] for v in status['videos']
    )
    status['ultima_actualizacion'] = datetime.now().isoformat()
    
    with open(status_path, 'w', encoding='utf-8') as f:
        json.dump(status, f, ensure_ascii=False, indent=2)
    
    print(f"   📊 Pipeline status actualizado")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        video_id = sys.argv[1]
    else:
        video_id = "n2BkstRXbV0"
    
    result = segment_video(video_id)
    update_pipeline_status(video_id, result['total_historias'])

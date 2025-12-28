#!/usr/bin/env python3
"""
Exporta las historias clasificadas a formato JSON para la web.
"""
import json
from pathlib import Path
from datetime import datetime


def load_pipeline_status() -> dict:
    """Carga el estado del pipeline"""
    with open("data/pipeline_status.json", 'r', encoding='utf-8') as f:
        return json.load(f)


def load_segmentation(video_id: str) -> dict:
    """Carga la segmentación de un video"""
    path = f"data/segmentacion/{video_id}.json"
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {'historias': []}


def load_video_info(video_id: str) -> dict:
    """Carga info del video desde videos_input.json"""
    try:
        with open("data/videos_input.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
            for video in data.get('videos', []):
                if video.get('id') == video_id:
                    return video
    except FileNotFoundError:
        pass
    return {}


def export_for_web():
    """
    Exporta todas las historias clasificadas a web/data/historias.json
    """
    print("\n📤 Exportando historias para la web...")
    
    status = load_pipeline_status()
    all_historias = []
    
    for video in status['videos']:
        video_id = video['video_id']
        
        # Cargar segmentación
        seg_data = load_segmentation(video_id)
        video_info = load_video_info(video_id)
        
        fecha_emision = video.get('fecha_emision') or video_info.get('fecha', '')
        titulo_video = video.get('titulo') or video_info.get('titulo', '')
        
        for historia in seg_data.get('historias', []):
            clf = historia.get('clasificacion', {})
            
            # Solo exportar historias clasificadas y que son historias reales
            if not clf.get('verificado_humano') or not clf.get('es_historia', True):
                continue
            
            # Construir URL de YouTube
            timestamp = int(historia['timestamp_inicio'])
            youtube_url = f"https://www.youtube.com/watch?v={video_id}&t={timestamp}s"
            
            export_historia = {
                'id': len(all_historias) + 1,
                'video_id': video_id,
                'video_titulo': titulo_video,
                'timestamp_inicio': historia['timestamp_inicio'],
                'timestamp_fin': historia.get('timestamp_fin', historia['timestamp_inicio'] + 300),
                'timestamp_fmt': historia.get('timestamp_fmt', ''),
                'titulo_inferido': clf.get('titulo', 'Historia sin título'),
                'resumen': clf.get('resumen', ''),
                'categoria': clf.get('categoria', 'otros'),
                'subcategoria': clf.get('subcategoria', 'general'),
                'tipo_narrador': clf.get('tipo_narrador', 'oyente'),
                'wtf_score': clf.get('wtf_score', 0.5),
                'verificado_humano': True,
                'fecha_emision': fecha_emision,
                'youtube_url': youtube_url
            }
            
            all_historias.append(export_historia)
    
    # Ordenar por WTF score (más alto primero)
    all_historias.sort(key=lambda x: x['wtf_score'], reverse=True)
    
    # Construir archivo de exportación
    export_data = {
        'generated_at': datetime.now().isoformat(),
        'total': len(all_historias),
        'historias': all_historias
    }
    
    # Guardar
    output_path = Path("web/data/historias.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)
    
    print(f"   ✅ Exportadas {len(all_historias)} historias a {output_path}")
    
    # Actualizar estado del pipeline
    for video in status['videos']:
        video['estado']['exportado_web'] = 'completado'
    
    status['ultima_actualizacion'] = datetime.now().isoformat()
    
    with open("data/pipeline_status.json", 'w', encoding='utf-8') as f:
        json.dump(status, f, ensure_ascii=False, indent=2)
    
    print("   📊 Pipeline status actualizado")
    
    return len(all_historias)


def print_stats():
    """Imprime estadísticas del dataset"""
    try:
        with open("web/data/historias.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("   ❌ No hay datos exportados aún")
        return
    
    historias = data.get('historias', [])
    
    print("\n📊 ESTADÍSTICAS:")
    print(f"   Total de historias: {len(historias)}")
    
    # Por categoría
    categorias = {}
    for h in historias:
        cat = h.get('categoria', 'otros')
        categorias[cat] = categorias.get(cat, 0) + 1
    
    print("\n   Por categoría:")
    for cat, count in sorted(categorias.items(), key=lambda x: x[1], reverse=True):
        print(f"      {cat}: {count}")
    
    # WTF promedio
    if historias:
        avg_wtf = sum(h.get('wtf_score', 0.5) for h in historias) / len(historias)
        print(f"\n   WTF Score promedio: {avg_wtf:.2f}")
    
    # Top 5 más WTF
    print("\n   🔥 Top 5 más WTF:")
    for h in historias[:5]:
        print(f"      [{h['wtf_score']:.2f}] {h['titulo_inferido'][:50]}...")


if __name__ == "__main__":
    count = export_for_web()
    if count > 0:
        print_stats()
    else:
        print("\n   ⚠️ No hay historias supervisadas para exportar")
        print("   Ejecutá primero: python3 scripts/supervise.py <video_id>")

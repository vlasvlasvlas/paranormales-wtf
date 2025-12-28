#!/usr/bin/env python3
"""
Script principal para ejecutar el pipeline completo.
"""
import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime

# Importar módulos del proyecto
sys.path.insert(0, str(Path(__file__).parent.parent))


def show_status():
    """Muestra el estado actual del pipeline"""
    try:
        with open("data/pipeline_status.json", 'r', encoding='utf-8') as f:
            status = json.load(f)
    except FileNotFoundError:
        print("❌ No se encontró pipeline_status.json")
        return
    
    print("\n" + "═" * 60)
    print(" 📊 ESTADO DEL PIPELINE")
    print("═" * 60)
    print(f" Última actualización: {status.get('ultima_actualizacion', '-')}")
    print()
    
    resumen = status.get('resumen_global', {})
    print(f" 📹 Videos totales: {resumen.get('total_videos', 0)}")
    print(f" 📚 Historias detectadas: {resumen.get('total_historias', 0)}")
    print(f" ✅ Historias supervisadas: {resumen.get('historias_supervisadas', 0)}")
    print(f" 🤖 Modelo entrenado: {'Sí' if resumen.get('modelo_entrenado') else 'No'}")
    print()
    
    print(" 📹 VIDEOS:")
    print(" ─" * 30)
    
    for video in status.get('videos', []):
        vid = video['video_id']
        estado = video.get('estado', {})
        metricas = video.get('metricas', {})
        
        # Iconos de estado
        icons = {
            'completado': '✅',
            'en_progreso': '🔄',
            'pendiente': '⏳',
            'error': '❌'
        }
        
        print(f"\n   [{vid}] {video.get('titulo', 'Sin título')}")
        print(f"      Subtítulos:   {icons.get(estado.get('subtitulos', 'pendiente'))} {estado.get('subtitulos', 'pendiente')}")
        print(f"      Segmentación: {icons.get(estado.get('segmentacion', 'pendiente'))} {estado.get('segmentacion', 'pendiente')}")
        print(f"      Supervisión:  {icons.get(estado.get('supervision_humana', 'pendiente'))} {metricas.get('historias_supervisadas', 0)}/{metricas.get('historias_detectadas', 0)}")
        print(f"      Exportación:  {icons.get(estado.get('exportado_web', 'pendiente'))} {estado.get('exportado_web', 'pendiente')}")
    
    print()


def run_ingest():
    """Ejecuta la fase de ingestión"""
    print("\n📥 FASE 1: INGESTIÓN DE SUBTÍTULOS")
    print("─" * 40)
    subprocess.run(['python3', 'src/ingestor.py'])


def run_segment(video_id: str = None):
    """Ejecuta la fase de segmentación"""
    print("\n🔍 FASE 2: SEGMENTACIÓN DE HISTORIAS")
    print("─" * 40)
    
    if video_id:
        subprocess.run(['python3', 'src/segmenter.py', video_id])
    else:
        # Procesar todos los videos con subtítulos
        with open("data/pipeline_status.json", 'r', encoding='utf-8') as f:
            status = json.load(f)
        
        for video in status.get('videos', []):
            if video['estado'].get('subtitulos') == 'completado':
                if video['estado'].get('segmentacion') != 'completado':
                    subprocess.run(['python3', 'src/segmenter.py', video['video_id']])


def print_help():
    """Muestra la ayuda"""
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                    PARANORMALES.WTF - PIPELINE                       ║
╚══════════════════════════════════════════════════════════════════════╝

USO:
    python3 scripts/run_pipeline.py <comando> [opciones]

COMANDOS:
    status              Muestra el estado actual del pipeline
    ingest              Descarga subtítulos de todos los videos pendientes
    segment [video_id]  Segmenta historias (todos o video específico)
    supervise <video_id> Abre el CLI de supervisión para un video
    export              Exporta historias clasificadas a la web
    all                 Ejecuta ingest + segment para todos

FLUJO TÍPICO:
    1. Agregar videos a data/videos_input.json
    2. python3 scripts/run_pipeline.py ingest
    3. python3 scripts/run_pipeline.py segment
    4. python3 scripts/supervise.py <video_id>
    5. python3 scripts/export_web.py

EJEMPLOS:
    python3 scripts/run_pipeline.py status
    python3 scripts/run_pipeline.py segment n2BkstRXbV0
    python3 scripts/supervise.py n2BkstRXbV0
""")


def main():
    if len(sys.argv) < 2:
        print_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == 'status':
        show_status()
    
    elif command == 'ingest':
        run_ingest()
    
    elif command == 'segment':
        video_id = sys.argv[2] if len(sys.argv) > 2 else None
        run_segment(video_id)
    
    elif command == 'supervise':
        if len(sys.argv) < 3:
            print("❌ Falta video_id")
            print("   Uso: python3 scripts/run_pipeline.py supervise <video_id>")
            return
        
        # Llamar al script de supervisión
        import subprocess
        subprocess.run(['python3', 'scripts/supervise.py', sys.argv[2]])
    
    elif command == 'export':
        import subprocess
        subprocess.run(['python3', 'scripts/export_web.py'])
    
    elif command == 'all':
        run_ingest()
        run_segment()
        show_status()
    
    else:
        print(f"❌ Comando desconocido: {command}")
        print_help()


if __name__ == "__main__":
    main()

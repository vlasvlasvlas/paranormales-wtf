#!/usr/bin/env python3
"""
CLI de supervisión de historias - Permite revisar y corregir clasificaciones.
"""
import json
import sys
from pathlib import Path
from datetime import datetime
import os

# Configuración
CATEGORIAS = {
    '1': 'fantasmas',
    '2': 'ovnis', 
    '3': 'criaturas',
    '4': 'premoniciones',
    '5': 'experiencias_misticas',
    '6': 'fenomenos_fisicos',
    '7': 'brujeria',
    '0': 'otros'
}

SUBCATEGORIAS = {
    'fantasmas': ['cementerios', 'casas_embrujadas', 'apariciones_familiares', 'hospitales', 'rutas', 'general'],
    'ovnis': ['avistamientos', 'contacto_cercano', 'abducciones', 'luces_nocturnas', 'general'],
    'criaturas': ['lobison', 'duendes', 'sombras', 'hombres_de_negro', 'general'],
    'premoniciones': ['suenos_premonitorios', 'presentimientos', 'deja_vu', 'general'],
    'experiencias_misticas': ['angeles', 'seres_de_luz', 'mensajes_fallecidos', 'general'],
    'fenomenos_fisicos': ['objetos_que_se_mueven', 'sonidos', 'olores', 'electricidad', 'general'],
    'brujeria': ['posesiones', 'embrujos', 'rituales', 'general'],
    'otros': ['general']
}

NARRADORES = {
    '1': 'oyente',
    '2': 'conductor',
    '3': 'invitado'
}


def clear_screen():
    """Limpia la pantalla"""
    os.system('cls' if os.name == 'nt' else 'clear')


def load_segmentation(video_id: str) -> dict:
    """Carga el archivo de segmentación"""
    path = f"data/segmentacion/{video_id}.json"
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_segmentation(video_id: str, data: dict):
    """Guarda el archivo de segmentación"""
    path = f"data/segmentacion/{video_id}.json"
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_gold_dataset() -> list:
    """Carga el dataset gold existente"""
    path = "data/dataset_gold.json"
    if Path(path).exists():
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def save_gold_dataset(data: list):
    """Guarda el dataset gold"""
    path = "data/dataset_gold.json"
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def update_pipeline_status(video_id: str, supervisadas: int, total: int):
    """Actualiza el estado del pipeline"""
    status_path = "data/pipeline_status.json"
    
    with open(status_path, 'r', encoding='utf-8') as f:
        status = json.load(f)
    
    for video in status['videos']:
        if video['video_id'] == video_id:
            video['metricas']['historias_supervisadas'] = supervisadas
            video['metricas']['historias_pendientes'] = total - supervisadas
            video['timestamps']['ultima_supervision'] = datetime.now().isoformat()
            
            if supervisadas == total:
                video['estado']['supervision_humana'] = 'completado'
            else:
                video['estado']['supervision_humana'] = 'en_progreso'
            break
    
    status['resumen_global']['historias_supervisadas'] = sum(
        v['metricas']['historias_supervisadas'] for v in status['videos']
    )
    status['ultima_actualizacion'] = datetime.now().isoformat()
    
    with open(status_path, 'w', encoding='utf-8') as f:
        json.dump(status, f, ensure_ascii=False, indent=2)


def display_story(story: dict, index: int, total: int, video_id: str):
    """Muestra una historia para supervisión"""
    clear_screen()
    
    print("═" * 70)
    print(f" SUPERVISIÓN DE HISTORIAS - {video_id} ({index + 1}/{total})")
    print("═" * 70)
    print()
    
    # URL de YouTube
    timestamp = int(story['timestamp_inicio'])
    url = f"https://youtube.com/watch?v={video_id}&t={timestamp}s"
    print(f"🔗 {url}")
    print(f"⏱️  [{story['timestamp_fmt']}] - Duración: {int(story['duracion_segundos'])}s")
    print()
    
    # Texto de la historia (primeros 500 caracteres)
    print("📝 TEXTO:")
    print("─" * 70)
    texto = story.get('texto_completo', '')[:500]
    # Formato mejorado
    print(texto)
    if len(story.get('texto_completo', '')) > 500:
        print("...")
    print("─" * 70)
    print()
    
    # Clasificación actual si existe
    if story.get('clasificacion'):
        clf = story['clasificacion']
        print("📊 CLASIFICACIÓN ACTUAL:")
        print(f"   • Categoría:    {clf.get('categoria', '-')}")
        print(f"   • Subcategoría: {clf.get('subcategoria', '-')}")
        print(f"   • Narrador:     {clf.get('tipo_narrador', '-')}")
        print(f"   • WTF Score:    {clf.get('wtf_score', '-')}")
        print(f"   • Título:       {clf.get('titulo', '-')}")
        print()


def get_category_input() -> str:
    """Obtiene la categoría del usuario"""
    print("\n📁 CATEGORÍAS:")
    for key, val in CATEGORIAS.items():
        print(f"   [{key}] {val}")
    
    while True:
        choice = input("\n   Tu elección: ").strip()
        if choice in CATEGORIAS:
            return CATEGORIAS[choice]
        print("   ❌ Opción inválida")


def get_subcategory_input(categoria: str) -> str:
    """Obtiene la subcategoría del usuario"""
    subs = SUBCATEGORIAS.get(categoria, ['general'])
    
    print(f"\n📂 SUBCATEGORÍAS de {categoria}:")
    for i, sub in enumerate(subs, 1):
        print(f"   [{i}] {sub}")
    
    while True:
        choice = input("\n   Tu elección: ").strip()
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(subs):
                return subs[idx]
        except ValueError:
            pass
        print("   ❌ Opción inválida")


def get_narrator_input() -> str:
    """Obtiene el tipo de narrador"""
    print("\n🎙️ TIPO DE NARRADOR:")
    for key, val in NARRADORES.items():
        print(f"   [{key}] {val}")
    
    while True:
        choice = input("\n   Tu elección: ").strip()
        if choice in NARRADORES:
            return NARRADORES[choice]
        print("   ❌ Opción inválida")


def get_wtf_score() -> float:
    """Obtiene el WTF score"""
    print("\n🔥 WTF SCORE (0.0 = normal, 1.0 = WTF total):")
    
    while True:
        choice = input("   Score (0.0-1.0): ").strip()
        try:
            score = float(choice)
            if 0.0 <= score <= 1.0:
                return round(score, 2)
        except ValueError:
            pass
        print("   ❌ Debe ser un número entre 0.0 y 1.0")


def get_title_input(texto: str) -> str:
    """Obtiene un título para la historia"""
    # Sugerir título basado en primeras palabras
    palabras = texto.split()[:10]
    sugerencia = ' '.join(palabras)[:50]
    
    print(f"\n📌 TÍTULO (Enter para auto: '{sugerencia}...'):")
    titulo = input("   Título: ").strip()
    
    if not titulo:
        titulo = sugerencia + "..."
    
    return titulo[:100]


def get_summary_input(texto: str) -> str:
    """Obtiene un resumen de la historia"""
    print("\n📝 RESUMEN (breve descripción de la historia):")
    resumen = input("   Resumen: ").strip()
    
    if not resumen:
        # Auto-generar de primeras 200 chars
        resumen = texto[:200].replace('\n', ' ') + "..."
    
    return resumen[:500]


def supervise_story(story: dict, index: int, total: int, video_id: str) -> dict | None | str:
    """
    Supervisa una historia individualmente.
    
    Returns:
        dict: clasificación si se completó
        None: si se descartó
        'skip': si se saltó
        'quit': si se quiere salir
    """
    display_story(story, index, total, video_id)
    
    print("\n" + "═" * 70)
    print(" COMANDOS:")
    print("   [c] Clasificar esta historia")
    print("   [d] Descartar (no es una historia)")
    print("   [n] Siguiente (saltar)")
    print("   [q] Guardar y salir")
    print("═" * 70)
    
    while True:
        choice = input("\n Tu elección: ").strip().lower()
        
        if choice == 'q':
            return 'quit'
        elif choice == 'n':
            return 'skip'
        elif choice == 'd':
            return None
        elif choice == 'c':
            # Clasificar
            categoria = get_category_input()
            subcategoria = get_subcategory_input(categoria)
            narrador = get_narrator_input()
            wtf_score = get_wtf_score()
            titulo = get_title_input(story.get('texto_completo', ''))
            resumen = get_summary_input(story.get('texto_completo', ''))
            
            clasificacion = {
                'categoria': categoria,
                'subcategoria': subcategoria,
                'tipo_narrador': narrador,
                'wtf_score': wtf_score,
                'titulo': titulo,
                'resumen': resumen,
                'verificado_humano': True,
                'fecha_supervision': datetime.now().isoformat()
            }
            
            # Confirmar
            print("\n" + "─" * 70)
            print("📋 RESUMEN DE CLASIFICACIÓN:")
            print(f"   Categoría:    {categoria}")
            print(f"   Subcategoría: {subcategoria}")
            print(f"   Narrador:     {narrador}")
            print(f"   WTF Score:    {wtf_score}")
            print(f"   Título:       {titulo}")
            print("─" * 70)
            
            confirm = input("\n¿Confirmar? [s/n]: ").strip().lower()
            if confirm == 's':
                return clasificacion
            else:
                print("   Cancelado. Volviendo al menú...")
                continue
        else:
            print("   ❌ Opción inválida")


def run_supervision(video_id: str):
    """
    Ejecuta el flujo de supervisión para un video.
    """
    print(f"\n🔍 Cargando segmentación de {video_id}...")
    
    try:
        data = load_segmentation(video_id)
    except FileNotFoundError:
        print(f"❌ No se encontró segmentación para {video_id}")
        print("   Ejecutá primero: python3 src/segmenter.py {video_id}")
        return
    
    historias = data.get('historias', [])
    total = len(historias)
    
    print(f"   📚 {total} historias encontradas")
    
    # Cargar dataset gold existente
    gold_dataset = load_gold_dataset()
    gold_ids = {(g['video_id'], g['timestamp_inicio']) for g in gold_dataset}
    
    # Contar supervisadas
    supervisadas = sum(1 for h in historias if h.get('clasificacion', {}).get('verificado_humano'))
    
    print(f"   ✅ {supervisadas} ya supervisadas")
    print(f"   ⏳ {total - supervisadas} pendientes")
    print()
    
    input("Presioná Enter para comenzar...")
    
    # Procesar cada historia
    for i, historia in enumerate(historias):
        # Saltar ya supervisadas
        if historia.get('clasificacion', {}).get('verificado_humano'):
            continue
        
        result = supervise_story(historia, i, total, video_id)
        
        if result == 'quit':
            break
        elif result == 'skip':
            continue
        elif result is None:
            # Descartada - marcar como no-historia
            historia['clasificacion'] = {
                'es_historia': False,
                'verificado_humano': True,
                'fecha_supervision': datetime.now().isoformat()
            }
            supervisadas += 1
        elif isinstance(result, dict):
            # Clasificada
            result['es_historia'] = True
            historia['clasificacion'] = result
            supervisadas += 1
            
            # Agregar al gold dataset
            gold_entry = {
                'video_id': video_id,
                'timestamp_inicio': historia['timestamp_inicio'],
                'timestamp_fin': historia['timestamp_fin'],
                'texto': historia.get('texto_completo', ''),
                **result
            }
            gold_dataset.append(gold_entry)
    
    # Guardar todo
    print("\n💾 Guardando cambios...")
    save_segmentation(video_id, data)
    save_gold_dataset(gold_dataset)
    update_pipeline_status(video_id, supervisadas, total)
    
    print(f"\n✅ Sesión completada:")
    print(f"   • Historias supervisadas: {supervisadas}/{total}")
    print(f"   • Gold dataset total: {len(gold_dataset)} historias")
    print()


def main():
    """Punto de entrada principal"""
    if len(sys.argv) < 2:
        print("Uso: python3 scripts/supervise.py <video_id>")
        print("Ejemplo: python3 scripts/supervise.py n2BkstRXbV0")
        sys.exit(1)
    
    video_id = sys.argv[1]
    run_supervision(video_id)


if __name__ == "__main__":
    main()

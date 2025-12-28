#!/usr/bin/env python3
"""
Módulo de base de datos SQLite con FTS5 para búsqueda full-text.
"""
import sqlite3
import json
from pathlib import Path
from typing import Optional
from datetime import datetime


DB_PATH = "data/historias.db"


def get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    """Obtiene conexión a la base de datos"""
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str = DB_PATH):
    """Inicializa la base de datos con el schema completo"""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    
    # Tabla de videos procesados
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS videos (
            video_id TEXT PRIMARY KEY,
            url TEXT NOT NULL,
            titulo TEXT,
            fecha_emision TEXT,
            duracion_minutos INTEGER,
            fecha_procesado TEXT,
            total_historias INTEGER DEFAULT 0
        )
    ''')
    
    # Tabla principal de historias
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id TEXT NOT NULL,
            timestamp_inicio REAL NOT NULL,
            timestamp_fin REAL,
            titulo_inferido TEXT,
            texto_completo TEXT NOT NULL,
            resumen TEXT,
            categoria TEXT,
            subcategoria TEXT,
            tipo_narrador TEXT,
            wtf_score REAL,
            es_publicidad INTEGER DEFAULT 0,
            clasificado_por TEXT,
            confianza_clasificacion REAL,
            verificado_humano INTEGER DEFAULT 0,
            fecha_clasificacion TEXT,
            FOREIGN KEY (video_id) REFERENCES videos(video_id)
        )
    ''')
    
    # Tabla de embeddings (para búsqueda semántica futura)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS embeddings (
            historia_id INTEGER PRIMARY KEY,
            vector BLOB,
            modelo TEXT,
            FOREIGN KEY (historia_id) REFERENCES historias(id)
        )
    ''')
    
    # Full-text search con FTS5
    cursor.execute('''
        CREATE VIRTUAL TABLE IF NOT EXISTS historias_fts USING fts5(
            titulo_inferido,
            texto_completo,
            resumen,
            content='historias',
            content_rowid='id'
        )
    ''')
    
    # Triggers para mantener FTS sincronizado
    cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS historias_ai AFTER INSERT ON historias BEGIN
            INSERT INTO historias_fts(rowid, titulo_inferido, texto_completo, resumen)
            VALUES (new.id, new.titulo_inferido, new.texto_completo, new.resumen);
        END
    ''')
    
    cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS historias_ad AFTER DELETE ON historias BEGIN
            INSERT INTO historias_fts(historias_fts, rowid, titulo_inferido, texto_completo, resumen)
            VALUES('delete', old.id, old.titulo_inferido, old.texto_completo, old.resumen);
        END
    ''')
    
    cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS historias_au AFTER UPDATE ON historias BEGIN
            INSERT INTO historias_fts(historias_fts, rowid, titulo_inferido, texto_completo, resumen)
            VALUES('delete', old.id, old.titulo_inferido, old.texto_completo, old.resumen);
            INSERT INTO historias_fts(rowid, titulo_inferido, texto_completo, resumen)
            VALUES (new.id, new.titulo_inferido, new.texto_completo, new.resumen);
        END
    ''')
    
    # Índices para búsquedas frecuentes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_historias_video ON historias(video_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_historias_categoria ON historias(categoria)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_historias_wtf ON historias(wtf_score)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_historias_verificado ON historias(verificado_humano)')
    
    conn.commit()
    conn.close()
    print(f"✅ Base de datos inicializada: {db_path}")


def insert_video(video_id: str, url: str, titulo: str = None, 
                 fecha_emision: str = None, duracion_minutos: int = None) -> bool:
    """Inserta o actualiza un video en la base de datos"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO videos (video_id, url, titulo, fecha_emision, duracion_minutos, fecha_procesado)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (video_id, url, titulo, fecha_emision, duracion_minutos, datetime.now().isoformat()))
    
    conn.commit()
    conn.close()
    return True


def insert_historia(video_id: str, timestamp_inicio: float, texto_completo: str,
                   timestamp_fin: float = None, titulo_inferido: str = None,
                   resumen: str = None, categoria: str = None, subcategoria: str = None,
                   tipo_narrador: str = None, wtf_score: float = None,
                   clasificado_por: str = "llm", confianza: float = None) -> int:
    """Inserta una historia y retorna su ID"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO historias (
            video_id, timestamp_inicio, timestamp_fin, titulo_inferido,
            texto_completo, resumen, categoria, subcategoria, tipo_narrador,
            wtf_score, clasificado_por, confianza_clasificacion, fecha_clasificacion
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (video_id, timestamp_inicio, timestamp_fin, titulo_inferido,
          texto_completo, resumen, categoria, subcategoria, tipo_narrador,
          wtf_score, clasificado_por, confianza, datetime.now().isoformat()))
    
    historia_id = cursor.lastrowid
    
    # Actualizar contador en videos
    cursor.execute('''
        UPDATE videos SET total_historias = (
            SELECT COUNT(*) FROM historias WHERE video_id = ?
        ) WHERE video_id = ?
    ''', (video_id, video_id))
    
    conn.commit()
    conn.close()
    return historia_id


def search_historias(query: str, limit: int = 20) -> list:
    """Búsqueda full-text en historias"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT h.*, 
               bm25(historias_fts) as relevancia,
               v.titulo as video_titulo,
               v.fecha_emision
        FROM historias_fts fts
        JOIN historias h ON fts.rowid = h.id
        JOIN videos v ON h.video_id = v.video_id
        WHERE historias_fts MATCH ?
        ORDER BY relevancia
        LIMIT ?
    ''', (query, limit))
    
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results


def get_historias_by_filter(categoria: str = None, subcategoria: str = None,
                            tipo_narrador: str = None, wtf_min: float = None,
                            wtf_max: float = None, solo_verificadas: bool = False,
                            limit: int = 50) -> list:
    """Obtiene historias con filtros"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = '''
        SELECT h.*, v.titulo as video_titulo, v.fecha_emision
        FROM historias h
        JOIN videos v ON h.video_id = v.video_id
        WHERE h.es_publicidad = 0
    '''
    params = []
    
    if categoria:
        query += ' AND h.categoria = ?'
        params.append(categoria)
    if subcategoria:
        query += ' AND h.subcategoria = ?'
        params.append(subcategoria)
    if tipo_narrador:
        query += ' AND h.tipo_narrador = ?'
        params.append(tipo_narrador)
    if wtf_min is not None:
        query += ' AND h.wtf_score >= ?'
        params.append(wtf_min)
    if wtf_max is not None:
        query += ' AND h.wtf_score <= ?'
        params.append(wtf_max)
    if solo_verificadas:
        query += ' AND h.verificado_humano = 1'
    
    query += ' ORDER BY h.wtf_score DESC LIMIT ?'
    params.append(limit)
    
    cursor.execute(query, params)
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results


def get_stats() -> dict:
    """Obtiene estadísticas de la base de datos"""
    conn = get_connection()
    cursor = conn.cursor()
    
    stats = {}
    
    cursor.execute('SELECT COUNT(*) FROM videos')
    stats['total_videos'] = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM historias WHERE es_publicidad = 0')
    stats['total_historias'] = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM historias WHERE verificado_humano = 1')
    stats['historias_verificadas'] = cursor.fetchone()[0]
    
    cursor.execute('''
        SELECT categoria, COUNT(*) as count 
        FROM historias 
        WHERE es_publicidad = 0 AND categoria IS NOT NULL
        GROUP BY categoria
        ORDER BY count DESC
    ''')
    stats['por_categoria'] = {row[0]: row[1] for row in cursor.fetchall()}
    
    cursor.execute('SELECT AVG(wtf_score) FROM historias WHERE wtf_score IS NOT NULL')
    stats['wtf_promedio'] = cursor.fetchone()[0]
    
    conn.close()
    return stats


def export_for_web(output_path: str = "web/data/historias.json") -> int:
    """Exporta historias para la web frontend"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            h.id,
            h.video_id,
            h.timestamp_inicio,
            h.timestamp_fin,
            h.titulo_inferido,
            h.resumen,
            h.categoria,
            h.subcategoria,
            h.tipo_narrador,
            h.wtf_score,
            h.verificado_humano,
            v.titulo as video_titulo,
            v.fecha_emision
        FROM historias h
        JOIN videos v ON h.video_id = v.video_id
        WHERE h.es_publicidad = 0
        ORDER BY h.wtf_score DESC
    ''')
    
    historias = []
    for row in cursor.fetchall():
        h = dict(row)
        # Generar URL de YouTube con timestamp
        h['youtube_url'] = f"https://www.youtube.com/watch?v={h['video_id']}&t={int(h['timestamp_inicio'])}s"
        historias.append(h)
    
    conn.close()
    
    # Guardar JSON
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({
            "generated_at": datetime.now().isoformat(),
            "total": len(historias),
            "historias": historias
        }, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Exportado: {output_path} ({len(historias)} historias)")
    return len(historias)


if __name__ == "__main__":
    # Inicializar base de datos
    init_db()
    
    # Mostrar stats
    stats = get_stats()
    print(f"\n📊 Estadísticas:")
    print(f"   Videos: {stats['total_videos']}")
    print(f"   Historias: {stats['total_historias']}")
    print(f"   Verificadas: {stats['historias_verificadas']}")

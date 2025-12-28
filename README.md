# 🔮 Paranormales.WTF

Buscador de historias paranormales del programa **"La Noche Paranormal"** con clasificación automática y links directos a YouTube.

![Paranormales.WTF](image.png)

## ¿Qué hace?

1. **Extrae subtítulos** de YouTube (sin descargar audio)
2. **Detecta historias** automáticamente con patrones
3. **Permite clasificar** manualmente con un CLI interactivo
4. **Web de búsqueda** con filtros por categoría y WTF score

## Instalación

```bash
git clone https://github.com/usuario/paranormales-wtf.git
cd paranormales-wtf
pip install -r requirements.txt
```

## Uso rápido

### Ver estado del pipeline
```bash
python3 scripts/run_pipeline.py status
```

### Procesar un video nuevo
```bash
# 1. Agregar URL a data/videos_input.json
# 2. Descargar subtítulos
python3 src/ingestor.py

# 3. Detectar historias
python3 src/segmenter.py VIDEO_ID

# 4. Clasificar manualmente
python3 scripts/supervise.py VIDEO_ID

# 5. Exportar a la web
python3 scripts/export_web.py
```

### Ver la web localmente
```bash
cd web && python3 -m http.server 8080
# Abrir http://localhost:8080
```

## Estructura del proyecto

```
paranormales-wtf/
├── data/
│   ├── videos_input.json       # Videos a procesar
│   ├── pipeline_status.json    # Estado del pipeline
│   ├── subtitulos/             # Subtítulos crudos
│   ├── segmentacion/           # Historias detectadas
│   └── dataset_gold.json       # Clasificaciones verificadas
├── src/
│   ├── ingestor.py             # Extrae subtítulos de YouTube
│   ├── segmenter.py            # Detecta inicio/fin de historias
│   └── db.py                   # Base de datos SQLite
├── scripts/
│   ├── run_pipeline.py         # Script maestro
│   ├── supervise.py            # CLI de clasificación
│   └── export_web.py           # Exporta a la web
├── web/
│   ├── index.html              # Página principal
│   ├── css/styles.css          # Estilos (tema oscuro)
│   ├── js/app.js               # Lógica de búsqueda
│   └── data/historias.json     # Datos para la web
└── config.yaml                 # Configuración
```

## Categorías de clasificación

| Categoría | Emoji | Ejemplos |
|-----------|-------|----------|
| Fantasmas | 👻 | Cementerios, casas, apariciones |
| OVNIs | 👽 | Avistamientos, abducciones |
| Criaturas | 🐺 | Lobisón, duendes, sombras |
| Premoniciones | 🔮 | Sueños, presentimientos |
| Brujería | 🕯️ | Posesiones, embrujos |
| Otros | ❓ | Inclasificables |

## WTF Score

El **WTF Score** (0.0 - 1.0) mide qué tan bizarra es una historia:

- **0.0 - 0.3**: Normal, creíble
- **0.4 - 0.6**: Interesante, algo extraño
- **0.7 - 0.8**: Muy raro, difícil de creer
- **0.9 - 1.0**: WTF total, absurdo nivel máximo

## Tecnologías

- **Python 3.8+**
- **youtube-transcript-api** - Subtítulos de YouTube
- **SQLite + FTS5** - Base de datos con búsqueda full-text
- **Vanilla JS** - Web sin frameworks
- **GitHub Pages** - Hosting (próximamente)

## Roadmap

- [x] Extracción de subtítulos de YouTube
- [x] Segmentación automática de historias
- [x] CLI de clasificación manual
- [x] Web de búsqueda con filtros
- [ ] Modelos supervisados (XGBoost/LightGBM)
- [ ] Deploy en GitHub Pages

## Contribuir

¡PRs bienvenidos! Especialmente para:
- Agregar más videos al dataset
- Mejorar los patrones de detección
- Entrenar modelos de clasificación

## Créditos

- Contenido: [La Noche Paranormal](https://www.youtube.com/@lanocheparanormal)
- Este proyecto es **fan-made** y no almacena audio ni video

---

Hecho con 👻 para fans del programa

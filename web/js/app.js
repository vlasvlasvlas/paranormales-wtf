/* ==========================================================================
   PARANORMALES.WTF - App JavaScript
   ========================================================================== */

// State
let allStories = [];
let filteredStories = [];
let currentCategory = 'all';
let currentSort = 'random';
let currentWtfMin = 0;
let currentSearch = '';

// DOM Elements
const searchInput = document.getElementById('searchInput');
const clearSearch = document.getElementById('clearSearch');
const categoryButtons = document.getElementById('categoryButtons');
const wtfSlider = document.getElementById('wtfSlider');
const wtfValue = document.getElementById('wtfValue');
const tabs = document.querySelectorAll('.tab');
const storiesGrid = document.getElementById('storiesGrid');
const resultsCount = document.getElementById('resultsCount');
const emptyState = document.getElementById('emptyState');

// --------------------------------------------------------------------------
// Data Loading
// --------------------------------------------------------------------------

async function loadData() {
    try {
        const response = await fetch('data/historias.json');
        if (!response.ok) throw new Error('Failed to load data');
        const data = await response.json();
        allStories = data.historias || [];
        initializeApp();
    } catch (error) {
        console.error('Error loading data:', error);
        showDemoData();
    }
}

function showDemoData() {
    // Demo data for testing
    allStories = [
        {
            id: 1,
            video_id: "n2BkstRXbV0",
            timestamp_inicio: 134,
            titulo_inferido: "La criatura del cementerio de Paraguay",
            resumen: "Una niña de 8-9 años ve a un nene desnudo de 2-3 años caminando por el patio de su hermana, frente al cementerio. La criatura desaparece en el fondo. Años después, ve a una anciana de pelo blanco entrar al cementerio, tirarse sobre un panteón y desaparecer. Dice tener visiones frecuentes, ver figuras en las paredes y letras en hebreo.",
            categoria: "fantasmas",
            subcategoria: "cementerios",
            tipo_narrador: "oyente",
            wtf_score: 0.82,
            fecha_emision: "2024-12-18"
        },
        {
            id: 2,
            video_id: "n2BkstRXbV0",
            timestamp_inicio: 701,
            titulo_inferido: "Los perros que miraban la puerta",
            resumen: "Una oyente cuenta que sus perros se quedaron mirando fijos hacia la puerta, quietos, sin moverse, como si hubiesen escuchado algo. Ella sintió una presencia extraña en la casa esa noche.",
            categoria: "fantasmas",
            subcategoria: "casas_embrujadas",
            tipo_narrador: "oyente",
            wtf_score: 0.55,
            fecha_emision: "2024-12-18"
        },
        {
            id: 3,
            video_id: "n2BkstRXbV0",
            timestamp_inicio: 979,
            titulo_inferido: "Temblando al salir del cementerio",
            resumen: "Un oyente relata su experiencia visitando un cementerio. Al cruzar el umbral hacia afuera, comenzó a temblar incontrolablemente. Sintió que algo lo había seguido desde adentro.",
            categoria: "fantasmas",
            subcategoria: "cementerios",
            tipo_narrador: "oyente",
            wtf_score: 0.68,
            fecha_emision: "2024-12-18"
        },
        {
            id: 4,
            video_id: "n2BkstRXbV0",
            timestamp_inicio: 2377,
            titulo_inferido: "Lo que pasa en los cerros",
            resumen: "Una historia sobre lo que se vive puertas adentro en una casa vieja en los cerros. Fenómenos extraños que la familia atribuye a presencias antiguas del lugar.",
            categoria: "fantasmas",
            subcategoria: "casas_embrujadas",
            tipo_narrador: "oyente",
            wtf_score: 0.71,
            fecha_emision: "2024-12-18"
        },
        {
            id: 5,
            video_id: "n2BkstRXbV0",
            timestamp_inicio: 2872,
            titulo_inferido: "El demonio que quería atormentarlos",
            resumen: "Una pareja descubrió la verdad sobre los fenómenos en su casa: un demonio quería atormentarlos. Tuvieron que recurrir a ayuda espiritual para librarse de la entidad.",
            categoria: "brujeria",
            subcategoria: "posesiones",
            tipo_narrador: "oyente",
            wtf_score: 0.88,
            fecha_emision: "2024-12-18"
        },
        {
            id: 6,
            video_id: "n2BkstRXbV0",
            timestamp_inicio: 3506,
            titulo_inferido: "Libélulas y mensajes del más allá",
            resumen: "Una oyente cuenta una experiencia con libélulas que aparecieron misteriosamente. Ella cree que era un mensaje de un ser querido fallecido, ya que las libélulas tienen un significado espiritual especial.",
            categoria: "premoniciones",
            subcategoria: "presentimientos",
            tipo_narrador: "oyente",
            wtf_score: 0.45,
            fecha_emision: "2024-12-18"
        }
    ];
    initializeApp();
}

// --------------------------------------------------------------------------
// Initialization
// --------------------------------------------------------------------------

function initializeApp() {
    updateCategoryCounts();
    applyFilters();
    setupEventListeners();
}

function setupEventListeners() {
    // Search
    searchInput.addEventListener('input', debounce(handleSearch, 300));
    clearSearch.addEventListener('click', handleClearSearch);

    // Categories
    categoryButtons.addEventListener('click', handleCategoryClick);

    // WTF Slider
    wtfSlider.addEventListener('input', handleWtfChange);

    // Tabs
    tabs.forEach(tab => {
        tab.addEventListener('click', handleTabClick);
    });
}

// --------------------------------------------------------------------------
// Event Handlers
// --------------------------------------------------------------------------

function handleSearch(e) {
    currentSearch = e.target.value.trim().toLowerCase();
    clearSearch.hidden = !currentSearch;
    applyFilters();
}

function handleClearSearch() {
    searchInput.value = '';
    currentSearch = '';
    clearSearch.hidden = true;
    applyFilters();
}

function handleCategoryClick(e) {
    const btn = e.target.closest('.category-btn');
    if (!btn) return;

    // Update active state
    categoryButtons.querySelectorAll('.category-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');

    currentCategory = btn.dataset.category;
    applyFilters();
}

function handleWtfChange(e) {
    currentWtfMin = e.target.value / 100;
    wtfValue.textContent = currentWtfMin.toFixed(1) + '+';
    applyFilters();
}

function handleTabClick(e) {
    tabs.forEach(t => t.classList.remove('active'));
    e.target.classList.add('active');

    currentSort = e.target.dataset.sort;
    applyFilters();
}

// --------------------------------------------------------------------------
// Filtering & Sorting
// --------------------------------------------------------------------------

function applyFilters() {
    let stories = [...allStories];

    // Filter by category
    if (currentCategory !== 'all') {
        stories = stories.filter(s => s.categoria === currentCategory);
    }

    // Filter by WTF score
    if (currentWtfMin > 0) {
        stories = stories.filter(s => (s.wtf_score || 0) >= currentWtfMin);
    }

    // Filter by search
    if (currentSearch) {
        stories = stories.filter(s => {
            const searchable = [
                s.titulo_inferido || '',
                s.resumen || '',
                s.categoria || '',
                s.subcategoria || ''
            ].join(' ').toLowerCase();
            return searchable.includes(currentSearch);
        });
    }

    // Sort
    switch (currentSort) {
        case 'wtf':
            stories.sort((a, b) => (b.wtf_score || 0) - (a.wtf_score || 0));
            break;
        case 'recent':
            stories.sort((a, b) => new Date(b.fecha_emision) - new Date(a.fecha_emision));
            break;
        case 'random':
            stories = shuffleArray(stories);
            break;
        case 'all':
        default:
            // Keep original order
            break;
    }

    filteredStories = stories;
    renderStories();
}

function updateCategoryCounts() {
    const counts = {
        all: allStories.length,
        fantasmas: 0,
        ovnis: 0,
        criaturas: 0,
        premoniciones: 0,
        otros: 0
    };

    allStories.forEach(s => {
        const cat = s.categoria || 'otros';
        if (counts.hasOwnProperty(cat)) {
            counts[cat]++;
        } else {
            counts.otros++;
        }
    });

    // Update DOM
    Object.entries(counts).forEach(([cat, count]) => {
        const el = document.getElementById(`count${capitalize(cat)}`);
        if (el) el.textContent = count;
    });
}

// --------------------------------------------------------------------------
// Rendering
// --------------------------------------------------------------------------

function renderStories() {
    // Update count
    resultsCount.textContent = filteredStories.length;

    // Show/hide empty state
    emptyState.hidden = filteredStories.length > 0;

    // Render cards
    if (filteredStories.length === 0) {
        storiesGrid.innerHTML = '';
        return;
    }

    storiesGrid.innerHTML = filteredStories.map(story => createStoryCard(story)).join('');
}

function createStoryCard(story) {
    const timestamp = formatTimestamp(story.timestamp_inicio);
    const youtubeUrl = `https://www.youtube.com/watch?v=${story.video_id}&t=${Math.floor(story.timestamp_inicio)}s`;
    const wtfScore = (story.wtf_score || 0).toFixed(2);
    const wtfPercent = Math.round((story.wtf_score || 0) * 100);
    const wtfColor = getWtfColor(story.wtf_score || 0);
    const categoryIcon = getCategoryIcon(story.categoria);
    const date = formatDate(story.fecha_emision);

    // Highlight search terms
    let title = story.titulo_inferido || 'Historia sin título';
    let summary = story.resumen || 'Sin resumen disponible.';

    if (currentSearch) {
        title = highlightText(title, currentSearch);
        summary = highlightText(summary, currentSearch);
    }

    return `
        <article class="story-card">
            <div class="story-card__header">
                <h2 class="story-card__title">${categoryIcon} ${title}</h2>
                <div class="story-card__wtf">
                    <span class="story-card__wtf-label">WTF</span>
                    <span class="story-card__wtf-value" style="color: ${wtfColor}">${wtfScore}</span>
                    <div class="story-card__wtf-bar">
                        <div class="story-card__wtf-fill" style="width: ${wtfPercent}%; background: ${wtfColor}"></div>
                    </div>
                </div>
            </div>
            
            <div class="story-card__meta">
                <span class="story-card__tag">${categoryIcon} ${capitalize(story.categoria || 'otros')}</span>
                <span class="story-card__tag">🎙️ ${capitalize(story.tipo_narrador || 'oyente')}</span>
            </div>
            
            <p class="story-card__summary">${summary}</p>
            
            <div class="story-card__actions">
                <span class="story-card__date">📅 ${date}</span>
                <a href="${youtubeUrl}" target="_blank" rel="noopener" class="play-btn">
                    <span class="play-btn__icon">▶</span>
                    Escuchar (${timestamp})
                </a>
            </div>
        </article>
    `;
}

// --------------------------------------------------------------------------
// Utilities
// --------------------------------------------------------------------------

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function shuffleArray(array) {
    const shuffled = [...array];
    for (let i = shuffled.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    return shuffled;
}

function capitalize(str) {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1);
}

function formatTimestamp(seconds) {
    if (!seconds) return '00:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

function formatDate(dateStr) {
    if (!dateStr) return 'Sin fecha';
    try {
        const date = new Date(dateStr);
        return date.toLocaleDateString('es-AR', { day: 'numeric', month: 'short', year: 'numeric' });
    } catch {
        return dateStr;
    }
}

function getCategoryIcon(category) {
    const icons = {
        fantasmas: '👻',
        ovnis: '👽',
        criaturas: '🐺',
        premoniciones: '🔮',
        experiencias_misticas: '✨',
        fenomenos_fisicos: '💫',
        brujeria: '🕯️',
        otros: '❓'
    };
    return icons[category] || '❓';
}

function getWtfColor(score) {
    // Interpolate between turquoise (low) and red (high)
    const lowColor = { r: 78, g: 205, b: 196 };  // #4ECDC4
    const highColor = { r: 255, g: 107, b: 107 }; // #FF6B6B

    const r = Math.round(lowColor.r + (highColor.r - lowColor.r) * score);
    const g = Math.round(lowColor.g + (highColor.g - lowColor.g) * score);
    const b = Math.round(lowColor.b + (highColor.b - lowColor.b) * score);

    return `rgb(${r}, ${g}, ${b})`;
}

function highlightText(text, search) {
    if (!search) return text;
    const regex = new RegExp(`(${escapeRegex(search)})`, 'gi');
    return text.replace(regex, '<span class="highlight">$1</span>');
}

function escapeRegex(str) {
    return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

// --------------------------------------------------------------------------
// Initialize
// --------------------------------------------------------------------------

document.addEventListener('DOMContentLoaded', loadData);

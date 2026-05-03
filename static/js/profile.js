const modal = document.getElementById('filterModal');
const openBtn = document.getElementById('openFilterBtn');
const closeBtn = document.getElementById('closeFilterBtn');

const filmModal = document.getElementById('filmModal');
const closeModalBtn = document.querySelector('.close-modal');

if (openBtn) {
    openBtn.onclick = function() { modal.style.display = 'block'; }
}

if (closeBtn) {
    closeBtn.onclick = function() { modal.style.display = 'none'; }
}

if (closeModalBtn) {
    closeModalBtn.onclick = function() { filmModal.style.display = 'none'; }
}

window.addEventListener('click', function(event) {
    if (event.target === modal) {
        modal.style.display = 'none';
    }
    if (event.target === filmModal) {
        filmModal.style.display = 'none';
    }
});

function handleFilmCardClick(event) {
    let target = event.target;
    let filmCard = target.closest('.film-card');

    if (!filmCard) return;

    if (target.classList.contains('remove-favorite') ||
        target.closest('.remove-favorite')) {
        return;
    }

    const filmId = filmCard.dataset.filmId;
    if (filmId) {
        showFilmDetails(filmId);
    }
}

function toggleGenre(element) {
    element.classList.toggle('active');
    updateSelectedGenres();
}

function updateSelectedGenres() {
    let selected = [];
    document.querySelectorAll('.filter-tag.active').forEach(tag => {
        selected.push(tag.dataset.genre);
    });
    const hiddenGenres = document.getElementById('selected-genres');
    if (hiddenGenres) hiddenGenres.value = selected.join(',');
}

const urlParams = new URLSearchParams(window.location.search);
const genresParam = urlParams.get('genres');
if (genresParam) {
    const selectedIds = genresParam.split(',');
    document.querySelectorAll('.filter-tag').forEach(tag => {
        if (selectedIds.includes(tag.dataset.genre)) {
            tag.classList.add('active');
        }
    });
    updateSelectedGenres();
}

const ratingVal = urlParams.get('rating');
if (ratingVal) {
    const ratingSelect = document.getElementById('rating');
    if (ratingSelect) ratingSelect.value = ratingVal;
}

const yearVal = urlParams.get('year');
if (yearVal) {
    const yearSelect = document.getElementById('year');
    if (yearSelect) yearSelect.value = yearVal;
}

document.querySelectorAll('.filter-tag').forEach(tag => {
    tag.onclick = function() { toggleGenre(this); }
});

function switchTab(tabName, event) {
    let tabs = document.querySelectorAll('.tab-content');
    for (let i = 0; i < tabs.length; i++) {
        tabs[i].classList.remove('active');
    }
    let btns = document.querySelectorAll('.tab-btn');
    for (let i = 0; i < btns.length; i++) {
        btns[i].classList.remove('active');
    }

    document.getElementById(tabName).classList.add('active');
    if (event && event.target) {
        event.target.classList.add('active');
    }
}

function saveTab(tabName, event) {
    localStorage.setItem('activeTab', tabName);
    switchTab(tabName, event);
}

async function showFilmDetails(filmId) {
    try {
        const response = await fetch(`/api/film/${filmId}`);
        const film = await response.json();

        const modalContent = document.getElementById('modalContent');

        let genresHtml = '';
        if (film.genres && film.genres.length > 0) {
            genresHtml = `<p><strong>Жанры:</strong> ${film.genres.map(g => g.name).join(', ')}</p>`;
        }

        modalContent.innerHTML = `
            <div class="film-detail">
                <div class="film-detail-header">
                    ${film.poster ?
                        `<img src="${film.poster}" alt="${film.name}" class="film-detail-poster">` :
                        '<div class="film-detail-no-poster">Нет постера</div>'
                    }
                    <div class="film-detail-info">
                        <h2>${film.name}</h2>
                        ${film.release_year ? `<p><strong>Год выпуска:</strong> ${film.release_year}</p>` : ''}
                        ${film.rating ? `<p><strong>Рейтинг:</strong> ★ ${film.rating.toFixed(1)}</p>` : ''}
                        ${genresHtml}
                    </div>
                </div>
                <div class="film-detail-description">
                    <h3>Описание</h3>
                    <p>${film.description || 'Описание отсутствует'}</p>
                </div>
            </div>
        `;

        filmModal.style.display = 'block';
    } catch (error) {
        console.error('Ошибка загрузки описания:', error);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const favoritesGrid = document.getElementById('favoritesGrid');
    const notInterestedGrid = document.getElementById('notInterestedGrid');

    if (favoritesGrid) {
        favoritesGrid.addEventListener('click', handleFilmCardClick);
    }
    if (notInterestedGrid) {
        notInterestedGrid.addEventListener('click', handleFilmCardClick);
    }

    let savedTab = localStorage.getItem('activeTab') || 'favorites';
    switchTab(savedTab);
    let btns = document.querySelectorAll('.tab-btn');
    for (let i = 0; i < btns.length; i++) {
        if (btns[i].getAttribute('data-tab') === savedTab) {
            btns[i].classList.add('active');
        }
    }

    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.onclick = function(e) {
            const tabName = this.getAttribute('data-tab');
            saveTab(tabName, e);
        }
    });
});

let allRecommendations = [];
let currentPage = 0;
let itemsPerPage = 5;

async function loadRecommendations() {
    const container = document.getElementById('recommendations-container');
    if (!container) return;

    try {
        const response = await fetch('/api/get_recommendations');
        const data = await response.json();

        if (data.error) {
            container.innerHTML = `<p style="text-align:center; color: #ffc107;">${data.error}</p>`;
            return;
        }

        if (data.recommendations && data.recommendations.length > 0) {
            allRecommendations = data.recommendations;
            currentPage = 0;
            renderCarousel();
        } else {
            container.innerHTML = '<p style="text-align:center;">У вас пока нет рекомендаций. Добавьте фильмы в избранное!</p>';
        }
    } catch (error) {
        container.innerHTML = '<p style="text-align:center; color: #dc3545;">Не удалось загрузить рекомендации</p>';
    }
}

function renderCarousel() {
    const container = document.getElementById('recommendations-container');
    if (!container) return;

    const totalPages = Math.ceil(allRecommendations.length / itemsPerPage);
    const start = currentPage * itemsPerPage;
    const currentFilms = allRecommendations.slice(start, start + itemsPerPage);

    let html = `
        <div class="recommendations-carousel">
            <button class="carousel-btn" onclick="prevPage()" ${currentPage === 0 ? 'disabled' : ''}>←</button>
            <div class="carousel-container">
                <div class="carousel-track">
                    <div class="carousel-slide">
                        <div class="recommendations-grid">
    `;

    currentFilms.forEach(film => {
        html += renderFilmCard(film);
    });

    for (let i = currentFilms.length; i < 5; i++) {
        html += `<div class="film-card-placeholder" style="visibility: hidden;"></div>`;
    }

    html += `
                        </div>
                    </div>
                </div>
            </div>
            <button class="carousel-btn" onclick="nextPage()" ${currentPage >= totalPages - 1 ? 'disabled' : ''}>→</button>
        </div>
        <div style="text-align: center; margin-top: 15px; color: #666; font-size: 14px;">
            Страница ${currentPage + 1} из ${totalPages} (всего ${allRecommendations.length} фильмов)
        </div>
    `;

    container.innerHTML = html;
    loadButtonStates();
}

function renderFilmCard(film) {
    let genresHtml = '';
    if (film.genres && film.genres.length > 0) {
        genresHtml = `<div class="film-genres">` + film.genres.map(genre =>
            `<span class="genre-tag">${genre.name}</span>`
        ).join('') + `</div>`;
    }

    return `
        <div class="film-card" data-film-id="${film.id}">
            <div class="film-poster-container">
                ${film.poster ?
                    `<img src="${film.poster}" alt="${film.name}" class="film-poster" 
                        onerror="this.onerror=null; this.src='https://via.placeholder.com/300x450?text=No+Poster'">` :
                    '<div style="width:100%;height:100%;display:flex;align-items:center;justify-content:center;background:#e9ecef;"><span>Нет постера</span></div>'
                }
            </div>
            <div class="film-info">
                <div class="film-title" title="${film.name}">${film.name}</div>
                ${film.release_year ? `<div class="film-year">Год: ${film.release_year}</div>` : ''}
                ${film.rating ? `<div class="film-rating">★ ${film.rating.toFixed(1)}</div>` : ''}
                ${genresHtml}
                <div class="film-actions">
                    <button class="btn-like" data-film-id="${film.id}">Нравится</button>
                    <button class="btn-not-interested" data-film-id="${film.id}">Не интересно</button>
                </div>
            </div>
        </div>
    `;
}

function prevPage() {
    if (currentPage > 0) {
        currentPage--;
        renderCarousel();
    }
}

function nextPage() {
    const totalPages = Math.ceil(allRecommendations.length / itemsPerPage);
    if (currentPage < totalPages - 1) {
        currentPage++;
        renderCarousel();
    }
}

async function loadButtonStates() {
    try {
        const response = await fetch('/api/user_films');
        const userFilms = await response.json();
        const filmStatusMap = {};
        userFilms.forEach(uf => { filmStatusMap[uf.film_id] = uf.status; });

        document.querySelectorAll('.btn-like').forEach(btn => {
            const filmId = parseInt(btn.dataset.filmId);
            if (filmStatusMap[filmId] === 'like') {
                btn.classList.add('active');
                btn.textContent = 'В избранном';
            } else {
                btn.classList.remove('active');
                btn.textContent = 'Нравится';
            }
        });

        document.querySelectorAll('.btn-not-interested').forEach(btn => {
            const filmId = parseInt(btn.dataset.filmId);
            if (filmStatusMap[filmId] === 'not_interested') {
                btn.classList.add('active');
                btn.textContent = 'Не интересно';
            } else {
                btn.classList.remove('active');
                btn.textContent = 'Не интересно';
            }
        });
    } catch (error) {
        console.error('Ошибка загрузки состояний:', error);
    }
}

async function updateFilmStatus(filmId, action) {
    try {
        let response;
        if (action === 'delete') {
            response = await fetch(`/api/favorites/${filmId}`, { method: 'DELETE' });
        } else {
            response = await fetch(`/api/favorites/${filmId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ status: action })
            });
        }

        if (response.ok) {
            await loadButtonStates();
        }
    } catch (error) {
        console.error('Ошибка:', error);
    }
}

document.addEventListener('click', async (e) => {
    const btn = e.target;
    if (btn.classList.contains('btn-like')) {
        const filmId = btn.dataset.filmId;
        const isActive = btn.classList.contains('active');

        if (isActive) {
            await updateFilmStatus(filmId, 'delete');
        } else {
            await updateFilmStatus(filmId, 'like');
        }
    }

    if (btn.classList.contains('btn-not-interested')) {
        const filmId = btn.dataset.filmId;
        const isActive = btn.classList.contains('active');

        if (isActive) {
            await updateFilmStatus(filmId, 'delete');
        } else {
            await updateFilmStatus(filmId, 'not_interested');
        }
    }
});

document.addEventListener('DOMContentLoaded', () => {
    loadRecommendations();
});
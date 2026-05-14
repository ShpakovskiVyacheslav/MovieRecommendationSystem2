let allRecommendations = [];
let currentPage = 0;
let itemsPerPage = 5;

// Получаем DOM-элементы окна и кнопки закрытия
const filmModal = document.getElementById('filmModal');
const closeModalBtn = document.querySelector('.close-modal');

// При клике на крестик скрываем окно
if (closeModalBtn) {
    closeModalBtn.onclick = function() { filmModal.style.display = 'none'; }
}

// Обработчик клика на всё окно браузера. Если кликнули именно по фону (элементу .modal),
// а не по содержимому .modal-content, то закрываем окно. Это позволяет закрыть окно
// при клике на тёмную область вокруг белого прямоугольника.
window.addEventListener('click', function(event) {
    if (event.target === filmModal) {
        filmModal.style.display = 'none';
    }
});

// Асинхронная функция, потому что мы ждём ответ от сервера (fetch)
async function showFilmDetails(filmId) {
    try {
        // Отправляем GET-запрос к API.
        const response = await fetch(`/api/film/${filmId}`);
        // Преобразуем ответ из JSON в JavaScript объект
        const film = await response.json();

        const modalContent = document.getElementById('modalContent');

        let genresHtml = '';
        if (film.genres && film.genres.length > 0) {
            genresHtml = `<p><strong>Жанры:</strong> ${film.genres.map(g => g.name).join(', ')}</p>`;  // Метод map() создаёт новый массив, применяя функцию к каждому элементу.
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

        // Показываем модальное окно (меняем display с none на block)
        filmModal.style.display = 'block';
    } catch (error) {
        console.error('Ошибка загрузки описания:', error);
    }
}

// Функция добавляет обработчик кликов на контейнер с рекомендациями.
function initRecommendationsClickHandler() {
    const recommendationsContainer = document.getElementById('recommendations-container');
    if (recommendationsContainer) {
        recommendationsContainer.addEventListener('click', function(event) {
            let target = event.target;
            // closest() поднимается вверх по DOM дереву, пока не найдёт элемент с классом .film-card
            let filmCard = target.closest('.film-card');

            if (!filmCard) return;

            // Если кликнули по кнопке или внутри кнопки то не открываем описание, чтобы кнопки работали нормально
            if (target.classList.contains('btn-like') ||
                target.classList.contains('btn-not-interested') ||
                target.closest('.btn-like') ||
                target.closest('.btn-not-interested')) {
                return;
            }

            const filmId = filmCard.dataset.filmId;
            if (filmId) {
                showFilmDetails(filmId);
            }
        });
    }
}

// Загружает рекомендации с сервера
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

// Отрисовывает карусель рекомендаций на текущей странице
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

    // Добавляем пустые невидимые карточки, чтобы сетка не сжималась, если фильмов меньше 5
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
        <div style="text-align: center; margin-top: 15px; color: #1a1a2e; font-size: 14px;">
            Страница ${currentPage + 1} из ${totalPages} (всего ${allRecommendations.length} фильмов)
        </div>
    `;

    container.innerHTML = html;
    // Обновляем состояния кнопок "Нравится"/"Не интересно"
    loadButtonStates();
    // Заново вешаем обработчик на новые карточки фильмов
    initRecommendationsClickHandler();
}

// Генерирует HTML одной карточки фильма для карусели
function renderFilmCard(film) {
    let genresHtml = '';
    if (film.genres && film.genres.length > 0) {
        // map() преобразует массив жанров в массив HTML строк, join() склеивает их
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

// Переключение на предыдущую страницу карусели
function prevPage() {
    if (currentPage > 0) {
        currentPage--;
        renderCarousel(); // Перерисовываем с новым currentPage
    }
}

// Переключение на следующую страницу карусели
function nextPage() {
    const totalPages = Math.ceil(allRecommendations.length / itemsPerPage);
    if (currentPage < totalPages - 1) {
        currentPage++;
        renderCarousel();
    }
}

// Загружает с сервера все фильмы, которые пользователь уже оценил (лайк/не интересно)
// и обновляет внешний вид кнопок на странице (зелёная/красная подсветка)
async function loadButtonStates() {
    try {
        const response = await fetch('/api/user_films');
        const userFilms = await response.json();
        const filmStatusMap = {};
        // Создаём объект, где ключ = film_id, значение = status ('like' или 'not_interested')
        userFilms.forEach(uf => { filmStatusMap[uf.film_id] = uf.status; });

        // Проходим по всем кнопкам "Нравится"
        document.querySelectorAll('.btn-like').forEach(btn => {
            const filmId = parseInt(btn.dataset.filmId);
            if (filmStatusMap[filmId] === 'like') {
                btn.classList.add('active');      // Добавляем класс для зелёного цвета
                btn.textContent = 'В избранном';
            } else {
                btn.classList.remove('active');
                btn.textContent = 'Нравится';
            }
        });

        // Проходим по всем кнопкам "Не интересно"
        document.querySelectorAll('.btn-not-interested').forEach(btn => {
            const filmId = parseInt(btn.dataset.filmId);
            if (filmStatusMap[filmId] === 'not_interested') {
                btn.classList.add('active');      // Добавляем класс для красного цвета
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

// Отправляет запрос на сервер для изменения статуса фильма
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
            await loadButtonStates(); // После успешного изменения обновляем состояние всех кнопок
        }
    } catch (error) {
        console.error('Ошибка:', error);
    }
}

// Глобальный обработчик кликов. Использует делегирование: ловит клики по всему документу.
document.addEventListener('click', async (e) => {
    const btn = e.target;
    if (btn.classList.contains('btn-like')) {
        // Предотвращает всплытие события
        e.stopPropagation();
        const filmId = btn.dataset.filmId;
        const isActive = btn.classList.contains('active');

        if (isActive) {
            await updateFilmStatus(filmId, 'delete');
        } else {
            await updateFilmStatus(filmId, 'like');
        }
    }

    if (btn.classList.contains('btn-not-interested')) {
        e.stopPropagation();
        const filmId = btn.dataset.filmId;
        const isActive = btn.classList.contains('active');

        if (isActive) {
            await updateFilmStatus(filmId, 'delete');
        } else {
            await updateFilmStatus(filmId, 'not_interested');
        }
    }
});

// Обработчик кликов по сетке фильмов (для открытия описания при клике на карточку)
function handleFilmCardClick(event) {
    let target = event.target;
    let filmCard = target.closest('.film-card');

    if (!filmCard) return;

    // Не открываем описание, если кликнули по кнопке или внутри кнопки
    if (target.classList.contains('btn-like') ||
        target.classList.contains('btn-not-interested') ||
        target.closest('.btn-like') ||
        target.closest('.btn-not-interested')) {
        return;
    }

    const filmId = filmCard.dataset.filmId;
    if (filmId) {
        showFilmDetails(filmId);
    }
}

// DOMContentLoaded срабатывает когда HTML полностью загружен и распарсен
document.addEventListener('DOMContentLoaded', () => {
    loadRecommendations();
    loadButtonStates();

    const filmsGrid = document.getElementById('filmsGrid');
    if (filmsGrid) {
        filmsGrid.addEventListener('click', handleFilmCardClick);
    }

    // Модальное окно с информацией о фильме с описанием
    const modal = document.getElementById('myModal');
    const openBtn = document.getElementById('openModalBtn');
    const closeBtn = document.querySelector('.close');

    if (openBtn) {
        openBtn.onclick = function() { modal.style.display = 'block'; }
    }
    if (closeBtn) {
        closeBtn.onclick = function() { modal.style.display = 'none'; }
    }
    window.addEventListener('click', function(event) {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });

    // Переключает класс 'active' у тега жанра
    function toggleGenre(element) {
        element.classList.toggle('active');
        updateSelectedGenres();
    }

    // Собирает все выбранные жанры (с классом active) и сохраняет их ID в скрытое поле
    function updateSelectedGenres() {
        let selected = [];
        document.querySelectorAll('.filter-tag.active').forEach(tag => {
            selected.push(tag.dataset.genre);
        });
        const hiddenGenres = document.getElementById('selected-genres');
        if (hiddenGenres) hiddenGenres.value = selected.join(',');
    }

    // Восстанавливаем значения фильтров из URL при загрузке страницы
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

    // Назначаем обработчик клика для каждого тега жанра
    document.querySelectorAll('.filter-tag').forEach(tag => {
        tag.onclick = function() { toggleGenre(this); }
    });
});

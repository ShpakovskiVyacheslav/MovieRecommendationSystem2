// Получаем DOM-элементы модального окна фильтров и кнопки открытия/закрытия
const modal = document.getElementById('filterModal');
const openBtn = document.getElementById('openFilterBtn');
const closeBtn = document.getElementById('closeFilterBtn');

// Получаем DOM-элементы модального окна описания фильма
const filmModal = document.getElementById('filmModal');
const closeModalBtn = document.querySelector('.close-modal');

// При клике на кнопку "Фильтры" показываем модальное окно (меняем display с none на block)
if (openBtn) {
    openBtn.onclick = function() { modal.style.display = 'block'; }
}

// При клике на крестик в окне фильтров скрываем его
if (closeBtn) {
    closeBtn.onclick = function() { modal.style.display = 'none'; }
}

// При клике на крестик в окне описания фильма скрываем его
if (closeModalBtn) {
    closeModalBtn.onclick = function() { filmModal.style.display = 'none'; }
}

// Обработчик кликов по всему окну браузера.
window.addEventListener('click', function(event) {
    if (event.target === modal) {
        modal.style.display = 'none';
    }
    if (event.target === filmModal) {
        filmModal.style.display = 'none';
    }
});

// Обработчик кликов по карточкам фильмов в профиле.

function handleFilmCardClick(event) {
    let target = event.target;
    let filmCard = target.closest('.film-card');

    if (!filmCard) return;

    // Если кликнули по кнопке удаления (.remove-favorite) или внутри неё,
    // то не открываем описание фильма, чтобы кнопка работала нормально
    if (target.classList.contains('remove-favorite') ||
        target.closest('.remove-favorite')) {
        return;
    }

    const filmId = filmCard.dataset.filmId;
    if (filmId) {
        showFilmDetails(filmId);
    }
}

// Переключает активное состояние тега жанра: добавляет или удаляет класс 'active'
function toggleGenre(element) {
    element.classList.toggle('active'); // Eсли класса нет, добавляет, если есть — удаляет
    updateSelectedGenres();
}

// Собирает все выбранные жанры и сохраняет их ID
function updateSelectedGenres() {
    let selected = [];
    document.querySelectorAll('.filter-tag.active').forEach(tag => {
        selected.push(tag.dataset.genre);
    });
    const hiddenGenres = document.getElementById('selected-genres');
    if (hiddenGenres) hiddenGenres.value = selected.join(',');
}

// Парсим URL и восстанавливаем значения фильтров после перезагрузки страницы
const urlParams = new URLSearchParams(window.location.search);

// Восстанавливаем выбранные жанры
const genresParam = urlParams.get('genres');
if (genresParam) {
    const selectedIds = genresParam.split(',');
    document.querySelectorAll('.filter-tag').forEach(tag => {
        if (selectedIds.includes(tag.dataset.genre)) {
            tag.classList.add('active');
        }
    });
    updateSelectedGenres();  // Обновляем скрытое поле
}

// Восстанавливаем выбранное значение рейтинга
const ratingVal = urlParams.get('rating');
if (ratingVal) {
    const ratingSelect = document.getElementById('rating');
    if (ratingSelect) ratingSelect.value = ratingVal;
}

// Восстанавливаем выбранный диапазон годов
const yearVal = urlParams.get('year');
if (yearVal) {
    const yearSelect = document.getElementById('year');
    if (yearSelect) yearSelect.value = yearVal;
}

// Назначаем обработчик клика для каждого тега жанра
document.querySelectorAll('.filter-tag').forEach(tag => {
    tag.onclick = function() { toggleGenre(this); }
});

// Переключает видимую вкладку (Избранные / Неинтересные)
function switchTab(tabName, event) {
    // Скрываем все вкладки (удаляем класс active у всех .tab-content)
    let tabs = document.querySelectorAll('.tab-content');
    for (let i = 0; i < tabs.length; i++) {
        tabs[i].classList.remove('active');
    }
    // Убираем активное состояние со всех кнопок вкладок
    let btns = document.querySelectorAll('.tab-btn');
    for (let i = 0; i < btns.length; i++) {
        btns[i].classList.remove('active');
    }

    // Показываем выбранную вкладку
    document.getElementById(tabName).classList.add('active');
    // Подсвечиваем кнопку, по которой кликнули
    if (event && event.target) {
        event.target.classList.add('active');
    }
}

// Сохраняет активную вкладку в localStorage и переключает её
function saveTab(tabName, event) {
    localStorage.setItem('activeTab', tabName);
    switchTab(tabName, event);
}

// Асинхронная функция для получения и отображения подробной информации о фильме
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

        // Показываем модальное окно
        filmModal.style.display = 'block';
    } catch (error) {
        console.error('Ошибка загрузки описания:', error);
    }
}

// DOMContentLoaded срабатывает когда HTML полностью загружен и распарсен
document.addEventListener('DOMContentLoaded', function() {
    // Находим контейнеры с карточками фильмов
    const favoritesGrid = document.getElementById('favoritesGrid');
    const notInterestedGrid = document.getElementById('notInterestedGrid');

    // Вешаем обработчик кликов на каждый контейнер (делегирование)
    if (favoritesGrid) {
        favoritesGrid.addEventListener('click', handleFilmCardClick);
    }
    if (notInterestedGrid) {
        notInterestedGrid.addEventListener('click', handleFilmCardClick);
    }

    // Восстанавливаем активную вкладку из localStorage, если нет — по умолчанию 'favorites'
    let savedTab = localStorage.getItem('activeTab') || 'favorites';
    switchTab(savedTab);

    // Подсвечиваем соответствующую кнопку вкладки
    let btns = document.querySelectorAll('.tab-btn');
    for (let i = 0; i < btns.length; i++) {
        if (btns[i].getAttribute('data-tab') === savedTab) {
            btns[i].classList.add('active');
        }
    }

    // Назначаем обработчики кликов для кнопок вкладок
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.onclick = function(e) {
            const tabName = this.getAttribute('data-tab');
            saveTab(tabName, e);
        }
    });
});

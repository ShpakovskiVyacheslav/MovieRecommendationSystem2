// Загрузка состояний из localStorage и сервера
        async function loadButtonStates() {
            var likedFilms = JSON.parse(localStorage.getItem('likedFilms') || '{}');
            var notInterestedFilms = JSON.parse(localStorage.getItem('notInterestedFilms') || '{}');

            // Обновляем кнопки из localStorage
            document.querySelectorAll('.btn-like').forEach(function(btn) {
                var filmId = btn.getAttribute('data-film-id');
                if (likedFilms[filmId]) {
                    btn.classList.add('active');
                } else {
                    btn.classList.remove('active');
                }
            });

            document.querySelectorAll('.btn-not-interested').forEach(function(btn) {
                var filmId = btn.getAttribute('data-film-id');
                if (notInterestedFilms[filmId]) {
                    btn.classList.add('active');
                } else {
                    btn.classList.remove('active');
                }
            });

            // Затем синхронизируем с сервером (получаем актуальное состояние)
            try {
                var response = await fetch('/api/user_films');
                if (response.ok) {
                    var data = await response.json();

                    // Обновляем localStorage и кнопки из данных сервера
                    var newLiked = {};
                    var newNotInterested = {};

                    data.forEach(function(item) {
                        if (item.status === 'like') {
                            newLiked[item.film_id] = true;
                        } else if (item.status === 'not_interested') {
                            newNotInterested[item.film_id] = true;
                        }
                    });

                    localStorage.setItem('likedFilms', JSON.stringify(newLiked));
                    localStorage.setItem('notInterestedFilms', JSON.stringify(newNotInterested));

                    // Обновляем кнопки
                    document.querySelectorAll('.btn-like').forEach(function(btn) {
                        var filmId = btn.getAttribute('data-film-id');
                        if (newLiked[filmId]) {
                            btn.classList.add('active');
                        } else {
                            btn.classList.remove('active');
                        }
                    });

                    document.querySelectorAll('.btn-not-interested').forEach(function(btn) {
                        var filmId = btn.getAttribute('data-film-id');
                        if (newNotInterested[filmId]) {
                            btn.classList.add('active');
                        } else {
                            btn.classList.remove('active');
                        }
                    });
                }
            } catch(e) {
                console.error('Ошибка синхронизации с сервером:', e);
            }
        }

        function handleLike(button, filmId) {
            var isActive = button.classList.contains('active');
            var notInterestedBtn = button.parentElement.querySelector('.btn-not-interested');

            if (isActive) {
                button.classList.remove('active');
            } else {
                button.classList.add('active');
                if (notInterestedBtn && notInterestedBtn.classList.contains('active')) {
                    notInterestedBtn.classList.remove('active');
                }
            }

            // Обновляем localStorage и отправляем на сервер
            if (isActive) {
                // Удаляем лайк
                var likedFilms = JSON.parse(localStorage.getItem('likedFilms') || '{}');
                delete likedFilms[filmId];
                localStorage.setItem('likedFilms', JSON.stringify(likedFilms));

                updateFilmStatus(filmId, 'remove');
            } else {
                // Добавляем лайк
                var likedFilms = JSON.parse(localStorage.getItem('likedFilms') || '{}');
                likedFilms[filmId] = true;
                localStorage.setItem('likedFilms', JSON.stringify(likedFilms));

                // Удаляем из неинтересных если было
                var notInterestedFilms = JSON.parse(localStorage.getItem('notInterestedFilms') || '{}');
                if (notInterestedFilms[filmId]) {
                    delete notInterestedFilms[filmId];
                    localStorage.setItem('notInterestedFilms', JSON.stringify(notInterestedFilms));
                }

                updateFilmStatus(filmId, 'like');
            }
        }

        function handleNotInterested(button, filmId) {
            var isActive = button.classList.contains('active');
            var likeBtn = button.parentElement.querySelector('.btn-like');

            if (isActive) {
                button.classList.remove('active');
            } else {
                button.classList.add('active');
                if (likeBtn && likeBtn.classList.contains('active')) {
                    likeBtn.classList.remove('active');
                }
            }

            // Обновляем localStorage и отправляем на сервер
            if (isActive) {
                // Удаляем отметку
                var notInterestedFilms = JSON.parse(localStorage.getItem('notInterestedFilms') || '{}');
                delete notInterestedFilms[filmId];
                localStorage.setItem('notInterestedFilms', JSON.stringify(notInterestedFilms));

                updateFilmStatus(filmId, 'remove');
            } else {
                // Добавляем отметку
                var notInterestedFilms = JSON.parse(localStorage.getItem('notInterestedFilms') || '{}');
                notInterestedFilms[filmId] = true;
                localStorage.setItem('notInterestedFilms', JSON.stringify(notInterestedFilms));

                // Удаляем из избранного если было
                var likedFilms = JSON.parse(localStorage.getItem('likedFilms') || '{}');
                if (likedFilms[filmId]) {
                    delete likedFilms[filmId];
                    localStorage.setItem('likedFilms', JSON.stringify(likedFilms));
                }

                updateFilmStatus(filmId, 'not_interested');
            }
        }

        function updateFilmStatus(filmId, status) {
            if (status === 'remove') {
                fetch('/api/favorites/' + filmId, { method: 'DELETE' })
                    .catch(function(error) { console.error('Error:', error); });
            } else {
                fetch('/api/favorites/' + filmId, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ status: status })
                }).catch(function(error) { console.error('Error:', error); });
            }
        }

        // Обработчики кликов
        document.addEventListener('click', function(e) {
            var target = e.target;
            if (target.classList && target.classList.contains('btn-like')) {
                var filmId = target.getAttribute('data-film-id');
                if (filmId) {
                    e.preventDefault();
                    handleLike(target, filmId);
                }
            } else if (target.classList && target.classList.contains('btn-not-interested')) {
                var filmId = target.getAttribute('data-film-id');
                if (filmId) {
                    e.preventDefault();
                    handleNotInterested(target, filmId);
                }
            }
        });

        // Синхронизация с сервером при загрузке страницы
        document.addEventListener('DOMContentLoaded', function() {
            loadButtonStates();

            // Синхронизируем каждые 30 секунд (на случай изменений в других вкладках)
            setInterval(loadButtonStates, 30000);
        });

        // Синхронизация при возврате на страницу (когда пользователь вернулся из профиля)
        window.addEventListener('pageshow', function() {
            loadButtonStates();
        });
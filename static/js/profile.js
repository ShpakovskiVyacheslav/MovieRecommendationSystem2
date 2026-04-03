// Переключение активного состояния жанра
        function toggleGenre(element) {
            element.classList.toggle('active');
        }

        // Применение фильтров
        function applyFilters() {
            let genres = [];
            document.querySelectorAll('.filter-tag.active').forEach(function(tag) {
                genres.push(tag.getAttribute('data-genre'));
            });
            let rating = document.getElementById('rating').value;
            let year = document.getElementById('year').value;
            alert('Применены фильтры:\nЖанры: ' + (genres.join(', ') || 'не выбраны') + '\nРейтинг: ' + rating + '\nГод: ' + year);
        }

        // Переключение между вкладками
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

        // Сохранение активной вкладки в localStorage
        function saveTab(tabName, event) {
            localStorage.setItem('activeTab', tabName);
            switchTab(tabName, event);
        }

        // Загрузка сохраненной вкладки при загрузке страницы
        document.addEventListener('DOMContentLoaded', function() {
            let savedTab = localStorage.getItem('activeTab') || 'favorites';
            switchTab(savedTab);
            let btns = document.querySelectorAll('.tab-btn');
            for (let i = 0; i < btns.length; i++) {
                if (btns[i].getAttribute('onclick') && btns[i].getAttribute('onclick').indexOf(savedTab) !== -1) {
                    btns[i].classList.add('active');
                }
            }
        });
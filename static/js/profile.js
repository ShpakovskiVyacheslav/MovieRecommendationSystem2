const modal = document.getElementById('filterModal');
const openBtn = document.getElementById('openFilterBtn');
const closeBtn = document.getElementById('closeFilterBtn');

if (openBtn) {
    openBtn.onclick = function() { modal.style.display = 'block'; }
}

if (closeBtn) {
    closeBtn.onclick = function() { modal.style.display = 'none'; }
}

window.onclick = function(event) {
    if (event.target == modal) modal.style.display = 'none';
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

document.addEventListener('DOMContentLoaded', function() {
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

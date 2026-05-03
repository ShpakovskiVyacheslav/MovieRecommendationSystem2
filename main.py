from flask import Flask, request, render_template, redirect, session, jsonify
import random
import os
import math
import requests
import re
import smtplib
from email.message import EmailMessage
import time

from data.db_session import global_init, create_session
from data.users import User
from data.films import Film
from data.film_genre import FilmGenre
from data.genres import Genre
from data.user_film import UserFilm
from sqlalchemy import case, func

app = Flask(__name__)
app.secret_key = '[k1l8a@\)Z}SQ2aHKCDjxFF–v#34RK'

EMAIL_ADDRESS = 'sistemarekomendacij@gmail.com'
APP_PASSWORD = 'gpvuwkwlgvvkspww'

db_path = os.path.join(os.path.dirname(__file__), 'db', 'database.db')
os.makedirs(os.path.dirname(db_path), exist_ok=True)
global_init(db_path)

static_dir = os.path.join(os.path.dirname(__file__), 'static')
css_dir = os.path.join(static_dir, 'css')
uploads_dir = os.path.join(static_dir, 'uploads')

os.makedirs(css_dir, exist_ok=True)
os.makedirs(uploads_dir, exist_ok=True)

reset_codes = {}


def send_reset_code(email_to, code):
    try:
        msg = EmailMessage()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = email_to
        msg['Subject'] = 'Код для сброса пароля'
        msg.set_content(f'Ваш код для сброса пароля: {code}\n\nКод действителен 10 минут.')

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_ADDRESS, APP_PASSWORD)
            server.send_message(msg)

        return True
    except Exception as e:
        print(f"Ошибка отправки: {e}")
        return False


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'GET':
        return render_template('login.html', error=None)
    elif request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')

        if not login or not password:
            return render_template('login.html', error='Пожалуйста, заполните все поля')

        db_sess = create_session()
        try:
            user = db_sess.query(User).filter(User.username == login).first()

            if user and user.check_password(password):
                session['user_id'] = user.id
                session['username'] = user.username
                return redirect(f'/main/{user.username}')
            else:
                return render_template('login.html', error='Неверный логин или пароль')
        finally:
            db_sess.close()


@app.route('/main/<username>', methods=['GET'])
def main_page(username):
    db_sess = create_session()
    try:
        user = db_sess.query(User).filter(User.username == username).first()

        if not user:
            return "Пользователь не найден", 404

        query = request.args.get('query', '')
        page = request.args.get('page', 1, type=int)
        per_page = 15

        genres_str = request.args.get('genres', '')
        selected_genres = [g.strip() for g in genres_str.split(',') if g.strip()]
        selected_rating = request.args.get('rating', 'any')
        selected_years = request.args.get('year', 'all')

        session['filters'] = {
            'genres': genres_str,
            'rating': selected_rating,
            'year': selected_years
        }

        base_query = db_sess.query(Film).order_by(Film.rating.desc().nullslast())

        if query:
            lower_query = query.lower()
            relevance = case(
                (func.lower(Film.name) == lower_query, 0),
                (func.lower(Film.name).like(f"{lower_query}%"), 1),
                else_=2
            )

            base_query = db_sess.query(Film).filter(
                func.lower(Film.name).like(f"%{lower_query}%")
            ).order_by(relevance, Film.rating.desc().nullslast())

        if selected_genres:
            base_query = base_query.join(FilmGenre).filter(
                FilmGenre.genre_id.in_(selected_genres)
            ).order_by(Film.rating.desc().nullslast())

        if selected_rating != "any":
            base_query = base_query.filter(
                Film.rating >= float(int(selected_rating))
            ).order_by(Film.rating.desc().nullslast())

        if selected_years != "all":
            start_year, end_year = map(int, selected_years.split('-'))
            base_query = base_query.filter(
                Film.release_year.between(start_year, end_year)
            ).order_by(Film.rating.desc().nullslast())

        total_films = base_query.count()
        total_pages = math.ceil(total_films / per_page) if total_films > 0 else 1
        films = base_query.offset((page - 1) * per_page).limit(per_page).all()

        return render_template('main.html',
                               login=username,
                               username=user.username,
                               query=query,
                               avatar_url=user.avatar,
                               films=films,
                               page=page,
                               rating=selected_rating,
                               year=selected_years,
                               genres=genres_str,
                               total_pages=total_pages,
                               total_films=total_films)
    finally:
        db_sess.close()


@app.route('/profile/<username>', methods=['GET', 'POST'])
def profile(username):
    db_sess = create_session()
    try:
        user = db_sess.query(User).filter(User.username == username).first()

        if not user:
            return "Пользователь не найден", 404

        if request.method == 'POST' and 'avatar' in request.files:
            file = request.files['avatar']
            if file and file.filename:
                filename = f"{username}_{random.randint(1000, 9999)}.jpg"
                file.save(os.path.join('static', 'uploads', filename))

                old_avatar = user.avatar
                if old_avatar:
                    old_path = os.path.join('static', 'uploads', old_avatar)
                    if os.path.exists(old_path):
                        os.remove(old_path)

                user.avatar = filename
                db_sess.commit()
                return redirect(f'/profile/{username}')

        page_liked = request.args.get('page_liked', 1, type=int)
        page_not_interested = request.args.get('page_not_interested', 1, type=int)
        per_page = 15

        genres_str = request.args.get('genres', '')
        selected_genres = [g.strip() for g in genres_str.split(',') if g.strip()]
        selected_rating = request.args.get('rating', 'any')
        selected_years = request.args.get('year', 'all')

        liked_count_total = db_sess.query(UserFilm).filter(
            UserFilm.user_id == user.id,
            UserFilm.status == 'like'
        ).count()

        not_interested_count_total = db_sess.query(UserFilm).filter(
            UserFilm.user_id == user.id,
            UserFilm.status == 'not_interested'
        ).count()

        favorite_films_query = db_sess.query(Film).join(UserFilm).filter(
            UserFilm.user_id == user.id,
            UserFilm.status == 'like'
        ).order_by(Film.rating.desc().nullslast())

        not_interested_films_query = db_sess.query(Film).join(UserFilm).filter(
            UserFilm.user_id == user.id,
            UserFilm.status == 'not_interested'
        ).order_by(Film.rating.desc().nullslast())

        if selected_genres:
            favorite_films_query = favorite_films_query.join(FilmGenre).filter(
                FilmGenre.genre_id.in_(selected_genres)
            ).order_by(Film.rating.desc().nullslast())

            not_interested_films_query = not_interested_films_query.join(FilmGenre).filter(
                FilmGenre.genre_id.in_(selected_genres)
            ).order_by(Film.rating.desc().nullslast())

        if selected_rating != "any":
            favorite_films_query = favorite_films_query.filter(
                Film.rating >= float(selected_rating)
            ).order_by(Film.rating.desc().nullslast())

            not_interested_films_query = not_interested_films_query.filter(
                Film.rating >= float(selected_rating)
            ).order_by(Film.rating.desc().nullslast())

        if selected_years != "all":
            start_year, end_year = map(int, selected_years.split('-'))
            favorite_films_query = favorite_films_query.filter(
                Film.release_year.between(start_year, end_year)
            ).order_by(Film.rating.desc().nullslast())

            not_interested_films_query = not_interested_films_query.filter(
                Film.release_year.between(start_year, end_year)
            ).order_by(Film.rating.desc().nullslast())

        total_pages_liked = math.ceil(liked_count_total / per_page) if liked_count_total > 0 else 1
        favorite_films = favorite_films_query.offset((page_liked - 1) * per_page).limit(per_page).all()

        total_pages_not_interested = math.ceil(
            not_interested_count_total / per_page) if not_interested_count_total > 0 else 1
        not_interested_films = not_interested_films_query.offset((page_not_interested - 1) * per_page).limit(
            per_page).all()

        return render_template('profile.html',
                               login=username,
                               user=user,
                               liked_count_total=liked_count_total,
                               not_interested_count_total=not_interested_count_total,
                               favorite_films=favorite_films,
                               not_interested_films=not_interested_films,
                               page_liked=page_liked,
                               total_pages_liked=total_pages_liked,
                               page_not_interested=page_not_interested,
                               total_pages_not_interested=total_pages_not_interested)
    finally:
        db_sess.close()


@app.route('/register', methods=['POST', 'GET'])
def register():
    error = None

    if request.method == 'GET':
        return render_template('register.html', error=error)

    elif request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        login = request.form.get('login')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            error = 'Пароли не совпадают'
            return render_template('register.html', error=error,
                                   email=email, username=username, login=login)

        # Проверка сложности пароля
        if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*])[A-Za-z\d!@#$%^&*]{8,16}$', password):
            error = 'Пароль должен содержать 8-16 символов: строчные и заглавные буквы, цифры и спецсимволы (!@#$%^&*)'
            return render_template('register.html', error=error,
                                   email=email, username=username, login=login)

        db_sess = create_session()
        try:
            existing_user = db_sess.query(User).filter(
                (User.username == login) | (User.email == email)
            ).first()

            if existing_user:
                error = 'Пользователь с таким логином или email уже существует'
                return render_template('register.html', error=error,
                                       email=email, username=username, login=login)

            user = User()
            user.username = login
            user.email = email
            user.set_password(password)

            db_sess.add(user)
            db_sess.commit()

            session['user_id'] = user.id
            session['username'] = user.username

            return redirect(f'/main/{user.username}')
        finally:
            db_sess.close()


@app.route('/reset', methods=['POST', 'GET'])
def reset():
    if request.method == 'GET':
        return render_template('reset_request.html')
    elif request.method == 'POST':
        email = request.form.get('email')

        if not email:
            return "Введите email", 400

        db_sess = create_session()
        user = db_sess.query(User).filter(User.email == email).first()
        db_sess.close()

        if not user:
            return "Пользователь с таким email не найден", 404

        reset_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        reset_codes[email] = {'code': reset_code, 'timestamp': time.time()}

        if send_reset_code(email, reset_code):
            return render_template('reset_verify.html', email=email)
        else:
            return "Ошибка отправки письма. Попробуйте позже.", 500


@app.route('/reset_confirm', methods=['POST'])
def reset_confirm():
    email = request.form.get('email')
    code = request.form.get('code')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')

    if new_password != confirm_password:
        return "Пароли не совпадают", 400

    # Проверка сложности нового пароля при сбросе
    if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*])[A-Za-z\d!@#$%^&*]{8,16}$', new_password):
        return "Пароль должен содержать 8-16 символов: строчные и заглавные буквы, цифры и спецсимволы (!@#$%^&*)", 400

    stored = reset_codes.get(email)
    if not stored or stored['code'] != code:
        return "Неверный код", 400

    if time.time() - stored['timestamp'] > 600:
        return "Код истёк. Запросите новый", 400

    db_sess = create_session()
    user = db_sess.query(User).filter(User.email == email).first()

    if user:
        user.set_password(new_password)
        db_sess.commit()
        del reset_codes[email]
        db_sess.close()
        return redirect('/')

    db_sess.close()
    return "Пользователь не найден", 404


@app.route('/api/favorites/<int:film_id>', methods=['POST', 'DELETE'])
def add_to_favorites(film_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Необходимо войти в систему'}), 401

    db_sess = create_session()
    try:
        if request.method == 'DELETE':
            user_film = db_sess.query(UserFilm).filter(
                UserFilm.user_id == session['user_id'],
                UserFilm.film_id == film_id
            ).first()
            if user_film:
                db_sess.delete(user_film)
                db_sess.commit()
            return jsonify({'success': True})

        data = request.get_json()
        status = data.get('status', 'like')

        film = db_sess.query(Film).get(film_id)
        if not film:
            return jsonify({'success': False, 'error': 'Фильм не найден'}), 404

        user_film = db_sess.query(UserFilm).filter(
            UserFilm.user_id == session['user_id'],
            UserFilm.film_id == film_id
        ).first()

        if user_film:
            user_film.status = status
        else:
            user_film = UserFilm(
                user_id=session['user_id'],
                film_id=film_id,
                status=status
            )
            db_sess.add(user_film)

        db_sess.commit()
        return jsonify({'success': True})
    finally:
        db_sess.close()


@app.route('/remove_favorite/<username>/<int:film_id>', methods=['GET'])
def remove_favorite(username, film_id):
    if 'user_id' not in session:
        return redirect('/')

    db_sess = create_session()
    try:
        user_film = db_sess.query(UserFilm).filter(
            UserFilm.user_id == session['user_id'],
            UserFilm.film_id == film_id
        ).first()

        if user_film:
            db_sess.delete(user_film)
            db_sess.commit()

        return redirect(f'/profile/{username}')
    finally:
        db_sess.close()


@app.route('/api/user_films', methods=['GET'])
def get_user_films():
    if 'user_id' not in session:
        return jsonify([])

    db_sess = create_session()
    try:
        user_films = db_sess.query(UserFilm).filter(
            UserFilm.user_id == session['user_id']
        ).all()

        result = []
        for uf in user_films:
            result.append({
                'film_id': uf.film_id,
                'status': uf.status
            })

        return jsonify(result)
    finally:
        db_sess.close()


@app.route('/api/get_recommendations', methods=['GET'])
def get_recommendations():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    try:
        filters = session.get('filters', {})
        selected_genres = filters.get('genres', '')
        selected_rating = filters.get('rating', 'any')
        selected_years = filters.get('year', 'all')

        response = requests.get(
            'http://127.0.0.1:5001/api/recommendations',
            params={'user_id': session['user_id']},
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()

            if data.get('recommendations'):
                db_sess = create_session()
                try:
                    recommended_ml_ids = data['recommendations']

                    user_films = db_sess.query(UserFilm).filter(
                        UserFilm.user_id == session['user_id']
                    ).all()
                    excluded_film_ids = {uf.film_id for uf in user_films}

                    chunk_size = 500
                    all_films = []

                    for i in range(0, len(recommended_ml_ids), chunk_size):
                        chunk = recommended_ml_ids[i:i + chunk_size]
                        films_chunk = db_sess.query(Film).filter(
                            Film.ml_id.in_(chunk)
                        ).all()
                        all_films.extend(films_chunk)

                    film_dict = {film.ml_id: film for film in all_films}

                    result = []
                    for ml_id in recommended_ml_ids:
                        film = film_dict.get(ml_id)
                        if not film or film.id in excluded_film_ids:
                            continue

                        if selected_genres:
                            film_genre_ids = [str(i.id) for i in film.genres]
                            if not any(i in selected_genres for i in film_genre_ids):
                                continue

                        if selected_rating != 'any':
                            try:
                                min_rating = float(selected_rating)
                                if film.rating < min_rating:
                                    continue
                            except ValueError:
                                pass

                        if selected_years != 'all':
                            try:
                                start, end = map(int, selected_years.split('-'))
                                if not (start <= film.release_year <= end):
                                    continue
                            except ValueError:
                                pass
                        genres = [{'id': g.id, 'name': g.name} for g in film.genres]
                        result.append({
                            'id': film.id,
                            'ml_id': film.ml_id,
                            'name': film.name,
                            'poster': film.poster,
                            'rating': film.rating,
                            'release_year': film.release_year,
                            'description': film.description,
                            'genres': genres
                        })

                    return jsonify({
                        'user_id': session['user_id'],
                        'recommendations': result,
                        'total': len(result)
                    })
                finally:
                    db_sess.close()
            else:
                return jsonify({
                    'user_id': session['user_id'],
                    'recommendations': [],
                    'message': data.get('message', 'No recommendations')
                })
        else:
            return jsonify({'error': 'Не удалось получить рекомендации'}), 500

    except requests.exceptions.Timeout:
        return jsonify({'error': 'Превышено время ожидания сервера', 'recommendations': []}), 200
    except requests.exceptions.ConnectionError:
        return jsonify(
            {'error': 'Сервис рекомендаций недоступен. Пожалуйста, запустите rec.py и обновите страницу.',
             'recommendations': []}), 200
    except Exception as e:
        return jsonify({'error': str(e), 'recommendations': []}), 200


@app.route('/api/film/<int:film_id>', methods=['GET'])
def get_film_details(film_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    db_sess = create_session()
    try:
        film = db_sess.query(Film).get(film_id)
        if not film:
            return jsonify({'error': 'Фильм не найден'}), 404

        genres = [{'id': g.id, 'name': g.name} for g in film.genres]

        return jsonify({
            'id': film.id,
            'name': film.name,
            'poster': film.poster,
            'description': film.description,
            'rating': film.rating,
            'release_year': film.release_year,
            'genres': genres
        })
    finally:
        db_sess.close()


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)

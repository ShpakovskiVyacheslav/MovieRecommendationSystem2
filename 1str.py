from flask import Flask, request, render_template, redirect, session, jsonify
import random
import os
import math

from data.db_session import global_init, create_session
from data.users import User
from data.films import Film
from data.genres import Genre
from data.user_film import UserFilm
from sqlalchemy import case, func

app = Flask(__name__)
app.secret_key = '[k1l8a@\)Z}SQ2aHKCDjxFF–v#34RK'

# Инициализация базы данных
db_path = os.path.join(os.path.dirname(__file__), 'db', 'database.db')
os.makedirs(os.path.dirname(db_path), exist_ok=True)
global_init(db_path)

# Создание папок для статики
static_dir = os.path.join(os.path.dirname(__file__), 'static')
css_dir = os.path.join(static_dir, 'css')
uploads_dir = os.path.join(static_dir, 'uploads')
posters_dir = os.path.join(static_dir, 'posters')

os.makedirs(css_dir, exist_ok=True)
os.makedirs(uploads_dir, exist_ok=True)
os.makedirs(posters_dir, exist_ok=True)

reset_codes = {}


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')

        db_sess = create_session()
        user = db_sess.query(User).filter(User.username == login).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(f'/main/{user.username}')
        else:
            return '''
            <h2>Ошибка входа</h2>
            <p>Неверный логин или пароль</p>
            <a href="/">Попробовать снова</a>
            '''


@app.route('/main/<username>', methods=['GET'])
def main_page(username):
    db_sess = create_session()
    user = db_sess.query(User).filter(User.username == username).first()

    if not user:
        return "Пользователь не найден", 404

    query = request.args.get('query', '')
    page = request.args.get('page', 1, type=int)
    per_page = 15

    films = []
    total_films = 0
    total_pages = 0

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
                           total_pages=total_pages,
                           total_films=total_films)


@app.route('/profile/<username>', methods=['GET', 'POST'])
def profile(username):
    db_sess = create_session()
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

    total_pages_liked = math.ceil(liked_count_total / per_page) if liked_count_total > 0 else 1
    favorite_films = favorite_films_query.offset((page_liked - 1) * per_page).limit(per_page).all()

    not_interested_films_query = db_sess.query(Film).join(UserFilm).filter(
        UserFilm.user_id == user.id,
        UserFilm.status == 'not_interested'
    ).order_by(Film.rating.desc().nullslast())

    total_pages_not_interested = math.ceil(
        not_interested_count_total / per_page) if not_interested_count_total > 0 else 1
    not_interested_films = not_interested_films_query.offset((page_not_interested - 1) * per_page).limit(per_page).all()

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

        # Проверка совпадения паролей
        if password != confirm_password:
            error = 'Пароли не совпадают'
            return render_template('register.html', error=error,
                                   email=email, username=username, login=login)

        db_sess = create_session()

        # Проверка существования пользователя
        existing_user = db_sess.query(User).filter(
            (User.username == login) | (User.email == email)
        ).first()

        if existing_user:
            error = 'Пользователь с таким логином или email уже существует'
            return render_template('register.html', error=error,
                                   email=email, username=username, login=login)

        # Создание пользователя
        user = User()
        user.username = login
        user.email = email
        user.set_password(password)

        db_sess.add(user)
        db_sess.commit()

        return redirect(f'/main/{user.username}')


@app.route('/reset', methods=['POST', 'GET'])
def reset():
    if request.method == 'GET':
        reset_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        reset_codes['current'] = reset_code
        return render_template('reset.html', reset_code=reset_code)
    elif request.method == 'POST':
        entered_code = request.form.get('reset_code')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_new_password')

        if entered_code != reset_codes.get('current'):
            return '''
            <h2>Ошибка!</h2>
            <p>Неверный код подтверждения</p>
            <a href="/reset">Попробовать снова</a>
            '''

        if new_password != confirm_password:
            return '''
            <h2>Ошибка!</h2>
            <p>Новые пароли не совпадают</p>
            <a href="/reset">Попробовать снова</a>
            '''

        reset_codes.pop('current', None)
        return '''
        <h2>Пароль успешно изменен!</h2>
        <p>Теперь вы можете <a href="/">войти с новым паролем</a></p>
        '''


@app.route('/api/favorites/<int:film_id>', methods=['POST', 'DELETE'])
def add_to_favorites(film_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Необходимо войти в систему'}), 401

    db_sess = create_session()

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


@app.route('/remove_favorite/<username>/<int:film_id>', methods=['GET'])
def remove_favorite(username, film_id):
    if 'user_id' not in session:
        return redirect('/')

    db_sess = create_session()

    user_film = db_sess.query(UserFilm).filter(
        UserFilm.user_id == session['user_id'],
        UserFilm.film_id == film_id
    ).first()

    if user_film:
        db_sess.delete(user_film)
        db_sess.commit()

    return redirect(f'/profile/{username}')


@app.route('/api/user_films', methods=['GET'])
def get_user_films():
    if 'user_id' not in session:
        return jsonify([])

    db_sess = create_session()
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


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)

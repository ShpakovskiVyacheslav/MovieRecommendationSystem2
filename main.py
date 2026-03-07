from flask import Flask, request, render_template, redirect
import random
import os
from data import db_session
from data.users import User
from data.films import Film

app = Flask(__name__)

db_session.global_init("db/database.db")

reset_codes = {}


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')

        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(
            (User.username == login) | (User.email == login)
        ).first()

        if user and user.check_password(password):
            return redirect(f'/main/{user.username}')
        else:
            return '''
            <h2>Ошибка входа</h2>
            <p>Неверный логин или пароль</p>
            <a href="/">Попробовать снова</a>
            '''


@app.route('/main/<login>', methods=['GET'])
def main_page(login):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.username == login).first()

    if not user:
        return "Пользователь не найден", 404

    query = request.args.get('query', '')
    avatar_url = user.avatar

    films = []
    if query:
        films = db_sess.query(Film).filter(Film.name.ilike(f'%{query}%')).all()

    return render_template('main.html', login=login, username=user.username,
                           query=query, avatar_url=avatar_url, films=films)


@app.route('/profile/<login>', methods=['GET', 'POST'])
def profile(login):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.username == login).first()

    if not user:
        return "Пользователь не найден", 404

    if request.method == 'POST' and 'avatar' in request.files:
        file = request.files['avatar']
        if file and file.filename:
            filename = f"{login}_{random.randint(1000, 9999)}.jpg"
            file.save(f'static/uploads/{filename}')

            old_avatar = user.avatar
            if old_avatar and os.path.exists(f'static/uploads/{old_avatar}'):
                os.remove(f'static/uploads/{old_avatar}')

            user.avatar = filename
            db_sess.commit()
            return redirect(f'/profile/{login}')

    return render_template('profile.html', login=login, user=user)


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        login = request.form.get('login')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            return '''
            <h2>Ошибка!</h2>
            <p>Пароли не совпадают</p>
            <a href="/register">Вернуться к регистрации</a>
            '''

        db_sess = db_session.create_session()

        existing_user = db_sess.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing_user:
            return '''
            <h2>Ошибка!</h2>
            <p>Пользователь с таким логином или email уже существует</p>
            <a href="/register">Вернуться к регистрации</a>
            '''

        user = User(
            username=username,
            email=email
        )
        user.set_password(password)

        db_sess.add(user)
        db_sess.commit()

        return f'''
        <h2>Регистрация успешна!</h2>
        <p>Добро пожаловать, {username}!</p>
        <p>Теперь вы можете <a href="/">войти в систему</a></p>
        '''


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


if __name__ == '__main__':
    app.run(debug=True)

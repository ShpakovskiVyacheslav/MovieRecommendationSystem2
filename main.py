from flask import Flask, request, render_template, redirect
import random
import os
from styles import CSS_CONTENT  # Импортируем стили из отдельного файла

app = Flask(__name__)

if not os.path.exists('static/css'):
    os.makedirs('static/css')
if not os.path.exists('static/uploads'):
    os.makedirs('static/uploads')

# Используем импортированные стили
with open('static/css/style.css', 'w', encoding='utf-8') as f:
    f.write(CSS_CONTENT)

reset_codes = {}
users_db = {}


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')

        if login in users_db and users_db[login]['password'] == password:
            return redirect(f'/main/{login}')
        else:
            return '''
            <h2>Ошибка входа</h2>
            <p>Неверный логин или пароль</p>
            <a href="/">Попробовать снова</a>
            '''


@app.route('/main/<login>', methods=['GET'])
def main_page(login):
    if login not in users_db:
        return "Пользователь не найден", 404

    username = users_db[login]['username']
    query = request.args.get('query', '')
    avatar_url = users_db[login].get('avatar')

    return render_template('main.html', login=login, username=username, query=query, avatar_url=avatar_url)


@app.route('/profile/<login>', methods=['GET', 'POST'])
def profile(login):
    if login not in users_db:
        return "Пользователь не найден", 404

    user = users_db[login]

    if request.method == 'POST' and 'avatar' in request.files:
        file = request.files['avatar']
        if file and file.filename:
            filename = f"{login}_{random.randint(1000, 9999)}.jpg"
            file.save(f'static/uploads/{filename}')

            old_avatar = user.get('avatar')
            if old_avatar and os.path.exists(f'static/uploads/{old_avatar}'):
                os.remove(f'static/uploads/{old_avatar}')

            users_db[login]['avatar'] = filename
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

        if login in users_db:
            return '''
            <h2>Ошибка!</h2>
            <p>Пользователь с таким логином уже существует</p>
            <a href="/register">Вернуться к регистрации</a>
            '''

        users_db[login] = {
            'email': email,
            'username': username,
            'password': password,
            'avatar': None
        }

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
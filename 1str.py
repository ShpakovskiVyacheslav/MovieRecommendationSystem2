from flask import Flask, request, render_template, redirect
import random
import os

app = Flask(__name__)

if not os.path.exists('static/css'):
    os.makedirs('static/css')
if not os.path.exists('static/uploads'):
    os.makedirs('static/uploads')

css_content = """
form.login_form {
    margin-left: auto;
    margin-right: auto;
    max-width: 400px;
    background-color: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 10px;
    padding: 30px;
    box-shadow: 0 0 10px rgba(0,0,0,0.1);
}

.form-title {
    text-align: center;
    margin-bottom: 30px;
    color: #333;
}

.switch-link {
    text-align: center;
    margin-top: 20px;
}

.switch-link a {
    color: #0d6efd;
    text-decoration: none;
    margin: 0 10px;
}

.switch-link a:hover {
    text-decoration: underline;
}

.reset-code {
    background-color: #e9ecef;
    padding: 15px;
    text-align: center;
    font-size: 24px;
    font-weight: bold;
    letter-spacing: 5px;
    border-radius: 5px;
    margin-bottom: 20px;
    color: #495057;
}

.main-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

.header {
    display: flex;
    justify-content: flex-end;
    padding: 10px 20px;
    background-color: #f8f9fa;
    border-bottom: 1px solid #dee2e6;
}

.profile-circle {
    width: 50px;
    height: 50px;
    border-radius: 50%;
    background-color: #0d6efd;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: bold;
    font-size: 20px;
    cursor: pointer;
    transition: background-color 0.3s;
    text-decoration: none;
}

.profile-circle:hover {
    background-color: #0b5ed7;
}

.recommended-section {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 40px;
    border-radius: 10px;
    margin: 30px 0;
    text-align: center;
    min-height: 200px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.recommended-section p {
    font-size: 18px;
    opacity: 0.9;
}

.search-section {
    margin: 30px 0;
}

.search-box {
    display: flex;
    gap: 10px;
    margin-bottom: 30px;
}

.search-input {
    flex: 1;
    padding: 15px;
    font-size: 16px;
    border: 2px solid #dee2e6;
    border-radius: 5px;
    transition: border-color 0.3s;
}

.search-input:focus {
    outline: none;
    border-color: #0d6efd;
}

.search-button {
    padding: 15px 30px;
    background-color: #0d6efd;
    color: white;
    border: none;
    border-radius: 5px;
    font-size: 16px;
    cursor: pointer;
    transition: background-color 0.3s;
}

.search-button:hover {
    background-color: #0b5ed7;
}

.results-section {
    margin-top: 30px;
    min-height: 200px;
    border: 2px dashed #dee2e6;
    border-radius: 10px;
    padding: 20px;
}

.results-placeholder {
    color: #6c757d;
    text-align: center;
    padding: 40px;
    font-size: 18px;
}

.profile-page {
    max-width: 1200px;
    margin: 40px auto;
    padding: 0 20px;
}

.profile-header {
    display: grid;
    grid-template-columns: 200px 1fr 300px;
    gap: 30px;
    background-color: #f8f9fa;
    padding: 30px;
    border-radius: 15px;
    box-shadow: 0 0 20px rgba(0,0,0,0.1);
}

.profile-avatar-section {
    text-align: center;
}

.profile-avatar {
    width: 150px;
    height: 150px;
    border-radius: 50%;
    background-color: #e9ecef;
    border: 3px solid #0d6efd;
    margin-bottom: 15px;
    cursor: pointer;
    transition: opacity 0.3s;
    object-fit: cover;
}

.profile-avatar:hover {
    opacity: 0.8;
}

.change-avatar-btn {
    background-color: #0d6efd;
    color: white;
    border: none;
    padding: 8px 15px;
    border-radius: 5px;
    cursor: pointer;
    font-size: 14px;
    transition: background-color 0.3s;
}

.change-avatar-btn:hover {
    background-color: #0b5ed7;
}

.profile-info-section {
    padding: 20px;
}

.profile-username {
    font-size: 28px;
    font-weight: bold;
    color: #333;
    margin-bottom: 10px;
}

.profile-email {
    color: #666;
    margin-bottom: 20px;
}

.profile-stats {
    background-color: white;
    padding: 20px;
    border-radius: 10px;
    border: 1px solid #dee2e6;
}

.profile-stats h3 {
    color: #333;
    margin-bottom: 15px;
    font-size: 18px;
}

.stat-item {
    display: flex;
    justify-content: space-between;
    padding: 10px 0;
    border-bottom: 1px solid #dee2e6;
}

.stat-item:last-child {
    border-bottom: none;
}

.stat-label {
    color: #666;
}

.stat-value {
    color: #0d6efd;
    font-weight: bold;
}

.profile-filters {
    background-color: white;
    padding: 20px;
    border-radius: 10px;
    border: 1px solid #dee2e6;
}

.profile-filters h3 {
    color: #333;
    margin-bottom: 15px;
    font-size: 18px;
}

.filter-group {
    margin-bottom: 20px;
}

.filter-group label {
    display: block;
    margin-bottom: 8px;
    color: #666;
    font-size: 14px;
}

.filter-select {
    width: 100%;
    padding: 8px;
    border: 1px solid #dee2e6;
    border-radius: 5px;
    color: #333;
    background-color: white;
    cursor: pointer;
}

.filter-select:hover {
    border-color: #0d6efd;
}

.filter-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 10px;
}

.filter-tag {
    display: inline-block;
    background-color: #e9ecef;
    padding: 8px 15px;
    border-radius: 20px;
    font-size: 14px;
    color: #495057;
    cursor: pointer;
    transition: all 0.3s;
    border: none;
    user-select: none;
}

.filter-tag:hover {
    background-color: #dee2e6;
}

.filter-tag.active {
    background-color: #0d6efd;
    color: white;
}

.favorites-section {
    margin-top: 30px;
    background-color: #f8f9fa;
    padding: 30px;
    border-radius: 15px;
    box-shadow: 0 0 20px rgba(0,0,0,0.1);
}

.favorites-section h3 {
    color: #333;
    margin-bottom: 20px;
    font-size: 22px;
}

.favorites-placeholder {
    color: #6c757d;
    text-align: center;
    padding: 60px;
    font-size: 18px;
    background-color: white;
    border-radius: 10px;
    border: 2px dashed #dee2e6;
}

.filters-form {
    width: 100%;
}

.apply-filters-btn {
    width: 100%;
    padding: 10px;
    background-color: #0d6efd;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-size: 14px;
    transition: background-color 0.3s;
    margin-top: 10px;
}

.apply-filters-btn:hover {
    background-color: #0b5ed7;
}
"""

with open('static/css/style.css', 'w', encoding='utf-8') as f:
    f.write(css_content)

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
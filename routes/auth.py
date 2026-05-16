from flask import Blueprint, render_template, request, redirect, session, make_response
import random
import re
import time
from data import create_session, User
from services.email_service import send_reset_code
from config import Config

auth_bp = Blueprint('auth', __name__)

reset_codes = {}

@auth_bp.route('/', methods=['POST', 'GET'])
def index():
    """Страница входа."""
    if request.method == 'GET':
        remember_token = request.cookies.get('remember_token')
        if remember_token:
            db_sess = create_session()
            try:
                user = db_sess.query(User).filter(User.remember_token == remember_token).first()
                if user:
                    session['user_id'] = user.id
                    session['login'] = user.login
                    return redirect(f'/main/{user.login}')
            finally:
                db_sess.close()
        return render_template('login.html', error=None)

    elif request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        remember_me = request.form.get('remember_me') == 'on'

        if not login or not password:
            return render_template('login.html', error='Пожалуйста, заполните все поля')

        db_sess = create_session()
        try:
            user = db_sess.query(User).filter(User.login == login).first()
            if user and user.check_password(password):
                session['user_id'] = user.id
                session['login'] = user.login
                response = make_response(redirect(f'/main/{user.login}'))

                if remember_me:
                    token = str(random.randint(10000000, 99999999)) + str(user.id)
                    user.remember_token = token
                    db_sess.commit()
                    response.set_cookie('remember_token', token, max_age=30 * 24 * 60 * 60)
                else:
                    response.set_cookie('remember_token', '', expires=0)
                    if user.remember_token:
                        user.remember_token = None
                        db_sess.commit()
                return response
            else:
                return render_template('login.html', error='Неверный логин или пароль')
        finally:
            db_sess.close()

@auth_bp.route('/register', methods=['POST', 'GET'])
def register():
    """Страница регистрации нового пользователя."""
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
            return render_template('register.html', error=error, email=email, username=username, login=login)

        if len(username) < 3 or len(username) > 20:
            error = 'Имя пользователя должно содержать от 3 до 20 символов'
            return render_template('register.html', error=error, email=email, username=username, login=login)

        if len(login) < 3 or len(login) > 20:
            error = 'Логин должен содержать от 3 до 20 символов'
            return render_template('register.html', error=error, email=email, username=username, login=login)

        if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*])[A-Za-z\d!@#$%^&*]{8,16}$', password):
            error = 'Пароль должен содержать 8-16 символов: строчные и заглавные буквы, цифры и спецсимволы (!@#$%^&*)'
            return render_template('register.html', error=error, email=email, username=username, login=login)

        db_sess = create_session()
        try:
            existing_user = db_sess.query(User).filter(
                (User.login == login) | (User.email == email)
            ).first()
            if existing_user:
                error = 'Пользователь с таким логином или email уже существует'
                return render_template('register.html', error=error, email=email, username=username, login=login)

            user = User()
            user.login = login
            user.username = username
            user.email = email
            user.set_password(password)

            db_sess.add(user)
            db_sess.commit()
            session['user_id'] = user.id
            session['login'] = user.login
            return redirect(f'/main/{user.login}')
        finally:
            db_sess.close()

@auth_bp.route('/reset', methods=['POST', 'GET'])
def reset():
    """Страница сброса пароля."""
    if request.method == 'GET':
        return render_template('reset_request.html')
    elif request.method == 'POST':
        email = request.form.get('email')
        if not email:
            return render_template('reset_request.html', error='Введите email')

        db_sess = create_session()
        user = db_sess.query(User).filter(User.email == email).first()
        db_sess.close()

        if not user:
            return render_template('reset_request.html', error='Пользователь с таким email не найден', email=email)

        reset_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        reset_codes[email] = {'code': reset_code, 'timestamp': time.time()}

        if send_reset_code(email, reset_code, Config.EMAIL_ADDRESS, Config.APP_PASSWORD):
            return render_template('reset_verify.html', email=email)
        else:
            return render_template('reset_request.html', error='Ошибка отправки письма. Попробуйте позже.', email=email)

@auth_bp.route('/reset_confirm', methods=['POST'])
def reset_confirm():
    """Установка нового пароля пользователя."""
    email = request.form.get('email')
    code = request.form.get('code')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')

    if new_password != confirm_password:
        return "Пароли не совпадают", 400

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

@auth_bp.route('/logout')
def logout():
    """Выход из системы."""
    if 'user_id' in session:
        db_sess = create_session()
        try:
            user = db_sess.query(User).filter(User.id == session['user_id']).first()
            if user:
                user.remember_token = None
                db_sess.commit()
        finally:
            db_sess.close()

    session.clear()
    response = make_response(redirect('/'))
    response.set_cookie('remember_token', '', expires=0)
    return response

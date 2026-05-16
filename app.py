from flask import Flask
import os
from data import global_init
from config import Config
from routes import auth_bp, main_bp, profile_bp, api_bp

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY

# Инициализация базы данных
os.makedirs(os.path.dirname(Config.DB_PATH), exist_ok=True)
global_init(Config.DB_PATH)

# Создание папок
os.makedirs(Config.CSS_DIR, exist_ok=True)
os.makedirs(Config.UPLOADS_DIR, exist_ok=True)

# Регистрация блюпринтов
app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(api_bp)

if __name__ == '__main__':
    app.run(debug=True)

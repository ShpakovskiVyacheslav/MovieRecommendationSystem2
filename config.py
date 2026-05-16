import os


class Config:
    SECRET_KEY = '[k1l8a@\)Z}SQ2aHKCDjxFF–v#34RK'
    EMAIL_ADDRESS = 'sistemarekomendacij@gmail.com'
    APP_PASSWORD = 'gpvuwkwlgvvkspww'

    DB_PATH = os.path.join(os.path.dirname(__file__), 'db', 'database.db')
    STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')
    CSS_DIR = os.path.join(STATIC_DIR, 'css')
    UPLOADS_DIR = os.path.join(STATIC_DIR, 'uploads')

# Для запуска использовать версию питона 3.10 или 3.11
# Рекомендуется использовать виртуальное окружение:
# python -m venv venv
#
# venv\Scripts\activate
#
# pip install numpy==1.26.4
# pip install scikit-surprise
# pip install pandas kagglehub scikit-learn
#
# python rec.py
# ЛИБО запускать в ноутбуке
# предварительно необходимо:
# !pip install surprise
# !pip install "numpy<2"

import numpy as np  # версия numpy должна быть меньше 2.0.0, например, 1.26.4
from sklearn.metrics.pairwise import cosine_similarity
from data.db_session import global_init, create_session
from data.users import User
from data.films import Film
from data.genres import Genre
from data.user_film import UserFilm
from surprise import Dataset, Reader
import pandas as pd
from flask_restful import reqparse, abort, Api, Resource
from flask import request, Flask
import os
import sys

# Получаем путь к папке data
current_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(current_dir, '..', 'data')

sys.path.append(data_dir)

# Теперь импортируем

app = Flask(__name__)
api = Api(app)


df = pd.read_csv("ratings.csv")

reader = Reader(rating_scale=(0.5, 5))
data = Dataset.load_from_df(df[['userId', 'movieId', 'rating']], reader)

trainset = data.build_full_trainset()

# Инициализация базы данных
db_path = os.path.join(os.path.dirname(__file__), 'db', 'database.db')
os.makedirs(os.path.dirname(db_path), exist_ok=True)
global_init(db_path)

movie_vectors = np.load('movie_vectors.npy')

inner_to_raw_movie = {
    inner_id: trainset.to_raw_iid(inner_id)
    for inner_id in trainset.all_items()
}
raw_to_inner_movie = {
    raw_id: inner_id
    for inner_id, raw_id in inner_to_raw_movie.items()
}

def get_recomindations(base_films):
    inner_ids = [raw_to_inner_movie[movie_id] for movie_id in base_films]

    # вектор выбранного фильма
    target_vectors = [movie_vectors[inner_id] for inner_id in inner_ids]

    average_vector = np.mean(target_vectors, axis=0)

    # cosine_similarity вычисляет схожесть фильмов с помощью угла между векторами фильмов
    similarities = cosine_similarity(
        [average_vector],
        movie_vectors
    )[0]

    # сортируем по похожести
    top_indices = np.argsort(similarities)[::-1]

    recommendations = []

    for inner_id in top_indices:
        raw_movie_id = inner_to_raw_movie[inner_id]
        recommendations.append(raw_movie_id)
        #print(f"Внутренний ID: {inner_id}  Исходный movieId: {raw_movie_id}")
    return recommendations

#print(get_recomindations([100, 250, 700, 1000, 5]))

class Recommendations(Resource):
    def get(self):
        db_sess = create_session()
        try:
            # Получаем user_id из аргументов запроса
            user_id = request.args.get('user_id', type=int)
            if not user_id:
                return {"error": "user_id required"}, 400

            favorite_films_query = db_sess.query(Film).join(UserFilm).filter(
                UserFilm.user_id == user_id,
                UserFilm.status == 'like'
            ).order_by(Film.rating.desc().nullslast())

            # Генерируем рекомендации
            recs = get_recomindations(favorite_films_query)

            return recs
        finally:
            db_sess.close()



api.add_resource(Recommendations, "/api/recommendations")

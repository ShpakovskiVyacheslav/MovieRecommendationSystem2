import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from data.db_session import global_init, create_session
from data.users import User
from data.films import Film
from data.genres import Genre
from data.user_film import UserFilm
import pandas as pd
from flask_restful import reqparse, abort, Api, Resource
from flask import request, Flask
import os
import sys
import json

# Получаем путь к папке data
current_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(current_dir, '..', 'data')

sys.path.append(data_dir)


app = Flask(__name__)
api = Api(app)

# Инициализация базы данных
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
db_path = os.path.join(parent_dir, 'db', 'database.db')
os.makedirs(os.path.dirname(db_path), exist_ok=True)
global_init(db_path)

movie_vectors = np.load('movie_vectors.npy')

with open('movie_id_mapping.json', 'r', encoding='utf-8') as f:
    inner_to_raw_movie_str = json.load(f)
    inner_to_raw_movie = {int(k): v for k, v in inner_to_raw_movie_str.items()}

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
    top_n = 1000 # тут чуть криво работает, на выходе не 1000, а примерно 500 (top_n / 2)
    top_indices = np.argsort(similarities)[-top_n:]
    top_indices = top_indices[np.argsort(similarities[top_indices])[::-1]]

    recommendations = [inner_to_raw_movie[i] for i in top_indices]
    return recommendations


class Recommendations(Resource):
    def get(self):
        db_sess = create_session()
        try:
            user_id = request.args.get('user_id', type=int)
            if not user_id:
                return {"error": "user_id required"}, 400

            favorite_films = db_sess.query(Film).join(UserFilm).filter(
                UserFilm.user_id == user_id,
                UserFilm.status == 'like'
            ).order_by(Film.rating.desc().nullslast()).all()

            favorite_ml_ids = []
            for film in favorite_films:
                if film.ml_id and not pd.isna(film.ml_id):
                    favorite_ml_ids.append(int(film.ml_id))

            if not favorite_ml_ids:
                return {
                    "user_id": user_id,
                    "message": "No valid ml_id found",
                    "recommendations": []
                }

            # Генерируем рекомендации
            recs = get_recomindations(favorite_ml_ids)

            return {
                "user_id": user_id,
                "recommendations": recs
            }
        finally:
            db_sess.close()



api.add_resource(Recommendations, "/api/recommendations")

if __name__ == '__main__':
    app.run(debug=True, port=5001, threaded=True, host='127.0.0.1')

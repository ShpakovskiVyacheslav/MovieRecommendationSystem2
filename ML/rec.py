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
from surprise import SVD, Dataset, Reader
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import kagglehub
import os

# загружаем датасет с Kaggle (пришлось сделать из-за размра файла, т. к. на гитхабе есть ограничение на размер файла)
path = kagglehub.dataset_download("grouplens/movielens-20m-dataset")
df = pd.read_csv(os.path.join(path, "rating.csv"))

reader = Reader(rating_scale=(0.5, 5))
data = Dataset.load_from_df(df[['userId', 'movieId', 'rating']], reader)

trainset = data.build_full_trainset()

# выбираем модель
model = SVD()
# обучаем модель
model.fit(trainset)

# model.qi - получившийся матрица фильмов
df_qi = pd.DataFrame(model.qi)
print(df_qi.head())
print(df_qi.shape)

# соотносим movieId с id в матрице фильмов
inner_to_raw_movie = {
    inner_id: trainset.to_raw_iid(inner_id)
    for inner_id in trainset.all_items()
}

# выбираем случайный фильм к которому мы будем рекомендовать
inner_id = np.random.randint(0, len(model.qi))

# вектор выбранного фильма
target_vector = model.qi[inner_id]

movie_vectors = model.qi

# cosine_similarity вычисляет схожесть фильмов с помощью угла между векторами фильмов
similarities = cosine_similarity(
    [target_vector],
    movie_vectors
)[0]

# сортируем по похожести
top_indices = np.argsort(similarities)[::-1]
print(top_indices)

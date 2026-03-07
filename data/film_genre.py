import sqlalchemy as sa
from .db_session import SqlAlchemyBase


class FilmGenre(SqlAlchemyBase):
    __tablename__ = "film_genres"

    film_id = sa.Column(sa.Integer, sa.ForeignKey("films.id"), primary_key=True)
    genre_id = sa.Column(sa.Integer, sa.ForeignKey("genres.id"), primary_key=True)

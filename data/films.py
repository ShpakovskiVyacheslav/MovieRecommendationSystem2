import sqlalchemy as sa
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Film(SqlAlchemyBase):
    __tablename__ = "films"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String, nullable=False)
    poster = sa.Column(sa.String, nullable=True)
    description = sa.Column(sa.String, nullable=True)
    rating = sa.Column(sa.Float, nullable=True)
    release_year = sa.Column(sa.Integer, nullable=True)

    genres = orm.relationship("Genre", secondary="film_genres", backref="films")

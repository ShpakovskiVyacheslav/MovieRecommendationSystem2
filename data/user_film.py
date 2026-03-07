import sqlalchemy as sa
from .db_session import SqlAlchemyBase


class UserFilm(SqlAlchemyBase):
    __tablename__ = "user_films"

    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), primary_key=True)
    film_id = sa.Column(sa.Integer, sa.ForeignKey("films.id"), primary_key=True)
    status = sa.Column(sa.String, nullable=False, default='like')

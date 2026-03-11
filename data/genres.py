import sqlalchemy as sa
from .db_session import SqlAlchemyBase


class Genre(SqlAlchemyBase):
    __tablename__ = "genres"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String, nullable=False, unique=True)

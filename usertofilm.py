import sqlalchemy
from db_session import SqlAlchemyBase


class UserToFilm(SqlAlchemyBase):
    __tablename__ = 'users_to_film'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, unique=False)
    film_id = sqlalchemy.Column(sqlalchemy.Integer,
                                primary_key=True, unique=False)

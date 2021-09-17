import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from data.db_session import SqlAlchemyBase


class Shop(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'shop'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    about = sqlalchemy.Column(sqlalchemy.String, nullable=True)
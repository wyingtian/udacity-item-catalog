# This setup the schema for the movie app database
import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


# The user schema, use email as identifier
class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    email = Column(String(250), nullable=False)


# Define a type of movie
class MovieType(Base):
    __tablename__ = 'movie_type'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)


# Define one movie Item
class MovieItem(Base):
    __tablename__ = 'movie_item'
    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    movie_type_name = Column(String, ForeignKey('movie_type.name'))
    movie_type = relationship(MovieType)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    # movie Item API
    @property
    def serialize(self):
        return{
            'name': self.name,
            'description': self.description,
            'id': self.id,
            'genre': self.movie_type_name,
        }

engine = create_engine('sqlite:///movies.db')
Base.metadata.create_all(engine)

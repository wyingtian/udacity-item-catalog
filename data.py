# This file import data to database using themoviedb.org API
# The ownership of these movie items is a admin User,
# User logged in through google+ can't edit or remove these items
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import MovieType, Base, MovieItem, User
from urllib2 import Request, urlopen
import json
import urllib

engine = create_engine('sqlite:///movies.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Here admin user is harded coded,
# all the data imported by this file is owned by admin
admin = User(email="admin@yingtian.me")

# use api.themoviedb.org to import data
query_args = {'api_key': '81303d4e4ebdfc0aa71f5b7b95000c24'}
encoded_args = urllib.urlencode(query_args)
# send json request to get all movie types
request = "http://api.themoviedb.org/3/genre/movie/list?"
request += encoded_args
response_body = urlopen(request).read()
data = json.loads(response_body)
genres_length = len(data['genres'])

# for each movie type, get movie data
for num in range(0, genres_length):
    genreName = data['genres'][num]['name']
    movieType = MovieType(name=genreName, user=admin, user_id=admin.id)
    session.add(movieType)
    session.commit()
    query_args.update({'with_genres': data['genres'][num]['id']})
    encoded_args = urllib.urlencode(query_args)
    url = "http://api.themoviedb.org/3/discover/movie?"
    url += encoded_args
    res = urlopen(url).read()
    json_movies = json.loads(res)
    # each type import 20 movies
    for item_num in range(0, 20):
        # if get the same movie, do not store in database,
        # all the movie item are unique
        count = session.query(MovieItem).filter_by(
            name=json_movies['results'][item_num]['original_title']).count()
        if count == 0:
            movieItem = MovieItem(
                name=json_movies['results'][item_num]['original_title'],
                description=json_movies['results'][item_num]['overview'],
                movie_type_name=genreName,
                movie_type=movieType,
                user=admin, user_id=admin.id)
            session.add(movieItem)
            session.commit()
        else:
            continue

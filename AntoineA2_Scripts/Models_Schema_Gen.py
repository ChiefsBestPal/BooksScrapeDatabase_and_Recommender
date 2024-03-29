from marshmallow import Schema, fields, post_load
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# SQLAlchemy models
class Movie(Base):
    __tablename__ = 'movie'

    movie_id = Column(Integer, primary_key=True, autoincrement=True)
    tmdb_id = Column(Integer, nullable=False,unique=True)
    imdb_id = Column(String(10), unique=True)
    title = Column(String(255), nullable=False)
    plot = Column(Text, nullable=False)
    content_rating = Column(String(255), nullable=False)
    rating = Column(Float(precision=5, scale=2))
    release_year = Column(Integer, nullable=True)
    AKA = Column(String(255), nullable=False)
    num_reviews = Column(Integer, nullable=False)
    runtime = Column(Integer, nullable=False)
    watchmode_id = Column(Integer, unique=True)

    genres = relationship('Genre', secondary='movie_genre')
    languages = relationship('Lang', secondary='movie_lang')
    keywords = relationship('Keyword', secondary='movie_keyword')
    countries = relationship('Country', secondary='movie_country')
    actors = relationship('Person', secondary='actor')
    directors = relationship('Person', secondary='director')
    creators = relationship('Person', secondary='creator')


class Genre(Base):
    __tablename__ = 'genre'

    genre_id = Column(Integer, primary_key=True, autoincrement=True)
    genre = Column(String(255), unique=True, nullable=False)


class MovieGenre(Base):
    __tablename__ = 'movie_genre'

    movie_genre_id = Column(Integer, primary_key=True, autoincrement=True)
    genre_id = Column(Integer, ForeignKey('genre.genre_id'), nullable=False)
    movie_id = Column(Integer, ForeignKey('movie.movie_id'), nullable=False)


class Lang(Base):
    __tablename__ = 'lang'

    lang_id = Column(Integer, primary_key=True, autoincrement=True)
    lang = Column(String(255), unique=True, nullable=False)


class MovieLang(Base):
    __tablename__ = 'movie_lang'

    movie_lang_id = Column(Integer, primary_key=True, autoincrement=True)
    lang_id = Column(Integer, ForeignKey('lang.lang_id'), nullable=False)
    movie_id = Column(Integer, ForeignKey('movie.movie_id'), nullable=False)


class Keyword(Base):
    __tablename__ = 'keyword'

    keyword_id = Column(Integer, primary_key=True, autoincrement=True)
    keyword = Column(String(255), unique=True, nullable=False)


class MovieKeyword(Base):
    __tablename__ = 'movie_keyword'

    movie_keyword_id = Column(Integer, primary_key=True, autoincrement=True)
    keyword_id = Column(Integer, ForeignKey('keyword.keyword_id'), nullable=False)
    movie_id = Column(Integer, ForeignKey('movie.movie_id'), nullable=False)


class Country(Base):
    __tablename__ = 'country'

    country_id = Column(Integer, primary_key=True, autoincrement=True)
    fullname = Column(String(255), unique=True, nullable=False)
    shortcode = Column(String(3), unique=True, nullable=False)

class MovieCountry(Base):
    __tablename__ = 'movie_country'

    movie_country_id = Column(Integer, primary_key=True, autoincrement=True)
    country_id = Column(Integer, ForeignKey('country.country_id'), nullable=False)
    movie_id = Column(Integer, ForeignKey('movie.movie_id'), nullable=False)


class Person(Base):
    __tablename__ = 'person'

    person_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False)


class Actor(Base):
    __tablename__ = 'actor'

    actor_id = Column(Integer, primary_key=True, autoincrement=True)
    person_id = Column(Integer, ForeignKey('person.person_id'), nullable=False)
    character_name = Column(String(255), nullable=False)


class Director(Base):
    __tablename__ = 'director'

    director_id = Column(Integer, primary_key=True, autoincrement=True)
    person_id = Column(Integer, ForeignKey('person.person_id'), nullable=False)
    movie_id = Column(Integer, ForeignKey('movie.movie_id'), nullable=False)


class Creator(Base):
    __tablename__ = 'creator'

    creator_id = Column(Integer, primary_key=True, autoincrement=True)
    person_id = Column(Integer, ForeignKey('person.person_id'), nullable=False)
    movie_id = Column(Integer, ForeignKey('movie.movie_id'), nullable=False)


# Marshmallow schemas
class MovieSchema(Schema):
    movie_id = fields.Integer()
    tmdb_id = fields.Integer(required=True)
    imdb_id = fields.String(validate=lambda s: len(s) <= 10)
    title = fields.String(required=True)
    plot = fields.String(required=True)
    content_rating = fields.String(required=True)
    rating = fields.Float()
    release_year = fields.Integer()
    AKA = fields.String(required=True)
    num_reviews = fields.Integer(required=True)
    runtime = fields.Integer(required=True)
    watchmode_id = fields.Integer()

    genres = fields.List(fields.Nested('GenreSchema'))
    languages = fields.List(fields.Nested('LangSchema'))
    keywords = fields.List(fields.Nested('KeywordSchema'))
    countries = fields.List(fields.Nested('CountrySchema'))
    actors = fields.List(fields.Nested('PersonSchema'))
    directors = fields.List(fields.Nested('PersonSchema'))
    creators = fields.List(fields.Nested('PersonSchema'))

    @post_load
    def make_movie(self, data, **kwargs):
        return Movie(**data)


class GenreSchema(Schema):
    genre_id = fields.Integer()
    genre = fields.String(required=True)


class LangSchema(Schema):
    lang_id = fields.Integer()
    lang = fields.String(required=True)


class KeywordSchema(Schema):
    keyword_id = fields.Integer()
    keyword = fields.String(required=True)


class CountrySchema(Schema):
    country_id = fields.Integer()
    fullname = fields.String(required=True)
    shortcode = fields.String(validate=lambda s: len(s) <= 3, required=True)

class PersonSchema(Schema):
    person_id = fields.Integer()
    name = fields.String(required=True)

if __name__ == '__main__':
    import MySQLdb
    from dotenv import load_dotenv
    import os
    
    #WDIR = os.path.abspath(os.path.dirname(__file__))
    # Create an SQLAlchemy engine and create the tables
    engine = create_engine('mysql://username:password@localhost/database_name')
    
    Base.metadata.create_all(engine)
    # poolProxiedConnection = engine.raw_connection()

    # cursor = poolProxiedConnection.cursor()
    # cursor.execute('SELECT 1')
    # cursor.close()

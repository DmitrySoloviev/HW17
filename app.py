# app.py

from flask import Flask, request, abort
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False


db = SQLAlchemy(app)
api = Api(app)

# объявление нэймспэйсов для api (flask_restx - Api)
movie_ns = api.namespace('movies')
director_ns = api.namespace('director')
genre_ns = api.namespace('genre')


class Movie(db.Model):
    """
    Класс Movie с таблицей movie (SQLAlchemy - db)
    """
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class Director(db.Model):
    """
    Класс Director с таблицей director (SQLAlchemy - db)
    """
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    """
    Класс Genre с таблицей genre (SQLAlchemy - db)
    """
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class GenreSchema(Schema):
    """
    Модель GenreSchema для перевода данных в JSON
    """
    id = fields.Int(dump_only=True)
    name = fields.Str()


class DirectorSchema(Schema):
    """
    Модель DirectorSchema
    """
    id = fields.Int(dump_only=True)
    name = fields.Str()


class MovieSchema(Schema):
    """
    Модель MovieSchema
    """
    id = fields.Int(dump_only=True)
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre = fields.Nested(GenreSchema)
    director = fields.Nested(DirectorSchema)


@app.errorhandler(404)
def page_not_found(e):
    """
        Представление для ошибки, возвращает строку и номер ошибки
    """
    return "Страница не найдена", 404


@movie_ns.route('/')
class MoviesView(Resource):
    """
    Представление для /movies
    """
    def get(self):
        """
        Обработка запроса GET
        :return: JSON или Ошибку
        """
        director_id = request.args.get('director_id')
        genre_id = request.args.get('genre_id')
        movies_schema = MovieSchema(many=True)
        if director_id:
            movie = Movie.query.filter(Movie.director_id == director_id).all()
            movie = movies_schema.dump(movie)
            if len(movie) > 0:
                return movie, 200
            else:
                return abort(404)
        if genre_id:
            movie = Movie.query.filter(Movie.genre_id == genre_id).all()
            movie = movies_schema.dump(movie)
            if len(movie) > 0:
                return movie, 200
            else:
                return abort(404)
        movie = Movie.query.all()
        movies = movies_schema.dump(movie)
        if len(movies) > 0:
            return movies, 200
        else:
            return abort(404)


@movie_ns.route('/<int:gid>')
class MovieView(Resource):
    """
    Представление для /movies/id
    """
    def get(self, gid: int):
        """
                Обработка запроса GET
                :return: JSON или Ошибку
        """
        movie = Movie.query.get(gid)
        movie_schema = MovieSchema()
        movie = movie_schema.dump(movie)
        if len(movie):
            return movie, 200
        else:
            return abort(404)


if __name__ == '__main__':
    app.run(port=5000, debug=True)

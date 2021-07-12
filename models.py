from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()


# Models for database schema

class User(db.Model):
    """ DB model for users """

    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    favorites = db.relationship(
        'Movie', secondary="favorites", backref="users")

    @classmethod
    def authenticate(cls, username, password):
        """ Method for handling authentication w/ Bcrypt """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False

    @classmethod
    def signup(cls, username, email, password):
        """Sign up user. Hashes password and adds user to database."""

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
        )

        db.session.add(user)
        return user


class Movie(db.Model):
    """ DB model for movies """

    __tablename__ = "movies"

    movie_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    tagline = db.Column(db.Text)
    overview = db.Column(db.Text)
    img_url = db.Column(db.Text)
    genres = db.Column(db.Text)
    rating = db.Column(db.Float, nullable=False)
    release_date = db.Column(db.Text, nullable=False)


class Favorite(db.Model):
    """ DB model for a user's favorites"""

    __tablename__ = "favorites"

    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id'), primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey(
        'movies.movie_id'), primary_key=True)


def connect_db(app):
    """Connects the db to the main app"""

    db.app = app
    db.init_app(app)

import os
from flask import Flask, render_template, request, flash, redirect, session, g, send_file
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from models import db, connect_db, User, Movie, Favorite
from forms import UserAddForm
from secrets import API_KEY, BASE_URL
import requests


# General config
app = Flask(__name__)
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 1
app.config['SECRET_KEY'] = "SECRET!"

debug = DebugToolbarExtension(app)

# Database config
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgres:///cinema-search'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
connect_db(app)


###############################################################################


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if "curr_user" in session:
        g.user = User.query.get(session["curr_user"])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session["curr_user"] = user.id


def do_logout():
    """Logout user."""

    if "curr_user" in session:
        del session["curr_user"]


@app.route('/signup', methods=["GET", "POST"])
def user_signup_form():
    """ Show signup form and add user to database """

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data)

            db.session.commit()

        except IntegrityError:
            flash("Username/Email already taken", 'danger')
            return render_template('signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('signup.html', form=form)


@app.route('/logout')
def log_out_user():
    """Handle logout of user."""

    do_logout()
    flash('Logout Successful', "success")

    return redirect('/signup')


###############################################


@app.route('/', defaults={'page': 1})
@app.route('/<int:page>')
def show_home_page(page):

    if g.user:
        params = {"api_key": API_KEY, 'page': page}
        response = requests.get(f"{BASE_URL}/movie/popular", params)

        if response.status_code != 200:
            flash("Could not get movies, please try again", "danger")
            return redirect('/logout')

        data = response.json()
        popular_movies_list = data['results']
        total_pages = data['total_pages']

        return render_template('popular_movies.html', popular_movies_list=popular_movies_list, page=page, total_pages=total_pages)
    else:
        return redirect('/signup')


@app.route('/top_rated', defaults={'page': 1})
@app.route('/top_rated/<int:page>')
def show_top_rated(page):

    params = {"api_key": API_KEY, 'page': page}
    response = requests.get(f"{BASE_URL}/movie/top_rated", params)

    if response.status_code != 200:
        flash("Could not get movies, please try again", "danger")
        return redirect('/')

    data = response.json()
    top_rated_movies = data['results']
    total_pages = data['total_pages']

    return render_template('top_rated_movies.html', top_rated_movies=top_rated_movies, page=page,total_pages=total_pages)


@app.route('/upcoming', defaults={'page': 1})
@app.route('/upcoming/<int:page>')
def show_upcoming(page):

    params = {"api_key": API_KEY, 'page': page}
    response = requests.get(f"{BASE_URL}/movie/upcoming", params)

    if response.status_code != 200:
        flash("Could not get movies, please try again", "danger")
        return redirect('/')

    data = response.json()
    upcoming_movies = data['results']
    total_pages = data['total_pages']

    return render_template('upcoming.html', upcoming_movies=upcoming_movies, page=page, total_pages=total_pages)


@app.route('/movie/<int:movie_id>')
def show_movie_details(movie_id):
    """ Returns template giving more info on a specific movie """

    params = {'api_key': API_KEY, 'language': 'en-us'}
    response = requests.get(f"{BASE_URL}/movie/{movie_id}", params)
    movie_data = response.json()
    similar_movies_response = requests.get(
        f"{BASE_URL}/movie/{movie_id}/similar", params)

    similar_data = similar_movies_response.json()
    similar_movie_data = similar_data['results']


    genre_list = [genre['name'] for genre in movie_data['genres']]
    curr_user = User.query.get(g.user.id)
    favorites_ids = [favorite.movie_id for favorite in curr_user.favorites]

    if movie_data["poster_path"] == None:
        img_url = None
    else:
        img_url = f"https://image.tmdb.org/t/p/w185{movie_data['poster_path']}"

    movie_exists = Movie.query.filter(Movie.movie_id == movie_id).all()
    if len(movie_exists) == 0:
        movie = Movie(movie_id=movie_data['id'], title=movie_data['title'], tagline=movie_data['tagline'],
                      overview=movie_data[
            'overview'], img_url=img_url,
            genres=genre_list, release_date=movie_data['release_date'],
            rating=movie_data['vote_average'])
        db.session.add(movie)
        db.session.commit()

    return render_template("movie_details.html", movie_data=movie_data, similar_movie_data=similar_movie_data, favorites_ids=favorites_ids)


@app.route('/search', methods=["GET", "POST"])
def get_search_results():

    search = request.args.get('search')
    params = {"api_key": API_KEY, 'query': search}

    response = requests.get(f"{BASE_URL}/search/movie", params)
    data = response.json()
    search_results = data['results']

    for movie in search_results:
        print(movie['poster_path'])

    return render_template('search.html', search_results=search_results)


@app.route('/my_list')
def show_user_list():
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    curr_user = User.query.get(g.user.id)
    favorites_list = curr_user.favorites

    return render_template('my_list.html', favorites_list=favorites_list)


@app.route('/my_list/add/<int:movie_id>', methods=['POST'])
def add_to_mylist(movie_id):

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    new_favorite = Favorite(user_id=g.user.id, movie_id=movie_id)
    db.session.add(new_favorite)
    db.session.commit()
    return redirect(f"/movie/{movie_id}")


@app.route('/my_list/delete/<int:movie_id>', methods=["POST"])
def delete_from_mylist(movie_id):

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user_id = g.user.id
    favorited_movie = Favorite.query.filter_by(
        user_id=user_id, movie_id=movie_id).first()
    db.session.delete(favorited_movie)
    db.session.commit()

    return redirect(f"/my_list")


@app.route('/movie/my_list/delete/<int:movie_id>', methods=["POST"])
def movie_view_delete_from_mylist(movie_id):

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user_id = g.user.id
    favorited_movie = Favorite.query.filter_by(
        user_id=user_id, movie_id=movie_id).first()
    db.session.delete(favorited_movie)
    db.session.commit()

    return redirect(f"/movie/{movie_id}")


@app.route('/export')
def export_to_txt():
    curr_user = User.query.get(g.user.id)
    favorites = curr_user.favorites
    username = g.user.username
    file_name = f"{username}'s_list.txt"
    file_path = "user_lists/" + file_name

    with open(file_path, 'w') as my_list:
        for movie in favorites:
            my_list.write(movie.title + "\n")

    return send_file(file_path, as_attachment=True, cache_timeout=0)

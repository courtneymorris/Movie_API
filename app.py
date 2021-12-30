from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://nhgxfsgmugxqhr:cdc1f714e4372bfac6eb23bfe6648c98f4ae64b0f0a447221fbfd4fde345b60c@ec2-52-70-205-234.compute-1.amazonaws.com:5432/d60pjrha2phnjf"

db = SQLAlchemy(app)
ma = Marshmallow(app)
CORS(app)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False, unique=True)
    genre = db.Column(db.String)
    mpaa_rating = db.Column(db.String)
    poster_image = db.Column(db.String)
    all_reviews = db.relationship("Review", backref="movie", cascade="all, delete, delete-orphan")

    def __init__(self, title, genre, mpaa_rating, poster_image):
        self.title = title
        self.genre = genre
        self.mpaa_rating = mpaa_rating
        self.poster_image = poster_image


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    star_rating = db.Column(db.Float, nullable=False)
    review_text = db.Column(db.Text)
    movie_id = db.Column(db.Integer, db.ForeignKey("movie.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __init__(self, star_rating, review_text, movie_id, user_id):
        self.star_rating = star_rating
        self.review_text = review_text
        self.movie_id = movie_id
        self.user_id = user_id


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    reviews_contributed = db.relationship("Review", backref="user", cascade="all, delete, delete-orphan")

    def __init__(self, username, password, reviews_contributed):
        self.username = username
        self.password = password
        self.reviews_contributed = reviews_contributed


class ReviewSchema(ma.Schema):
    class Meta:
        fields = ("id", "star_rating", "review_text", "movie_id", "user_id")

review_schema = ReviewSchema()
multiple_review_schema = ReviewSchema(many=True)

class MovieSchema(ma.Schema):
    class Meta:
        fields = ('id', 'title', 'genre', 'mpaa_rating', 'poster_image', 'all_reviews')
    all_reviews = ma.Nested(multiple_review_schema)

movie_schema = MovieSchema()
multiple_movie_schema = MovieSchema(many=True)

class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'username', 'password', 'reviews_contributed')
    reviews_contributed = ma.Nested(multiple_review_schema)

user_schema = UserSchema()
multiple_user_schema = UserSchema(many=True)


@app.route('/movie/add', methods=['POST'])
def add_movie():
    if request.content_type != 'application/json':
        return jsonify('Error: Data must be sent as JSON')

    post_data = request.get_json()
    title = post_data.get('title')
    genre = post_data.get('genre')
    mpaa_rating = post_data.get('mpaa_rating')
    poster_image = post_data.get('poster_image')

    if title == None:
        return jsonify("Error: data must have a 'title' key")
    if mpaa_rating == None:
        return jsonify("Error: data must have a 'mpaa_rating' key")

    new_record = Movie(title, genre, mpaa_rating, poster_image)
    db.session.add(new_record)
    db.session.commit()

    return jsonify(movie_schema.dump(new_record))


@app.route('/movie/get', methods=["GET"])
def get_movies():
    all_movies = db.session.query(Movie).all()
    return jsonify(multiple_movie_schema.dump(all_movies))


@app.route('/movie/get/id/<id>', methods=["GET"])
def get_movie_by_id(id):
    one_movie = db.session.query(Movie).filter(Movie.id == id).first()
    return jsonify(movie_schema.dump(one_movie))


@app.route('/movie/get/title/<title>', methods=["GET"])
def get_movie_by_title(title):
    one_movie = db.session.query(Movie).filter(Movie.title == title).first()
    return jsonify(movie_schema.dump(one_movie))


@app.route("/movie/update/id/<id>", methods=["PUT"])
def update_movie(id):
    if request.content_type != "application/json":
        return jsonify("Error: Data must be sent as json")

    data = request.get_json()
    title = data.get("title")
    genre = data.get("genre")
    mpaa_rating = data.get("mpaa_rating")
    poster_image = data.get("poster_image")
    all_reviews = data.get("all_reviews")

    movie_to_update = db.session.query(Movie).filter(Movie.id == id).first()

    if title != None:
        movie_to_update.title = title
    if genre != None:
        movie_to_update.genre = genre
    if mpaa_rating != None:
        movie_to_update.mpaa_rating = mpaa_rating
    if poster_image != None:
        movie_to_update.poster_image = poster_image
    if all_reviews != None:
        movie_to_update.all_reviews = all_reviews

    db.session.commit()

    return jsonify(movie_schema.dump(movie_to_update))


@app.route("/movie/delete/id/<id>", methods=["DELETE"])
def delete_movie(id):
    movie_to_delete = db.session.query(Movie).filter(Movie.id == id).first()
    db.session.delete(movie_to_delete)
    db.session.commit()
    return jsonify("Movie successfully deleted")













if __name__ == "__main__":
    app.run(debug=True)



# pipenv install flask flask-sqlalchemy flask-marshmallow marshmallow-sqlalchemy flask cors gunicorn psycopg2
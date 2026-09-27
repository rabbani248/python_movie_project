from flask import Flask, render_template, redirect, url_for, request, session
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
from ratemovie_form import  RateMovieForm
from add_form import AddForm
from dotenv import load_dotenv
import requests, os


load_dotenv("./secrets.env")
'''
Red underlines? Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)

headers={
    "Authorization":f"{os.getenv("TOKEN")}"
}

# CREATE DB
class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] ="sqlite:///movies.db"
# Create the extension
db= SQLAlchemy(model_class=Base)
# initialise the app with the extension
db.init_app(app)

# CREATE TABLE

class Movie(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=True)
    rating: Mapped[Float] = mapped_column(Float, nullable=False)
    popularity: Mapped[Float] = mapped_column(Float, nullable=False)
    ranking: Mapped[int] = mapped_column(Integer, nullable=False)
    review: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)

    def __repr__(self):
        return f"<Movie {Movie.title}"

# with app.app_context():
#     db.create_all()

# with app.app_context():
#     db.session.execute(
#         db.text("ALTER TABLE movie ADD COLUMN popularity FLOAT")
#     )
#     db.session.commit()
@app.route("/")
def home():
    result= db.session.execute(db.select(Movie).order_by(Movie.rating.desc()))
    all_movies=result.scalars().all()
    for rank, movie in enumerate(all_movies, start=1):
        movie.ranking = rank
    db.session.commit()
    return render_template("index.html", movies=all_movies)

#Create table schema in the database, requires application context
#
# with app.app_context():
#     db.create_all()
#     new_movie = Movie(
#     title="Avatar The Way of Water",
#     year=2022,
#     description="Set more than a decade after the events of the first film, learn the story of the Sully family (Jake, Neytiri, and their kids), the trouble that follows them, the lengths they go to keep each other safe, the battles they fight to stay alive, and the tragedies they endure.",
#     rating=7.3,
#     ranking=9,
#     review="I liked the water.",
#     img_url="https://image.tmdb.org/t/p/w500/t6HIqrRAclMCA60NsSmeqe9RmNV.jpg"
# )
#     db.session.add(new_movie)
#     db.session.commit()
#
#
# @app.route("/edit/<int:id>", methods=["POST","GET"])
# def edit(id):
#     form= RateMovieForm()
#     if form.validate_on_submit():
#         new_rating=form.rating.data
#         new_review=form.review.data
#         movie_update= db.session.execute(db.select(Movie).where(Movie.id==id)).scalar()
#         movie_update.rating=new_rating
#         movie_update.review=new_review
#         db.session.commit()
#         return redirect(url_for('home'))
#     return render_template('edit.html', form=form, id=id)

@app.route("/edit", methods=["POST","GET"])
def edit():
    form= RateMovieForm()
    movie_id=request.args.get("id")
    movie_to_update= db.get_or_404(Movie,movie_id)
    if form.validate_on_submit():
        new_rating=form.rating.data
        new_review=form.review.data
        movie_to_update.rating=new_rating
        movie_to_update.review=new_review
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('edit.html', form=form, movie=movie_to_update)

@app.route("/delete", methods=["GET"])
def delete():
    movie_id=request.args.get("id")
    movie_to_delete=db.get_or_404(Movie,movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for("home"))

@app.route("/select")
def select():
    movie_name= request.args.get("title")
    body={
        "query":movie_name
    }
    response=requests.get(os.getenv("SEARCH_MOVIES_URL"), params=body, headers=headers)
    results=response.json()["results"]
    print(results)

    movie_results=[{"title":movie_output.get("original_title","unknown")   ,"year":movie_output.get("release_date","unknown"),
                    "description":movie_output.get("overview","unknown"),
                    "rating":movie_output.get("vote_average",0.0),
                    "popularity":movie_output.get("popularity",0.0),
                    "image_url":movie_output.get("poster_path","unknown")} for movie_output in results]
    # print(movie_results)
    return render_template("select.html", movies=movie_results)

@app.route("/add", methods=["POST","GET"])
def add():
    form=AddForm()
    if form.validate_on_submit():
        title_entered= form.movie_title.data
        return redirect(url_for('select',title=title_entered))
    return render_template("add.html", form=form)


@app.route("/persist", methods=["GET","POST"])
def persist():
    if request.method=="POST":
        title = request.form.get("title")
        year = request.form.get("year")
        description = request.form.get("description")
        rating = request.form.get("rating")
        popularity = request.form.get("popularity")
        image_url = request.form.get("image_url")


        new_movie = Movie(
            title=title,
            year=year,
            description=description,
            rating=rating,
            popularity=popularity,
            ranking="None",
            review="",
            img_url=f"https://image.tmdb.org/t/p/w500{image_url}"
        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for("home"))
    return redirect(url_for('select'))


if __name__ == '__main__':
    app.run(debug=True)

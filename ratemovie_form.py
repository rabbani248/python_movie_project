from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.fields import FloatField
from wtforms.fields.simple import SubmitField
from wtforms.validators import InputRequired


class RateMovieForm(FlaskForm):
    rating = FloatField(label='rating', validators=[InputRequired()])
    review =StringField(label='review', validators=[InputRequired()])
    submit=SubmitField(label='update')

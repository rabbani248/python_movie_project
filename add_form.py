from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.fields import FloatField
from wtforms.fields.simple import SubmitField
from wtforms.validators import InputRequired

class AddForm(FlaskForm):
    movie_title = StringField(label='title', validators=[InputRequired()])
    submit = SubmitField(label='add')
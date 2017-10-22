from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FieldList, FormField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    submit = SubmitField('Login')


class ScrapeForm(FlaskForm):
    search_terms = StringField('Term: ', [DataRequired(message='Please enter a search term.')])
    search_locations = StringField('Location: ', [DataRequired(message='Please enter a search location.')])
    search = SubmitField('Search')
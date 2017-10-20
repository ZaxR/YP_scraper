from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    submit = SubmitField('Login')


class ScrapeForm(FlaskForm):
    search_term = StringField('Term: ', [DataRequired()])
    search_location = StringField('Location: ')
    search = SubmitField('Search')
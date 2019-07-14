from flask_wtf import FlaskForm
from wtforms import BooleanField, FieldList, PasswordField, StringField, SubmitField
from wtforms.validators import Email, EqualTo, InputRequired, Optional, ValidationError

from app.models import User


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired()])
    password2 = PasswordField('Repeat Password', validators=[InputRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired()])
    password = PasswordField('password', validators=[InputRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')


# Implemented manual validation instead, until validation for FieldList solution is found
class ScrapeForm(FlaskForm):
    search_terms = FieldList(StringField('Term: ', [Optional(strip_whitespace=True)]), min_entries=1, max_entries=10)
    search_locations = FieldList(StringField('Location: ', [InputRequired(
        message='Please enter a search location.')]), min_entries=1, max_entries=10)

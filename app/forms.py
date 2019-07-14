from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import Email, EqualTo, InputRequired, Length, ValidationError

from app.models import User


class CommaSeparatedEmails(Email):
    # TODO clean this class up
    def __call__(self, form, field):
        emails = [e.strip() for e in field.data.strip().split(",")]
        bad_email_msgs = []
        for email in emails:
            field.data = email
            try:
                Email.__call__(self, form, field)
            except ValidationError as e:
                bad_email_msgs.append(" ".join(e.args) + ": " + email)
        if bad_email_msgs:
            raise ValidationError("\n".join(bad_email_msgs))


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


class ScrapeForm(FlaskForm):
    search_term = StringField('Term: ', validators=[InputRequired(message='Please enter a search term.'),
                                                    Length(min=2, message='Terms must be at least two characters.')])
    search_location = StringField('Location: ',
                                  validators=[InputRequired(message='Please enter a search location.'),
                                              Length(min=2, message='Locations must be at least two characters.')])
    recipient_emails = StringField('Recipient Emails: ', validators=[InputRequired(), CommaSeparatedEmails()])
    submit = SubmitField('Scrape & E-mail')

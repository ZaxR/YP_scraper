from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login


class Records(db.Model):
    __tablename__ = "records"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task_id = db.Column(db.Integer, index=True, unique=False)
    business_name = db.Column(db.String(30), index=True, unique=False)
    primary_phone = db.Column(db.String(17), index=True, unique=False)
    street_address = db.Column(db.String(30), index=True, unique=False)
    locality = db.Column(db.String(30), index=True, unique=False)
    region = db.Column(db.String(2), index=True, unique=False)
    postal_code = db.Column(db.Integer, index=True, unique=False)
    website = db.Column(db.String(), index=True, unique=False)


class SearchHistory(db.Model):
    __tablename__ = "search_history"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    term = db.Column(db.String(17), index=True, unique=False)
    location = db.Column(db.String(30), index=True, unique=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column('username', db.String(50), unique=True, index=True)
    password_hash = db.Column('password', db.String(128))
    email = db.Column('email', db.String(50), unique=True, index=True)
    history = db.relationship('SearchHistory', backref='searcher', lazy='dynamic')
    # registered_on = db.Column('registered_on', db.DateTime)
    # is_admin = db.Column(db.Boolean, default=False)

    @property
    def password(self):
        """ Prevent password from being accessed"""
        raise AttributeError('Password is not a readable attribute.')

    @password.setter
    def password(self, password):
        """Set password to a hashed password"""
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """Check if hashed password matches actual password."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return self.username


@login.user_loader
def load_user(id):
    return User.query.get(int(id))

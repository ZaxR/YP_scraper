from flask import Flask, flash, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

from app import views, models

# Start fresh records table and create all missing tables
models.Records.__table__.drop(db.session.bind, checkfirst=True)
db.create_all()
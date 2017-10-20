from flask import Flask, flash, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

from app import views, models

# for k in db.get_binds():
#     print(k)

models.Records.__table__.drop(db.session.bind, checkfirst=True)
db.create_all()
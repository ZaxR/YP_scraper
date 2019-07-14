"""Test."""
from celery import Celery
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate, MigrateCommand
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect


def make_celery(app):
    celery = Celery(app.import_name)
    celery.config_from_object('celery_config')

    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


app = Flask(__name__)
app.config.from_object('config')

# Instantiate Flask extensions
login = LoginManager(app)
csrf_protect = CSRFProtect(app)
db = SQLAlchemy(app)
mail = Mail(app)
migrate = Migrate(app, db)
bootstrap = Bootstrap(app)
celery = make_celery(app)

from app import views, models

# Start fresh records table and create all missing tables
# models.Records.__table__.drop(db.session.bind, checkfirst=True)
db.create_all()  # https://docs.sqlalchemy.org/en/13/core/metadata.html#sqlalchemy.schema.MetaData.create_all

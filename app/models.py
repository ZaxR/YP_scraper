from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class Records(db.Model):
    __tablename__ = "records"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30), index=True, unique=False)
    phone = db.Column(db.String(17), index=True, unique=False)
    address = db.Column(db.String(30), index=True, unique=False)
    city = db.Column(db.String(30), index=True, unique=False)
    state = db.Column(db.String(2), index=True, unique=False)
    zip_code = db.Column(db.Integer, index=True, unique=False)
    website = db.Column(db.String(), index=True, unique=False)

    def __init__(self, name, phone, address, city, state, zip_code, website):
        # self.id = id
        self.name = name
        self.phone = phone
        self.address = address
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.website = website


class Users(db.Model):
    __tablename__ = "users"
    id = db.Column('user_id', db.Integer, primary_key=True)
    username = db.Column('username', db.String(50), unique=True, index=True)
    password_hash = db.Column('password', db.String(128))
    email = db.Column('email', db.String(50), unique=True, index=True)
    # registered_on = db.Column('registered_on', db.DateTime)
    # is_admin = db.Column(db.Boolean, default=False)

    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email
        # self.registered_on = datetime.utcnow()

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

    @property
    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return True

    @property
    def is_active(self):
        """Always True, as all users are active."""
        return True

    @property
    def is_anonymous(self):
        """Always False, as anonymous users aren't supported."""
        return False

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return '<User: {}>'.format(self.username)

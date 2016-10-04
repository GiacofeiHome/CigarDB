# project/server/models.py


import datetime

from project.server import app, db, bcrypt


class User(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, email, password, admin=False):
        self.email = email
        self.password = bcrypt.generate_password_hash(
            password, app.config.get('BCRYPT_LOG_ROUNDS')
        )
        self.registered_on = datetime.datetime.now()
        self.admin = admin

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def __repr__(self):
        return '<User {0}>'.format(self.email)


class Brand(db.Model):

    __tablename__ = "brands"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64))

    products = db.relationship('Product', backref='brands', lazy='dynamic')

    def __repr__(self):
        return '{}'.format(self.name)


class Product(db.Model):

    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64))
    brand = db.Column(db.Integer, db.ForeignKey('brands.id'))

    inventory = db.relationship('Inventory', backref='products', lazy='dynamic')

    def __repr__(self):
        return '{}'.format(self.name)


class Size(db.Model):

    __tablename__ = "sizes"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64))

    inventory = db.relationship('Inventory', backref='sizes', lazy='dynamic')

    def __repr__(self):
        return '{}'.format(self.name)

class Location(db.Model):

    __tablename__ = "locations"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64))

    inventory = db.relationship('Inventory', backref='locations', lazy='dynamic')

    def __repr__(self):
        return '{}'.format(self.name)


class Inventory(db.Model):

    __tablename__ = "cigars"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    hash = db.Column(db.String(64))
    product = db.Column(db.Integer, db.ForeignKey('products.id'))
    size = db.Column(db.Integer, db.ForeignKey('sizes.id'))
    location = db.Column(db.Integer, db.ForeignKey('locations.id'))

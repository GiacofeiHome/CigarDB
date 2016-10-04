# project/server/models.py

from flask_security import UserMixin, RoleMixin
import datetime

from project.server import app, db, bcrypt


roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return self.name


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    def __str__(self):
        return self.email


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

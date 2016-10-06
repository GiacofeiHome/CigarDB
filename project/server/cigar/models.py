# project/server/models.py


import datetime
from flask_login import current_user

from project.server import app, db, bcrypt
from project.server.models import User


class Brand(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64))

    products = db.relationship('Product', backref='brand', lazy='dynamic')

    def __repr__(self):
        return '{}'.format(self.name)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64))
    brand_id = db.Column(db.Integer, db.ForeignKey('brand.id'))

    cigars = db.relationship('Cigar', backref='product', lazy='dynamic')

    def __repr__(self):
        return '{}'.format(self.name)


class Size(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64))
    width_64 = db.Column(db.Numeric(12, 2))
    width_mm = db.Column(db.Numeric(12, 2))
    length_cm = db.Column(db.Numeric(12, 2))
    length_in = db.Column(db.Numeric(12, 2))

    cigars = db.relationship('Cigar', backref='size', lazy='dynamic')

    def __repr__(self):
        return '{}'.format(self.name)

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64))
    owner = db.Column(db.Integer, db.ForeignKey('users.id'), default=current_user)

    cigars = db.relationship('Cigar', backref='location', lazy='dynamic')

    def __repr__(self):
        return '{} {}'.format(self.owner, self.name)


session_inventory = db.Table(
    'session_inventory',
    db.Column('session_id', db.Integer(), db.ForeignKey('session.id')),
    db.Column('cigar_id', db.String(64), db.ForeignKey('cigar.id'))
)

class Cigar(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    owner = db.Column(db.Integer, db.ForeignKey('users.id'), default=current_user)
    hash = db.Column(db.String(64), unique=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    size_id = db.Column(db.Integer, db.ForeignKey('size.id'))
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    purchase_date = db.Column(db.Date, nullable=True)
    purchase_price = db.Column(db.Numeric(12, 2), nullable=True)
    ratings = db.relationship('Rating', backref='cigar', lazy='dynamic')
    smoked = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '{} {} ({}) - {}'.format(
            self.owner,
            self.product.name,
            self.size.name,
            self.location.name
        )


class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    owner = db.Column(db.Integer, db.ForeignKey('users.id'), default=current_user)
    cigar_id = db.Column(db.String(64), db.ForeignKey('cigar.id'))
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'))
    app_notes = db.Column(db.String(200), nullable=True)
    app_score = db.Column(db.Integer)
    smoke_notes = db.Column(db.String(200), nullable=True)
    smoke_score = db.Column(db.Integer)
    taste_notes = db.Column(db.String(200), nullable=True)
    taste_score = db.Column(db.Integer)
    overall_notes = db.Column(db.String(200), nullable=True)
    overall_score = db.Column(db.Integer)
    
    @property
    def total(self):
        return self.app_score + self.smoke_score + self.taste_score + self.overall_score

    def __repr__(self):
        score = self.app_score + self.smoke_score + self.taste_score + self.overall_score
        return '{} {} ({})'.format(self.owner, self.session.date, score)


class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    owner = db.Column(db.Integer, db.ForeignKey('users.id'), default=current_user)
    date = db.Column(db.Date)
    cigars = db.relationship('Cigar', secondary=session_inventory,
                            backref=db.backref('session', lazy='dynamic'))
    ratings = db.relationship('Rating', backref='session', lazy='dynamic')

    def __repr__(self):
        return '{} {} Smoked: {}'.format(
            self.owner,
            self.date,
            ['{} {}'.format(x.product.brand.name, x.product.name) for x in self.cigars]
        )


class Transfer(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cigar_id = db.Column(db.String(64), db.ForeignKey('cigar.id'))
    from_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    to_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    date = db.Column(db.DateTime)


class ContainerType(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64))
    containers = db.relationship('Container', backref='container_type', lazy='dynamic')

    def __repr__(self):
        return self.name


container_inventory = db.Table(
    'container_inventory',
    db.Column('container_id', db.Integer(), db.ForeignKey('container.id')),
    db.Column('hash', db.String(64), db.ForeignKey('cigar.hash'))
)

class Container(db.Model):
    def __init__(self, parent=None):
        self.parent = parent

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    owner = db.Column(db.Integer, db.ForeignKey('users.id'), default=current_user)
    name = db.Column(db.String(64))
    type_id = db.Column(db.Integer, db.ForeignKey('container_type.id'))
    parent_id = db.Column(db.Integer, db.ForeignKey('container.id'))

    children = db.relationship(
        'Container',

        # cascade deletions
        cascade="all",

        # many to one + adjacency list - remote_side
        # is required to reference the 'remote'
        # column in the join condition.
        backref=db.backref("parent", remote_side='Container.id')
    )

    cigars = db.relationship('Cigar', secondary=container_inventory,
                            backref=db.backref('container', lazy='dynamic'))

    #~ def append(self, nodename):
        #~ self.children[nodename] = Container(nodename, parent=self)

    def __repr__(self):
        return "Container(name=%r, id=%r, parent_id=%r)" % (
                    self.name,
                    self.id,
                    self.parent_id
                )

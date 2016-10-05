# project/server/models.py


import datetime
from flask_login import current_user

from project.server import app, db, bcrypt


class User(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)

    locations = db.relationship('Location', backref='user', lazy='dynamic')
    cigars = db.relationship('Cigar', backref='user', lazy='dynamic')
    containers = db.relationship('Container', backref='user', lazy='dynamic')
    ratings = db.relationship('Rating', backref='user', lazy='dynamic')
    sessions = db.relationship('Session', backref='user', lazy='dynamic')

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
        return '<{0}>'.format(self.email)


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

    cigar = db.relationship('Cigar', backref='product', lazy='dynamic')

    def __repr__(self):
        return '{}'.format(self.name)


class Size(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64))
    width_64 = db.Column(db.Numeric(12, 2))
    width_mm = db.Column(db.Numeric(12, 2))
    length_cm = db.Column(db.Numeric(12, 2))
    length_in = db.Column(db.Numeric(12, 2))

    cigar = db.relationship('Cigar', backref='size', lazy='dynamic')

    def __repr__(self):
        return '{}'.format(self.name)

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64))
    owner = db.Column(db.String(64), db.ForeignKey('users.id'), default=current_user)

    cigar = db.relationship('Cigar', backref='location', lazy='dynamic')

    def __repr__(self):
        return '{} {}'.format(self.owner, self.name)


session_inventory = db.Table(
    'session_inventory',
    db.Column('session_id', db.Integer(), db.ForeignKey('session.id')),
    db.Column('cigar_id', db.String(64), db.ForeignKey('cigar.id'))
)

class Cigar(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    owner = db.Column(db.String(64), db.ForeignKey('users.id'), default=current_user)
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
    owner = db.Column(db.String(64), db.ForeignKey('users.id'), default=current_user)
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

    def __repr__(self):
        score = self.app_score + self.smoke_score + self.taste_score + self.overall_score
        return '{} {} ({})'.format(self.owner, self.session.date, score)


class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    owner = db.Column(db.String(64), db.ForeignKey('users.id'), default=current_user)
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
    owner = db.Column(db.String(64), db.ForeignKey('users.id'), default=current_user)
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

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
                            backref=db.backref('user', lazy='dynamic'))

    def __str__(self):
        return self.email


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

    cigar = db.relationship('Cigar', backref='location', lazy='dynamic')

    def __repr__(self):
        return '{}'.format(self.name)


session_inventory = db.Table(
    'session_inventory',
    db.Column('session_id', db.Integer(), db.ForeignKey('session.id')),
    db.Column('cigar_id', db.String(64), db.ForeignKey('cigar.id'))
)

class Cigar(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    hash = db.Column(db.String(64), unique=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    size_id = db.Column(db.Integer, db.ForeignKey('size.id'))
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    purchase_date = db.Column(db.Date, nullable=True)
    purchase_price = db.Column(db.Numeric(12, 2), nullable=True)
    ratings = db.relationship('Rating', backref='cigar', lazy='dynamic')

    def __repr__(self):
        return '{} ({}) - {}'.format(
            self.product.name,
            self.size.name,
            self.location.name
        )


class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
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
        return '{} ({})'.format(self.session.date, score)


class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.Date)
    cigars = db.relationship('Cigar', secondary=session_inventory,
                            backref=db.backref('session', lazy='dynamic'))
    ratings = db.relationship('Rating', backref='session', lazy='dynamic')

    def __repr__(self):
        return '{} Smoked: {}'.format(
            self.date, ['{} {}'.format(x.product.brand.name, x.product.name) for x in self.cigars]
        )


class Transfer(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cigar_id = db.Column(db.String(64), db.ForeignKey('cigar.id'))
    from_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    to_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    date = db.Column(db.DateTime)


#~ class ContainerType(db.Model):
    #~ id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    #~ name = db.Column(db.String(64))


#~ container_inventory = db.Table(
    #~ 'container_inventory',
    #~ db.Column('container_id', db.Integer(), db.ForeignKey('container.id')),
    #~ db.Column('hash', db.String(64), db.ForeignKey('cigar.hash'))
#~ )
#~ class Container(db.Model):
    #~ id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    #~ name = db.Column(db.String(64))
    #~ type_id = db.Column(db.Integer, db.ForeignKey('container_type.id'))
    #~ parent = db.Column(db.Integer, db.ForeignKey('container.id'))
    #~ cigars = db.relationship('Cigar', secondary=container_inventory,
                            #~ backref=db.backref('container', lazy='dynamic'))

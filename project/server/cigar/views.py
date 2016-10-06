# project/server/user/views.py


#################
#### imports ####
#################

from flask import render_template, Blueprint, url_for, \
    redirect, flash, request
from flask_login import login_required

from project.server import bcrypt, db
from project.server.cigar.models import Cigar, Brand, Product, Location

################
#### config ####
################

cigar_blueprint = Blueprint('cigar', __name__,)


################
#### routes ####
################
@cigar_blueprint.route('/cigar/<string:cigar_hash>')
@login_required
def show_cigar(cigar_hash):
    cigar = Cigar.query.filter_by(hash=cigar_hash).first()

    return render_template('cigar/stick.html', cigar=cigar)

@cigar_blueprint.route('/location/<int:id>')
@login_required
def show_location(id):
    location = Location.query.filter_by(id=id).first()

    return '{}<br>{}'.format(location, list(location.cigars))
    
@cigar_blueprint.route('/brand/<int:id>')
def show_brand(id):
    brand = Brand.query.filter_by(id=id).first()
    products = [x for x in brand.products]
    cigars = {}
    for product in products:
        cigars[product] = list(product.cigars)

    return '{}<br>{}'.format(brand.name, cigars)

@cigar_blueprint.route('/product/<int:id>')
def show_product(id):
    product = Product.query.filter_by(id=id).first()

    return '{}<br>{}'.format(product.name, list(product.cigars))

# project/server/main/views.py


#################
#### imports ####
#################

from flask import render_template, Blueprint

from project.server.models import Cigar, Brand, Product

################
#### config ####
################

main_blueprint = Blueprint('main', __name__,)


################
#### routes ####
################


@main_blueprint.route('/')
def home():
    return render_template('main/home.html')


@main_blueprint.route("/about/")
def about():
    return render_template("main/about.html")


@main_blueprint.route('/cigar/<string:cigar_hash>')
def show_cigar(cigar_hash):
    cigar = Cigar.query.filter_by(hash=cigar_hash).first()

    return '{}'.format(cigar)

@main_blueprint.route('/brand/<int:id>')
def show_brand(id):
    brand = Brand.query.filter_by(id=id).first()

    return '{}'.format(brand.name)

@main_blueprint.route('/product/<int:id>')
def show_product(id):
    product = Product.query.filter_by(id=id).first()

    return '{}'.format(product.name)

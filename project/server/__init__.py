# project/server/__init__.py




#################
#### imports ####
#################

import os

from flask import Flask, render_template
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_debugtoolbar import DebugToolbarExtension
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy

################
#### config ####
################

app = Flask(
    __name__,
    template_folder='../client/templates',
    static_folder='../client/static'
)


app_settings = os.getenv('APP_SETTINGS', 'project.server.config.DevelopmentConfig')
app.config.from_object(app_settings)


####################
#### extensions ####
####################

login_manager = LoginManager()
login_manager.init_app(app)
bcrypt = Bcrypt(app)
toolbar = DebugToolbarExtension(app)
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)

###################
### blueprints ####
###################

from project.server.user.views import user_blueprint
from project.server.main.views import main_blueprint
app.register_blueprint(user_blueprint)
app.register_blueprint(main_blueprint)

###################
### flask-login ####
###################

from project.server.models import User

login_manager.login_view = "user.login"
login_manager.login_message_category = 'danger'


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter(User.id == int(user_id)).first()


###################
### admin stuff ####
###################
from project.server.models import Brand
from project.server.models import Product
from project.server.models import Size
from project.server.models import Inventory
from project.server.models import Location

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView


admin = Admin(app, template_mode='bootstrap3')
admin.add_view(ModelView(User, db.session, endpoint='user-admin'))
admin.add_view(ModelView(Brand, db.session, endpoint='brand-admin'))
admin.add_view(ModelView(Product, db.session, endpoint='product-admin'))
admin.add_view(ModelView(Size, db.session, endpoint='size-admin'))
admin.add_view(ModelView(Inventory, db.session, endpoint='inventory-admin'))
admin.add_view(ModelView(Location, db.session, endpoint='location-admin'))

########################
#### error handlers ####
########################

@app.errorhandler(401)
def forbidden_page(error):
    return render_template("errors/401.html"), 401


@app.errorhandler(403)
def forbidden_page(error):
    return render_template("errors/403.html"), 403


@app.errorhandler(404)
def page_not_found(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error_page(error):
    return render_template("errors/500.html"), 500

# project/server/__init__.py


#------------------------------------------------------------------------------
# imports
#------------------------------------------------------------------------------

import os

from flask import Flask, render_template, redirect, url_for, request
from flask_login import LoginManager, current_user
from flask_bcrypt import Bcrypt
from flask_debugtoolbar import DebugToolbarExtension
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy


#------------------------------------------------------------------------------
# config
#------------------------------------------------------------------------------

app = Flask(
    __name__,
    template_folder='../client/templates',
    static_folder='../client/static'
)


app_settings = os.getenv('APP_SETTINGS', 'project.server.config.DevelopmentConfig')
app.config.from_object(app_settings)


#------------------------------------------------------------------------------
# extensions
#------------------------------------------------------------------------------

login_manager = LoginManager()
login_manager.init_app(app)
bcrypt = Bcrypt(app)
toolbar = DebugToolbarExtension(app)
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)


#------------------------------------------------------------------------------
# blueprints
#------------------------------------------------------------------------------

from project.server.user.views import user_blueprint
from project.server.main.views import main_blueprint
app.register_blueprint(user_blueprint)
app.register_blueprint(main_blueprint)


#------------------------------------------------------------------------------
# flask-login
#------------------------------------------------------------------------------

from project.server.models import User

login_manager.login_view = "user.login"
login_manager.login_message_category = 'danger'


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter(User.id == int(user_id)).first()

#------------------------------------------------------------------------------
# flask-admin
#------------------------------------------------------------------------------
from flask_admin import Admin
from flask_admin import helpers as admin_helpers
from flask_admin.form import rules
from flask_admin.contrib.sqla import ModelView

from project.server.models import Brand
from project.server.models import Product
from project.server.models import Size
from project.server.models import Cigar
from project.server.models import Location
from project.server.models import Rating
from project.server.models import Session
from project.server.models import Transfer
from project.server.models import Container
from project.server.models import ContainerType

# Create customized model view class
class CustomModelView(ModelView):

    def is_accessible(self):
        if current_user.admin and current_user.is_authenticated():
            return True
        
        return False

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('user.login', next=request.url))


admin = Admin(app)

admin.add_view(CustomModelView(User, db.session, endpoint='users'))
admin.add_view(CustomModelView(Brand, db.session))
admin.add_view(CustomModelView(Product, db.session))
admin.add_view(CustomModelView(Size, db.session))
admin.add_view(CustomModelView(Cigar, db.session))
admin.add_view(CustomModelView(Location, db.session))
admin.add_view(CustomModelView(Rating, db.session))
admin.add_view(CustomModelView(Session, db.session))
admin.add_view(CustomModelView(Transfer, db.session))
admin.add_view(CustomModelView(Container, db.session))
admin.add_view(CustomModelView(ContainerType, db.session))

#------------------------------------------------------------------------------
# error handlers
#------------------------------------------------------------------------------

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

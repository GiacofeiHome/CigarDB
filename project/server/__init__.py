# project/server/__init__.py




#################
#### imports ####
#################

import os

from flask import Flask, render_template, url_for
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_debugtoolbar import DebugToolbarExtension
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required, current_user

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

from project.server.models import User, Role

#~ login_manager.login_view = "user.login"
#~ login_manager.login_message_category = 'danger'


#~ @login_manager.user_loader
#~ def load_user(user_id):
    #~ return User.query.filter(User.id == int(user_id)).first()


###################
### admin stuff ####
###################
from project.server.models import Brand
from project.server.models import Product
from project.server.models import Size
from project.server.models import Cigar
from project.server.models import Location

from flask_admin import Admin
from flask_admin import helpers as admin_helpers
from flask_admin.contrib.sqla import ModelView

from flask_security import current_user

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

# Create customized model view class
class MyModelView(ModelView):

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.has_role('superuser'):
            return True

        return False

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))


admin = Admin(app, template_mode='bootstrap3')
#~ admin = Admin(
    #~ app,
    #~ 'Example: Auth',
    #~ base_template='my_master.html',
    #~ template_mode='bootstrap3',
#~ )

admin.add_view(MyModelView(User, db.session, endpoint='user-admin'))
admin.add_view(MyModelView(Brand, db.session, endpoint='brand-admin'))
admin.add_view(MyModelView(Product, db.session, endpoint='product-admin'))
admin.add_view(MyModelView(Size, db.session, endpoint='size-admin'))
admin.add_view(MyModelView(Cigar, db.session, endpoint='inventory-admin'))
admin.add_view(MyModelView(Location, db.session, endpoint='location-admin'))

# define a context processor for merging flask-admin's template context into the
# flask-security views.
@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=admin_helpers,
        get_url=url_for
    )


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

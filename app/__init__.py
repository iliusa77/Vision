#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template
from flask_mail import Mail
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required
from flask.ext.admin import Admin
from flask.ext import admin, login
from flask.ext.babel import Babel
from flask.ext.blogging import SQLAStorage, BloggingEngine
from sqlalchemy import create_engine, MetaData
from flask.ext.principal import Principal, RoleNeed, Permission, ActionNeed
from raven.contrib.flask import Sentry

app = Flask(__name__, static_url_path='/app/static')
app.config.from_object('config')
db = SQLAlchemy(app)

# blogging
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
meta = MetaData()
sql_storage = SQLAStorage(engine, metadata=meta)
blog = BloggingEngine(app, sql_storage)

mail = Mail(app)
babel = Babel(app)
sentry = Sentry(app)

# Needs
be_admin = RoleNeed('admin')
be_user = RoleNeed('user')
be_guest = RoleNeed('quest')
be_blogger = RoleNeed('blogger')

# Permissions
guest_per = Permission(be_guest)
guest_per.description = "Guest's permissions"

user_per = Permission(be_user)
user_per.description = "User's permissions"

blogger_per = Permission(be_blogger)
blogger_per.description = "Blogger's permissions"

admin_per = Permission(be_admin)
admin_per.description = "Admin's permissions"

apps_needs = [
    be_admin, be_user, be_guest, be_blogger
]

apps_permissions = [
    admin_per, user_per, guest_per, blogger_per
]

Principal(app)


from app.users.models import User

#create diagnostics table
from app.diagnostic.models import *
db.create_all(app=app)



from app.admin.views import MyAdminIndexView

backend = Admin(
    app
    , app.config['APP_NAME']
    , index_view=MyAdminIndexView()
    , template_mode='bootstrap3'
    , base_template='admin.html'
)


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def error_500(error):
    return render_template('500.html'), 500


@app.errorhandler(403)
def error_403(error):
    return render_template('403.html'), 403


# Initialize flask-login
def init_login():
    login_manager = login.LoginManager()
    login_manager.init_app(app)

    # Create user loader function
    @login_manager.user_loader
    @blog.user_loader
    def load_user(user_id):
        return db.session.query(User).get(user_id)


# Initialize flask-login
init_login()

from app.users.models import User, Role

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

from app.home.views import mod as homeModule

app.register_blueprint(homeModule)

from app.users.views import mod as userModule

app.register_blueprint(userModule)

# register page
from app.pages.views import mod as pageModule

app.register_blueprint(pageModule)

# register tree
from app.tree.views import mod as treeModule
app.register_blueprint(treeModule)

# register Lab Manager
# from app.diagnostic.views import lab_profile, test_type_profile, fluid_profile
# from app.diagnostic.views import test_type_result_table_profile, EquipmentView
# from app.diagnostic.views import test_profile, campaign_profile, equipment_profile, contract_profile
# from app.diagnostic.views import blueprints, EquipmentView, NormFuranView, NormPhysicView
# from app.diagnostic.views import NormFuranView, NormGasView, NormIsolationView
from app.diagnostic.views import *
backend.add_view(EquipmentView(db.session))
backend.add_view(NormFuranView(db.session))
backend.add_view(NormPhysicView(db.session))
backend.add_view(NormIsolationView(db.session))
backend.add_view(NormGasView(db.session))
backend.add_view(AirCircuitBreakerView(db.session))
backend.add_view(ManufacturerView(db.session))
backend.add_view(BushingView(db.session))
backend.add_view(CableView(db.session))
backend.add_view(CapacitorView(db.session))
backend.add_view(RectifierView(db.session))
backend.add_view(NeutralResistanceView(db.session))
backend.add_view(TankView(db.session))
backend.add_view(LoadTapChangerView(db.session))
backend.add_view(BreakerView(db.session))
backend.add_view(SwitchGearView(db.session))
backend.add_view(SynchronousMachineView(db.session))
backend.add_view(InductionMachineView(db.session))
backend.add_view(TransformerView(db.session))
backend.add_view(GasSensorView(db.session))
backend.add_view(FluidTypeView(db.session))
backend.add_view(LocationView(db.session))
for item in my_simple_views:
    exec('''backend.add_view({model}View(db.session))'''.format(model=item['model']))

backend.add_view(LabView(db.session))
backend.add_view(CampaignView(db.session))
backend.add_view(ContractView(db.session))
backend.add_view(FluidProfileView(db.session))
backend.add_view(TestStatusView(db.session))
backend.add_view(TestTypeView(db.session))
backend.add_view(TestTypeResultTableView(db.session))
backend.add_view(TestResultView(db.session))
backend.add_view(EquipmentTypeView(db.session))
backend.add_view(ElectricalProfileView(db.session))
backend.add_view(MaterialView(db.session))
backend.add_view(PowerSourceView(db.session))
backend.add_view(NormView(db.session))
backend.add_view(RecommendationView(db.session))


from app.admin.views import UserAdmin, RoleAdmin, FileView, ImageView, MenuView
from app.admin.models import File, Image

backend.add_view(UserAdmin(db.session))
backend.add_view(RoleAdmin(db.session))

backend.add_view(FileView(File, db.session))
backend.add_view(ImageView(Image, db.session))

backend.add_view(MenuView(name="Menu"))

# create tree table
from app.tree.models import BaseManager
BaseManager.metadata.create_all(engine)


# if app.config['DEBUG']:
#     import sys
#     sys.path.append('/home/vision/.pycharm_helpers/pydev')
#     import pydevd
#     pydevd.settrace('192.168.88.1', port=9004, stdoutToServer=True, stderrToServer=True)

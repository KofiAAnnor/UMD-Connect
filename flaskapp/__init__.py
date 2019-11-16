from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager


app = Flask(__name__)

app.config['SECRET_KEY'] = '22d6a8cc268a1deffba6bdbfb1b9966b'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'


from flaskapp import routes
from flaskapp.models import User

db.drop_all()
db.create_all()

admin = User(username='admin', email='admin@admin.com', password=bcrypt.generate_password_hash("admin").decode('utf-8'))
db.session.add(admin)
db.session.commit()

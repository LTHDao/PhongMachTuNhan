from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_babelex import Babel
import cloudinary


app = Flask(__name__)
app.secret_key = 'hjf97reayjfjghff&^$#fjyrd'

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:123456@localhost/phongmach?charset=utf8mb4"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

login = LoginManager(app=app)

db = SQLAlchemy(app=app)

cloudinary.config(cloud_name="btlde1", api_key="552619991478794", api_secret="Sn3YuymDtIPCIG0zVugrVJgSlx8")

babel = Babel(app=app)


@babel.localeselector
def get_locate():
    return 'vi'
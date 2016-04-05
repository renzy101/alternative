from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import os
from flask.ext.bcrypt import Bcrypt


current_path = os.path.dirname(__file__)
client_path = os.path.abspath(os.path.join(current_path, '..', '..', 'client'))
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['TOKEN_SECRET'] = "efhrtesfdjghgnjeovgtmfcnhujgvufrmngd,imuhtrhbvbxdnhtfdngmflrntgjkhyfjgrhjek"
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:admin@localhost/alternative"
bcrypt = Bcrypt(app)
#app.config['SQLALCHEMY_DATABASE_URI'] = 
db = SQLAlchemy(app)

from project import views,models
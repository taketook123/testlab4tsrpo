from flask import Flask, request, jsonify
import uuid
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Api
import os


app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:SomePassword@localhost/test"
app.config['SQLALCHEMY_DATABASE_URI'] = "postgres://lab4testserv_user:JNTiH7jPXqzWIP5EA3CXkcnylV2CVkwt@dpg-clo65mv5felc73a2tqh0-a/lab4testserv"
app.config['JWT_SECRET_KEY'] = os.environ('JWT_SECRET_KEY')
app.config['JWT_ALGORITHM'] = "HS256"
db = SQLAlchemy(app)
migrate = Migrate(app, db)
api = Api(app)

import labproject1.views
import labproject1.models


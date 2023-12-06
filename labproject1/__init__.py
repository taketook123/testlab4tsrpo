from flask import Flask, request, jsonify
import uuid
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:SomePassword@localhost/test"
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://testlab3db_q1ss_user:UMK3TtGSlxbwmixK5QPVAN20CQVsW74x@dpg-cles1ac15k1s73f5kshg-a/testlab3db_q1ss"
db = SQLAlchemy(app)
migrate = Migrate(app, db)

import labproject1.views
import labproject1.models


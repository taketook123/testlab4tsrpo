from labproject1 import db
from datetime import datetime



class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=30), nullable=False, unique=True)

    record = db.relationship("Record", back_populates="user", lazy="dynamic")
    usercategory = db.relationship("UserCategory", back_populates="user", lazy="dynamic")

    def __repr__(self):
        return f'User {self.name}'

class Category(db.Model):
    __tablename__ = "category"    

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=30), nullable=False, unique=True)

    record = db.relationship("Record", back_populates="category", lazy="dynamic")

class Record(db.Model):
    __tablename__ = "record"    

    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=False, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), unique=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sum = db.Column(db.Float(precision=2), unique=False, nullable=False)

    user = db.relationship("User", back_populates="record")
    category = db.relationship("Category", back_populates="record")

class UserCategory(db.Model):
    __tablename__ = "usercategory"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=40), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=False, nullable=False)
    is_public = db.Column(db.Boolean, nullable=False, default=True)

    user = db.relationship("User", back_populates="usercategory")

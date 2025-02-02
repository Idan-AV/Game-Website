from . import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(10), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=True)

from sqlalchemy import ForeignKey, PrimaryKeyConstraint, func
from db import db


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    text = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return '<Task %r>' % self.id


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False, unique=True)
    email = db.Column(db.String(30), nullable=False, unique=True)
    psw_hash = db.Column(db.String(72), nullable=False)

    def __repr__(self):
        return '<Task %r>' % self.id


class Completed(db.Model):
    user_id = db.Column(db.Integer, ForeignKey(User.id), nullable=False)
    task_id = db.Column(db.Integer, ForeignKey(Task.id), nullable=False)
    time = db.Column(db.DateTime, server_default=func.now())

    __table_args__ = (PrimaryKeyConstraint(user_id, task_id),)

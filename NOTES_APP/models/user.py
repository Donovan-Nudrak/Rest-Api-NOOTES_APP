#!/usr/bin/env python3
"""User account ORM model; password stored as werkzeug hash only."""

from database.db import db
from datetime import datetime 

class User(db.Model):

    __tablename__ = 'users' 

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    notes = db.relationship('Note', backref='user', lazy=True) 

    def __repr__(self):
        return f"<User {self.username}>" 




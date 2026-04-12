#!/usr/bin/env python3
"""Note ORM model and many-to-many link table for users a note is shared with."""

from database.db import db
from datetime import datetime

# Association table: one row per (note, user) share pair.
note_shares = db.Table(
    'note_shares',
    db.Column('note_id', db.Integer, db.ForeignKey('notes.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
)

class Note(db.Model):

    __tablename__ = 'notes' 

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    visibility = db.Column(db.String(10), default='private', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    shared_with = db.relationship(
        'User',
        secondary='note_shares',
        backref='shared_notes', 
        lazy='dynamic',
    )

    def __repr__(self):
        return f"<Note {self.title}>" 


    

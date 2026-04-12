#!/usr/bin/env python
"""Single SQLAlchemy extension instance; imported by models and app."""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


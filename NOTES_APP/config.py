#!/usr/bin/env python3
"""Environment-specific settings. Switch app.config to TestingConfig or ProductionConfig as needed."""

import os

class Config:

    SECRET_KEY = os.environ.get('SECRET_KEY', 'super_secret_key')

    DEBUG = False

    TESTING = False

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    DB_PATH = os.path.join(BASE_DIR, 'database', 'notes_app.db')  # file created on first run

    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH}"

    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):

    SQLALCHEMY_DATABASE_URI = f"sqlite:///{Config.DB_PATH}"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True


class TestingConfig(Config):

    TESTING = True

    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


class ProductionConfig(Config):

    DEBUG = False

import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


# TODO IMPLEMENT DATABASE URL
# Database URI for development
# SQLALCHEMY_DATABASE_URI = 'postgresql://fsnd:fsnd@localhost:5432/fyyur-app'
# Database uri for production
SQLALCHEMY_DATABASE_URI= 'postgresql-crystalline-88147'
SQLALCHEMY_TRACK_MODIFICATIONS = False
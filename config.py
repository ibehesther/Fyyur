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
SQLALCHEMY_DATABASE_URI= 'postgres://tmjtdyscympkim:ffef5e10b77aeeb6d2cd374f11640bc1d6f458171db291d4dd71bc491723b7e9@ec2-107-22-122-106.compute-1.amazonaws.com:5432/d1q335bmo2sl5h'
SQLALCHEMY_TRACK_MODIFICATIONS = False
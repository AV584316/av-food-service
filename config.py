import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'mysecretkey')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///orders.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

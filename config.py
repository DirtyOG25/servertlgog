import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "cambia-esto-en-produccion")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEFAULT_MAX_DEVICES = int(os.getenv("DEFAULT_MAX_DEVICES", "1"))
    AUTO_BIND_FIRST_DEVICE = os.getenv("AUTO_BIND_FIRST_DEVICE", "1") == "1"

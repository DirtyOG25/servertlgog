from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

def utcnow():
    return datetime.now(timezone.utc)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow)

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    email = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=utcnow)
    licenses = db.relationship("License", backref="client", lazy=True)

class License(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    license_id = db.Column(db.String(64), unique=True, nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey("client.id"))
    plan = db.Column(db.String(64), default="premium")
    status = db.Column(db.String(32), default="active")
    max_devices = db.Column(db.Integer, default=1)
    expires_at = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=utcnow)
    devices = db.relationship("Device", backref="license", lazy=True, cascade="all,delete-orphan")
    payments = db.relationship("Payment", backref="license", lazy=True, cascade="all,delete-orphan")

class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    license_id = db.Column(db.Integer, db.ForeignKey("license.id"))
    device_id = db.Column(db.String(128), nullable=False)
    activated_at = db.Column(db.DateTime, default=utcnow)
    last_seen = db.Column(db.DateTime, default=utcnow)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    license_id = db.Column(db.Integer, db.ForeignKey("license.id"))
    amount = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(16), default="USDT")
    txid = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=utcnow)

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    license_id = db.Column(db.Integer, nullable=True)
    event = db.Column(db.String(255))
    data = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=utcnow)

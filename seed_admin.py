import os
from getpass import getpass
from werkzeug.security import generate_password_hash
from app import create_app
from models import db, User

app = create_app()
with app.app_context():
    email = os.getenv("ADMIN_EMAIL") or input("Admin email: ").strip()
    pw = os.getenv("ADMIN_PASSWORD") or getpass("Admin password: ")
    if User.query.filter_by(email=email).first():
        print("Ya existe un admin con ese email.")
    else:
        u = User(email=email, password_hash=generate_password_hash(pw))
        db.session.add(u)
        db.session.commit()
        print("Admin creado:", email)

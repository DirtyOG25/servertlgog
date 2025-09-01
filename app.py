import base64, hmac, hashlib, os
from datetime import datetime, timezone
from flask import Flask, request, jsonify, redirect, url_for
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from config import Config
from models import db, User, Client, License, Device, Payment, AuditLog

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    with app.app_context():
        db.create_all()

    login_manager = LoginManager(app)
    login_manager.login_view = "login"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    class AuthModelView(ModelView):
        def is_accessible(self):
            return current_user.is_authenticated
        def inaccessible_callback(self, name, **kwargs):
            return redirect(url_for("login"))

    admin = Admin(app, name="Licencias Admin", template_mode="bootstrap4")
    admin.add_view(AuthModelView(User, db.session))
    admin.add_view(AuthModelView(Client, db.session))
    admin.add_view(AuthModelView(License, db.session))
    admin.add_view(AuthModelView(Device, db.session))
    admin.add_view(AuthModelView(Payment, db.session))
    admin.add_view(AuthModelView(AuditLog, db.session))

    def hmac_ok(license_id: str, client_id: str, signature: str) -> bool:
        secret = app.config["SECRET_KEY"]
        msg = f"{license_id}:{client_id}".encode("utf-8")
        good = base64.b64encode(hmac.new(secret.encode("utf-8"), msg, hashlib.sha256).digest()).decode()
        return hmac.compare_digest(good, signature or "")

    def days_left(expires_at):
        if not expires_at:
            return None
        now = datetime.now(timezone.utc)
        delta = expires_at - now
        return max(0, int(delta.total_seconds() // 86400))

    @app.get("/")
    def health():
        return "License server OK", 200

    @app.post("/api/verify")
    def api_verify():
        data = request.get_json(force=True, silent=True) or {}
        lic_id = (data.get("license_id") or "").strip()
        client_id = (data.get("client_id") or "").strip()
        signature = data.get("signature") or ""
        device_id = (data.get("device_id") or "").strip()

        if not lic_id or not client_id or not signature:
            return jsonify({"valid": False, "message": "faltan campos"}), 200
        if not hmac_ok(lic_id, client_id, signature):
            return jsonify({"valid": False, "message": "signature inválida"}), 200

        lic = License.query.filter_by(license_id=lic_id).first()
        if not lic:
            return jsonify({"valid": False, "message": "license_id no existe"}), 200

        if lic.status in ("banned", "paused"):
            return jsonify({"valid": False, "message": f"licencia {lic.status}"}), 200

        if lic.expires_at and lic.expires_at <= datetime.now(timezone.utc):
            lic.status = "expired"
            db.session.commit()
            return jsonify({"valid": False, "message": "licencia expirada"}), 200

        if device_id:
            dev = Device.query.filter_by(license_id=lic.id, device_id=device_id).first()
            if not dev:
                total = Device.query.filter_by(license_id=lic.id).count()
                if total >= (lic.max_devices or 1):
                    return jsonify({"valid": False, "message": "límite de dispositivos alcanzado"}), 200
                db.session.add(Device(license_id=lic.id, device_id=device_id))
                db.session.commit()
            else:
                dev.last_seen = datetime.now(timezone.utc)
                db.session.commit()

        dleft = days_left(lic.expires_at)
        return jsonify({
            "valid": True,
            "message": "Licencia válida",
            "plan": lic.plan,
            "expires_at": lic.expires_at.isoformat() if lic.expires_at else None,
            "days_left": dleft,
            "max_devices": lic.max_devices
        }), 200

    @app.get("/login")
    def login():
        return (
            "<form method='post'>"
            "<h3>Admin Login</h3>"
            "<input name='email'><br>"
            "<input name='password' type='password'><br>"
            "<button type='submit'>Entrar</button>"
            "</form>"
        )

    @app.post("/login")
    def do_login():
        email = (request.form.get("email") or "").strip()
        pw = request.form.get("password") or ""
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, pw):
            login_user(user)
            return redirect("/admin")
        return "Credenciales inválidas", 401

    @app.get("/logout")
    @login_required
    def logout():
        logout_user()
        return redirect(url_for("login"))

    return app

app = create_app()
if __name__ == "__main__":
    app.run("0.0.0.0", int(os.getenv("PORT", "8000")))

import os, hmac, hashlib, base64

SECRET_KEY = os.getenv("SECRET_KEY", "cambia-esto-en-produccion")

license_id = os.getenv("LICENSE_ID", "LIC-0001")
client_id  = os.getenv("CLIENT_ID", "cliente-ejemplo")

msg = f"{license_id}:{client_id}".encode("utf-8")
signature = base64.b64encode(hmac.new(SECRET_KEY.encode("utf-8"), msg, hashlib.sha256).digest()).decode()

print("license_id:", license_id)
print("client_id :", client_id)
print("signature :", signature)

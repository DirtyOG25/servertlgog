# License Server Backend

## Local
```powershell
python -m venv .venv
.\.venv\Scripts\Activate
pip install -r requirements.txt

$env:SECRET_KEY = "tu-clave-super-secreta"

$env:ADMIN_EMAIL = "admin@tudominio.com"
$env:ADMIN_PASSWORD = "admin123"
python seed_admin.py

python app.py
```

## Render
- Conecta repo
- Build: `pip install -r requirements.txt`
- Start: `gunicorn app:app -b 0.0.0.0:$PORT`
- Env Vars: `SECRET_KEY`, `DATABASE_URL`, `ADMIN_EMAIL`, `ADMIN_PASSWORD`

## Licencias
```powershell
$env:SECRET_KEY = "la-misma-que-en-server"
$env:LICENSE_ID = "LIC-0001"
$env:CLIENT_ID = "cliente-ejemplo"
python genera_firma.py
```

Crea license.json:
```json
{
  "license_id": "LIC-0001",
  "client_id": "cliente-ejemplo",
  "signature": "firma"
}
```

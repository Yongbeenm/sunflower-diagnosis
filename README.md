# Doctor Sunflower

Flask app for sunflower disease information, symptom checking, feedback, and admin/Expert Sunflower management. The local project currently uses SQLite databases in `instance/` and includes English/Khmer UI data.

## Current Data

- Main database: `instance/doctor_sunflower.db`
- Language databases: `instance/i18n_en.db`, `instance/i18n_km.db`
- Disease records: 26
- Disease images: `app/static/images/`
- Feedback uploads: `app/static/uploads/feedback/`

## Run Locally

```bash
source .venv/bin/activate
python run.py
```

Open:

```text
http://127.0.0.1:5000
```

If port `5000` is busy, the app starts on:

```text
http://127.0.0.1:5050
```

You can set a custom port:

```bash
PORT=8000 python run.py
```

## Setup From Scratch

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

## Default Accounts

The app creates these users if the database is empty:

```text
Admin username: admin
Admin password: admin123

Expert Sunflower username: doctor
Expert Sunflower password: doctor123
```

Optional environment variables:

```bash
export ADMIN_USERNAME="admin"
export ADMIN_EMAIL="admin@local.test"
export ADMIN_PASSWORD="admin123"
export DOCTOR_USERNAME="doctor"
export DOCTOR_EMAIL="doctor@local.test"
export DOCTOR_PASSWORD="doctor123"
export SECRET_KEY="change-me"
```

## Main Pages

- `/` home
- `/disease-library` disease library
- `/disease/<slug>` disease detail
- `/diagnose` symptom checker
- `/symptom-history` user symptom history
- `/feedback` feedback form
- `/search` search
- `/register`, `/login`, `/logout`
- `/user/profile`
- `/admin/dashboard`
- `/admin/diseases`
- `/admin/checklists`
- `/admin/symptoms/all`
- `/admin/feedback`
- `/admin/users`
- `/admin/roles`
- `/admin/symptom-checks`
- `/doctor/dashboard` Expert Sunflower dashboard
- `/doctor/diseases` Expert Sunflower disease center
- `/doctor/checklists` Expert Sunflower symptom rules
- `/doctor/symptoms/all` Expert Sunflower symptom catalog
- `/doctor/feedback` Expert Sunflower feedback inbox
- `/doctor/symptom-checks` Expert Sunflower symptom history

## Database Configuration

By default, the app uses SQLite:

```text
sqlite:///instance/doctor_sunflower.db
sqlite:///instance/i18n_en.db
sqlite:///instance/i18n_km.db
```

Optional SQLAlchemy URLs:

```bash
export DATABASE_URL="sqlite:////absolute/path/to/doctor_sunflower.db"
export I18N_EN_DATABASE_URL="sqlite:////absolute/path/to/i18n_en.db"
export I18N_KM_DATABASE_URL="sqlite:////absolute/path/to/i18n_km.db"
```

MySQL is also supported:

```bash
export MYSQL_USER="root"
export MYSQL_PASSWORD=""
export MYSQL_HOST="127.0.0.1"
export MYSQL_PORT="3306"
export MYSQL_DB="doctor_sunflower"
export DATABASE_URL="mysql+pymysql://root:@127.0.0.1:3306/doctor_sunflower?charset=utf8mb4"
python run.py
```

## Project Files

```text
run.py                 app entry point
config.py              database and app config
extensions.py          Flask extension objects
app/                   Flask app package
app/routes/            public, auth, user, admin, Expert Sunflower routes
app/models/            SQLAlchemy models
app/services/          disease, diagnosis, i18n, seed helpers
app/templates/         Jinja templates
app/static/            CSS, JS, images, uploads
instance/              local SQLite databases
requirements.txt       Python dependencies
```

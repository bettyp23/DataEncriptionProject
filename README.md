# Secure Employee Portal

This project demonstrates secure data management for a small organization using SQLite, Fernet encryption, and a Flask web application. It implements the full assignment requirements: encrypted database scripts, a web UI with encrypted CRUD operations, and decrypted credential outputs for testing.

## Project Layout

- `employee_create_db.py` – Drops/creates the `Employee` table, inserts six encrypted rows, prints encrypted results, and shows a decrypted credential matrix for mentors.
- `payraise_create_db.py` – Drops/creates the `EmpPayRaise` table, inserts six encrypted rows with matching employee IDs, and prints encrypted results.
- `security_utils.py` – Centralized Fernet key management plus `encrypt_text` / `decrypt_text` helpers reused by all scripts and the Flask app.
- `app.py` – Flask site covering login, employee management, and pay raise views; encrypts before writes and decrypts for displays.
- `templates/` & `static/` – Minimal Jinja2 HTML and CSS files used by the Flask app.
- `requirements.txt` – Dependency pinning for reproducible installs.

## Prerequisites

- Python 3.10+ (tested with Homebrew Python 3.14 on macOS)
- Git (for version control)

## Setup

```bash
cd /Users/bettyphipps/Desktop/DataEncriptionProject
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

The first run of any script automatically creates `fernet.key` in the project root. Keep this file safe; it must remain consistent between the database scripts and Flask app.

## Database Scripts

Run each script once (after activating the virtual environment) to initialize data:

```bash
python employee_create_db.py
python payraise_create_db.py
```

You should see the encrypted row outputs and the decrypted credential matrix required for instructor testing.

## Flask Application

With the virtual environment active and the database seeded:

```bash
python app.py
```

Open http://127.0.0.1:5000/ in your browser. Login using any decrypted credential printed by `employee_create_db.py`. All add/list operations encrypt sensitive values before storing them and decrypt for display.

## Deployment Notes

- Always run scripts from the project root to ensure `company.db` and `fernet.key` resolve correctly.
- Update `app.config["SECRET_KEY"]` in `app.py` before any production deployment.
- Re-run the database scripts whenever you want to reset the tables with the original seeded data.


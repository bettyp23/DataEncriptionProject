# Secure Employee Portal

This project demonstrates secure data management for a small organization using SQLite, Fernet encryption, and a Flask web application. It implements the full assignment requirements: encrypted database scripts, a web UI with encrypted CRUD operations, and decrypted credential outputs for testing.

## Project Layout

- `employee_create_db.py` – Drops/creates the `Employee` table, inserts six encrypted rows, prints encrypted results, and shows a decrypted credential matrix for mentors.
- `payraise_create_db.py` – Drops/creates the `EmpPayRaise` table, inserts six encrypted rows with matching employee IDs, and prints encrypted results.
- `security_utils.py` – Centralized Fernet key management plus `encrypt_text` / `decrypt_text` helpers reused by all scripts and the Flask app.
- `app.py` – Flask site covering login, employee management, and pay raise views; encrypts before writes and decrypts for displays.
- `process_payraise_deletion_server.py` – TCP server that listens on localhost:9999 for encrypted deletion requests and processes pay raise deletions.
- `templates/` & `static/` – Minimal Jinja2 HTML and CSS files used by the Flask app.
- `requirements.txt` – Dependency pinning for reproducible installs.

## Prerequisites

- Python 3.10+ (tested with Homebrew Python 3.14 on macOS)
- Git (for version control)

## Setup

1. Clone or download the repository:

```bash
git clone https://github.com/bettyp23/DataEncriptionProject.git
cd DataEncriptionProject
```

2. Create and activate a virtual environment (recommended):

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
```

3. Install dependencies:

```bash
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

## Running the Application

### Step 1: Start the TCP Server (Required for pay raise deletions)

In a separate terminal window, with the virtual environment active:

```bash
python process_payraise_deletion_server.py
```

The server will start listening on `localhost:9999`. Keep this terminal open while using the Flask app.

### Step 2: Start the Flask Application

In another terminal window, with the virtual environment active:

```bash
python app.py
```

### Step 3: Access the Web Application

Open http://127.0.0.1:5000/ in your browser. Login using any decrypted credential printed by `employee_create_db.py`. 

**Available Features:**
- All users: List/Add employees and pay raises, view your own pay raises
- Users with SecurityLevel <= 2: Submit to Delete a Pay Raise (requires TCP server to be running)

## Quick Start Summary

1. **Setup**: `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
2. **Initialize Database**: `python employee_create_db.py && python payraise_create_db.py`
3. **Start TCP Server**: `python process_payraise_deletion_server.py` (keep running in separate terminal)
4. **Start Flask App**: `python app.py` (in another terminal)
5. **Access**: Open http://127.0.0.1:5000/ and login with credentials from step 2

## Submission Files

For assignment submission, include the following files:

**Required Core Files:**
- `employee_create_db.py` - Employee table creation with encrypted fields
- `payraise_create_db.py` - Pay raise table creation with encrypted raise amounts
- `app.py` - Flask web application with encryption/decryption
- `security_utils.py` - Encryption utilities (required dependency)

**Flask Application Files:**
- `templates/` - All HTML templates
- `static/styles.css` - CSS styling
- `requirements.txt` - Python dependencies

**Optional Files:**
- `process_payraise_deletion_server.py` - TCP server for Module 12 features
- `README.md` - This documentation

## Deployment Notes

- Always run scripts from the project root to ensure `company.db` and `fernet.key` resolve correctly.
- Update `app.config["SECRET_KEY"]` in `app.py` before any production deployment.
- Re-run the database scripts whenever you want to reset the tables with the original seeded data.
- The TCP server must be running before attempting to submit pay raise deletion requests.


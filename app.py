"""
Program: Secure Employee Portal Flask App
Author: GPT-5 Codex
Date: 2025-11-13
Purpose: Demonstrate encrypted storage and retrieval of employee data.
"""
from __future__ import annotations

import sqlite3
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict

from flask import (
    Flask,
    redirect,
    render_template,
    request,
    session,
    url_for,
    flash,
)

import security_utils

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "company.db"

app = Flask(__name__)
app.config["SECRET_KEY"] = "change-this-secret-key"
app.config["DATABASE"] = str(DB_PATH)


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(app.config["DATABASE"])
    conn.row_factory = sqlite3.Row
    return conn


def login_required(view: Callable) -> Callable:
    @wraps(view)
    def wrapped_view(*args: Any, **kwargs: Any) -> Any:
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped_view


@app.route("/", methods=["GET", "POST"])
def login():
    error: str | None = None
    name_value = ""
    if request.method == "POST":
        name_value = request.form.get("name", "").strip()
        password = request.form.get("password", "")

        try:
            encrypted_name = security_utils.encrypt_text(name_value)
            encrypted_password = security_utils.encrypt_text(password)
        except ValueError:
            error = "Name and password are required."
        else:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT UserId, Name, SecurityLevel
                    FROM Employee
                    WHERE Name = ? AND LoginPassword = ?;
                    """,
                    (encrypted_name, encrypted_password),
                )
                user = cursor.fetchone()
                if user:
                    session["user_id"] = user["UserId"]
                    session["user_name"] = security_utils.decrypt_text(user["Name"])
                    session["security_level"] = user["SecurityLevel"]
                    flash(f"Welcome back, {session['user_name']}!", "success")
                    return redirect(url_for("list_employees"))
                error = "Invalid credentials. Please try again."

    with get_db_connection() as conn:
        rows = conn.execute("SELECT Name FROM Employee ORDER BY UserId;").fetchall()
    known_names = [security_utils.decrypt_text(row["Name"]) for row in rows]

    return render_template(
        "login.html",
        error=error,
        name=name_value,
        known_names=known_names,
    )


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


@app.route("/employees")
@login_required
def list_employees():
    with get_db_connection() as conn:
        rows = conn.execute(
            """
            SELECT UserId, Name, Age, PhNum, SecurityLevel, LoginPassword
            FROM Employee
            ORDER BY UserId;
            """
        ).fetchall()

    employees = [
        {
            "UserId": row["UserId"],
            "Name": security_utils.decrypt_text(row["Name"]),
            "Age": row["Age"],
            "PhNum": security_utils.decrypt_text(row["PhNum"]),
            "SecurityLevel": row["SecurityLevel"],
            "LoginPassword": security_utils.decrypt_text(row["LoginPassword"]),
        }
        for row in rows
    ]

    return render_template("employees.html", employees=employees)


@app.route("/employees/add", methods=["GET", "POST"])
@login_required
def add_employee():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        age = request.form.get("age", "").strip()
        phnum = request.form.get("phnum", "").strip()
        security_level = request.form.get("security_level", "").strip()
        password = request.form.get("password", "")

        if not all([name, age, phnum, security_level, password]):
            flash("All fields are required.", "danger")
            return redirect(url_for("add_employee"))

        try:
            age_value = int(age)
            security_value = int(security_level)
        except ValueError:
            flash("Age and security level must be numeric.", "danger")
            return redirect(url_for("add_employee"))

        encrypted_name = security_utils.encrypt_text(name)
        encrypted_phone = security_utils.encrypt_text(phnum)
        encrypted_password = security_utils.encrypt_text(password)

        with get_db_connection() as conn:
            conn.execute(
                """
                INSERT INTO Employee (Name, Age, PhNum, SecurityLevel, LoginPassword)
                VALUES (?, ?, ?, ?, ?);
                """,
                (
                    encrypted_name,
                    age_value,
                    encrypted_phone,
                    security_value,
                    encrypted_password,
                ),
            )
            conn.commit()

        flash(f"Employee {name} added successfully.", "success")
        return redirect(url_for("list_employees"))

    return render_template("add_employee.html")


@app.route("/payraises")
@login_required
def list_pay_raises():
    with get_db_connection() as conn:
        rows = conn.execute(
            """
            SELECT PayRaiseId, EmpId, PayRaiseDate, RaiseAmt
            FROM EmpPayRaise
            ORDER BY PayRaiseDate DESC;
            """
        ).fetchall()

    pay_raises = [
        {
            "PayRaiseId": row["PayRaiseId"],
            "EmpId": row["EmpId"],
            "PayRaiseDate": row["PayRaiseDate"],
            "RaiseAmt": security_utils.decrypt_text(row["RaiseAmt"]),
        }
        for row in rows
    ]

    return render_template("payraises.html", pay_raises=pay_raises)


@app.route("/payraises/me")
@login_required
def my_pay_raises():
    user_id = session["user_id"]
    with get_db_connection() as conn:
        rows = conn.execute(
            """
            SELECT PayRaiseId, PayRaiseDate, RaiseAmt
            FROM EmpPayRaise
            WHERE EmpId = ?
            ORDER BY PayRaiseDate DESC;
            """,
            (user_id,),
        ).fetchall()

    pay_raises = [
        {
            "PayRaiseId": row["PayRaiseId"],
            "PayRaiseDate": row["PayRaiseDate"],
            "RaiseAmt": security_utils.decrypt_text(row["RaiseAmt"]),
        }
        for row in rows
    ]

    return render_template("my_payraises.html", pay_raises=pay_raises)


@app.route("/payraises/add", methods=["GET", "POST"])
@login_required
def add_pay_raise():
    if request.method == "POST":
        emp_id = request.form.get("emp_id", "").strip()
        pay_raise_date = request.form.get("pay_raise_date", "").strip()
        raise_amount = request.form.get("raise_amt", "").strip()

        if not all([emp_id, pay_raise_date, raise_amount]):
            flash("All fields are required.", "danger")
            return redirect(url_for("add_pay_raise"))

        try:
            emp_id_value = int(emp_id)
            amount_value = float(raise_amount)
        except ValueError:
            flash("Employee ID must be an integer and raise amount must be numeric.", "danger")
            return redirect(url_for("add_pay_raise"))

        encrypted_amount = security_utils.encrypt_text(f"{amount_value:.2f}")

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM Employee WHERE UserId = ?;", (emp_id_value,))
            if cursor.fetchone() is None:
                flash("Employee ID does not exist.", "danger")
                return redirect(url_for("add_pay_raise"))

            cursor.execute(
                """
                INSERT INTO EmpPayRaise (EmpId, PayRaiseDate, RaiseAmt)
                VALUES (?, ?, ?);
                """,
                (
                    emp_id_value,
                    pay_raise_date,
                    encrypted_amount,
                ),
            )
            conn.commit()

        flash("Pay raise added successfully.", "success")
        return redirect(url_for("list_pay_raises"))

    with get_db_connection() as conn:
        employees = conn.execute(
            "SELECT UserId, Name FROM Employee ORDER BY UserId;"
        ).fetchall()

    dropdown_employees = [
        {
            "UserId": row["UserId"],
            "Name": security_utils.decrypt_text(row["Name"]),
        }
        for row in employees
    ]

    return render_template("add_payraise.html", employees=dropdown_employees)


@app.context_processor
def inject_user() -> Dict[str, Any]:
    return {
        "current_user": {
            "id": session.get("user_id"),
            "name": session.get("user_name"),
            "security_level": session.get("security_level"),
        }
    }


if __name__ == "__main__":
    app.run(debug=True)


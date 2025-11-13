"""
Program: Employee Table Encryption Setup
Author: GPT-5 Codex
Date: 2025-11-13
Purpose: Drop, recreate, and populate the Employee table with encrypted fields.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable, Tuple

import security_utils

DB_PATH = Path(__file__).resolve().parent / "company.db"

# (UserId, Name, Age, PhNum, SecurityLevel, LoginPassword)
EMPLOYEE_ROWS: Iterable[Tuple[int, str, int, str, int, str]] = [
    (1, "Alice Johnson", 34, "555-100-2211", 1, "A1ic3!Secure"),
    (2, "Brian Smith", 42, "555-200-3322", 2, "Br14n#2024"),
    (3, "Carla Gomez", 29, "555-300-4433", 3, "Carla$Vault"),
    (4, "Dinesh Patel", 37, "555-400-5544", 2, "D1n3sh%Key"),
    (5, "Emily Zhang", 31, "555-500-6655", 1, "Em!ly_Ready"),
    (6, "Felix Brown", 45, "555-600-7766", 2, "Felix^Pass"),
]


def encrypt_employee_row(row: Tuple[int, str, int, str, int, str]) -> Tuple[int, bytes, int, bytes, int, bytes]:
    user_id, name, age, phone, security_level, password = row
    return (
        user_id,
        security_utils.encrypt_text(name),
        age,
        security_utils.encrypt_text(phone),
        security_level,
        security_utils.encrypt_text(password),
    )


def main() -> None:
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute("DROP TABLE IF EXISTS Employee;")
    print("Employee table dropped.")

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Employee (
            UserId INTEGER PRIMARY KEY,
            Name BLOB NOT NULL,
            Age INTEGER NOT NULL,
            PhNum BLOB NOT NULL,
            SecurityLevel INTEGER NOT NULL,
            LoginPassword BLOB NOT NULL
        );
        """
    )
    print("Employee table created.")

    encrypted_rows = [encrypt_employee_row(row) for row in EMPLOYEE_ROWS]

    cursor.executemany(
        """
        INSERT INTO Employee (UserId, Name, Age, PhNum, SecurityLevel, LoginPassword)
        VALUES (?, ?, ?, ?, ?, ?);
        """,
        encrypted_rows,
    )
    connection.commit()
    print(f"{len(encrypted_rows)} employee records inserted.")

    cursor.execute("SELECT UserId, Name, Age, PhNum, SecurityLevel, LoginPassword FROM Employee;")
    all_rows = cursor.fetchall()
    for db_row in all_rows:
        print(tuple(db_row))

    print("\nDecrypted credentials for mentor validation:")
    for user_id, enc_name, _, _, security_level, enc_password in all_rows:
        name = security_utils.decrypt_text(enc_name)
        password = security_utils.decrypt_text(enc_password)
        print(f"UserId {user_id}: Name={name}, Password={password}, SecurityLevel={security_level}")

    connection.close()
    print("Connection closed.")


if __name__ == "__main__":
    main()


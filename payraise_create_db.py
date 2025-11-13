"""
Program: Employee Pay Raise Encryption Setup
Author: GPT-5 Codex
Date: 2025-11-13
Purpose: Drop, recreate, and populate the EmpPayRaise table with encrypted raise amounts.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable, Tuple

import security_utils

DB_PATH = Path(__file__).resolve().parent / "company.db"

# (PayRaiseId, EmpId, PayRaiseDate, RaiseAmt)
PAY_RAISE_ROWS: Iterable[Tuple[int, int, str, float]] = [
    (1, 1, "2023-02-14", 1500.00),
    (2, 2, "2023-05-01", 2750.50),
    (3, 3, "2024-01-22", 3200.75),
    (4, 4, "2024-09-18", 1850.25),
    (5, 5, "2025-03-05", 2400.00),
    (6, 6, "2025-06-30", 4100.90),
]


def encrypt_pay_raise_row(row: Tuple[int, int, str, float]) -> Tuple[int, int, str, bytes]:
    raise_id, emp_id, date_value, amount = row
    encrypted_amount = security_utils.encrypt_text(f"{amount:.2f}")
    return raise_id, emp_id, date_value, encrypted_amount


def main() -> None:
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute("DROP TABLE IF EXISTS EmpPayRaise;")
    print("EmpPayRaise table dropped.")

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS EmpPayRaise (
            PayRaiseId INTEGER PRIMARY KEY,
            EmpId INTEGER NOT NULL,
            PayRaiseDate TEXT NOT NULL,
            RaiseAmt BLOB NOT NULL,
            FOREIGN KEY (EmpId) REFERENCES Employee(UserId)
        );
        """
    )
    print("EmpPayRaise table created.")

    encrypted_rows = [encrypt_pay_raise_row(row) for row in PAY_RAISE_ROWS]
    cursor.executemany(
        """
        INSERT INTO EmpPayRaise (PayRaiseId, EmpId, PayRaiseDate, RaiseAmt)
        VALUES (?, ?, ?, ?);
        """,
        encrypted_rows,
    )
    connection.commit()
    print(f"{len(encrypted_rows)} pay raise records inserted.")

    cursor.execute("SELECT PayRaiseId, EmpId, PayRaiseDate, RaiseAmt FROM EmpPayRaise;")
    all_rows = cursor.fetchall()
    for db_row in all_rows:
        print(tuple(db_row))

    connection.close()
    print("Connection closed.")


if __name__ == "__main__":
    main()


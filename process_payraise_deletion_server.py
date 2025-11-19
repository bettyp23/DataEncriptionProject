"""
Program: Process Pay Raise Deletion Server
Author: Betty Phipps
Date: 2025-11-13
Purpose: TCP server that receives encrypted deletion requests and processes pay raise deletions.
"""
from __future__ import annotations

import sqlite3
import socketserver
from pathlib import Path
from typing import Tuple

import security_utils

DB_PATH = Path(__file__).resolve().parent / "company.db"
MESSAGE_SEPARATOR = "^%$"
HOST = "localhost"
PORT = 9999


class PayRaiseDeletionHandler(socketserver.BaseRequestHandler):
    """
    Request handler for processing encrypted pay raise deletion requests.
    """

    def handle(self) -> None:
        """
        Handle incoming connection: receive, decrypt, validate, and delete record.
        """
        # Receive encrypted message
        encrypted_data = self.request.recv(4096)

        if not encrypted_data:
            print(f"{self.client_address[0]} sent empty message")
            return

        try:
            # Decrypt message
            decrypted_message = security_utils.decrypt_text(encrypted_data)
            print(f"{self.client_address[0]}    sent message:    {decrypted_message}")

            # Split message using preset separator
            parts = decrypted_message.split(MESSAGE_SEPARATOR)
            if len(parts) != 2:
                print(f"ERROR: Invalid message format. Expected 2 parts separated by '{MESSAGE_SEPARATOR}', got {len(parts)}")
                return

            emp_id_str, pay_raise_date = parts[0].strip(), parts[1].strip()

            try:
                emp_id = int(emp_id_str)
            except ValueError:
                print(f"ERROR: Invalid Employee ID format: '{emp_id_str}'")
                return

            print(f"EmpId: {emp_id}")
            print(f"PayRaiseDate: {pay_raise_date}")

            # Validate that record exists
            connection = sqlite3.connect(DB_PATH)
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT PayRaiseId
                FROM EmpPayRaise
                WHERE EmpId = ? AND PayRaiseDate = ?;
                """,
                (emp_id, pay_raise_date),
            )
            record = cursor.fetchone()

            if not record:
                print(f"ERROR: No pay raise record found for Employee ID {emp_id} with date {pay_raise_date}")
                connection.close()
                return

            # Delete the record
            cursor.execute(
                """
                DELETE FROM EmpPayRaise
                WHERE EmpId = ? AND PayRaiseDate = ?;
                """,
                (emp_id, pay_raise_date),
            )
            connection.commit()
            connection.close()

            print("Record successfully deleted")

        except ValueError as e:
            print(f"ERROR: Decryption or validation failed: {e}")
        except sqlite3.Error as e:
            print(f"ERROR: Database operation failed: {e}")
        except Exception as e:
            print(f"ERROR: Unexpected error: {e}")


def main() -> None:
    """
    Start the TCP server on localhost:9999.
    """
    server = socketserver.TCPServer((HOST, PORT), PayRaiseDeletionHandler)
    print(f"Pay Raise Deletion Server listening on {HOST}:{PORT}")
    print("Press Ctrl+C to stop the server")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        server.shutdown()


if __name__ == "__main__":
    main()


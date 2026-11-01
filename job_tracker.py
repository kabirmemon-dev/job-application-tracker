"""Job Application Tracker: a command-line app using Python and SQLite.

Run:  python3 job_tracker.py
Keeps track of where you applied, the status, and what to do next.
"""
import sqlite3
from datetime import date

DB_FILE = "jobs.db"
STATUSES = ["applied", "interview", "offer", "rejected"]


def connect():
    conn = sqlite3.connect(DB_FILE)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS applications (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               company TEXT NOT NULL,
               role TEXT NOT NULL,
               applied_on TEXT NOT NULL,
               status TEXT NOT NULL DEFAULT 'applied',
               notes TEXT)"""
    )
    return conn


def add_application(conn):
    company = input("Company: ").strip()
    role = input("Role: ").strip()
    notes = input("Notes (optional): ").strip()
    if not company or not role:
        print("Company and role are required.")
        return
    conn.execute(
        "INSERT INTO applications (company, role, applied_on, notes) VALUES (?, ?, ?, ?)",
        (company, role, date.today().isoformat(), notes),
    )
    conn.commit()
    print("Saved.")


def list_applications(conn, status=None):
    if status:
        rows = conn.execute(
            "SELECT id, company, role, applied_on, status FROM applications "
            "WHERE status = ? ORDER BY applied_on DESC",
            (status,),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT id, company, role, applied_on, status FROM applications "
            "ORDER BY applied_on DESC"
        ).fetchall()
    if not rows:
        print("Nothing here yet.")
        return
    print(f"{'ID':<4}{'Company':<22}{'Role':<30}{'Date':<12}{'Status'}")
    for row in rows:
        print(f"{row[0]:<4}{row[1]:<22}{row[2]:<30}{row[3]:<12}{row[4]}")


def update_status(conn):
    list_applications(conn)
    try:
        app_id = int(input("ID to update: "))
    except ValueError:
        print("Please enter a number.")
        return
    new_status = input(f"New status {STATUSES}: ").strip().lower()
    if new_status not in STATUSES:
        print("Invalid status.")
        return
    cur = conn.execute("UPDATE applications SET status = ? WHERE id = ?", (new_status, app_id))
    conn.commit()
    print("Updated." if cur.rowcount else "No application with that ID.")


def search(conn):
    term = input("Search company or role: ").strip()
    rows = conn.execute(
        "SELECT id, company, role, applied_on, status FROM applications "
        "WHERE company LIKE ? OR role LIKE ?",
        (f"%{term}%", f"%{term}%"),
    ).fetchall()
    for row in rows:
        print(row)
    if not rows:
        print("No matches.")


def summary(conn):
    """Aggregate query: how many applications per status."""
    rows = conn.execute(
        "SELECT status, COUNT(*) FROM applications GROUP BY status ORDER BY COUNT(*) DESC"
    ).fetchall()
    total = sum(count for _, count in rows)
    print(f"Total applications: {total}")
    for status, count in rows:
        print(f"  {status:<10} {count}")


MENU = """
1) Add application
2) List all
3) List by status
4) Update status
5) Search
6) Summary
0) Quit
"""


def main():
    conn = connect()
    while True:
        print(MENU)
        choice = input("Choose: ").strip()
        if choice == "1":
            add_application(conn)
        elif choice == "2":
            list_applications(conn)
        elif choice == "3":
            list_applications(conn, input(f"Status {STATUSES}: ").strip().lower())
        elif choice == "4":
            update_status(conn)
        elif choice == "5":
            search(conn)
        elif choice == "6":
            summary(conn)
        elif choice == "0":
            break
        else:
            print("Unknown option.")
    conn.close()


if __name__ == "__main__":
    main()

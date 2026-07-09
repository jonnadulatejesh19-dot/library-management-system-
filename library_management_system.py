import sqlite3
from datetime import datetime, timedelta

DB_NAME = "library.db"
LOAN_DAYS = 14
FINE_PER_DAY = 5

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_NAME)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.setup()

    def setup(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                isbn TEXT UNIQUE,
                copies INTEGER NOT NULL,
                available INTEGER NOT NULL
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS loans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER,
                member_id INTEGER,
                checkout_date TEXT,
                due_date TEXT,
                return_date TEXT,
                FOREIGN KEY(book_id) REFERENCES books(id),
                FOREIGN KEY(member_id) REFERENCES members(id)
            )
        """)
        self.conn.commit()

    def commit(self):
        self.conn.commit()


class Library:
    def __init__(self, db):
        self.db = db

    def add_book(self, title, author, isbn, copies):
        try:
            self.db.cursor.execute(
                "INSERT INTO books (title, author, isbn, copies, available) VALUES (?, ?, ?, ?, ?)",
                (title, author, isbn, copies, copies)
            )
            self.db.commit()
            print(f"Added book: {title}")
        except sqlite3.IntegrityError:
            print("A book with that ISBN already exists.")

    def remove_book(self, book_id):
        self.db.cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
        self.db.commit()
        print("Book removed.")

    def search_books(self, keyword):
        query = "%" + keyword + "%"
        self.db.cursor.execute(
            "SELECT * FROM books WHERE title LIKE ? OR author LIKE ? OR isbn LIKE ?",
            (query, query, query)
        )
        return self.db.cursor.fetchall()

    def list_books(self):
        self.db.cursor.execute("SELECT * FROM books")
        return self.db.cursor.fetchall()

    def add_member(self, name, email):
        try:
            self.db.cursor.execute(
                "INSERT INTO members (name, email) VALUES (?, ?)",
                (name, email)
            )
            self.db.commit()
            print(f"Added member: {name}")
        except sqlite3.IntegrityError:
            print("A member with that email already exists.")

    def list_members(self):
        self.db.cursor.execute("SELECT * FROM members")
        return self.db.cursor.fetchall()

    def checkout_book(self, book_id, member_id):
        self.db.cursor.execute("SELECT available FROM books WHERE id = ?", (book_id,))
        row = self.db.cursor.fetchone()
        if row is None:
            print("Book not found.")
            return
        if row["available"] <= 0:
            print("No copies available.")
            return

        checkout_date = datetime.now()
        due_date = checkout_date + timedelta(days=LOAN_DAYS)

        self.db.cursor.execute(
            "INSERT INTO loans (book_id, member_id, checkout_date, due_date, return_date) VALUES (?, ?, ?, ?, NULL)",
            (book_id, member_id, checkout_date.isoformat(), due_date.isoformat())
        )
        self.db.cursor.execute(
            "UPDATE books SET available = available - 1 WHERE id = ?", (book_id,)
        )
        self.db.commit()
        print(f"Checked out. Due date: {due_date.strftime('%Y-%m-%d')}")

    def return_book(self, loan_id):
        self.db.cursor.execute("SELECT * FROM loans WHERE id = ?", (loan_id,))
        loan = self.db.cursor.fetchone()
        if loan is None:
            print("Loan not found.")
            return
        if loan["return_date"] is not None:
            print("This book was already returned.")
            return

        return_date = datetime.now()
        due_date = datetime.fromisoformat(loan["due_date"])
        fine = 0
        if return_date > due_date:
            days_late = (return_date - due_date).days
            fine = days_late * FINE_PER_DAY

        self.db.cursor.execute(
            "UPDATE loans SET return_date = ? WHERE id = ?",
            (return_date.isoformat(), loan_id)
        )
        self.db.cursor.execute(
            "UPDATE books SET available = available + 1 WHERE id = ?", (loan["book_id"],)
        )
        self.db.commit()

        if fine > 0:
            print(f"Book returned late. Fine: ${fine}")
        else:
            print("Book returned on time. No fine.")

    def active_loans(self):
        self.db.cursor.execute("""
            SELECT loans.id, books.title, members.name, loans.checkout_date, loans.due_date
            FROM loans
            JOIN books ON loans.book_id = books.id
            JOIN members ON loans.member_id = members.id
            WHERE loans.return_date IS NULL
        """)
        return self.db.cursor.fetchall()

    def overdue_loans(self):
        today = datetime.now().isoformat()
        self.db.cursor.execute("""
            SELECT loans.id, books.title, members.name, loans.due_date
            FROM loans
            JOIN books ON loans.book_id = books.id
            JOIN members ON loans.member_id = members.id
            WHERE loans.return_date IS NULL AND loans.due_date < ?
        """, (today,))
        return self.db.cursor.fetchall()


def print_books(books):
    if not books:
        print("No books found.")
        return
    for b in books:
        print(f"[{b['id']}] {b['title']} by {b['author']} | ISBN: {b['isbn']} | Available: {b['available']}/{b['copies']}")

def print_members(members):
    if not members:
        print("No members found.")
        return
    for m in members:
        print(f"[{m['id']}] {m['name']} | {m['email']}")

def print_loans(loans, overdue=False):
    if not loans:
        print("No loans found.")
        return
    for l in loans:
        if overdue:
            print(f"[{l['id']}] {l['title']} - {l['name']} | Due: {l['due_date'][:10]}")
        else:
            print(f"[{l['id']}] {l['title']} - {l['name']} | Checked out: {l['checkout_date'][:10]} | Due: {l['due_date'][:10]}")


def main():
    db = Database()
    library = Library(db)

    menu = """
--- Library Management System ---
1. Add book
2. Remove book
3. Search books
4. List all books
5. Add member
6. List members
7. Checkout book
8. Return book
9. View active loans
10. View overdue loans
11. Quit
"""

    while True:
        print(menu)
        choice = input("Choose an option: ").strip()

        if choice == "1":
            title = input("Title: ")
            author = input("Author: ")
            isbn = input("ISBN: ")
            copies = int(input("Number of copies: "))
            library.add_book(title, author, isbn, copies)

        elif choice == "2":
            book_id = int(input("Book ID to remove: "))
            library.remove_book(book_id)

        elif choice == "3":
            keyword = input("Search keyword: ")
            print_books(library.search_books(keyword))

        elif choice == "4":
            print_books(library.list_books())

        elif choice == "5":
            name = input("Member name: ")
            email = input("Member email: ")
            library.add_member(name, email)

        elif choice == "6":
            print_members(library.list_members())

        elif choice == "7":
            book_id = int(input("Book ID: "))
            member_id = int(input("Member ID: "))
            library.checkout_book(book_id, member_id)

        elif choice == "8":
            loan_id = int(input("Loan ID: "))
            library.return_book(loan_id)

        elif choice == "9":
            print_loans(library.active_loans())

        elif choice == "10":
            print_loans(library.overdue_loans(), overdue=True)

        elif choice == "11":
            print("Goodbye!")
            break

        else:
            print("Invalid choice, try again.")


if __name__ == "__main__":
    main()

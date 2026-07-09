# Library Management System
A simple command-line Library Management System built with Python and SQLite. Manage books, members, and loans — including checkout/return tracking and automatic overdue fine calculation.
Features
Add, remove, and search books by title, author, or ISBN
Add and list members
Checkout and return books with due date tracking
Automatic fine calculation for overdue returns ($5/day)
View active loans
View overdue loans
Persistent storage using SQLite (`library.db`)
Requirements
Python 3.7+
No external dependencies (uses Python's built-in `sqlite3` module)
Installation
```bash
git clone https://github.com/your-username/library-management-system.git
cd library-management-system
```
Usage
Run the script:
```bash
python library_management_system.py
```
On first run, a `library.db` SQLite database file will be created automatically in the same folder.
You'll see a menu like this:
```
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
```
Follow the prompts to manage your library.
How It Works
Books are stored with title, author, ISBN, total copies, and available copies.
Members are stored with name and email.
Loans link a book and a member, with checkout date, due date, and return date.
Checking out a book reduces its available copies and creates a loan with a due date 14 days from checkout.
Returning a book increases available copies and calculates a fine if returned after the due date.
Configuration
You can adjust these constants at the top of the script:
```python
LOAN_DAYS = 14        # Number of days before a book is due
FINE_PER_DAY = 5      # Fine charged per day overdue
```
Database Schema
books
Column	Type
id	INTEGER
title	TEXT
author	TEXT
isbn	TEXT
copies	INTEGER
available	INTEGER
members
Column	Type
id	INTEGER
name	TEXT
email	TEXT
loans
Column	Type
id	INTEGER
book_id	INTEGER
member_id	INTEGER
checkout_date	TEXT
due_date	TEXT
return_date	TEXT
License
This project is open source and available under the MIT License.
Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you'd like to change.


import sqlite3
import heapq
from datetime import datetime
from collections import defaultdict

# ==========================================
# DATABASE CONNECTION AND INITIALIZATION
# ==========================================

conn = sqlite3.connect("expenses.db")
cursor = conn.cursor()


def initialize_database():

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        amount REAL,
        category TEXT,
        date TEXT,
        description TEXT
    )
    """)

    cursor.execute("PRAGMA table_info(expenses)")
    columns = [column[1] for column in cursor.fetchall()]

    # Add missing columns if necessary
    required_columns = {
        "title": "TEXT",
        "amount": "REAL",
        "category": "TEXT",
        "date": "TEXT",
        "description": "TEXT"
    }

    for column, data_type in required_columns.items():
        if column not in columns:
            cursor.execute(
                f"ALTER TABLE expenses ADD COLUMN "
                f"{column} {data_type}"
            )

    conn.commit()


initialize_database()


# ==========================================
# INPUT VALIDATION
# ==========================================

def get_amount():

    while True:
        try:
            amount = float(input("Enter amount: ₹"))

            if amount <= 0:
                print("Amount must be greater than zero.")
                continue

            return amount

        except ValueError:
            print("Please enter a valid amount.")


def get_date():

    while True:

        date = input(
            "Enter date (YYYY-MM-DD) "
            "or press Enter for today: "
        ).strip()

        if date == "":
            return datetime.now().strftime("%Y-%m-%d")

        try:
            datetime.strptime(date, "%Y-%m-%d")
            return date

        except ValueError:
            print("Invalid date format. Please try again.")


# ==========================================
# 1. ADD EXPENSE
# ==========================================

def add_expense():

    print("\n========== ADD EXPENSE ==========")

    title = input("Enter expense name: ").strip()

    if not title:
        print("Expense name cannot be empty.")
        return

    amount = get_amount()

    category = input("Enter category: ").strip()

    if not category:
        print("Category cannot be empty.")
        return

    date = get_date()

    description = input("Enter description: ").strip()

    cursor.execute("""
        INSERT INTO expenses
        (title, amount, category, date, description)
        VALUES (?, ?, ?, ?, ?)
    """, (title, amount, category, date, description))

    conn.commit()

    print("\nExpense added successfully!")


# ==========================================
# 2. VIEW ALL EXPENSES
# ==========================================

def view_expenses():

    print("\n========== ALL EXPENSES ==========")

    cursor.execute(
        "SELECT * FROM expenses ORDER BY id"
    )

    expenses = cursor.fetchall()

    if not expenses:
        print("No expenses found.")
        return

    print("-" * 95)

    print(
        f"{'ID':<5}"
        f"{'Title':<20}"
        f"{'Amount':<12}"
        f"{'Category':<18}"
        f"{'Date':<15}"
        f"{'Description'}"
    )

    print("-" * 95)

    for expense in expenses:

        print(
            f"{expense[0]:<5}"
            f"{str(expense[1] or ''):<20}"
            f"₹{(expense[2] or 0):<11.2f}"
            f"{str(expense[3] or ''):<18}"
            f"{str(expense[4] or ''):<15}"
            f"{expense[5] or ''}"
        )

    print("-" * 95)


# ==========================================
# 3. UPDATE EXPENSE
# ==========================================

def update_expense():

    print("\n========== UPDATE EXPENSE ==========")

    view_expenses()

    try:
        expense_id = int(
            input("\nEnter expense ID to update: ")
        )

    except ValueError:
        print("Invalid ID.")
        return

    cursor.execute(
        "SELECT * FROM expenses WHERE id = ?",
        (expense_id,)
    )

    expense = cursor.fetchone()

    if not expense:
        print("Expense not found.")
        return

    print("\nPress Enter to keep the existing value.")

    title = input(
        f"New title [{expense[1]}]: "
    ).strip()

    amount_input = input(
        f"New amount [{expense[2]}]: "
    ).strip()

    category = input(
        f"New category [{expense[3]}]: "
    ).strip()

    date = input(
        f"New date [{expense[4]}]: "
    ).strip()

    description = input(
        f"New description [{expense[5]}]: "
    ).strip()

    if not title:
        title = expense[1]

    if amount_input:

        try:
            amount = float(amount_input)

            if amount <= 0:
                print("Amount must be greater than zero.")
                return

        except ValueError:
            print("Invalid amount.")
            return

    else:
        amount = expense[2]

    if not category:
        category = expense[3]

    if not date:
        date = expense[4]

    else:

        try:
            datetime.strptime(date, "%Y-%m-%d")

        except ValueError:
            print("Invalid date format.")
            return

    if not description:
        description = expense[5]

    cursor.execute("""
        UPDATE expenses
        SET title = ?,
            amount = ?,
            category = ?,
            date = ?,
            description = ?
        WHERE id = ?
    """, (
        title,
        amount,
        category,
        date,
        description,
        expense_id
    ))

    conn.commit()

    print("\nExpense updated successfully!")


# ==========================================
# 4. DELETE EXPENSE
# ==========================================

def delete_expense():

    print("\n========== DELETE EXPENSE ==========")

    view_expenses()

    try:
        expense_id = int(
            input("\nEnter expense ID to delete: ")
        )

    except ValueError:
        print("Invalid ID.")
        return

    cursor.execute(
        "SELECT * FROM expenses WHERE id = ?",
        (expense_id,)
    )

    expense = cursor.fetchone()

    if not expense:
        print("Expense not found.")
        return

    confirm = input(
        f"Delete '{expense[1]}'? (yes/no): "
    ).strip().lower()

    if confirm == "yes":

        cursor.execute(
            "DELETE FROM expenses WHERE id = ?",
            (expense_id,)
        )

        conn.commit()

        print("Expense deleted successfully!")

    else:
        print("Deletion cancelled.")


# ==========================================
# 5. SEARCH EXPENSE
# ==========================================

def search_expense():

    print("\n========== SEARCH EXPENSE ==========")

    keyword = input(
        "Enter title or category to search: "
    ).strip()

    cursor.execute("""
        SELECT * FROM expenses
        WHERE title LIKE ? OR category LIKE ?
        ORDER BY id
    """, (
        "%" + keyword + "%",
        "%" + keyword + "%"
    ))

    results = cursor.fetchall()

    if not results:
        print("No matching expenses found.")
        return

    print("\nSearch Results:")

    for expense in results:

        print(
            f"\nID: {expense[0]}"
            f"\nTitle: {expense[1]}"
            f"\nAmount: ₹{expense[2]:.2f}"
            f"\nCategory: {expense[3]}"
            f"\nDate: {expense[4]}"
            f"\nDescription: {expense[5]}"
        )


# ==========================================
# 6. SORT EXPENSES
# ==========================================

def sort_expenses():

    print("\n========== SORT EXPENSES ==========")

    print("1. Amount - Low to High")
    print("2. Amount - High to Low")
    print("3. Date - Oldest First")
    print("4. Date - Newest First")

    choice = input("Enter choice: ").strip()

    sorting_options = {
        "1": "amount ASC",
        "2": "amount DESC",
        "3": "date ASC",
        "4": "date DESC"
    }

    if choice not in sorting_options:
        print("Invalid choice.")
        return

    query = (
        "SELECT * FROM expenses ORDER BY "
        + sorting_options[choice]
    )

    cursor.execute(query)

    results = cursor.fetchall()

    if not results:
        print("No expenses available.")
        return

    print("\nSorted Expenses:")

    for expense in results:

        print(
            f"ID: {expense[0]} | "
            f"{expense[1]} | "
            f"₹{expense[2]:.2f} | "
            f"{expense[3]} | "
            f"{expense[4]}"
        )


# ==========================================
# 7. TOTAL EXPENSE ANALYSIS
# ==========================================

def total_expenses():

    print("\n========== EXPENSE SUMMARY ==========")

    cursor.execute("""
        SELECT COUNT(*), SUM(amount)
        FROM expenses
    """)

    count, total = cursor.fetchone()

    total = total or 0

    print("Total number of expenses:", count)

    print(
        f"Total money spent: ₹{total:.2f}"
    )


# ==========================================
# 8. CATEGORY ANALYSIS
# HASH MAP USING DICTIONARY
# ==========================================

def category_analysis():

    print("\n========== CATEGORY ANALYSIS ==========")

    cursor.execute("""
        SELECT category, amount
        FROM expenses
    """)

    records = cursor.fetchall()

    if not records:
        print("No expenses available.")
        return

    category_totals = defaultdict(float)

    for category, amount in records:

        category_totals[category] += amount

    print("\nSpending by Category:")

    for category, amount in sorted(
        category_totals.items()
    ):

        print(
            f"{category:<20} ₹{amount:.2f}"
        )


# ==========================================
# 9. TOP 5 SPENDING CATEGORIES
# HEAP DATA STRUCTURE
# ==========================================

def top_categories():

    print("\n========== TOP 5 CATEGORIES ==========")

    cursor.execute("""
        SELECT category, amount
        FROM expenses
    """)

    records = cursor.fetchall()

    if not records:
        print("No expenses available.")
        return

    category_totals = defaultdict(float)

    for category, amount in records:

        category_totals[category] += amount

    top_five = heapq.nlargest(
        5,
        category_totals.items(),
        key=lambda item: item[1]
    )

    print("\nHighest Spending Categories:")

    for rank, (category, amount) in enumerate(
        top_five, 1
    ):

        print(
            f"{rank}. {category} - ₹{amount:.2f}"
        )


# ==========================================
# 10. MONTHLY EXPENSE REPORT
# ==========================================

def monthly_report():

    print("\n========== MONTHLY REPORT ==========")

    month = input(
        "Enter month (YYYY-MM): "
    ).strip()

    try:
        datetime.strptime(month, "%Y-%m")

    except ValueError:
        print("Invalid month format.")
        return

    cursor.execute("""
        SELECT title, amount, category, date
        FROM expenses
        WHERE date LIKE ?
        ORDER BY date
    """, (month + "%",))

    results = cursor.fetchall()

    if not results:
        print("No expenses found for this month.")
        return

    total = 0

    print("\nMonthly Expense Details:")

    for title, amount, category, date in results:

        print(
            f"{date} | {title} | "
            f"{category} | ₹{amount:.2f}"
        )

        total += amount

    print("-" * 45)

    print(
        f"Total expenses for {month}: ₹{total:.2f}"
    )


# ==========================================
# MAIN MENU
# ==========================================

def main():

    while True:

        print("\n")
        print("=" * 45)

        print("       EXPENSE ANALYTICS SYSTEM")

        print("=" * 45)

        print("1.  Add Expense")
        print("2.  View All Expenses")
        print("3.  Update Expense")
        print("4.  Delete Expense")
        print("5.  Search Expense")
        print("6.  Sort Expenses")
        print("7.  Total Expense Summary")
        print("8.  Category Analysis")
        print("9.  Top 5 Spending Categories")
        print("10. Monthly Expense Report")
        print("0.  Exit")

        print("=" * 45)

        choice = input(
            "Enter your choice: "
        ).strip()

        if choice == "1":
            add_expense()

        elif choice == "2":
            view_expenses()

        elif choice == "3":
            update_expense()

        elif choice == "4":
            delete_expense()

        elif choice == "5":
            search_expense()

        elif choice == "6":
            sort_expenses()

        elif choice == "7":
            total_expenses()

        elif choice == "8":
            category_analysis()

        elif choice == "9":
            top_categories()

        elif choice == "10":
            monthly_report()

        elif choice == "0":

            print(
                "\nThank you for using "
                "Expense Analytics System!"
            )

            break

        else:
            print("Invalid choice. Please try again.")


# ==========================================
# PROGRAM EXECUTION
# ==========================================

if __name__ == "__main__":

    try:
        main()

    except KeyboardInterrupt:
        print("\nProgram interrupted.")

    finally:
        conn.close()
        print("Database connection closed.")

import sqlite3
from datetime import datetime, timedelta

# -----------------------------
# Database Setup
# -----------------------------
conn = sqlite3.connect("payroll.db")
cursor = conn.cursor()

# Employees table
cursor.execute('''CREATE TABLE IF NOT EXISTS Employees (
    emp_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    designation TEXT,
    department TEXT,
    basic_salary REAL
)''')

# Attendance table
cursor.execute('''CREATE TABLE IF NOT EXISTS Attendance (
    att_id INTEGER PRIMARY KEY AUTOINCREMENT,
    emp_id INTEGER,
    date TEXT,
    status TEXT CHECK(status IN ('Present','Absent','Half-day')),
    FOREIGN KEY(emp_id) REFERENCES Employees(emp_id)
)''')

# Leave table
cursor.execute('''CREATE TABLE IF NOT EXISTS Leaves (
    leave_id INTEGER PRIMARY KEY AUTOINCREMENT,
    emp_id INTEGER,
    start_date TEXT,
    end_date TEXT,
    reason TEXT,
    status TEXT CHECK(status IN ('Pending','Approved','Rejected')) DEFAULT 'Pending',
    FOREIGN KEY(emp_id) REFERENCES Employees(emp_id)
)''')

# Payroll table
cursor.execute('''CREATE TABLE IF NOT EXISTS Payroll (
    payroll_id INTEGER PRIMARY KEY AUTOINCREMENT,
    emp_id INTEGER,
    month TEXT,
    basic_salary REAL,
    allowances REAL,
    deductions REAL,
    net_salary REAL,
    generated_at TEXT,
    FOREIGN KEY(emp_id) REFERENCES Employees(emp_id)
)''')

conn.commit()

# -----------------------------
# EMPLOYEE MANAGEMENT
# -----------------------------
def add_employee():
    name = input("Enter Name: ")
    designation = input("Enter Designation: ")
    department = input("Enter Department: ")
    basic_salary = float(input("Enter Basic Salary: "))
    cursor.execute("INSERT INTO Employees (name, designation, department, basic_salary) VALUES (?, ?, ?, ?)",
                   (name, designation, department, basic_salary))
    conn.commit()
    print("✅ Employee added")

def view_employees():
    cursor.execute("SELECT * FROM Employees")
    for emp in cursor.fetchall():
        print(emp)

def update_employee():
    view_employees()
    emp_id = int(input("Enter Employee ID to update: "))
    name = input("New Name: ")
    designation = input("New Designation: ")
    department = input("New Department: ")
    basic_salary = float(input("New Basic Salary: "))
    cursor.execute("UPDATE Employees SET name=?, designation=?, department=?, basic_salary=? WHERE emp_id=?",
                   (name, designation, department, basic_salary, emp_id))
    conn.commit()
    print("✅ Employee updated")

def delete_employee():
    view_employees()
    emp_id = int(input("Enter Employee ID to delete: "))
    cursor.execute("DELETE FROM Employees WHERE emp_id=?", (emp_id,))
    cursor.execute("DELETE FROM Attendance WHERE emp_id=?", (emp_id,))
    cursor.execute("DELETE FROM Leaves WHERE emp_id=?", (emp_id,))
    cursor.execute("DELETE FROM Payroll WHERE emp_id=?", (emp_id,))
    conn.commit()
    print("✅ Employee deleted")

# -----------------------------
# ATTENDANCE MANAGEMENT
# -----------------------------
def mark_attendance():
    view_employees()
    emp_id = int(input("Enter Employee ID: "))
    date = input("Enter Date (YYYY-MM-DD): ")
    status = input("Enter Status (Present/Absent/Half-day): ")
    cursor.execute("INSERT INTO Attendance (emp_id, date, status) VALUES (?, ?, ?)", (emp_id, date, status))
    conn.commit()
    print("✅ Attendance marked")

def view_attendance():
    cursor.execute('''SELECT a.att_id, e.name, a.date, a.status
                      FROM Attendance a
                      JOIN Employees e ON a.emp_id = e.emp_id''')
    for row in cursor.fetchall():
        print(row)

# -----------------------------
# LEAVE MANAGEMENT
# -----------------------------
def apply_leave():
    view_employees()
    emp_id = int(input("Enter Employee ID: "))
    start_date = input("Start Date (YYYY-MM-DD): ")
    end_date = input("End Date (YYYY-MM-DD): ")
    reason = input("Reason: ")
    cursor.execute("INSERT INTO Leaves (emp_id, start_date, end_date, reason) VALUES (?, ?, ?, ?)",
                   (emp_id, start_date, end_date, reason))
    conn.commit()
    print("✅ Leave Applied")

def view_leaves():
    cursor.execute('''SELECT l.leave_id, e.name, l.start_date, l.end_date, l.reason, l.status
                      FROM Leaves l
                      JOIN Employees e ON l.emp_id = e.emp_id''')
    for row in cursor.fetchall():
        print(row)

def approve_leave():
    view_leaves()
    leave_id = int(input("Enter Leave ID to Approve: "))
    cursor.execute("UPDATE Leaves SET status='Approved' WHERE leave_id=?", (leave_id,))
    conn.commit()
    print("✅ Leave Approved")

def reject_leave():
    view_leaves()
    leave_id = int(input("Enter Leave ID to Reject: "))
    cursor.execute("UPDATE Leaves SET status='Rejected' WHERE leave_id=?", (leave_id,))
    conn.commit()
    print("❌ Leave Rejected")

# -----------------------------
# PAYROLL MANAGEMENT
# -----------------------------
def generate_payroll():
    month = input("Enter Month (YYYY-MM): ")
    view_employees()
    emp_id = int(input("Enter Employee ID for Payroll: "))

    # Get basic salary
    cursor.execute("SELECT basic_salary FROM Employees WHERE emp_id=?", (emp_id,))
    basic_salary = cursor.fetchone()[0]

    # Count absents & half-days
    cursor.execute('''SELECT status FROM Attendance 
                      WHERE emp_id=? AND date LIKE ?''', (emp_id, month+'%'))
    records = cursor.fetchall()
    absent_days = sum(1 for r in records if r[0] == "Absent")
    half_days = sum(1 for r in records if r[0] == "Half-day")

    # Simple calculation
    deductions = absent_days * (basic_salary/30) + half_days * (basic_salary/30)/2
    allowances = basic_salary * 0.1  # 10% allowance
    net_salary = basic_salary + allowances - deductions
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute('''INSERT INTO Payroll (emp_id, month, basic_salary, allowances, deductions, net_salary, generated_at)
                      VALUES (?, ?, ?, ?, ?, ?, ?)''',
                   (emp_id, month, basic_salary, allowances, deductions, net_salary, generated_at))
    conn.commit()
    print(f"✅ Payroll generated. Net Salary: {net_salary:.2f}")

def view_payroll():
    cursor.execute('''SELECT p.payroll_id, e.name, p.month, p.basic_salary, p.allowances, p.deductions, p.net_salary, p.generated_at
                      FROM Payroll p
                      JOIN Employees e ON p.emp_id = e.emp_id''')
    for row in cursor.fetchall():
        print(row)

def search_employee_by_department():
    department = input("Enter Department: ")
    cursor.execute("SELECT * FROM Employees WHERE department=?", (department,))
    for row in cursor.fetchall():
        print(row)

# -----------------------------
# MAIN MENU
# -----------------------------
def menu():
    while True:
        print("\n--- Employee Payroll Management ---")
        print("1. Manage Employees")
        print("2. Attendance")
        print("3. Leaves")
        print("4. Payroll")
        print("5. Reports/Search")
        print("6. Exit")
        choice = input("Enter choice: ")

        if choice == "1":
            print("a. Add Employee\nb. View Employees\nc. Update Employee\nd. Delete Employee")
            sub = input("Choice: ")
            if sub == "a": add_employee()
            elif sub == "b": view_employees()
            elif sub == "c": update_employee()
            elif sub == "d": delete_employee()
        elif choice == "2":
            print("a. Mark Attendance\nb. View Attendance")
            sub = input("Choice: ")
            if sub == "a": mark_attendance()
            elif sub == "b": view_attendance()
        elif choice == "3":
            print("a. Apply Leave\nb. View Leaves\nc. Approve Leave\nd. Reject Leave")
            sub = input("Choice: ")
            if sub == "a": apply_leave()
            elif sub == "b": view_leaves()
            elif sub == "c": approve_leave()
            elif sub == "d": reject_leave()
        elif choice == "4":
            print("a. Generate Payroll\nb. View Payroll")
            sub = input("Choice: ")
            if sub == "a": generate_payroll()
            elif sub == "b": view_payroll()
        elif choice == "5":
            print("a. Search Employee by Department")
            sub = input("Choice: ")
            if sub == "a": search_employee_by_department()
        elif choice == "6":
            print("Exiting...")
            break
        else:
            print("❌ Invalid Choice")

# -----------------------------
# RUN SYSTEM
# -----------------------------
if __name__ == "__main__":
    menu()

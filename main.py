
import csv
import os

EMPLOYEE_FILE = "employees.csv"


class Employee:
    def __init__(
        self, emp_id, name, basic_salary, allowances, deductions
    ):
        self.emp_id = emp_id
        self.name = name
        self.basic_salary = basic_salary
        self.allowances = allowances
        self.deductions = deductions

    def calculate_final_salary(self):
        return self.basic_salary + self.allowances - self.deductions

    def display(self):
        print(
            f"{self.emp_id:<12} {self.name:<20} "
            f"{self.basic_salary:>12.2f} "
            f"{self.allowances:>12.2f} "
            f"{self.deductions:>12.2f} "
            f"{self.calculate_final_salary():>12.2f}"
        )


def create_csv():
    if not os.path.exists(EMPLOYEE_FILE):
        with open(EMPLOYEE_FILE, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([
                "emp_id", "name", "basic_salary",
                "allowances", "deductions", "final_salary"
            ])


def load_employees():
    employees = []

    create_csv()

    with open(EMPLOYEE_FILE, "r", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            employees.append(
                Employee(
                    row["emp_id"],
                    row["name"],
                    float(row["basic_salary"]),
                    float(row["allowances"]),
                    float(row["deductions"])
                )
            )

    return employees


def save_employees(employees):
    with open(EMPLOYEE_FILE, "w", newline="") as file:
        fields = [
            "emp_id", "name", "basic_salary",
            "allowances", "deductions", "final_salary"
        ]

        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()

        for emp in employees:
            writer.writerow({
                "emp_id": emp.emp_id,
                "name": emp.name,
                "basic_salary": emp.basic_salary,
                "allowances": emp.allowances,
                "deductions": emp.deductions,
                "final_salary": emp.calculate_final_salary()
            })


def add_employee():
    employees = load_employees()

    print("\n--- Add New Employee ---")

    emp_id = input("Enter employee ID: ").strip()

    if not emp_id:
        print("Employee ID cannot be empty.")
        return

    if any(emp.emp_id == emp_id for emp in employees):
        print("This employee ID already exists.")
        return

    name = input("Enter employee name: ").strip()

    if not name:
        print("Employee name cannot be empty.")
        return

    try:
        basic = float(input("Enter basic salary: "))
        allowances = float(input("Enter allowances: "))
        deductions = float(input("Enter deductions: "))

        if basic < 0 or allowances < 0 or deductions < 0:
            print("Salary amounts cannot be negative.")
            return

        if deductions > basic + allowances:
            print("Deductions cannot exceed basic salary plus allowances.")
            return

    except ValueError:
        print("Please enter valid numeric salary amounts.")
        return

    employee = Employee(emp_id, name, basic, allowances, deductions)
    employees.append(employee)
    save_employees(employees)

    print(f"\nEmployee saved successfully!")
    print(f"Final salary: Rs. {employee.calculate_final_salary():,.2f}")


def view_employees():
    employees = load_employees()

    if not employees:
        print("\nNo employees found.")
        return

    print("\n--- Employee Salary Records ---")
    print(
        f"{'ID':<12} {'Name':<20} {'Basic':>12} "
        f"{'Allowance':>12} {'Deduction':>12} {'Final Salary':>12}"
    )
    print("-" * 82)

    for emp in employees:
        emp.display()


def search_employee():
    employees = load_employees()
    emp_id = input("Enter employee ID to search: ").strip()

    for emp in employees:
        if emp.emp_id.lower() == emp_id.lower():
            print("\nEmployee found:")
            print(
                f"{'ID':<12} {'Name':<20} {'Basic':>12} "
                f"{'Allowance':>12} {'Deduction':>12} {'Final Salary':>12}"
            )
            emp.display()
            return

    print("Employee not found.")


def sort_by_salary():
    employees = load_employees()

    # Sorting algorithm: Bubble Sort
    n = len(employees)

    for i in range(n):
        for j in range(0, n - i - 1):
            if (
                employees[j].calculate_final_salary()
                > employees[j + 1].calculate_final_salary()
            ):
                employees[j], employees[j + 1] = (
                    employees[j + 1], employees[j]
                )

    print("\n--- Employees Sorted by Final Salary ---")

    for emp in employees:
        print(
            emp.emp_id, emp.name,
            f"Rs. {emp.calculate_final_salary():,.2f}"
        )


def main():
    create_csv()

    while True:
        print("\n======================================")
        print(" EMPLOYEE FINANCIAL MANAGEMENT SYSTEM")
        print("======================================")
        print("1. Add Employee")
        print("2. View All Employees")
        print("3. Search Employee")
        print("4. Sort by Final Salary")
        print("5. Exit")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            add_employee()
        elif choice == "2":
            view_employees()
        elif choice == "3":
            search_employee()
        elif choice == "4":
            sort_by_salary()
        elif choice == "5":
            print("Thank you for using the system!")
            break
        else:
            print("Invalid choice. Please select 1 to 5.")


if __name__ == "__main__":
    main()

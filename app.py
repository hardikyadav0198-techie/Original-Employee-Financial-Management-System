
import csv
from pathlib import Path

import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).parent
CSV_FILE = BASE_DIR / "employees.csv"

COLUMNS = [
    "emp_id",
    "name",
    "basic_salary",
    "allowances",
    "deductions",
    "final_salary",
]


def load_employees():
    if not CSV_FILE.exists():
        return pd.DataFrame(columns=COLUMNS)

    try:
        df = pd.read_csv(CSV_FILE, dtype={"emp_id": str})
        for column in COLUMNS:
            if column not in df.columns:
                df[column] = "" if column in ["emp_id", "name"] else 0

        for column in COLUMNS[2:]:
            df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0)

        return df[COLUMNS]
    except (pd.errors.EmptyDataError, pd.errors.ParserError):
        return pd.DataFrame(columns=COLUMNS)


def save_employees(df):
    df.to_csv(CSV_FILE, index=False)


st.set_page_config(
    page_title="Employee Financial Management",
    page_icon="💼",
    layout="wide",
)

st.title("💼 Employee Financial Management System")
st.caption("Manage employee records, calculate salaries, and view payroll analytics.")

df = load_employees()

total_employees = len(df)
total_payroll = df["final_salary"].sum()
average_salary = df["final_salary"].mean() if total_employees else 0
highest_salary = df["final_salary"].max() if total_employees else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Employees", total_employees)
c2.metric("Total Payroll", f"₹{total_payroll:,.2f}")
c3.metric("Average Salary", f"₹{average_salary:,.2f}")
c4.metric("Highest Salary", f"₹{highest_salary:,.2f}")

st.divider()

tab1, tab2, tab3 = st.tabs(
    ["Employee Records", "Add Employee", "Salary Analytics"]
)

with tab1:
    st.subheader("Employee Records")

    if df.empty:
        st.info("No employees found. Use the Add Employee tab to get started.")
    else:
        search = st.text_input("Search by employee ID or name")

        filtered = df[
            df["emp_id"].astype(str).str.contains(search, case=False, na=False)
            | df["name"].astype(str).str.contains(search, case=False, na=False)
        ]

        st.dataframe(
            filtered,
            use_container_width=True,
            hide_index=True,
            column_config={
                "basic_salary": st.column_config.NumberColumn(
                    "Basic Salary", format="₹%.2f"
                ),
                "allowances": st.column_config.NumberColumn(
                    "Allowances", format="₹%.2f"
                ),
                "deductions": st.column_config.NumberColumn(
                    "Deductions", format="₹%.2f"
                ),
                "final_salary": st.column_config.NumberColumn(
                    "Final Salary", format="₹%.2f"
                ),
            },
        )

        st.download_button(
            "Download employee records as CSV",
            data=filtered.to_csv(index=False).encode("utf-8"),
            file_name="employee_records.csv",
            mime="text/csv",
        )

with tab2:
    st.subheader("Add a New Employee")

    with st.form("employee_form", clear_on_submit=True):
        emp_id = st.text_input("Employee ID").strip()
        name = st.text_input("Employee Name").strip()

        col1, col2, col3 = st.columns(3)
        basic = col1.number_input("Basic Salary (₹)", min_value=0.0, step=1000.0)
        allowance = col2.number_input("Allowances (₹)", min_value=0.0, step=500.0)
        deduction = col3.number_input("Deductions (₹)", min_value=0.0, step=500.0)

        submitted = st.form_submit_button("Save Employee", type="primary")

        if submitted:
            if not emp_id or not name:
                st.error("Please enter both employee ID and name.")
            elif df["emp_id"].astype(str).str.lower().eq(emp_id.lower()).any():
                st.error("This employee ID already exists.")
            elif deduction > basic + allowance:
                st.error("Deductions cannot exceed basic salary plus allowances.")
            else:
                final_salary = basic + allowance - deduction

                new_employee = pd.DataFrame([{
                    "emp_id": emp_id,
                    "name": name,
                    "basic_salary": basic,
                    "allowances": allowance,
                    "deductions": deduction,
                    "final_salary": final_salary,
                }])

                updated = pd.concat([df, new_employee], ignore_index=True)

                try:
                    save_employees(updated)
                    st.success(
                        f"Employee saved! Final salary: ₹{final_salary:,.2f}"
                    )
                    st.rerun()
                except OSError:
                    st.error("Could not save the CSV file. Please try again.")

with tab3:
    st.subheader("Salary Analytics")

    if df.empty:
        st.info("Add employees to see salary analytics.")
    else:
        chart_df = df.sort_values("final_salary", ascending=False)

        st.write("**Final salary by employee**")
        st.bar_chart(
            chart_df.set_index("name")[["final_salary"]],
            y_label="Salary (₹)",
        )

        st.write("**Salary component comparison**")
        components = df[
            ["basic_salary", "allowances", "deductions"]
        ].sum()

        st.bar_chart(components, y_label="Total amount (₹)")

        st.write("**Top 5 highest-paid employees**")
        st.dataframe(
            chart_df.head(5)[["emp_id", "name", "final_salary"]],
            use_container_width=True,
            hide_index=True,
        )

st.divider()
st.caption("Employee Financial Management System | Python + Streamlit + CSV")

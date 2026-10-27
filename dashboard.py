
import csv
import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

from dsa import highest_paid_employees, sort_by_salary, SalaryTree

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, "employees.csv")
PORT = 8000


def load_employees():
    employees = []

    if not os.path.exists(CSV_FILE):
        return employees

    with open(CSV_FILE, newline="", encoding="utf-8") as file:
        for row in csv.DictReader(file):
            try:
                basic = float(row["basic_salary"])
                allowance = float(row["allowances"])
                deduction = float(row["deductions"])

                employees.append({
                    "emp_id": row["emp_id"],
                    "name": row["name"],
                    "basic_salary": basic,
                    "allowances": allowance,
                    "deductions": deduction,
                    "final_salary": basic + allowance - deduction
                })
            except (ValueError, KeyError):
                continue

    return employees


def money(amount):
    return "₹{:,.2f}".format(amount)


def make_page():
    employees = load_employees()
    total = len(employees)
    payroll = sum(e["final_salary"] for e in employees)
    average = payroll / total if total else 0
    highest = max(employees, key=lambda e: e["final_salary"], default=None)

    # Visualize salary comparisons with plain JavaScript.
    salary_data = [
        {"name": e["name"], "salary": e["final_salary"]}
        for e in employees
    ]

    departments = {"All Employees": total}
    top_five = sorted(
        employees, key=lambda e: e["final_salary"], reverse=True
    )[:5]

    rows = ""
    for e in employees:
        rows += f"""
        <tr>
          <td>{e['emp_id']}</td>
          <td>{e['name']}</td>
          <td>{money(e['basic_salary'])}</td>
          <td>{money(e['allowances'])}</td>
          <td>{money(e['deductions'])}</td>
          <td class="salary">{money(e['final_salary'])}</td>
        </tr>"""

    top_rows = ""
    for e in top_five:
        top_rows += f"""
        <tr>
          <td>{e['emp_id']}</td>
          <td>{e['name']}</td>
          <td>{money(e['final_salary'])}</td>
        </tr>"""

    highest_name = highest["name"] if highest else "No employees yet"
    highest_salary = money(highest["final_salary"]) if highest else "₹0.00"

    page = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Employee Financial Management</title>
<style>
:root {
  --bg: #f3f6fc;
  --card: #ffffff;
  --ink: #192641;
  --muted: #64748b;
  --accent: #3659d9;
  --line: #e4eaf4;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: Arial, Helvetica, sans-serif;
  color: var(--ink);
  background: var(--bg);
}
header {
  padding: 28px 5%;
  color: white;
  background: linear-gradient(120deg, #14294f, #3659d9);
}
header h1 { margin: 0 0 8px; font-size: 27px; }
header p { margin: 0; color: #dbe6ff; }
main { max-width: 1250px; margin: auto; padding: 28px 4%; }
.cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
  gap: 17px;
}
.card, .panel {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 15px;
  padding: 22px;
  box-shadow: 0 5px 20px #182b4b0a;
}
.card .label { color: var(--muted); font-size: 14px; }
.card .value { font-size: 25px; font-weight: 700; margin-top: 12px; }
.card .note { font-size: 12px; color: var(--muted); margin-top: 8px; }
.panel { margin-top: 22px; }
.panel h2 { margin: 0 0 17px; font-size: 19px; }
.tools { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 17px; }
input, select, button {
  padding: 11px 13px;
  border: 1px solid var(--line);
  border-radius: 8px;
  font-size: 14px;
}
input { flex: 1; min-width: 190px; }
button { cursor: pointer; background: var(--accent); color: white; border: none; }
button.secondary { background: #e9eeff; color: #243e9b; }
.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; white-space: nowrap; }
th, td { padding: 13px 12px; border-bottom: 1px solid var(--line); text-align: left; }
th { color: var(--muted); background: #f8faff; font-size: 12px; text-transform: uppercase; }
td { font-size: 13px; }
.salary { color: #16784b; font-weight: 700; }
.chart-row { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.bar-item { margin: 15px 0; }

/* Compact financial charts */
.mini-chart-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-top: 20px;
}

.mini-chart-row .panel {
  margin-top: 0;
  min-width: 0;
}

.donut-layout {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 22px;
  flex-wrap: wrap;
  padding: 10px 0;
}

.donut {
  width: 145px;
  height: 145px;
  border-radius: 50%;
  flex-shrink: 0;
  position: relative;
}

.donut::after {
  content: "";
  position: absolute;
  inset: 30px;
  background: white;
  border-radius: 50%;
}

.donut-legend {
  display: grid;
  gap: 12px;
  min-width: 130px;
}

.legend-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  font-size: 12px;
}

.legend-dot {
  width: 10px;
  height: 10px;
  margin-top: 3px;
  border-radius: 3px;
  flex-shrink: 0;
}

.legend-value {
  display: block;
  color: #64748b;
  margin-top: 3px;
}

@media(max-width:700px) {
  .mini-chart-row {
    grid-template-columns: 1fr;
  }

  .donut {
    width: 125px;
    height: 125px;
  }
}

.bar-label { display: flex; justify-content: space-between; gap: 12px; font-size: 12px; margin-bottom: 6px; }
.bar-track { background: #eaf0ff; height: 12px; border-radius: 20px; overflow: hidden; }
.bar-fill { background: linear-gradient(90deg, #5279f5, #38b9a1); height: 100%; border-radius: 20px; }
.chart-scroll { max-height: 400px; overflow-y: auto; }
footer { text-align: center; padding: 28px; color: var(--muted); font-size: 12px; }
@media(max-width:700px) {
  .chart-row { grid-template-columns: 1fr; }
  header h1 { font-size: 22px; }
}
</style>
</head>
<body>
<header>
  <h1>💼 Employee Financial Management</h1>
  <p>Salary overview · Payroll analytics · Employee records</p>
</header>
<main>
  <section class="cards">
    <div class="card">
      <div class="label">Total Employees</div>
      <div class="value">__TOTAL__</div>
      <div class="note">Employees in CSV records</div>
    </div>
    <div class="card">
      <div class="label">Total Payroll</div>
      <div class="value">__PAYROLL__</div>
      <div class="note">Combined final salary</div>
    </div>
    <div class="card">
      <div class="label">Average Final Salary</div>
      <div class="value">__AVERAGE__</div>
      <div class="note">Payroll divided by employee count</div>
    </div>
    <div class="card">
      <div class="label">Highest-Paid Employee</div>
      <div class="value" style="font-size:19px">__HIGHNAME__</div>
      <div class="note">Final salary: __HIGHSALARY__</div>
    </div>
  </section>

  <section class="chart-row">
    <div class="panel">
      <h2>📊 Salary Comparison</h2>
      <div id="salaryChart" class="chart-scroll"></div>
    </div>
    <div class="panel">
      <h2>💰 Salary Components</h2>
      <p style="color:#64748b;font-size:13px">
        Combined basic salary, allowances and deductions for all employees.
      </p>
      <div id="componentChart"></div>
      <h2 style="margin-top:24px">🏆 Highest-Paid Employees</h2>
      <div class="table-wrap">
        <table>
          <thead><tr><th>ID</th><th>Name</th><th>Final Salary</th></tr></thead>
          <tbody>__TOPROWS__</tbody>
        </table>
      </div>
    </div>
  </section>

  
<section class="mini-chart-row">
  <div class="panel">
    <h2>📊 Salary Range Distribution</h2>
    <p style="font-size:12px;color:#64748b">
      Number of employees in each salary bracket
    </p>
    <div id="salaryDistribution"></div>
  </div>

  <div class="panel">
    <h2>💰 Payroll Composition</h2>
    <p style="font-size:12px;color:#64748b">
      Share of basic salary, allowances and deductions
    </p>
    <div id="payrollComposition"></div>
  </div>
</section>

  <section class="panel">
    <h2>👥 Employee Salary Records</h2>
    <div class="tools">
      <input id="search" type="search" placeholder="Search by employee ID or name...">
      <select id="sort">
        <option value="original">Original order</option>
        <option value="asc">Final salary: low to high</option>
        <option value="desc">Final salary: high to low</option>
        <option value="name">Name: A to Z</option>
      </select>
      <button onclick="window.location.reload()" class="secondary">Refresh CSV data</button>
    </div>
    <div class="table-wrap">
      <table id="employeeTable">
        <thead>
          <tr>
            <th>Employee ID</th><th>Name</th><th>Basic Salary</th>
            <th>Allowances</th><th>Deductions</th><th>Final Salary</th>
          </tr>
        </thead>
        <tbody>__ROWS__</tbody>
      </table>
      <p id="count" style="color:#64748b;font-size:13px"></p>
    </div>
  </section>
</main>
<footer>Employee Financial Management System · Python + CSV + HTML/CSS/JavaScript</footer>
<script>
const salaryData = __SALARYDATA__;
const componentData = __COMPONENTDATA__;

const bandData = __BANDDATA__;

const chartColors = ["#5279f5", "#35b9a1", "#f5a623", "#8b70df"];

function drawDonut(elementId, items, valueKey) {
  const container = document.getElementById(elementId);
  const total = items.reduce((sum, item) => sum + item[valueKey], 0);

  if (!total) {
    container.textContent = "No data available yet.";
    return;
  }

  let current = 0;
  const segments = items.map((item, i) => {
    const start = current;
    current += item[valueKey] / total * 100;
    return `${chartColors[i % chartColors.length]} ${start}% ${current}%`;
  });

  const legend = items.map((item, i) => `
    <div class="legend-item">
      <span class="legend-dot"
        style="background:${chartColors[i % chartColors.length]}"></span>
      <span>${item.label}
        <strong class="legend-value">
          ${valueKey === "count" ? item[valueKey] + " employees"
            : formatMoney(item[valueKey])}
        </strong>
      </span>
    </div>
  `).join("");

  container.innerHTML = `
    <div class="donut-layout">
      <div class="donut"
        style="background:conic-gradient(${segments.join(",")})"></div>
      <div class="donut-legend">${legend}</div>
    </div>`;
}

drawDonut("salaryDistribution", bandData, "count");
drawDonut("payrollComposition", componentData, "value");


function formatMoney(value) {
  return "₹" + Number(value).toLocaleString("en-IN", {
    maximumFractionDigits: 2, minimumFractionDigits: 2
  });
}
function drawBars(containerId, items) {
  const container = document.getElementById(containerId);
  if (!items.length) {
    container.textContent = "Add employees to see financial charts.";
    return;
  }
  const max = Math.max(...items.map(x => x.value), 1);
  container.innerHTML = items.map(x => `
    <div class="bar-item">
      <div class="bar-label">
        <span>${x.label}</span><strong>${formatMoney(x.value)}</strong>
      </div>
      <div class="bar-track">
        <div class="bar-fill" style="width:${Math.max(0, x.value / max * 100)}%"></div>
      </div>
    </div>`).join("");
}
drawBars("salaryChart", salaryData.map(x => ({
  label: x.name + " (" + x.id + ")", value: x.salary
})));
drawBars("componentChart", componentData.map(x => ({
  label: x.label, value: x.value
})));

const table = document.getElementById("employeeTable");
const tbody = table.querySelector("tbody");
const originalRows = Array.from(tbody.querySelectorAll("tr"));
function updateTable() {
  const term = document.getElementById("search").value.toLowerCase();
  const sort = document.getElementById("sort").value;
  let rows = originalRows.filter(row =>
    row.cells[0].textContent.toLowerCase().includes(term) ||
    row.cells[1].textContent.toLowerCase().includes(term)
  );
  if (sort === "asc" || sort === "desc") {
    rows.sort((a,b) => {
      const x = parseFloat(a.cells[5].textContent.replace(/[₹,]/g, ""));
      const y = parseFloat(b.cells[5].textContent.replace(/[₹,]/g, ""));
      return sort === "asc" ? x-y : y-x;
    });
  } else if (sort === "name") {
    rows.sort((a,b) => a.cells[1].textContent.localeCompare(b.cells[1].textContent));
  }
  tbody.replaceChildren(...rows);
  document.getElementById("count").textContent =
    "Showing " + rows.length + " of " + originalRows.length + " employees.";
}
document.getElementById("search").addEventListener("input", updateTable);
document.getElementById("sort").addEventListener("change", updateTable);
updateTable();
</script>
</body>
</html>"""

    
    # Group employees into salary brackets
    salary_bands = [
        {"label": "Below ₹30,000", "min": 0, "max": 30000},
        {"label": "₹30,000–₹59,999", "min": 30000, "max": 60000},
        {"label": "₹60,000–₹89,999", "min": 60000, "max": 90000},
        {"label": "₹90,000+", "min": 90000, "max": float("inf")}
    ]

    band_data = []

    for band in salary_bands:
        count = sum(
            band["min"] <= e["final_salary"] < band["max"]
            for e in employees
        )
        band_data.append({
            "label": band["label"],
            "count": count
        })

    components = [
        {"label": "Basic Salary", "value": sum(e["basic_salary"] for e in employees)},
        {"label": "Allowances", "value": sum(e["allowances"] for e in employees)},
        {"label": "Deductions", "value": sum(e["deductions"] for e in employees)}
    ]

    replacements = {
        "__TOTAL__": str(total),
        "__PAYROLL__": money(payroll),
        "__AVERAGE__": money(average),
        "__HIGHNAME__": highest_name,
        "__HIGHSALARY__": highest_salary,
        "__ROWS__": rows or '<tr><td colspan="6">No employee records found.</td></tr>',
        "__TOPROWS__": top_rows or '<tr><td colspan="3">No records</td></tr>',
        "__SALARYDATA__": json.dumps([
            {"id": e["emp_id"], "name": e["name"], "salary": e["final_salary"]}
            for e in employees
        ]),
        "__COMPONENTDATA__": json.dumps(components),
"__BANDDATA__": json.dumps(band_data),
    }

    for key, value in replacements.items():
        page = page.replace(key, value)

    return page.encode("utf-8")


class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path

        if path == "/":
            content = make_page()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)

        elif path == "/api/employees":
            content = json.dumps(load_employees()).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)

        else:
            self.send_error(404, "Page not found")

    def log_message(self, format_string, *args):
        print("[Dashboard]", format_string % args)


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), DashboardHandler)
    print(f"Dashboard server running on port {PORT}")
    print("Open your Nimbus forwarded port 8000 URL in the browser.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDashboard server stopped.")
        server.server_close()

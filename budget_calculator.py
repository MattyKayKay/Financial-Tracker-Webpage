from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


def calc_take_home(salary: float, pension_percent: float, student_loan_plan: str):
    pension = round(salary * (pension_percent / 100.0), 2)
    taxable = max(0.0, salary - pension)

    # Simple UK-style approximations (adjust thresholds/rates as needed)
    personal_allowance = 12570.0
    basic_rate = 0.20
    income_tax = round(max(0.0, taxable - personal_allowance) * basic_rate, 2)

    # National Insurance (very simplified)
    ni_threshold = 12570.0
    ni_rate = 0.12
    national_insurance = round(max(0.0, taxable - ni_threshold) * ni_rate, 2)

    # Student loan approximations
    loan_rates = {
        "none": (1e12, 0.0),
        "plan1": (22130.0, 0.09),
        "plan2": (27295.0, 0.09),
        "plan4": (25000.0, 0.09),
        "pgl": (21000.0, 0.06),
    }
    threshold, rate = loan_rates.get(student_loan_plan, (1e12, 0.0))
    student_loan = round(max(0.0, taxable - threshold) * rate, 2)

    take_home = round(salary - pension - income_tax - national_insurance - student_loan, 2)

    return {
        "Gross": round(salary, 2),
        "Pension": pension,
        "Income Tax": income_tax,
        "National Insurance": national_insurance,
        "Student Loan": student_loan,
        "Take Home": take_home,
    }


@app.route("/calculate", methods=["POST"])
def calculate():
    data = request.get_json(force=True) or {}
    salary = float(data.get("salary", 0.0))
    pension_percent = float(data.get("pension_percent", 0.0))
    student_loan_plan = data.get("student_loan_plan", "none")
    if salary <= 0:
        return jsonify({"error": "invalid salary"}), 400
    result = calc_take_home(salary, pension_percent, student_loan_plan)
    return jsonify(result)


@app.route("/calculate_living", methods=["POST"])
def calculate_living():
    data = request.get_json(force=True) or {}
    take_home = float(data.get("take_home", 0.0))
    monthly_rent = data.get("monthly_rent")
    yearly_council_tax = data.get("yearly_council_tax")

    # Use sensible defaults if client omits values
    monthly_rent = float(monthly_rent) if monthly_rent is not None else 595.0
    yearly_council_tax = float(yearly_council_tax) if yearly_council_tax is not None else 1818.05

    monthly_council = yearly_council_tax / 12.0
    bills = round(monthly_rent + monthly_council, 2)
    remaining = round(take_home - bills, 2)
    return jsonify({"Bills": bills, "Remaining After Bills": remaining})


@app.route("/calculate_foodshop", methods=["POST"])
def calculate_foodshop():
    data = request.get_json(force=True) or {}
    items = data.get("items", [])
    remaining_after_bills = float(data.get("remaining_after_bills", 0.0))

    weekly_total = round(sum(float(i.get("price", 0.0)) for i in items), 2)
    monthly_total = round(weekly_total * 52.0 / 12.0, 2)
    remaining_after_food = round(remaining_after_bills - monthly_total, 2)

    return jsonify({
        "total": weekly_total,
        "monthly_total": monthly_total,
        "remaining_after_food": remaining_after_food
    })


if __name__ == "__main__":
    # For local debugging only; gunicorn will import `app`.
    app.run(host="0.0.0.0", port=5000, debug=True)
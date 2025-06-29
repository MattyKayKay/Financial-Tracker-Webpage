from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # This enables CORS for all routes


# Budget Calculator Function

def calculate_budget(gross_salary, employee_pension_percent, student_loan_plan="plan2",
                     monthly_rent=None, yearly_council_tax=None):

    # --- Section 1: Take Home Deductions Calculation ---

    # Rate Percents
    employer_pension_percent = 0.03
    pension_percent = employer_pension_percent + (employee_pension_percent / 100)
    income_tax_percent = 0.20
    ni_tier1_percent = 0.08
    ni_tier2_percent = 0.02

    # Thresholds
    income_tax_threshold = 12570
    ni_tier1_lower_threshold = 242
    ni_tier1_upper_threshold = 967
    ni_tier2_lower_threshold = 967

    # Student Loan Plan Thresholds (monthly)
    STUDENT_LOAN_PLANS = {
    "none": {"threshold": float('inf'), "rate": 0.00},
    "plan1": {"threshold": 2082.50, "rate": 0.09},
    "plan2": {"threshold": 2274.58, "rate": 0.09},
    "plan4": {"threshold": 2500.00, "rate": 0.09},
    "pgl":   {"threshold": 1750.00, "rate": 0.06}
    }

    # Gross Calculations
    monthly_gross = gross_salary / 12
    weekly_gross = gross_salary / 52

    # Pension Calculations
    pension = monthly_gross * pension_percent

    # Income Tax Calculations using UK tax bands + personal allowance taper
    gross_minus_pension = gross_salary - (pension * 12)

    # Personal Allowance Tapering
    if gross_minus_pension <= 100000:
        personal_allowance = 12570
    elif gross_minus_pension >= 125140:
        personal_allowance = 0
    else:
        reduction = (gross_minus_pension - 100000) / 2
        personal_allowance = max(0, 12570 - reduction)

    # Calculate taxable income after personal allowance
    taxable_income = max(0, gross_minus_pension - personal_allowance)

    income_tax = 0

    # Tax Band Widths
    basic_rate_limit = 50270
    higher_rate_limit = 125140

    # Basic Rate: 20% on £12,571–£50,270 (band width: £37,700)
    if taxable_income > 0:
        basic_band = min(taxable_income, 37700)
        income_tax += basic_band * 0.20

    # Higher Rate: 40% on £50,271–£125,140 (band width: £74,870)
    if taxable_income > 37700:
        higher_band = min(taxable_income - 37700, 74870)
        income_tax += higher_band * 0.40

    # Additional Rate: 45% on income over £125,140
    if taxable_income > 112570:  # £12,570 + £37,700 + £74,870 = £125,140
        additional_band = taxable_income - 112570
        income_tax += additional_band * 0.45

    # Convert annual tax to monthly
    income_tax /= 12

    # NI Calculations
    WEEKS_PER_YEAR = 52
    MONTHS_PER_YEAR = 12
    WEEKS_PER_MONTH_BY_YEAR = WEEKS_PER_YEAR / MONTHS_PER_YEAR

    ni_band_width = ni_tier1_upper_threshold - ni_tier1_lower_threshold
    income_above_lower = weekly_gross - ni_tier1_lower_threshold

    if income_above_lower > 0:
        ni_tier1_income = min(max(0, income_above_lower), ni_band_width)
        tier1_national_insurance = ni_tier1_income * ni_tier1_percent * WEEKS_PER_MONTH_BY_YEAR
    else:
        tier1_national_insurance = 0

    ni_tier2_income = max(0, weekly_gross - ni_tier2_lower_threshold)
    tier2_national_insurance = ni_tier2_income * ni_tier2_percent * WEEKS_PER_MONTH_BY_YEAR

    national_insurance = tier1_national_insurance + tier2_national_insurance

    # Student Loan Calculation (based on selected plan)
    plan = STUDENT_LOAN_PLANS.get(student_loan_plan.lower(), STUDENT_LOAN_PLANS["none"])
    threshold = plan["threshold"]
    rate = plan["rate"]

    sl_income = max(0, monthly_gross - threshold)
    student_loan = sl_income * rate if sl_income > 0 else 0


    # Total & Net
    total_deductions = pension + income_tax + national_insurance + student_loan
    take_home = monthly_gross - total_deductions

    # --- Section 2: Living Costs Calculation ---

    # Ask user for monthly rent and yearly council tax
    if monthly_rent is None:
        try:
            monthly_rent = float(input("Enter your monthly rent (£): "))
        except Exception:
            monthly_rent = 595.00  # Default value

    if yearly_council_tax is None:
        try:
            yearly_council_tax = float(input("Enter your yearly council tax (£): "))
        except Exception:
            yearly_council_tax = 1818.05  # Default value

    # Assumed yearly costs (can be made user inputs if needed)
    yearly_water_bill = 286.00
    yearly_gas_electric = 1712.00
    yearly_home_insurance = 125.00

    # Convert yearly costs to monthly
    monthly_council_tax = yearly_council_tax / 12
    monthly_water_bill = yearly_water_bill / 12
    monthly_gas_electric = yearly_gas_electric / 12
    monthly_home_insurance = yearly_home_insurance / 12

    # Calculate total living costs
    living_costs = (
        monthly_rent +
        monthly_council_tax +
        monthly_water_bill +
        monthly_gas_electric +
        monthly_home_insurance
    )

    # Calculate remaining income after living costs
    remaining_after_living = take_home - living_costs

    # Add these to the results dictionary
    results = {
        "Gross": round(monthly_gross, 2),
        "Pension": round(pension, 2),
        "Income Tax": round(income_tax, 2),
        "National Insurance": round(national_insurance, 2),
        "Student Loan": round(student_loan, 2),
        "Total Deductions": round(total_deductions, 2),
        "Take Home": round(take_home, 2),
        "Living Costs": round(living_costs, 2),
        "Remaining After Living Costs": round(remaining_after_living, 2)
    }

    return results

@app.route('/calculate', methods=['POST', 'OPTIONS'])
def calculate():
    if request.method == 'OPTIONS':
        return '', 204  # Preflight response for CORS

    data = request.json
    try:
        salary = float(data.get('salary', 0))
        pension_percent = float(data.get('pension_percent', 0))
        loan_plan = data.get('student_loan_plan', 'none')

        result = calculate_budget(salary, pension_percent, loan_plan)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/calculate_living', methods=['POST', 'OPTIONS'])
def calculate_living():
    if request.method == 'OPTIONS':
        return '', 204  # Preflight response for CORS

    data = request.json
    try:
        # Ensure all values are provided and valid numbers
        take_home = data.get('take_home')
        monthly_rent = data.get('monthly_rent')
        yearly_council_tax = data.get('yearly_council_tax')

        if take_home is None or monthly_rent is None or yearly_council_tax is None:
            raise ValueError("All fields are required.")

        take_home = float(take_home)
        monthly_rent = float(monthly_rent)
        yearly_council_tax = float(yearly_council_tax)

        # Assumed yearly costs
        yearly_water_bill = 286.00
        yearly_gas_electric = 1712.00
        yearly_home_insurance = 125.00

        monthly_council_tax = yearly_council_tax / 12
        monthly_water_bill = yearly_water_bill / 12
        monthly_gas_electric = yearly_gas_electric / 12
        monthly_home_insurance = yearly_home_insurance / 12

        living_costs = (
            monthly_rent +
            monthly_council_tax +
            monthly_water_bill +
            monthly_gas_electric +
            monthly_home_insurance
        )
        remaining_after_living = take_home - living_costs

        return jsonify({
            "Living Costs": round(living_costs, 2),
            "Remaining After Living Costs": round(remaining_after_living, 2)
        })
    except Exception as e:
        return jsonify({'error': f'Invalid input: {str(e)}'}), 400


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    return response


# Render uses this, don't remove it
if __name__ == "__main__":
    # Example test values
    gross_salary = 38000
    pension_percent = 10
    student_loan_plan = "plan2"
    rent = 600
    council_tax = 1800

    result = calculate_budget(
        gross_salary,
        pension_percent,
        student_loan_plan,
        monthly_rent=rent,
        yearly_council_tax=council_tax
    )

    print("Test run result:")
    for k, v in result.items():
        print(f"{k}: £{v:.2f}")

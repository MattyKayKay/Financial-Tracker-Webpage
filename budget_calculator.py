from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)

def calculate_budget(gross_salary, employee_pension_percent):

    # Rate Percents
    employer_pension_percent = 0.03
    pension_percent = employer_pension_percent + (employee_pension_percent / 100)
    income_tax_percent = 0.20
    ni_tier1_percent = 0.08
    ni_tier2_percent = 0.02
    student_loan_percent = 0.09

    # Thresholds
    income_tax_threshold = 12570
    ni_tier1_lower_threshold = 242
    ni_tier1_upper_threshold = 967
    ni_tier2_lower_threshold = 967
    student_loan_threshold = 2172

    # Gross Calculations
    monthly_gross = gross_salary / 12
    weekly_gross = gross_salary / 52

    # Pension Calculations
    pension = monthly_gross * pension_percent

    # Income Tax Calculations
    taxable_income = max(0, gross_salary - income_tax_threshold - pension * 12)
    income_tax = (taxable_income * income_tax_percent) / 12 if taxable_income > 0 else 0

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

    # Student Loan
    sl_income = max(0, monthly_gross - student_loan_threshold)
    student_loan = sl_income * student_loan_percent if sl_income > 0 else 0

    # Total & Net
    total_deductions = pension + income_tax + national_insurance + student_loan
    take_home = monthly_gross - total_deductions

    return {
        "Gross": round(monthly_gross, 2),
        "Pension": round(pension, 2),
        "Income Tax": round(income_tax, 2),
        "National Insurance": round(national_insurance, 2),
        "Student Loan": round(student_loan, 2),
        "Total Deductions": round(total_deductions, 2),
        "Take Home": round(take_home, 2)
    }

# API endpoint
@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json
    try:
        salary = float(data.get('salary', 0))
        pension_pct = float(data.get('pension_percent', 5))  # Default to 5% if not provided
        result = calculate_budget(salary, pension_pct)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Render uses this, don't remove it
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)

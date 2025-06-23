from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)

def calculate_budget(gross_salary):

    # Rate Percents
    employer_pension_percent = 0.03
    employee_pension_percent = float(input("Enter your desired pension contribution percentage (as a number, e.g., 5 for 5%): ")) / 100
    pension_percent = employer_pension_percent + employee_pension_percent
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
    
    #National Insurance Calculations
    WEEKS_PER_YEAR   = 52
    MONTHS_PER_YEAR  = 12
    WEEKS_PER_MONTH_BY_YEAR  = WEEKS_PER_YEAR / MONTHS_PER_YEAR
    #Tier 1 National Insurance
    ni_band_width = ni_tier1_upper_threshold - ni_tier1_lower_threshold
    income_above_lower = weekly_gross - ni_tier1_lower_threshold

    if income_above_lower > 0:
        ni_tier1_income = min(max(0, income_above_lower), ni_band_width)
        tier1_national_insurance = ni_tier1_income * ni_tier1_percent * WEEKS_PER_MONTH_BY_YEAR  # Monthly
    else:
        tier1_national_insurance = 0

    #Tier 2 National Insurance
    ni_tier2_income = max(0, weekly_gross - ni_tier2_lower_threshold)
    tier2_national_insurance = ni_tier2_income * ni_tier2_percent * WEEKS_PER_MONTH_BY_YEAR  # Monthly   
    
    #Total National Insurance
    national_insurance = tier1_national_insurance + tier2_national_insurance


    # ni_tier1_income = max(0, min(weekly_gross, ni_tier1_upper_threshold) - ni_tier1_lower_threshold)
    # tier1_national_insurance = (ni_tier1_income * ni_tier1_percent) * 4 if ni_tier1_income > 0 else 0

    # Student Loan Calculations
    sl_income = max(0, monthly_gross - student_loan_threshold)
    student_loan = (sl_income * student_loan_percent) if sl_income > 0 else 0
     

    total_deductions = pension + income_tax + tier1_national_insurance + student_loan
    take_home = monthly_gross - total_deductions




    # Results as a dictionary
    results = {
        "Gross": monthly_gross,
        "Pension": pension,
        "Income Tax": income_tax,
        "National Insurance": national_insurance,
        "Student Loan": student_loan,
        "Total Deductions": total_deductions,
        "Take Home": take_home
    }
    return results

if __name__ == "__main__":
    gross_salary = float(input("Enter your annual gross salary: "))
    results = calculate_budget(gross_salary)
    print("\nMonthly Breakdown:")
    for k, v in results.items():
        print(f"{k}: £{v:.2f}")

    # Save to CSV
    df = pd.DataFrame([results])
    df.to_csv("budget_results.csv", index=False)
    print("\nResults saved to budget_results.csv")


# API endpoint
@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json
    try:
        salary = float(data.get('salary', 0))
        result = calculate_budget(salary)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Only used locally
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
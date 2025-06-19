import pandas as pd

def calculate_budget(gross_salary):

    # Example constants (replace with values from your spreadsheet)
    employer_pension_percent = 0.03
    employee_pension_percent = float(input("Enter your desired pension contribution percentage (as a number, e.g., 5 for 5%): ")) / 100
    pension_percent = employer_pension_percent + employee_pension_percent
    income_tax_percent = 0.20
    ni_percent = 0.08
    student_loan_percent = 0.09

    # Example thresholds (replace with your actual values)
    income_tax_threshold = 12570
    ni_threshold = 967
    student_loan_threshold = 2172

    # Calculations
    monthly_gross = gross_salary / 12
    pension = monthly_gross * pension_percent
    taxable_income = max(0, gross_salary - income_tax_threshold - pension * 12)
    income_tax = (taxable_income * income_tax_percent) / 12 if taxable_income > 0 else 0
    ni_income = max(0, monthly_gross - ni_threshold)
    national_insurance = ni_income * ni_percent if ni_income > 0 else 0
    sl_income = max(0, gross_salary - student_loan_threshold)
    student_loan = (sl_income * student_loan_percent) / 12 if sl_income > 0 else 0

    total_deductions = pension + income_tax + national_insurance + student_loan
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
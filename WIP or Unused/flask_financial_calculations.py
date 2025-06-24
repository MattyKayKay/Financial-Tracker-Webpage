from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        gross_salary = float(request.form['gross_salary'])
        # Example calculation (replace with your logic)
        monthly = gross_salary / 12
        result = f"Monthly salary: £{monthly:.2f}"
    return render_template('index.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)
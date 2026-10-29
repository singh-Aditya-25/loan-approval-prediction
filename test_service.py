import requests

BASE_URL = 'http://localhost:8000'

def test_health():
    r = requests.get(f'{BASE_URL}/health')
    print('Health Check Status:', r.status_code, r.json())

def test_predict_approved():
    payload = {
        'Gender': 'Male', 'Married': 'Yes', 'Dependents': '0', 'Education': 'Graduate',
        'Self_Employed': 'No', 'ApplicantIncome': 6000, 'CoapplicantIncome': 2500,
        'LoanAmount': 140, 'Loan_Amount_Term': 360, 'Credit_History': 1.0, 'Property_Area': 'Semiurban'
    }
    r = requests.post(f'{BASE_URL}/predict', json=payload)
    print('Approved Case Prediction:', r.status_code, r.json())

if __name__ == '__main__':
    try:
        test_health()
        test_predict_approved()
    except Exception as e:
        print('Service test error:', str(e))

import time
import logging
import numpy as np
import pandas as pd
import joblib
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from prometheus_client import Counter, Histogram, make_asgi_app

# Setup JSON Logging
logging.basicConfig(level=logging.INFO, format='{"time":"%(asctime)s", "level":"%(levelname)s", "message":%(message)s}')
logger = logging.getLogger('loan_service')

# Initialize FastAPI & Prometheus Metrics
app = FastAPI(title='Loan Approval Prediction API', version='1.0.0')
metrics_app = make_asgi_app()
app.mount('/metrics', metrics_app)

PREDICTION_COUNTER = Counter('loan_predictions_total', 'Total predictions', ['status'])
LATENCY_HISTOGRAM = Histogram('prediction_latency_seconds', 'Inference latency')

# Load Pre-trained Model
try:
    model = joblib.load('loan_model.joblib')
    logger.info('Model successfully loaded into memory.')
except Exception as e:
    logger.error(f'Failed to load model: {str(e)}')
    model = None

class LoanApplication(BaseModel):
    Gender: str = Field(..., example='Male')
    Married: str = Field(..., example='Yes')
    Dependents: str = Field(..., example='0')
    Education: str = Field(..., example='Graduate')
    Self_Employed: str = Field(..., example='No')
    ApplicantIncome: float = Field(..., example=5000)
    CoapplicantIncome: float = Field(..., example=2000)
    LoanAmount: float = Field(..., example=150)
    Loan_Amount_Term: float = Field(..., example=360)
    Credit_History: float = Field(..., example=1.0)
    Property_Area: str = Field(..., example='Semiurban')

@app.get('/health')
def health_check():
    if model is None:
        raise HTTPException(status_code=503, detail='Model not loaded')
    return {'status': 'healthy', 'model': 'RandomForest_v1.0'}

@app.post('/predict')
def predict_loan(app_data: LoanApplication):
    start_time = time.time()
    if model is None:
        raise HTTPException(status_code=500, detail='Inference engine unavailable')
    
    # Convert input to DataFrame & compute engineered features
    data = app_data.dict()
    df = pd.DataFrame([data])
    df['Total_Income'] = df['ApplicantIncome'] + df['CoapplicantIncome']
    df['Total_Income_Log'] = np.log1p(df['Total_Income'])
    df['LoanAmount_Log'] = np.log1p(df['LoanAmount'])
    df['EMI'] = df['LoanAmount'] / df['Loan_Amount_Term']
    df['Balance_Income'] = df['Total_Income'] - (df['EMI'] * 1000)
    
    # Predict
    prob = float(model.predict_proba(df)[:, 1][0])
    prediction = 'Approved' if prob >= 0.5 else 'Rejected'
    
    latency = time.time() - start_time
    LATENCY_HISTOGRAM.observe(latency)
    PREDICTION_COUNTER.labels(status=prediction).inc()
    
    logger.info(f'{{"applicant_income":{app_data.ApplicantIncome}, "credit_history":{app_data.Credit_History}, "result":"{prediction}", "probability":{prob:.4f}, "latency_ms":{latency*1000:.2f}}}')
    return {'status': prediction, 'approval_probability': round(prob, 4), 'latency_seconds': round(latency, 4)}
# YuvaIntern Week 5 - AI Service Deployment Repository

## Quick Start Instructions
1. **Build Docker Image:**
   ```bash
   docker build -t loan-approval-api:v1 .
   ```
2. **Run Container:**
   ```bash
   docker run -d -p 8000:8000 --name loan_service loan-approval-api:v1
   ```
3. **Test API:**
   - Health Check: `http://localhost:8000/health`
   - Swagger Docs: `http://localhost:8000/docs`
   - Prometheus Metrics: `http://localhost:8000/metrics`

# 🚀 End-to-End MLOps Deployment Guide

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Hub Registry                       │
│              (Public Docker Image Repository)               │
│                                                              │
│  📦 your-username/heart-api:latest                         │
│     ├─ FastAPI Backend                                    │
│     ├─ Model Pipeline (model_pipeline.pkl)               │
│     └─ All Dependencies                                  │
└─────────────────────────────────────────────────────────────┘
         ↑                                      ↓
         │                               (Pull & Run)
         │
    (Push Image)                      ┌──────────────────────┐
         │                            │  Docker Container    │
         │                            │  Port 8000           │
    ┌────┴─────────┐                 │  FastAPI Running     │
    │              │                 └──────────────────────┘
    │   Your PC    │                        ↑
    │   (Local)    │                        │ HTTP Requests
    │              │                        │
    │ Docker       │────────────────────────┤
    │ Build        │                        │
    │ & Push       │                 ┌──────┴──────────────┐
    │              │                 │  Streamlit Cloud    │
    │              │                 │  (Frontend UI)      │
    │              │                 │  https://...        │
    └──────────────┘                 └─────────────────────┘
```

---

## Step 1: Prerequisites

### 1.1 Create Docker Hub Account
- Go to https://hub.docker.com/
- Sign up for a free account
- Note your username (e.g., `your-username`)

### 1.2 Install Required Tools
- Docker Desktop: https://www.docker.com/products/docker-desktop
- Git: https://git-scm.com/
- Python 3.10+: https://www.python.org/

---

## Step 2: Push Docker Image to Docker Hub

### 2.1 Login to Docker Hub (PowerShell)
```powershell
docker login
```
Enter your Docker Hub credentials when prompted.

### 2.2 Tag Your Image
```powershell
docker tag heart-api:latest your-username/heart-api:latest
```
Replace `your-username` with your actual Docker Hub username.

### 2.3 Push Image to Docker Hub
```powershell
docker push your-username/heart-api:latest
```
This will upload the image (~1.5GB). Wait for completion.

### 2.4 Verify on Docker Hub
- Go to https://hub.docker.com/
- Login and navigate to Repositories
- You should see `your-username/heart-api` listed

---

## Step 3: Local Testing (Before Cloud Deployment)

### 3.1 Run Backend (FastAPI)
```powershell
docker run -d -p 8000:8000 --name heart-api-backend your-username/heart-api:latest
```

### 3.2 Run Frontend (Streamlit) - Local Terminal
In a different PowerShell window:
```powershell
cd "path\to\your\project"
pip install streamlit requests
streamlit run streamlit_app.py
```

### 3.3 Test the Full Application
- Open Streamlit UI: http://localhost:8501
- API URL should be: http://localhost:8000
- Fill in the form and click "Predict Risk"
- You should see the prediction result!

---

## Step 4: Deploy Frontend to Streamlit Cloud (FREE)

### 4.1 Prepare GitHub Repository
1. Create a GitHub account: https://github.com/
2. Create a new repository: `heart-disease-mlops`
3. Push your code:
```bash
git add .
git commit -m "MLOps Heart Disease Application"
git push origin main
```

Make sure these files are in your repo:
- `streamlit_app.py` (Your Streamlit frontend)
- `requirements.txt` (Python dependencies)
- `README.md` (Project documentation)

### 4.2 Create Streamlit Cloud App
1. Go to https://streamlit.io/cloud
2. Click "New app"
3. Connect your GitHub account
4. Select repository: `your-username/heart-disease-mlops`
5. Select branch: `main`
6. Set main file path: `streamlit_app.py`

### 4.3 Configure Secrets (Optional)
In Streamlit Cloud dashboard:
1. Go to App Settings
2. Secrets tab
3. Add if needed:
```toml
API_URL = "your-deployed-api-url"
```

### 4.4 Deploy!
- Click "Deploy"
- Streamlit will build and deploy your app
- You'll get a public URL like: `https://your-username-heart-disease.streamlit.app`

---

## Step 5: Deploy Backend to Cloud (Optional)

### Option A: AWS EC2 (Simple)
```bash
# 1. Launch EC2 instance (Ubuntu)
# 2. SSH into instance
sudo apt-get update
sudo apt-get install docker.io

# 3. Pull and run your image
sudo docker pull your-username/heart-api:latest
sudo docker run -d -p 8000:8000 your-username/heart-api:latest

# 4. Access at: http://your-ec2-ip:8000
```

### Option B: Google Cloud Run (Easiest)
```bash
# 1. Install Google Cloud SDK
# 2. Authenticate
gcloud auth login

# 3. Deploy
gcloud run deploy heart-api \
  --image your-username/heart-api:latest \
  --platform managed \
  --region us-central1 \
  --port 8000 \
  --allow-unauthenticated
```

### Option C: Heroku (Legacy, may have billing)
```bash
# 1. Login to Heroku
heroku login

# 2. Create app
heroku create your-app-name

# 3. Push Docker image
heroku container:push web -a your-app-name
heroku container:release web -a your-app-name

# 4. Access at: https://your-app-name.herokuapp.com
```

---

## Step 6: Update Streamlit Frontend with Backend URL

### 6.1 Modify streamlit_app.py
Replace the default API URL with your cloud deployment:
```python
api_url = st.text_input(
    "API Backend URL",
    value="https://your-deployed-api-url",  # Update this!
    help="Enter the FastAPI backend URL"
)
```

### 6.2 Commit and Push
```bash
git add streamlit_app.py
git commit -m "Update API URL for production"
git push origin main
```

Streamlit Cloud will automatically redeploy!

---

## Testing Checklist

- [ ] Docker image builds successfully
- [ ] Docker image runs locally on port 8000
- [ ] API endpoints respond correctly:
  - `GET /health` returns `{"status": "ok"}`
  - `POST /predict` returns prediction result
- [ ] Streamlit frontend runs locally
- [ ] Frontend can connect to backend API
- [ ] Predictions work end-to-end
- [ ] Docker image pushed to Docker Hub
- [ ] Streamlit app deployed to Streamlit Cloud
- [ ] Frontend and backend communicate in cloud

---

## API Endpoints (FastAPI Documentation)

Once deployed, visit: `https://your-api-url/docs`

You'll see interactive API documentation with Swagger UI!

### /health
```bash
curl http://localhost:8000/health
# Response: {"status": "ok", "model_loaded": true}
```

### /predict
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "age": 63,
    "sex": 1,
    "cp": 3,
    "trestbps": 145,
    "chol": 233,
    "fbs": 1,
    "restecg": 0,
    "thalach": 150,
    "exang": 0,
    "oldpeak": 2.3,
    "slope": 0,
    "ca": 0,
    "thal": 1
  }'
# Response: {"prediction": 0, "probability": 0.375}
```

### /metrics
```bash
curl http://localhost:8000/metrics
# Returns Prometheus metrics
```

---

## Troubleshooting

### Docker Image Won't Push
```powershell
# Check Docker login
docker ps

# Re-login if needed
docker logout
docker login
```

### API Not Responding
```powershell
# Check container status
docker ps

# View logs
docker logs heart-api-container

# Check health
Invoke-RestMethod -Uri http://localhost:8000/health
```

### Streamlit Can't Connect to API
- Verify API URL in Streamlit app
- Check API is running and accessible
- Look for CORS issues in logs

---

## Production Checklist

✅ Code is version controlled (GitHub)  
✅ Docker image is in registry (Docker Hub)  
✅ Backend is deployed and accessible  
✅ Frontend is deployed (Streamlit Cloud)  
✅ Frontend and backend communicate  
✅ Model predictions are accurate  
✅ API has proper error handling  
✅ Logging is enabled  
✅ Documentation is complete  

---

## Example URLs After Deployment

- **Frontend**: `https://your-username-heart-disease.streamlit.app`
- **Backend API**: `https://heart-api-xxxxx.a.run.app` (if using Cloud Run)
- **API Docs**: `https://heart-api-xxxxx.a.run.app/docs`
- **Docker Hub**: `https://hub.docker.com/r/your-username/heart-api`

---

## Support Your Supervisor's Review

When presenting to your supervisor, show them:

1. **Docker Hub Repository**
   - Screenshot of your image on Docker Hub
   - Show the build history

2. **Running Container**
   - Screenshot of `docker ps` showing container running
   - API health check response

3. **Streamlit Cloud Deployment**
   - Live link to your Streamlit app
   - Show it making predictions

4. **Architecture Diagram**
   - Show this diagram in your presentation
   - Explain the separation of concerns

5. **API Documentation**
   - Show Swagger UI at `/docs`
   - Demonstrate API calls

---

## Summary

You've created a **production-grade MLOps application**:

- ✅ Machine Learning Model (scikit-learn)
- ✅ Experiment Tracking (MLflow)
- ✅ REST API Backend (FastAPI)
- ✅ Web Frontend (Streamlit)
- ✅ Containerization (Docker)
- ✅ Cloud Deployment (Docker Hub + Streamlit Cloud)

This is **exactly what enterprises use in production**! 🎉

---

**Created**: January 6, 2026  
**MLOps E2E Project**: Heart Disease Risk Prediction

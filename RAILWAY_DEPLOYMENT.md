# 🚀 Deploy to Railway - Step by Step

## What is Railway?

Railway is a **free cloud platform** that runs Docker containers. Perfect for deploying your FastAPI backend!

---

## **Complete Deployment Steps**

### **Step 1: Create Railway Account**

1. Go to https://railway.app/
2. Click "Start Project"
3. Sign up with GitHub (recommended) or email
4. Verify email if needed

---

### **Step 2: Create New Project**

1. Click "Create New Project"
2. Select **"Deploy from Docker Image"**

---

### **Step 3: Deploy Your Docker Hub Image**

1. You'll see a form asking for:
   - **Registry**: Select `Docker Hub`
   - **Image**: `shubhamsongire/heart-api:latest`

2. Click **"Deploy"**

3. Wait for deployment (takes 2-5 minutes)

---

### **Step 4: Configure Port**

1. Once deployed, go to your **project dashboard**
2. Click on the **"heart-api" service**
3. Go to **"Variables"** tab
4. Look for **PORT** variable
5. Make sure it's set to **`8000`**

Or add it manually:
- Variable Name: `PORT`
- Variable Value: `8000`

---

### **Step 5: Get Your Public URL**

1. Still in the service details
2. Look for **"Public Domain"** or **"Deployments"**
3. You'll see a URL like:
   ```
   https://heart-api-production-xxxx.railway.app
   ```
4. **Copy this URL** - you'll need it for Streamlit!

---

### **Step 6: Test Your Deployed API**

Open in browser:
```
https://your-railway-url/health
```

You should see:
```json
{"status": "ok", "model_loaded": true}
```

---

### **Step 7: Update Streamlit App**

Update `streamlit_app.py` line 25:

```python
api_url = st.text_input(
    "API Backend URL",
    value="https://your-railway-url",  # Replace with your actual URL
    help="Enter the FastAPI backend URL"
)
```

Then push to GitHub:
```bash
git add streamlit_app.py
git commit -m "Update API URL to Railway deployment"
git push origin master
```

---

## **Verification Checklist**

- [ ] Railway account created
- [ ] Docker image deployed
- [ ] Port configured to 8000
- [ ] Public URL obtained
- [ ] `/health` endpoint responds
- [ ] Streamlit updated with new URL
- [ ] Code pushed to GitHub

---

## **Troubleshooting**

### **API not responding**

Check Railway logs:
1. Go to your service on Railway
2. Click "Deployments"
3. Click the latest deployment
4. Check logs for errors

### **Port issues**

Make sure PORT variable is set to `8000` in Railway settings.

### **Model not found error**

The model should be in the Docker image already. If not, ensure:
1. `models/model_pipeline.pkl` exists locally
2. Image was rebuilt after adding model
3. Re-push to Docker Hub if needed

---

## **Your Complete E2E Application URLs**

Once done, you'll have:

1. **Docker Image**: https://hub.docker.com/r/shubhamsongire/heart-api
2. **Backend API**: https://your-railway-url
3. **API Docs**: https://your-railway-url/docs
4. **Streamlit Frontend**: Run locally with `streamlit run streamlit_app.py`

---

## **Show Your Supervisor**

1. ✅ Docker Hub image
2. ✅ Railway deployment running
3. ✅ Streamlit UI connecting to cloud API
4. ✅ Working end-to-end predictions

**Perfect production-ready MLOps application!** 🎉

---

## **Cost**

Railway free tier includes:
- Up to 5 deployments
- 500 hours per month
- Perfect for student projects!

More info: https://railway.app/pricing

---

## **Additional Notes**

- Railway auto-deploys when Docker image updates
- Logs are available in Railway dashboard
- You can scale if needed (paid features)
- Use environment variables for sensitive data

For questions: https://docs.railway.app/

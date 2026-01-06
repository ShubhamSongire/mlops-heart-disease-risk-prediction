import streamlit as st
import requests
import json

# Page configuration
st.set_page_config(
    page_title="Heart Disease Risk Predictor",
    page_icon="❤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# App title and description
st.title("❤️ Heart Disease Risk Predictor")
st.markdown("""
This application predicts the risk of heart disease based on medical parameters.
Enter your medical information below and click **Predict** to get a risk assessment.
""")

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ API Configuration")
    api_url = st.text_input(
        "API Backend URL",
        value="https://heart-api-production.up.railway.app",
        help="Enter the FastAPI backend URL"
    )
    
    st.header("📋 Instructions")
    st.markdown("""
    1. **Fill in your medical data** using the input fields
    2. **Click the Predict button** to get a risk assessment
    3. **Review the results** showing your risk level and probability
    
    **Note:** This tool is for educational purposes only. Always consult a healthcare professional.
    """)

# Check API health
def check_api_health(url):
    try:
        response = requests.get(f"{url}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Enter Your Medical Information")
    
    # Check API availability
    if not check_api_health(api_url):
        st.warning(f"⚠️ API not available at {api_url}. Make sure the backend is running!")
        st.markdown("""
        **How to start the backend:**
        ```bash
        docker run -d -p 8000:8000 shubhamsongire/heart-api:latest
        ```
        Or locally:
        ```bash
        uvicorn app.main:app --host 0.0.0.0 --port 8000
        ```
        """)
        st.info("""
        **Docker Hub Image**: https://hub.docker.com/r/shubhamsongire/heart-api
        """)
        st.stop()
    
    st.success(f"✅ Connected to API at {api_url}")
    
    # Create form for input
    with st.form("prediction_form"):
        # Create columns for better layout
        input_col1, input_col2 = st.columns(2)
        
        with input_col1:
            age = st.number_input(
                "Age (years)",
                min_value=1, max_value=150, value=50,
                help="Your age in years"
            )
            sex = st.selectbox(
                "Sex",
                options=[0, 1],
                format_func=lambda x: "Female" if x == 0 else "Male",
                help="0 = Female, 1 = Male"
            )
            cp = st.selectbox(
                "Chest Pain Type",
                options=[0, 1, 2, 3],
                format_func=lambda x: ["Typical Angina", "Atypical Angina", "Non-anginal Pain", "Asymptomatic"][x],
                help="Type of chest pain experienced"
            )
            trestbps = st.number_input(
                "Resting Blood Pressure (mmHg)",
                min_value=80, max_value=200, value=120,
                help="Resting blood pressure in mmHg"
            )
            chol = st.number_input(
                "Serum Cholesterol (mg/dl)",
                min_value=100, max_value=400, value=200,
                help="Serum cholesterol level"
            )
            fbs = st.selectbox(
                "Fasting Blood Sugar > 120 mg/dl",
                options=[0, 1],
                format_func=lambda x: "No (≤ 120)" if x == 0 else "Yes (> 120)",
                help="0 = No, 1 = Yes"
            )
        
        with input_col2:
            restecg = st.selectbox(
                "Resting ECG Results",
                options=[0, 1, 2],
                format_func=lambda x: ["Normal", "ST-T Abnormality", "LV Hypertrophy"][x],
                help="Resting electrocardiographic results"
            )
            thalach = st.number_input(
                "Max Heart Rate Achieved",
                min_value=60, max_value=220, value=150,
                help="Maximum heart rate achieved during exercise"
            )
            exang = st.selectbox(
                "Exercise Induced Angina",
                options=[0, 1],
                format_func=lambda x: "No" if x == 0 else "Yes",
                help="0 = No, 1 = Yes"
            )
            oldpeak = st.number_input(
                "ST Depression (oldpeak)",
                min_value=0.0, max_value=10.0, value=1.0, step=0.1,
                help="ST depression induced by exercise"
            )
            slope = st.selectbox(
                "ST Slope",
                options=[0, 1, 2],
                format_func=lambda x: ["Upsloping", "Flat", "Downsloping"][x],
                help="Slope of the ST segment"
            )
            ca = st.number_input(
                "Major Vessels Colored (0-4)",
                min_value=0, max_value=4, value=0,
                help="Number of major vessels (0-4) colored by flourosopy"
            )
            thal = st.selectbox(
                "Thalassemia",
                options=[0, 1, 2, 3],
                format_func=lambda x: ["Normal", "Fixed Defect", "Reversible Defect", "Unknown"][x] if x > 0 else "Normal",
                help="Thalassemia type"
            )
        
        # Prediction button
        submitted = st.form_submit_button("🔍 Predict Risk", use_container_width=True)

# Display prediction results
if submitted:
    try:
        # Prepare input data
        input_payload = {
            "age": age,
            "sex": sex,
            "cp": cp,
            "trestbps": trestbps,
            "chol": chol,
            "fbs": fbs,
            "restecg": restecg,
            "thalach": thalach,
            "exang": exang,
            "oldpeak": oldpeak,
            "slope": slope,
            "ca": ca,
            "thal": thal
        }
        
        # Call API
        with st.spinner("🔄 Processing..."):
            response = requests.post(
                f"{api_url}/predict",
                json=input_payload,
                timeout=10
            )
        
        if response.status_code == 200:
            result = response.json()
            
            if "error" in result:
                st.error(f"❌ API Error: {result['error']}")
            else:
                prediction = result["prediction"]
                probability = result["probability"]
                
                # Display results in right column
                with col2:
                    st.subheader("🎯 Result")
                    
                    if prediction == 1:
                        st.error(f"⚠️ HIGH RISK")
                        risk_text = "High Risk of Heart Disease"
                    else:
                        st.success(f"✅ LOW RISK")
                        risk_text = "Low Risk of Heart Disease"
                    
                    st.metric(
                        label="Risk Assessment",
                        value=risk_text
                    )
                    
                    st.metric(
                        label="Risk Probability",
                        value=f"{probability*100:.1f}%"
                    )
                
                # Display detailed results
                st.divider()
                st.subheader("📊 Detailed Analysis")
                
                results_col1, results_col2, results_col3 = st.columns(3)
                
                with results_col1:
                    st.metric(
                        "Prediction",
                        "🔴 Disease Detected" if prediction == 1 else "🟢 No Disease"
                    )
                
                with results_col2:
                    st.metric(
                        "Risk Score",
                        f"{probability:.2%}"
                    )
                
                with results_col3:
                    confidence = max(probability, 1-probability)
                    st.metric(
                        "Confidence",
                        f"{confidence:.2%}"
                    )
                
                # Input summary
                st.divider()
                st.subheader("📝 Input Summary")
                
                summary_data = {
                    "Parameter": list(input_payload.keys()),
                    "Value": list(input_payload.values())
                }
                
                import pandas as pd
                summary_df = pd.DataFrame(summary_data)
                st.table(summary_df)
                
        else:
            st.error(f"❌ API Error: Status {response.status_code}")
            st.write(response.text)
        
    except requests.exceptions.ConnectionError:
        st.error(f"❌ Cannot connect to API at {api_url}")
        st.info("Make sure the backend is running!")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

# Footer
st.divider()
st.markdown("""
---
**Disclaimer:** This application is for educational purposes only. 
It should not be used for actual medical diagnosis. 
Always consult a qualified healthcare professional for medical advice.

**Architecture:** FastAPI Backend + Streamlit Frontend
""")
st.caption("Heart Disease MLOps Project - Production Ready E2E Application")

FROM python:3.10-slim

WORKDIR /app

# Copy all source files and project metadata
COPY . .

# Install dependencies (excluding -e . which requires full project)
RUN pip install --no-cache-dir pandas numpy scikit-learn matplotlib seaborn mlflow fastapi uvicorn[standard] prometheus-client joblib pydantic requests

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

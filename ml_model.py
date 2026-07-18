import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import os

MODEL_PATH = "dropout_model.pkl"

def get_model():
    if os.path.exists(MODEL_PATH):
        return joblib.load(MODEL_PATH)
    return None

def predict_risk(gpa, attendance, assignments):
    model = get_model()
    if not model:
        return "Unknown", 0.0

    data = np.array([[gpa, attendance, assignments]])
    
    try:
        prediction = model.predict(data)[0]
        # Some models support predict_proba
        if hasattr(model, "predict_proba"):
            probabilities = model.predict_proba(data)[0]
            confidence = float(np.max(probabilities)) * 100
        else:
            confidence = 100.0 # fallback
    except Exception:
        prediction = 0
        confidence = 0.0

    if prediction == 0:
        return "Low", confidence
    elif prediction == 1:
        return "Medium", confidence
    else:
        return "High", confidence

def train_model(csv_path):
    df = pd.read_csv(csv_path)
    
    # Expected columns: gpa, attendance, assignments_completed, dropout_label
    required_cols = ['gpa', 'attendance', 'assignments_completed', 'dropout_label']
    if not all(col in df.columns for col in required_cols):
        raise ValueError(f"CSV must contain the following columns: {required_cols}")
        
    X = df[['gpa', 'attendance', 'assignments_completed']]
    y = df['dropout_label']
    
    # Use Random Forest as default
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    
    joblib.dump(model, MODEL_PATH)
    return True
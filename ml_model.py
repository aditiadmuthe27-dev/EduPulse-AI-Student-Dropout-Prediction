import os

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier

MODEL_PATH = "dropout_model.pkl"

model = joblib.load(MODEL_PATH) if os.path.exists(MODEL_PATH) else None


def train_and_save_model():
    """Train a baseline model when no saved model exists."""
    global model
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
        return model

    rng = np.random.default_rng(42)
    samples = []
    labels = []
    for _ in range(200):
        gpa = rng.uniform(1.0, 4.0)
        attendance = rng.uniform(40, 100)
        assignments = int(rng.integers(5, 50))
        dropout = int(gpa < 2.2 or attendance < 70 or assignments < 20)
        samples.append([gpa, attendance, assignments])
        labels.append(dropout)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(samples, labels)
    joblib.dump(model, MODEL_PATH)
    return model


def _get_model():
    global model
    if model is None:
        model = train_and_save_model()
    return model


def predict_risk(gpa, attendance, assignments):
    clf = _get_model()
    data = np.array([[gpa, attendance, assignments]])
    proba = clf.predict_proba(data)[0]
    dropout_prob = float(proba[1]) if len(proba) > 1 else float(proba[0])

    if dropout_prob < 0.4:
        risk_label = "Low"
    elif dropout_prob < 0.7:
        risk_label = "Medium"
    else:
        risk_label = "High"

    return round(dropout_prob, 2), risk_label

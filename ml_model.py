import joblib
import numpy as np

model = joblib.load("dropout_model.pkl")

def predict_risk(gpa, attendance, assignments):

    data = np.array([[gpa, attendance, assignments]])

    prediction = model.predict(data)[0]

    if prediction == 0:
        return "Low"

    elif prediction == 1:
        return "Medium"

    else:
        return "High"
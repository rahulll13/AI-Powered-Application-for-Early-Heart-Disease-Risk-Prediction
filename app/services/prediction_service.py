import pickle
import json
import os
import pandas as pd
import shap
from datetime import datetime, timedelta

# Define paths to model artifacts
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(os.path.dirname(BASE_DIR), 'ml_models')
PIPELINE_PATH = os.path.join(MODEL_DIR, 'heart_disease_pipeline.pkl')
COLUMNS_PATH = os.path.join(MODEL_DIR, 'model_columns.json')
SHAP_EXPLAINER_PATH = os.path.join(MODEL_DIR, 'shap_explainer.pkl')

pipeline = None
model_columns = None
explainer = None

# --- === NEW: RECOMMENDATION MAPPING === ---
# This maps feature names to actionable advice.
RECOMMENDATION_MAP = {
    "trestbps": "Your blood pressure was a key factor. Consider discussing salt reduction and regular exercise with your doctor.",
    "chol": "Your cholesterol level was a significant contributor. Dietary changes and exercise can help. Please consult your doctor.",
    "fbs": "Your high fasting blood sugar (over 120 mg/dl) is a risk factor. Please consult your doctor about managing blood glucose.",
    "exang": "Experiencing chest pain (angina) during exercise is a strong risk factor. Avoid strenuous activity until you consult a doctor.",
    "oldpeak": "The ST depression ('oldpeak') in your EKG is a significant factor. This requires medical evaluation.",
    "cp": "The type of chest pain ('cp') you reported is a major factor. Please discuss this symptom with your doctor immediately.",
    "age": "Age is a non-modifiable risk factor. It's important to manage all other controllable risk factors like diet and exercise."
    # Add more mappings for other features as needed
}
# ---------------------------------------------

def calculate_streak(predictions):
    """
    Calculates the user's prediction streak.
    (This function is unchanged)
    """
    if not predictions:
        return 0

    today = datetime.utcnow()
    streak = 0

    # We check week by week, going backwards from today
    for i in range(52): # Check up to a year of weeks
        start_of_period = today - timedelta(days=7 * (i + 1))
        end_of_period = today - timedelta(days=7 * i)

        # Check if there was any prediction within this 7-day window
        has_prediction_in_period = any(
            start_of_period < p.timestamp <= end_of_period
            for p in predictions
        )

        if has_prediction_in_period:
            streak += 1
        else:
            # If we find a week with no prediction, the streak is broken
            break 

    return streak

def load_models():
    """Loads the pipeline, model columns, and SHAP explainer from disk."""
    global pipeline, model_columns, explainer

    try:
        # Load saved ML model pipeline
        with open(PIPELINE_PATH, 'rb') as f:
            pipeline = pickle.load(f)

        with open(COLUMNS_PATH, 'r') as f:
            model_columns = json.load(f)
            
        # Load the SHAP explainer
        with open(SHAP_EXPLAINER_PATH, 'rb') as f:
            explainer = pickle.load(f)

        print("Prediction pipeline, columns, and SHAP explainer loaded successfully.")
    except FileNotFoundError as e:
        print(f"Error loading model artifacts: {e}. Please run the training script first.")
        raise

def predict(data):
    """
    Performs a prediction, generates explanations, and provides recommendations.
    """
    if not pipeline or not model_columns or not explainer:
        raise RuntimeError("Models are not loaded. Call load_models() first.")

    # Convert the input data dictionary to a pandas DataFrame
    df = pd.DataFrame(data, index=[0])

    # Align columns with the training data
    for col in model_columns:
        if col not in df.columns:
            df[col] = 0
    df = df[model_columns]

    # --- Standard Prediction Logic ---
    prediction_raw = pipeline.predict(df)[0]
    prediction_proba = pipeline.predict_proba(df)[0][1] 

    # Implement prediction logic with risk categorization
    if prediction_proba < 0.3:
        risk = "Low"
    elif prediction_proba < 0.7:
        risk = "Medium"
    else:
        risk = "High"

    # --- Generate SHAP Explanation ---
    scaler = pipeline.named_steps['scaler']
    input_scaled = scaler.transform(df)

    # Get SHAP values
    shap_values = explainer.shap_values(input_scaled)
    # Get values for class 1 (High Risk)
    shap_values_for_class_1 = shap_values[0, :, 1]
        
    # Map feature names to their SHAP values
    feature_contributions = dict(zip(model_columns, shap_values_for_class_1))

    # Sort features by the *magnitude* of their contribution
    sorted_contributions = sorted(
        feature_contributions.items(), 
        key=lambda item: abs(item[1]), 
        reverse=True
    )

    # Create a user-friendly list of explanations
    explanation_list = []
    for feature, value in sorted_contributions:
        input_value = df[feature].values[0] # Get the actual value user provided
        if abs(value) > 0.01: # Only show features that had a real impact
            direction = "increased" if value > 0 else "decreased"
            explanation_list.append({
                "feature": feature,
                "value_provided": str(input_value),
                "impact": value, # The raw SHAP value
                "description": f"Your value of '{input_value}' for '{feature}' {direction} your risk."
            })

    # --- === NEW: GENERATE RECOMMENDATIONS === ---
    recommendations = []
    added_advice = set() # To avoid duplicate advice
    
    # Check the top 4 most impactful factors
    for feature, value in sorted_contributions[:4]:
        # If the factor *increased* risk (value > 0) and we have advice for it
        if value > 0 and feature in RECOMMENDATION_MAP:
            if feature not in added_advice:
                recommendations.append({
                    "feature": feature,
                    "advice": RECOMMENDATION_MAP[feature]
                })
                added_advice.add(feature)
    # ---------------------------------------------

    # --- 9. Updated Return Dictionary ---
    return {
        "prediction": int(prediction_raw),
        "probability": float(prediction_proba),
        "risk_category": risk,
        "explanations": explanation_list,
        "base_value": explainer.expected_value[1],
        "recommendations": recommendations  # <--- ADDED
    }
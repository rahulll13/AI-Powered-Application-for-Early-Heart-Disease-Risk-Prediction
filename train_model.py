import pandas as pd
import pickle
import json
import shap  # <--- 1. Import SHAP
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

print("--- Starting Model Training ---")

# 1. Load Data
try:
    df = pd.read_csv("Data/Heartdata.csv")
    print("Dataset loaded successfully.")
except FileNotFoundError:
    print("Error: 'Data/Heartdata.csv' not found. Please ensure the file is in the correct directory.")
    exit()

# 2. Preprocess Data
X = df.drop('target', axis=1)
y = df['target']
X = pd.get_dummies(X)
X = X.fillna(X.median())
model_columns = X.columns.tolist()

# 3. Split Data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print("Data split into training and testing sets.")

# 4. Create and Train the Scikit-learn Pipeline
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
])

print("Training the pipeline (Scaler + RandomForest)...")
pipeline.fit(X_train, y_train)
print("Model training complete.")

# 5. Evaluate the Model
accuracy = pipeline.score(X_test, y_test)
print(f"Model Accuracy on Test Set: {accuracy:.4f}")

# 6. --- NEW: Create and Save SHAP Explainer ---
print("Creating SHAP Explainer...")

# Extract the trained model and scaler from the pipeline
model = pipeline.named_steps['classifier']
scaler = pipeline.named_steps['scaler']

# Scale the training data (SHAP explainer should be fit on the same data format the model was)
# We use pd.DataFrame to keep feature names, which makes explanations readable
X_train_scaled = pd.DataFrame(scaler.transform(X_train), columns=model_columns)

# Create the explainer. shap.Explainer will auto-select the fast TreeExplainer
# We pass X_train_scaled as the "background dataset" to get accurate Shapley values
explainer = shap.Explainer(model, X_train_scaled)

print("SHAP Explainer created.")

# 7. Save the Pipeline, Columns, and NEW Explainer
with open('ml_models/heart_disease_pipeline.pkl', 'wb') as f:
    pickle.dump(pipeline, f)

with open('ml_models/model_columns.json', 'w') as f:
    json.dump(model_columns, f)

# --- NEW: Save the explainer object ---
with open('ml_models/shap_explainer.pkl', 'wb') as f:
    pickle.dump(explainer, f)

print("\n--- Model artifacts saved successfully ---")
print("1. 'ml_models/heart_disease_pipeline.pkl' (the trained pipeline)")
print("2. 'ml_models/model_columns.json' (the required feature list)")
print("3. 'ml_models/shap_explainer.pkl' (the new SHAP explainer)") # <--- 8. Updated print
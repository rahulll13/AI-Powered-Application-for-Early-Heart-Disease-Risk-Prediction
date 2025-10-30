# =============================================================================
# SECTION 1: IMPORT LIBRARIES 
# =============================================================================
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# --- Scikit-learn ---
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder

# Import robust classification models
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier

# Import metrics for evaluation
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score


# =============================================================================
# SECTION 2: CONFIGURATION AND DATA LOADING uploading the csv file path here
# =============================================================================

# --- !!! USER CONFIGURATION !!! ---
# Modify these two lines to point to your data file and target column
file_path = 'Data/Heartdata.csv'        # <--- 1. CHANGE THIS to your CSV file's name
target_column = 'target'          # <--- 2. CHANGE THIS to your target column's name
# --- !!! END OF CONFIGURATION !!! ---

# --- Load Data ---
try:
    df = pd.read_csv('Data/Heartdata.csv')
    print(f"Successfully loaded dataset: '{file_path}'. Shape: {df.shape}")
except FileNotFoundError:
    print(f"Error: The file '{file_path}' was not found.")
    print("For demonstration, a sample risk dataset will be created.")
    # Create a relevant dummy dataset for risk categorization
    data = {
        'credit_score': np.random.randint(300, 850, 500),
        'loan_amount': np.random.uniform(1000, 50000, 500),
        'age': np.random.randint(18, 70, 500),
        'employment_status': np.random.choice(['Employed', 'Self-Employed', 'Unemployed'], 500),
        'debt_to_income_ratio': np.random.uniform(0.1, 0.9, 500),
        'risk_level': np.random.choice(['Low', 'Medium', 'High'], 500, p=[0.5, 0.3, 0.2])
    }
    df = pd.DataFrame(data)
    print("Sample risk dataset created with shape:", df.shape)


# =============================================================================
# SECTION 3: DATA PREPROCESSING AND FEATURE ENGINEERING
# =============================================================================

# --- 1. Handle Categorical Target Variable ---
# ML models require numerical targets. We use LabelEncoder to convert text labels to numbers.
# E.g., 'Low' -> 0, 'Medium' -> 1, 'High' -> 2
le = LabelEncoder()
df[target_column] = le.fit_transform(df[target_column])
# Store the mapping from encoded number back to original label for later use
label_mapping = {index: label for index, label in enumerate(le.classes_)}
print(f"\nTarget variable '{target_column}' has been encoded.")
print("Label mapping:", label_mapping)

# --- 2. Handle Categorical Feature Variables ---
# Convert text-based feature columns into numerical format using one-hot encoding.
df = pd.get_dummies(df, drop_first=True)
print("\nData head after converting all categorical columns:")
print(df.head())

# --- 3. Separate Features (X) and Target (y) ---
try:
    X = df.drop(target_column, axis=1)
    y = df[target_column]
except KeyError:
    print(f"\n[FATAL ERROR] The target column '{target_column}' is not in the dataframe after processing.")
    exit()

# --- 4. Split Data into Training and Test Sets ---
# Using 'stratify=y' ensures that the proportion of risk levels is the same in both train and test sets.
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)

# --- 5. Scale Numerical Features ---
# This standardizes features to have a mean of 0 and a standard deviation of 1.
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

print("\nData preprocessing complete. Data is split and scaled.")
print(f"Training data shape: {X_train.shape}")
print(f"Testing data shape: {X_test.shape}")


# =============================================================================
# SECTION 4: COMPARE MODELS USING CROSS-VALIDATION
# =============================================================================
print("\n--- Starting Model Comparison using 5-Fold Cross-Validation ---")

# Define a dictionary of models to evaluate
models = {
    "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
    "Random Forest": RandomForestClassifier(random_state=42),
    "Gradient Boosting": GradientBoostingClassifier(random_state=42),
    "Support Vector Machine": SVC(random_state=42)
}

# Use 'f1_weighted' as the scoring metric, which is excellent for classification,
# especially with imbalanced classes.
scoring_metric = 'f1_weighted'
results = {}

for model_name, model in models.items():
    scores = cross_val_score(model, X_train, y_train, cv=5, scoring=scoring_metric, n_jobs=-1)
    results[model_name] = {
        'mean_score': scores.mean(),
        'std_dev': scores.std()
    }
    print(f"  - {model_name}: Mean {scoring_metric} = {scores.mean():.4f} (+/- {scores.std():.4f})")

# Display a summary dataframe of the results
results_df = pd.DataFrame(results).T.sort_values(by='mean_score', ascending=False)
print("\n--- Cross-Validation Results Summary ---")
print(results_df)


# =============================================================================
# SECTION 5: FINAL EVALUATION OF THE BEST MODEL
# =============================================================================

# =============================================================================
# SECTION 5: FINAL EVALUATION OF THE BEST MODEL
# =============================================================================

# Select the best performing model from the cross-validation results
best_model_name = results_df.index[0]
best_model = models[best_model_name]

print(f"\n--- Training and Evaluating the Best Model: {best_model_name} ---")

# Train the best model on the entire training dataset
best_model.fit(X_train, y_train)

# Make predictions on the unseen test set
y_pred = best_model.predict(X_test)

# Evaluate the final model's performance
final_accuracy = accuracy_score(y_test, y_pred)
print(f"\nFinal Accuracy on Test Set: {final_accuracy:.4f}")

# Display a detailed classification report (Precision, Recall, F1-Score for each class)
# --- THIS IS THE FIX ---
# We ensure all class names are strings, which is what the report function expects.
target_names = [str(c) for c in le.classes_]

print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=target_names))

# Visualize the confusion matrix
cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='YlGnBu', xticklabels=target_names, yticklabels=target_names)
plt.title(f'Confusion Matrix for {best_model_name}')
plt.xlabel('Predicted Risk Level')
plt.ylabel('Actual Risk Level')
plt.show()

print("\n--- SCRIPT FINISHED ---")
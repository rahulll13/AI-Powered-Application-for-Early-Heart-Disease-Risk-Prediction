# =============================================================================
# SECTION 1: IMPORT NECESSARY LIBRARIES
# =============================================================================
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# --- Scikit-learn ---
# For data handling and preprocessing
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler

# For ML models
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier

# For performance evaluation
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix


# =============================================================================
# SECTION 2: LOAD AND PREPARE YOUR CUSTOM DATASET
# =============================================================================

# --- !!! USER CONFIGURATION !!! ---
# Modify these two lines to point to your data file and target column
file_path = 'Data/HeartData.csv'      # <--- 1. CHANGE THIS to your CSV file's name
target_column = 'target'              # <--- 2. CHANGE THIS to your target column's name
# --- !!! END OF CONFIGURATION !!! ---

# --- Load Data ---
try:
    df = pd.read_csv('Data/HeartData.csv')
    print(f"Successfully loaded dataset: '{file_path}'. Shape: {df.shape}")
except FileNotFoundError:
    print(f"Error: The file '{file_path}' was not found.")
    print("For demonstration, a sample dataset will be created.")
    # Create a dummy dataframe if the specified file is not found
    data = {
        'feature_A': np.random.randn(250) * 10,
        'feature_B': np.random.randn(250) * 5,
        'feature_C': np.random.rand(250) * 20,
        'category_type': ['Type X', 'Type Y', 'Type Z'] * 83 + ['Type X'],
        'target': np.random.randint(0, 2, 250)
    }
    df = pd.DataFrame(data)
    print("Sample dataset created with shape:", df.shape)

# --- Preprocess Data ---

# Handle missing values (you can uncomment and adapt these lines if needed)
# if df.isnull().sum().sum() > 0:
#     print(f"\nMissing values detected. Dropping rows with nulls...")
#     df.dropna(inplace=True)

# Convert categorical features into numerical format using one-hot encoding
# This is crucial for ML models to work correctly.
df = pd.get_dummies(df, drop_first=True)
print("\nData head after converting categorical columns (if any):")
print(df.head())

# --- Separate Features (X) and Target (y) ---
try:
    X = df.drop('target', axis=1)
    y = df['target']
except KeyError:
    print(f"\n[FATAL ERROR] The target column '{target_column}' does not exist in the dataframe.")
    print("Please check the column name. Available columns are:", df.columns.tolist())
    exit() # Stop the script if the target column is invalid

# --- Split data into a full training set and a final test set ---
# The test set is held out until the very end for an unbiased evaluation.
X_train_full, X_test, y_train_full, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=(y if y.nunique() > 1 else None)
)

# --- Scale numerical features ---
# This standardizes the data (mean=0, std=1), which is important for many models.
scaler = StandardScaler()
X_train_full = scaler.fit_transform(X_train_full)
X_test = scaler.transform(X_test)

print(f"\nData preparation complete.")
print(f"Shape of data for cross-validation (X_train_full): {X_train_full.shape}")
print(f"Shape of final test data (X_test): {X_test.shape}")


# =============================================================================
# SECTION 3: PERFORM CROSS-VALIDATION TO COMPARE MODELS
# =============================================================================
print("\n--- Starting Model Comparison using 10-Fold Cross-Validation ---")

# Define a dictionary of machine learning models to evaluate
models_to_evaluate = {
    "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
    "Support Vector Machine": SVC(random_state=42),
    "K-Nearest Neighbors": KNeighborsClassifier(),
    "Decision Tree": DecisionTreeClassifier(random_state=42),
    "Random Forest": RandomForestClassifier(random_state=42),
    "Gradient Boosting": GradientBoostingClassifier(random_state=42)
}

# Dictionary to store the cross-validation results
cv_results = {}
n_folds = 10

# Loop through each model and perform cross-validation
for model_name, model in models_to_evaluate.items():
    # cross_val_score performs the entire K-Fold process automatically
    scores = cross_val_score(model, X_train_full, y_train_full, cv=n_folds, scoring='accuracy', n_jobs=-1)
    
    # Store the mean and standard deviation of the accuracy
    cv_results[model_name] = {
        'mean_accuracy': scores.mean(),
        'std_accuracy': scores.std()
    }
    print(f"  {model_name}: Accuracy = {scores.mean():.4f} (+/- {scores.std():.4f})")

# Create a DataFrame for easy comparison of results
cv_results_df = pd.DataFrame(cv_results).T
cv_results_df = cv_results_df.sort_values(by='mean_accuracy', ascending=False)

print("\n--- Cross-Validation Results Summary ---")
print(cv_results_df)


# =============================================================================
# SECTION 4: FINAL EVALUATION OF THE BEST MODEL
# =============================================================================

# Select the best performing model based on mean cross-validation accuracy
best_model_name = cv_results_df.index[0]
best_model = models_to_evaluate[best_model_name]

print(f"\n--- Training and Evaluating the Best Model: {best_model_name} ---")

# Train the best model on the *entire* available training data
best_model.fit(X_train_full, y_train_full)

# Make predictions on the held-out test set
y_pred_final = best_model.predict(X_test)

# Calculate final performance metrics
final_accuracy = accuracy_score(y_test, y_pred_final)
print(f"\nFinal Accuracy on Unseen Test Set: {final_accuracy:.4f}")

# Display a detailed classification report
print("\nClassification Report:")
print(classification_report(y_test, y_pred_final))

# Visualize the confusion matrix
print("\nConfusion Matrix:")
cm = confusion_matrix(y_test, y_pred_final)
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Greens', cbar=True)
plt.title(f'Confusion Matrix for {best_model_name}')
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.show()

print("\n--- SCRIPT FINISHED ---")
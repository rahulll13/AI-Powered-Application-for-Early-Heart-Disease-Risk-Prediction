import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score

# Load your dataset
df = pd.read_csv("Data/Heartdata.csv")  # Update path if needed

# Check if 'target' column exists
if 'target' not in df.columns:
    raise ValueError("Column 'target' not found in dataset.")

# Drop rows with missing target
df = df.dropna(subset=['target'])

# Separate features and target
X = df.drop('target', axis=1)
y = df['target']

# Convert categorical columns to numeric (if any)
X = pd.get_dummies(X)

# Fill missing values with column median
X = X.fillna(X.median())

# Split data into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create and train the Random Forest model
rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)

# Make predictions
y_pred = rf.predict(X_test)

# Evaluate the model
print("Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))
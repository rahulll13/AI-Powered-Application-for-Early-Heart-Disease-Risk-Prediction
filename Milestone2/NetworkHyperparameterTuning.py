# =============================================================================
# SECTION 1: IMPORT LIBRARIES
# =============================================================================
import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers # type: ignore
import keras_tuner as kt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt

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
    # Create a sample dataframe for a binary classification task
    data = {
        'feature1': np.random.randn(500) * 10, 'feature2': np.random.randn(500) * 5,
        'feature3': np.random.rand(500) * 20,  'feature4': np.random.randn(500),
        'category': ['Type A', 'Type B', 'Type C', 'Type B'] * 125,
        'target': np.random.randint(0, 2, 500)
    }
    df = pd.DataFrame(data)
    print("Sample dataset created with shape:", df.shape)

# --- Preprocess Data ---
# Convert categorical features into numerical format
df = pd.get_dummies(df, drop_first=True)

# Separate Features (X) and Target (y)
try:
    X = df.drop('target', axis=1)
    y = df['target']
except KeyError:
    print(f"\n[FATAL ERROR] The target column '{target_column}' does not exist.")
    print("Available columns are:", df.columns.tolist())
    exit()

# --- Create Three Data Splits: Training, Validation, and Test ---
# 1. First split: separate the test set (e.g., 20%)
X_train_full, X_test, y_train_full, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=(y if y.nunique() > 1 else None))

# 2. Second split: use the remaining data to create a training and a validation set (e.g., 25% of the remainder for validation)
X_train, X_val, y_train, y_val = train_test_split(
    X_train_full, y_train_full, test_size=0.25, random_state=42, stratify=(y_train_full if y_train_full.nunique() > 1 else None))

# --- Scale numerical features ---
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_val = scaler.transform(X_val)
X_test = scaler.transform(X_test)

print("\nData preparation complete.")
print(f"Training data shape: {X_train.shape}")
print(f"Validation data shape: {X_val.shape}")
print(f"Test data shape: {X_test.shape}")


# =============================================================================
# SECTION 3: DEFINE THE HYPERMODEL
# =============================================================================
# This function defines the neural network architecture and the hyperparameters to search.
def build_model(hp):
    model = keras.Sequential()
    
    # Input layer
    model.add(layers.Input(shape=(X_train.shape[1],)))

    # Tune the number of hidden layers and their units
    for i in range(hp.Int('num_layers', 1, 3)): # Search between 1 and 3 hidden layers
        model.add(layers.Dense(
            units=hp.Int(f'units_{i}', min_value=32, max_value=256, step=32), # Search units from 32 to 256
            activation='relu'
        ))
        # Tune whether to add a Dropout layer
        if hp.Boolean(f'dropout_{i}'):
            model.add(layers.Dropout(rate=hp.Float(f'dropout_rate_{i}', min_value=0.1, max_value=0.5, step=0.1)))

    # Output layer
    # For binary classification, use 1 unit and 'sigmoid' activation.
    # For multi-class, use `y.nunique()` units and 'softmax'.
    # For regression, use 1 unit and no activation.
    model.add(layers.Dense(1, activation='sigmoid'))

    # Tune the learning rate for the optimizer
    hp_learning_rate = hp.Choice('learning_rate', values=[1e-2, 1e-3, 1e-4])

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=hp_learning_rate),
        loss='binary_crossentropy', # Use 'categorical_crossentropy' for multi-class, 'mse' for regression
        metrics=['accuracy'] # Use 'mae' or 'mse' for regression
    )
    return model


# =============================================================================
# SECTION 4: INSTANTIATE AND RUN THE TUNER
# =============================================================================
print("\n--- Starting Hyperparameter Search ---")

# Instantiate the tuner. RandomSearch is a good starting point.
# The objective is to maximize validation accuracy ('val_accuracy').
tuner = kt.RandomSearch(
    build_model,
    objective='val_accuracy',
    max_trials=15,  # Total number of different hyperparameter combinations to test
    executions_per_trial=2,  # Number of times to train each combination (for robustness)
    directory='keras_tuner_dir',
    project_name='my_nn_tuning'
)

# Add an EarlyStopping callback to prevent overfitting and save time
stop_early = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=5)

# Start the search process
tuner.search(X_train, y_train, epochs=50, validation_data=(X_val, y_val), callbacks=[stop_early])

# Get the optimal hyperparameters
best_hps = tuner.get_best_hyperparameters(num_trials=1)[0]

print("\n--- Hyperparameter Search Complete ---")
print(f"""
The optimal number of layers is {best_hps.get('num_layers')}.
The optimal learning rate for the optimizer is {best_hps.get('learning_rate')}.
""")
# You can print other found hyperparameters similarly.
print("Full optimal hyperparameters:")
print(best_hps.values)


# =============================================================================
# SECTION 5: TRAIN AND EVALUATE THE BEST MODEL
# =============================================================================
print("\n--- Training the Best Model on the Full Training Data ---")

# Build the model with the best hyperparameters
best_model = tuner.hypermodel.build(best_hps)

# Retrain the model on the combined training and validation data for more robust learning
history = best_model.fit(
    X_train_full, y_train_full,
    epochs=100, # Train for more epochs on the final model
    validation_split=0.2, # Use a portion of the full data for validation during this final training
    callbacks=[stop_early] # Use early stopping again
)

print("\n--- Final Evaluation on the Unseen Test Set ---")
loss, accuracy = best_model.evaluate(X_test, y_test)
print(f"Test Accuracy: {accuracy:.4f}")

# Make predictions
y_pred_proba = best_model.predict(X_test)
y_pred = (y_pred_proba > 0.5).astype("int32") # Convert probabilities to binary classes

# Display detailed report
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# Visualize the confusion matrix
print("\nConfusion Matrix:")
cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
plt.title(f'Final Model Confusion Matrix')
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.show()
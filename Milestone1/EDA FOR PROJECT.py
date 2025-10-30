# --- Import necessary libraries ---
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import numpy as np


def perform_eda(filepath): 
    # =========================================================================
    # STEP 1: DATA LOADING AND INITIAL INSPECTION
    # =========================================================================
    
    print(f"\nReading data from: {filepath}")
    try:
        df = pd.read_csv('Data/Heartdata.csv')
    except FileNotFoundError:
        print(f"Error: The file '{filepath}' was not found. Please check the path and filename and try again.")
        return
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return

    print("Data loaded successfully!")

    print("\n--- 1. Initial Data Inspection ---")
    print("\nFirst 5 Rows:")
    print(df.head())
    print(f"\nShape of the dataset (Rows, Columns): {df.shape}")
    print("\nData Types and Non-Null Values:")
    df.info()

    
    # =========================================================================
    # STEP 2: DESCRIPTIVE STATISTICS
    # =========================================================================
    
    print("\n--- 2. Descriptive Statistics ---")
    print("\nFor Numerical Columns:")
    print(df.describe())
    
    try:
        print("\nFor Categorical Columns:")
        print(df.describe(include=['object', 'category']))
    except ValueError:
        print("No categorical columns found to describe.")


    # =========================================================================
    # STEP 3: MISSING VALUES ANALYSIS
    # =========================================================================
    
    print("\n--- 3. Missing Values Count ---")
    missing_values = df.isnull().sum()
    print("Columns with missing values:")
    print(missing_values[missing_values > 0].sort_values(ascending=False))


    # =========================================================================
    # STEP 4: DATA VISUALIZATION (MODIFIED TO DISPLAY PLOTS)
    # =========================================================================
    
    print("\n--- 4. Generating and Displaying Plots ---")
    # --- IMPORTANT INSTRUCTION FOR THE USER ---
    print("\n>>> IMPORTANT: Close each plot window that appears to proceed to the next one. <<<")
    
    output_dir = "EDA_Plots"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    print(f"\nPlots will also be saved in the '{output_dir}' directory for your records.")

    numerical_cols = df.select_dtypes(include=np.number).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

    # --- Histograms for Numerical Columns ---
    for col in numerical_cols:
        plt.figure(figsize=(10, 6))
        sns.histplot(df[col], kde=True, bins=30)
        plt.title(f'Histogram of {col}')
        plt.xlabel(col)
        plt.ylabel('Frequency')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f'{col}_histogram.png'))
        plt.show() # This line displays the plot
        plt.close() # Closes the figure to free up memory

    # --- Count Plots for Categorical Columns ---
    for col in categorical_cols:
        plt.figure(figsize=(12, 7))
        sns.countplot(y=col, data=df, order=df[col].value_counts().index)
        plt.title(f'Count Plot of {col}')
        plt.xlabel('Count')
        plt.ylabel(col)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f'{col}_countplot.png'))
        plt.show() # This line displays the plot
        plt.close()

    # --- Correlation Heatmap for Numerical Columns ---
    if len(numerical_cols) > 1:
        plt.figure(figsize=(12, 8))
        correlation_matrix = df[numerical_cols].corr()
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f')
        plt.title('Correlation Matrix of Numerical Columns')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'correlation_heatmap.png'))
        plt.show() # This line displays the plot
        plt.close()

    print("\nEDA complete. All plots have been displayed and saved successfully.")


# =========================================================================
# SCRIPT ENTRY POINT
# =========================================================================
if __name__ == "__main__":
    
    DATA_FOLDER = "data"

    if not os.path.isdir(DATA_FOLDER):
        print(f"--- SETUP ERROR ---")
        print(f"A folder named '{DATA_FOLDER}' was not found in this directory.")
        print(f"Please create a '{DATA_FOLDER}' folder, place your CSV file inside it, and run the script again.")
    else:
        filename = input(f"Enter the filename of your CSV (must be in the '{DATA_FOLDER}' folder): ").strip()
        full_path = os.path.join(DATA_FOLDER, filename)
        perform_eda(full_path)
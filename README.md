# AI-Powered-Application-For-Early-Heart-Disease-Risk-Prediction

AI Powered Application used to Predict early risk of heart disease using an explainable AI model along with a simple web interface. This repository contains code for data processing, model training, inference, and a small web app to let users enter health parameters and receive a risk estimate.

## Table of Contents
- Overview
- Features
- Quick Demo
- Getting Started
  - Prerequisites
  - Installation
  - Running locally
- Usage
  - Web UI
  - API
- Data & Model
  - Dataset (example)
  - Training
  - Inference
- Configuration
- Tests
- Contributing
- License
- Contact
- Acknowledgements

## Overview
This project aims to provide an accessible, auditable pipeline for early heart disease risk prediction. It uses classical ML (and/or deep learning) with standard health features to produce risk scores and basic explanations so clinicians and users can understand model outputs.

## Features
High-Accuracy Prediction: Utilizes a RandomForestClassifier with 98.5% accuracy on the validation set to predict heart disease risk based on 13 clinical features.

Explainable AI (XAI): Integrates the SHAP library to provide clear, user-friendly explanations for each prediction, building trust by showing which factors (e.g., cholesterol, age) contributed most to the risk score.

Personalized Recommendations: A dynamic recommendation engine that parses the XAI results and generates actionable health advice tailored to the user's specific risk factors.

Secure User Authentication: Full user registration and login system with secure, stateless authentication using JSON Web Tokens (JWT).

Document Management with OCR: Users can upload medical documents (images or PDFs), with Tesseract OCR automatically extracting text for their records.

PDF Report Generation: Users can download a PDF summary of their prediction results for their records or to share with a healthcare provider.

Role-Based Access: Includes a "Doctor" role with a separate dashboard to view a list of registered patients.

## Quick Demo
1. Start the app (instructions below).
2. Open the web UI at http://localhost:5000 (or the port configured).
3. Enter patient features and get a risk score with a short explanation.

## Getting Started

### Prerequisites
- Python 3.8+
- pip
- Tesseract OCR
- Installation instructions can be found on the official Tesseract GitHub. You must update the path in config.py.
- Recommended: virtualenv or venv

### Installation and setup
Clone the repo:
```bash
git clone https://github.com/rahulll13/AI-Powered-Application-for-Early-Heart-Disease-Risk-Prediction-Application.git
cd AI-Powered-Application-for-Early-Heart-Disease-Risk-Prediction-Application
```

### Create and activate a virtual environment:
```bash
# for windows
python -m venv venv
.\venv\Scripts\Activate.ps1
```
### Configure environment variables: Create a .env file in the root directory. Use the .env.example as a template and add your credentials.
```bash
# .env file
SECRET_KEY='a-very-secret-key'

# For Gmail, you may need an App Password
MAIL_USERNAME='your-email@gmail.com'
MAIL_PASSWORD='your-email-password'
```
### Initialize the database:
```bash
flask db init
flask db migrate -m "Initial migration."
flask db upgrade
```
### Train the ML Model: This is a critical step. Run the training script to generate the serialized model and explainer files.
```bash
python train_model.py
```
### Running the application
Use the provided utility script to launch both the backend and frontend servers concurrently.:
```bash
python start_servers.py
```
Then open http://localhost:5000 in your browser.

## Usage

### Web UI
- Fill in patient information (age, sex, blood pressure, cholesterol, etc.)
- Submit to receive a risk score and short explanation/high-level feature contributions.

### API (example)
A sample POST request to the model endpoint:
```bash
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "age": 54,
    "sex": 1,
    "cp": 3,
    "trestbps": 140,
    "chol": 239,
    "fbs": 0,
    "restecg": 1,
    "thalach": 160,
    "exang": 0,
    "oldpeak": 1.2,
    "slope": 2,
    "ca": 0,
    "thal": 2
  }'
```
Response (example):
```json
{
  "risk_score": 0.72,
  "risk_level": "High",
  "explanation": {
    "top_features": {
      "age": 0.22,
      "chol": 0.18,
      "thalach": -0.15
    }
  }
}
```

Note: The exact input schema and keys depend on the implementation. See `api/` or `app.py` for exact details.

## Data & Model

### Dataset (example)
This project is compatible with common heart disease datasets (for example, the UCI Heart Disease dataset). Place datasets in a `data/` directory and follow the preprocessing script expectations.

### Training
A training script is expected at `scripts/train.py` or `train.py`. Typical steps:
1. Load and split the dataset
2. Preprocess features
3. Train model(s)
4. Evaluate and save the best model to `models/`

Example run:
```bash
python scripts/train.py --data data/heart.csv --output models/
```

### Inference
Saved model files are loaded by the web app / API to perform inference. Models should be versioned and stored in `models/` with clear naming.

## Configuration
Use environment variables or a config file (e.g., `.env` or `config.yaml`) for:
- FLASK_ENV, FLASK_APP
- MODEL_PATH
- SECRET_KEY
- PORT

Example `.env`:
```
FLASK_ENV=development
MODEL_PATH=models/best_model.pkl
PORT=5000
```
## Contributing
Contributions are welcome. Typical workflow:
1. Fork the repository
2. Create a feature branch: git checkout -b feature/awesome
3. Commit changes and push
4. Open a pull request describing changes and motivation

Please follow repository coding style and add tests for new functionality.

## License
This project is provided under the MIT License — see the LICENSE file for details.

## Contact
GitHub: https://github.com/rahulll13
Email: sinha.rahul2318@gmail.com

## Acknowledgements
- This project was developed as part of the Infosys Springboard Virtual Internship Program.
- Thanks to the open-source community for the incredible libraries that made this project possible.

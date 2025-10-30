# run.py
from app import create_app, db
from app.models import User, Prediction, MedicalDocument

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Prediction': Prediction, 'MedicalDocument': MedicalDocument}
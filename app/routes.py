# app/routes.py

import os
import secrets
from PIL import Image
from flask import request, jsonify, current_app, send_file
from flask_restful import Resource, reqparse
from werkzeug.utils import secure_filename

from app import db, mail
from app.decorators import doctor_required
from .models import User, Prediction, MedicalDocument
from .services import prediction_service, ocr_service, pdf_service

from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_mail import Message


# Helper Function
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

# --- API Resource Classes ---

class Home(Resource):
    def get(self):
        return {'message': 'Welcome to the Heart Disease Detection API!'}, 200


# ... (Helper function and other Resource classes like Home, HealthCheck, ApiStatus are unchanged) ...

# --- THIS CLASS IS NOW SIMPLIFIED ---
class UserRegistration(Resource):
    """Endpoint for new user registration. Users will default to the 'Patient' role."""
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True, help='Username cannot be blank')
        parser.add_argument('email', type=str, required=True, help='Email cannot be blank')
        parser.add_argument('password', type=str, required=True, help='Password cannot be blank')
        args = parser.parse_args()
        if User.query.filter_by(username=args['username']).first():
            return {'message': 'Username already exists'}, 400
        if User.query.filter_by(email=args['email']).first():
            return {'message': 'Email already exists'}, 400
        # User role defaults to 'Patient' as per the model definition
        new_user = User(username=args['username'], email=args['email'])
        new_user.set_password(args['password'])
        db.session.add(new_user)
        db.session.commit()
        return {'message': 'User registered successfully'}, 201

class UserLogin(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True, help='Username cannot be blank')
        parser.add_argument('password', type=str, required=True, help='Password cannot be blank')
        args = parser.parse_args()
        user = User.query.filter_by(username=args['username']).first()
        if user and user.check_password(args['password']):
            access_token = create_access_token(identity=str(user.id))
            return {'access_token': access_token}, 200
        return {'message': 'Invalid credentials'}, 401

class PredictionAPI(Resource):
    @jwt_required()
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('age', type=int, required=True)
        parser.add_argument('sex', type=int, required=True)
        parser.add_argument('cp', type=int, required=True)
        parser.add_argument('trestbps', type=int, required=True)
        parser.add_argument('chol', type=int, required=True)
        parser.add_argument('fbs', type=int, required=True)
        parser.add_argument('restecg', type=int, required=True)
        parser.add_argument('thalach', type=int, required=True)
        parser.add_argument('exang', type=int, required=True)
        parser.add_argument('oldpeak', type=float, required=True)
        parser.add_argument('slope', type=int, required=True)
        parser.add_argument('ca', type=int, required=True)
        parser.add_argument('thal', type=int, required=True)
        args = parser.parse_args()
        result = prediction_service.predict(args)
        current_user_id = get_jwt_identity()
        prediction_record = Prediction(user_id=int(current_user_id), prediction_result=result['prediction'], risk_category=result['risk_category'])
        db.session.add(prediction_record)
        db.session.commit()
        return result, 200

class ForgotPassword(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, required=True)
        args = parser.parse_args()
        user = User.query.filter_by(email=args['email']).first()
        if user:
            token = user.get_reset_token()
            msg = Message('Password Reset Request', sender='noreply@demo.com', recipients=[user.email])
            msg.body = f'To reset your password, please use the following token:\n{token}\nIf you did not make this request then simply ignore this email.'
            mail.send(msg)
        return {'message': 'If an account with that email exists, a password reset link has been sent.'}, 200

class ResetPassword(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('token', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        args = parser.parse_args()
        user = User.verify_reset_token(args['token'])
        if user is None:
            return {'message': 'That is an invalid or expired token'}, 400
        user.set_password(args['password'])
        db.session.commit()
        return {'message': 'Your password has been successfully updated!'}, 200

class DocumentUpload(Resource):
    @jwt_required()
    def post(self):
        if 'document' not in request.files:
            return {'message': 'No document part in the request'}, 400
        file = request.files['document']
        if file.filename == '':
            return {'message': 'No selected file'}, 400
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            extracted_text = ocr_service.extract_text_from_image(filepath)
            current_user_id = get_jwt_identity()
            new_document = MedicalDocument(filename=filename, filepath=filepath, user_id=int(current_user_id), ocr_text=extracted_text)
            db.session.add(new_document)
            db.session.commit()
            return {'message': 'Document uploaded and processed successfully', 'filename': filename, 'extracted_text': extracted_text.strip()}, 201
        else:
            return {'message': 'File type not allowed'}, 400

class DocumentList(Resource):
    @jwt_required()
    def get(self):
        current_user_id = get_jwt_identity()
        user_id = int(current_user_id)
        documents = MedicalDocument.query.filter_by(user_id=user_id).all()
        output = []
        for doc in documents:
            doc_data = {'id': doc.id, 'filename': doc.filename, 'upload_timestamp': doc.upload_timestamp.isoformat(), 'ocr_text': doc.ocr_text}
            output.append(doc_data)
        return jsonify(output)

class DocumentResource(Resource):
    @jwt_required()
    def get(self, doc_id):
        current_user_id = get_jwt_identity()
        doc = MedicalDocument.query.get_or_404(doc_id)
        if str(doc.user_id) != current_user_id:
            return {'message': 'Permission denied'}, 403
        return jsonify({'id': doc.id, 'filename': doc.filename, 'upload_timestamp': doc.upload_timestamp.isoformat(), 'ocr_text': doc.ocr_text})

    @jwt_required()
    def delete(self, doc_id):
        current_user_id = get_jwt_identity()
        doc = MedicalDocument.query.get_or_404(doc_id)
        if str(doc.user_id) != current_user_id:
            return {'message': 'Permission denied'}, 403
        try:
            os.remove(doc.filepath)
        except OSError as e:
            print(f"Error deleting file {doc.filepath}: {e}")
        db.session.delete(doc)
        db.session.commit()
        return {'message': 'Document deleted successfully'}, 200

class PredictionList(Resource):
    @jwt_required()
    def get(self):
        current_user_id = get_jwt_identity()
        user_id = int(current_user_id)
        predictions = Prediction.query.filter_by(user_id=user_id).order_by(Prediction.timestamp.desc()).all()
        output = []
        for pred in predictions:
            pred_data = {'id': pred.id, 'prediction_result': pred.prediction_result, 'risk_category': pred.risk_category, 'timestamp': pred.timestamp.isoformat()}
            output.append(pred_data)
        return jsonify(output)

class PredictionReport(Resource):
    @jwt_required()
    def get(self, pred_id):
        current_user_id = get_jwt_identity()
        pred = Prediction.query.get_or_404(pred_id)
        if str(pred.user_id) != current_user_id:
            return {'message': 'Permission denied'}, 403
        user_id = int(current_user_id)
        user = User.query.get(user_id)
        if not user:
             return {'message': 'User not found'}, 404
        pdf_buffer = pdf_service.create_prediction_report(pred, user)
        return send_file(pdf_buffer, as_attachment=True, download_name=f'prediction_report_{pred.id}.pdf', mimetype='application/pdf')

class UserProfile(Resource):
    @jwt_required()
    def get(self):
        current_user_id = get_jwt_identity()
        user_id = int(current_user_id)
        user = User.query.get_or_404(user_id)

        # Get all predictions for the user
        user_predictions = user.predictions.all()

        # Calculate the streak
        streak = prediction_service.calculate_streak(user_predictions)

        # The profile_image_url is no longer returned
        return jsonify({
            'username': user.username, 
            'email': user.email,
            'prediction_count': len(user_predictions),
            'prediction_streak': streak # Return the new streak data
        })

class ProfilePictureUpload(Resource):
    @jwt_required()
    def post(self):
        current_user_id = get_jwt_identity()
        user = User.query.get_or_404(int(current_user_id))
        if 'picture' not in request.files:
            return {'message': 'No picture part in the request'}, 400
        file = request.files['picture']
        if file.filename == '':
            return {'message': 'No selected file'}, 400
        if file and allowed_file(file.filename):
            random_hex = secrets.token_hex(8)
            _, f_ext = os.path.splitext(file.filename)
            picture_fn = random_hex + f_ext
            profile_pics_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'profile_pics')
            os.makedirs(profile_pics_path, exist_ok=True)
            picture_path = os.path.join(profile_pics_path, picture_fn)
            output_size = (150, 150)
            i = Image.open(file)
            i.thumbnail(output_size)
            i.save(picture_path)
            user.profile_image_file = picture_fn
            db.session.commit()
            return {'message': 'Profile picture updated!'}, 200
        else:
            return {'message': 'File type not allowed'}, 400
        
class PatientList(Resource):
    @doctor_required
    def get(self):
        # This endpoint is protected, only users with 'Doctor' role can access it.
        # Query the database for all users where the role is 'Patient'.
        patients = User.query.filter_by(role='Patient').all()
        
        output = []
        for patient in patients:
            patient_data = {
                'id': patient.id,
                'username': patient.username,
                'email': patient.email,
                'prediction_count': patient.predictions.count()
            }
            output.append(patient_data)
            
        return jsonify(output)

class PatientResource(Resource):
    @doctor_required
    def delete(self, patient_id):
        # Find the user to be deleted
        patient = User.query.get_or_404(patient_id)

        # Security check: ensure the user being deleted is a 'Patient'
        if patient.role != 'Patient':
            return {'message': 'Cannot delete a user who is not a patient.'}, 403

        # Delete the user from the database
        db.session.delete(patient)
        db.session.commit()
        return {'message': f'Patient {patient.username} has been successfully removed.'}, 200


# --- Function to Initialize All Routes ---
def initialize_routes(api):
    api.add_resource(Home, '/')
    api.add_resource(UserRegistration, '/register')
    api.add_resource(UserLogin, '/login')
    api.add_resource(PredictionAPI, '/predict')
    api.add_resource(ForgotPassword, '/forgot-password')
    api.add_resource(ResetPassword, '/reset-password')
    api.add_resource(DocumentUpload, '/upload-document')
    api.add_resource(DocumentList, '/documents')
    api.add_resource(DocumentResource, '/documents/<int:doc_id>')
    api.add_resource(PredictionList, '/predictions')
    api.add_resource(PredictionReport, '/predictions/<int:pred_id>/export')
    api.add_resource(UserProfile, '/profile')
    api.add_resource(ProfilePictureUpload, '/profile/picture')
    api.add_resource(PatientList, '/doctor/patients')
    api.add_resource(PatientResource, '/doctor/patients/<int:patient_id>')

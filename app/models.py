from app import db, bcrypt
from flask import current_app
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(10), index=True, default='Patient')
    
    # The 'profile_image_file' column has been removed.
    
    predictions = db.relationship('Prediction', backref='author', lazy='dynamic')
    documents = db.relationship('MedicalDocument', backref='owner', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def get_reset_token(self):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps(self.id, salt='password-reset-salt')

    @staticmethod
    def verify_reset_token(token, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, salt='password-reset-salt', max_age=expires_sec)
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f'<User {self.username}>'

class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prediction_result = db.Column(db.Integer, nullable=False)
    risk_category = db.Column(db.String(64))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<Prediction {self.id} - Result: {self.prediction_result}>'

class MedicalDocument(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(128), nullable=False)
    filepath = db.Column(db.String(256), nullable=False)
    upload_timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    ocr_text = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<MedicalDocument {self.filename}>'

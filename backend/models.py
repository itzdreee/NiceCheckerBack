from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class User(db.Model):
    """Modelo de Usuario"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    analyses = db.relationship('Analysis', backref='user', lazy=True)
    
    def set_password(self, password):
        """Encripta la contraseña usando bcrypt con salt automático"""
        import bcrypt
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
    
    def check_password(self, password):
        """Verifica la contraseña de forma segura"""
        import bcrypt
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash)
    
    def to_dict(self):
        """Convierte el usuario a diccionario (sin datos sensibles)"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'analysis_count': len(self.analyses),
            'is_active': self.is_active
        }

class Analysis(db.Model):
    """Modelo de Análisis de Imágenes"""
    __tablename__ = 'analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    location_exposure = db.Column(db.String(20), nullable=False)
    body_exposure = db.Column(db.String(20), nullable=False)
    has_gps = db.Column(db.Boolean, default=False)
    gps_coordinates = db.Column(db.String(100))
    location_details = db.Column(db.Text)  # JSON string
    has_faces = db.Column(db.Boolean, default=False)
    face_count = db.Column(db.Integer, default=0)
    exposure_details = db.Column(db.Text)  # JSON string
    recommendations = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_location_details(self, details_list):
        """Guarda los detalles de ubicación como JSON"""
        self.location_details = json.dumps(details_list)
    
    def get_location_details(self):
        """Obtiene los detalles de ubicación del JSON"""
        if self.location_details:
            return json.loads(self.location_details)
        return []
    
    def set_exposure_details(self, details_list):
        """Guarda los detalles de exposición como JSON"""
        self.exposure_details = json.dumps(details_list)
    
    def get_exposure_details(self):
        """Obtiene los detalles de exposición del JSON"""
        if self.exposure_details:
            return json.loads(self.exposure_details)
        return []
    
    def set_recommendations(self, recommendations_list):
        """Guarda las recomendaciones como JSON"""
        self.recommendations = json.dumps(recommendations_list)
    
    def get_recommendations(self):
        """Obtiene las recomendaciones del JSON"""
        if self.recommendations:
            return json.loads(self.recommendations)
        return []
    
    def to_dict(self):
        """Convierte el análisis a diccionario"""
        return {
            'id': self.id,
            'location_exposure': self.location_exposure,
            'body_exposure': self.body_exposure,
            'has_gps': self.has_gps,
            'gps_coordinates': self.gps_coordinates,
            'has_faces': self.has_faces,
            'face_count': self.face_count,
            'created_at': self.created_at.isoformat()
        }

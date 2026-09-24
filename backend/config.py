import os
from datetime import timedelta

class Config:
    """Configuración principal de la aplicación"""
    
    # Seguridad
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-change-in-production')
    JWT_EXPIRATION_HOURS = 24
    
    # Base de datos - compatible con Railway PostgreSQL y desarrollo local SQLite
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///users.db')
    if DATABASE_URL.startswith('postgres://'):
        SQLALCHEMY_DATABASE_URI = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    else:
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Archivos
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    # CORS - permite localhost (desarrollo) y dominios de producción
    FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:3000')
    CORS_ORIGINS = FRONTEND_URL
    
    # Rate limiting
    RATE_LIMIT_DEFAULT = "200 per day"
    RATE_LIMIT_PER_HOUR = "50 per hour"
    
    # Rate limits específicos por endpoint
    RATE_LIMIT_REGISTER = "5 per hour"
    RATE_LIMIT_LOGIN = "10 per hour"
    RATE_LIMIT_ANALYZE = "30 per hour"
    
    # Puerto para Railway
    PORT = int(os.environ.get('PORT', 5000))

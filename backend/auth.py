import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
from models import User, db
from config import Config

def generate_token(user_id):
    """Genera un token JWT seguro"""
    expiration = datetime.utcnow() + timedelta(hours=Config.JWT_EXPIRATION_HOURS)
    token = jwt.encode({
        'user_id': user_id,
        'exp': expiration
    }, Config.JWT_SECRET_KEY, algorithm='HS256')
    return token

def token_required(f):
    """Decorador para proteger rutas que requieren autenticación"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'Token de autenticación requerido'}), 401
        
        try:
            # Extraer el token del header "Bearer <token>"
            if token.startswith('Bearer '):
                token = token[7:]
            
            # Decodificar y verificar el token
            data = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
            
            if not current_user or not current_user.is_active:
                return jsonify({'error': 'Token inválido o usuario inactivo'}), 401
                
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token inválido'}), 401
        except Exception as e:
            return jsonify({'error': 'Error de autenticación'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated

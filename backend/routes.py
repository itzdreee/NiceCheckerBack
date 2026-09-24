from flask import request, jsonify
from werkzeug.utils import secure_filename
import os
from email_validator import validate_email, EmailNotValidError
from models import User, Analysis, db
from auth import token_required, generate_token
from image_analysis import analyze_exif_data, analyze_body_exposure, generate_recommendations
from config import Config
import logging

logger = logging.getLogger(__name__)

def allowed_file(filename):
    """Verifica que el archivo tenga una extensión permitida de forma segura"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def register():
    """Registro de usuarios con encriptación de contraseña y validación de email"""
    try:
        data = request.get_json()
        
        # Validaciones básicas
        if not data or not data.get('username') or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Todos los campos son requeridos'}), 400
        
        username = data['username'].strip()
        email = data['email'].strip().lower()
        password = data['password']
        
        # Validar formato de email
        try:
            validate_email(email)
        except EmailNotValidError:
            logger.warning(f'Email inválido en registro: {email}')
            return jsonify({'error': 'Formato de email inválido'}), 400
        
        # Validar longitud de contraseña
        if len(password) < 8:
            return jsonify({'error': 'La contraseña debe tener al menos 8 caracteres'}), 400
        
        # Validar complejidad de contraseña
        if not any(c.isupper() for c in password):
            return jsonify({'error': 'La contraseña debe contener al menos una mayúscula'}), 400
        
        if not any(c.islower() for c in password):
            return jsonify({'error': 'La contraseña debe contener al menos una minúscula'}), 400
        
        if not any(c.isdigit() for c in password):
            return jsonify({'error': 'La contraseña debe contener al menos un número'}), 400
        
        # Validar nombre de usuario
        if len(username) < 3 or len(username) > 20:
            return jsonify({'error': 'El nombre de usuario debe tener entre 3 y 20 caracteres'}), 400
        
        if not username.isalnum():
            return jsonify({'error': 'El nombre de usuario solo puede contener letras y números'}), 400
        
        # Verificar si el usuario ya existe
        if User.query.filter_by(username=username).first():
            logger.warning(f'Intento de registro con usuario existente: {username}')
            return jsonify({'error': 'El nombre de usuario ya existe'}), 409
        
        if User.query.filter_by(email=email).first():
            logger.warning(f'Intento de registro con email existente: {email}')
            return jsonify({'error': 'El email ya está registrado'}), 409
        
        # Crear nuevo usuario
        user = User(username=username, email=email)
        user.set_password(password)  # Encripta la contraseña con bcrypt
        
        db.session.add(user)
        db.session.commit()
        
        logger.info(f'Nuevo usuario registrado: {username}')
        
        return jsonify({
            'message': 'Usuario registrado exitosamente',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error en registro: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

def login():
    """Inicio de sesión con verificación de contraseña encriptada"""
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Usuario y contraseña son requeridos'}), 400
        
        username = data['username'].strip()
        password = data['password']
        
        # Buscar usuario
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            logger.warning(f'Intento de login fallido: {username}')
            return jsonify({'error': 'Credenciales inválidas'}), 401
        
        if not user.is_active:
            logger.warning(f'Intento de login con usuario inactivo: {username}')
            return jsonify({'error': 'Usuario inactivo'}), 403
        
        # Actualizar último login
        from datetime import datetime
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Generar token JWT
        token = generate_token(user.id)
        
        logger.info(f'Login exitoso: {username}')
        
        return jsonify({
            'message': 'Login exitoso',
            'token': token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        }), 200
        
    except Exception as e:
        logger.error(f'Error en login: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

def logout(current_user):
    """Cierre de sesión (el cliente debe eliminar el token)"""
    try:
        logger.info(f'Logout: {current_user.username}')
        return jsonify({'message': 'Sesión cerrada exitosamente'}), 200
    except Exception as e:
        logger.error(f'Error en logout: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

def get_current_user(current_user):
    """Obtener información del usuario actual"""
    try:
        return jsonify({
            'user': current_user.to_dict()
        }), 200
    except Exception as e:
        logger.error(f'Error al obtener usuario: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

def analyze_image(current_user):
    """Endpoint para analizar imágenes de forma segura (requiere autenticación)"""
    try:
        # Verificar que se envió un archivo
        if 'file' not in request.files:
            logger.warning(f'Intento de análisis sin archivo por usuario: {current_user.username}')
            return jsonify({'error': 'No se proporcionó ningún archivo'}), 400
        
        file = request.files['file']
        
        # Verificar que el archivo tiene nombre
        if file.filename == '':
            logger.warning(f'Archivo sin nombre por usuario: {current_user.username}')
            return jsonify({'error': 'Archivo sin nombre'}), 400
        
        # Verificar extensión de forma segura
        if not allowed_file(file.filename):
            logger.warning(f'Intento de subir archivo no permitido: {file.filename} por usuario: {current_user.username}')
            return jsonify({'error': 'Tipo de archivo no permitido'}), 400
        
        # Sanitizar el nombre del archivo
        filename = secure_filename(file.filename)
        
        # Crear directorio de uploads si no existe
        if not os.path.exists(Config.UPLOAD_FOLDER):
            os.makedirs(Config.UPLOAD_FOLDER)
        
        # Guardar archivo de forma segura
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        logger.info(f'Archivo recibido y guardado: {filename} por usuario: {current_user.username}')
        
        # Análisis real de la imagen con IA
        exif_analysis = analyze_exif_data(filepath)
        body_analysis = analyze_body_exposure(filepath)
        recommendations = generate_recommendations(exif_analysis, body_analysis)
        
        # Guardar análisis en la base de datos
        analysis = Analysis(
            user_id=current_user.id,
            location_exposure=exif_analysis['location_exposure'],
            body_exposure=body_analysis['body_exposure'],
            has_gps=exif_analysis['has_gps'],
            gps_coordinates=exif_analysis['gps_coordinates'],
            has_faces=body_analysis['has_faces'],
            face_count=body_analysis['face_count']
        )
        
        analysis.set_location_details(exif_analysis.get('location_details', []))
        analysis.set_exposure_details(body_analysis.get('exposure_details', []))
        analysis.set_recommendations(recommendations)
        
        db.session.add(analysis)
        db.session.commit()
        
        result = {
            'location_exposure': exif_analysis['location_exposure'],
            'body_exposure': body_analysis['body_exposure'],
            'has_gps': exif_analysis['has_gps'],
            'gps_coordinates': exif_analysis['gps_coordinates'],
            'location_details': exif_analysis.get('location_details', []),
            'has_faces': body_analysis['has_faces'],
            'face_count': body_analysis['face_count'],
            'exposure_details': body_analysis.get('exposure_details', []),
            'recommendations': recommendations,
            'analyzed_by': current_user.username,
            'analysis_id': analysis.id
        }
        
        # Eliminar el archivo después del análisis por seguridad
        os.remove(filepath)
        
        logger.info(f'Análisis completado para usuario: {current_user.username}')
        
        return jsonify(result), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error en análisis por usuario {current_user.username}: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

def get_user_analyses(current_user):
    """Obtener historial de análisis del usuario"""
    try:
        # Obtener los últimos 20 análisis
        analyses = Analysis.query.filter_by(user_id=current_user.id)\
            .order_by(Analysis.created_at.desc())\
            .limit(20)\
            .all()
        
        analyses_data = []
        for analysis in analyses:
            analyses_data.append({
                'id': analysis.id,
                'location_exposure': analysis.location_exposure,
                'body_exposure': analysis.body_exposure,
                'has_gps': analysis.has_gps,
                'has_faces': analysis.has_faces,
                'face_count': analysis.face_count,
                'created_at': analysis.created_at.isoformat()
            })
        
        return jsonify({
            'analyses': analyses_data,
            'total': len(current_user.analyses)
        }), 200
        
    except Exception as e:
        logger.error(f'Error al obtener análisis del usuario: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

def delete_account(current_user):
    """Eliminar cuenta de usuario y todos sus datos"""
    try:
        # Eliminar todos los análisis del usuario
        Analysis.query.filter_by(user_id=current_user.id).delete()
        
        # Eliminar usuario
        db.session.delete(current_user)
        db.session.commit()
        
        logger.info(f'Cuenta eliminada: {current_user.username}')
        
        return jsonify({'message': 'Cuenta eliminada exitosamente'}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error al eliminar cuenta: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

def health_check():
    """Endpoint para verificar que el servidor está funcionando"""
    return jsonify({'status': 'healthy', 'message': 'Backend funcionando correctamente'}), 200

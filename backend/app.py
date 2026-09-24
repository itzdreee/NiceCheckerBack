from flask import Flask
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
from logging.handlers import RotatingFileHandler
import os

# Importar configuraciones y modelos
from config import Config
from models import db
from auth import token_required
from routes import (
    register, login, logout, get_current_user,
    analyze_image, get_user_analyses, delete_account, health_check
)

# Crear aplicación Flask
app = Flask(__name__)

# Cargar configuración
app.config.from_object(Config)

# Configurar CORS
CORS(app, resources={r"/*": {"origins": Config.CORS_ORIGINS}})

# Configurar rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=[Config.RATE_LIMIT_DEFAULT, Config.RATE_LIMIT_PER_HOUR]
)

# Configurar base de datos
db.init_app(app)

# Configurar logging seguro
if not os.path.exists('logs'):
    os.makedirs('logs')
    
handler = RotatingFileHandler('logs/app.log', maxBytes=1024*1024, backupCount=10)
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

# Registrar rutas
@app.route('/api/auth/register', methods=['POST'])
@limiter.limit(Config.RATE_LIMIT_REGISTER)
def register_route():
    return register()

@app.route('/api/auth/login', methods=['POST'])
@limiter.limit(Config.RATE_LIMIT_LOGIN)
def login_route():
    return login()

@app.route('/api/auth/logout', methods=['POST'])
@token_required
def logout_route():
    return logout()

@app.route('/api/auth/me', methods=['GET'])
@token_required
def me_route():
    return get_current_user()

@app.route('/api/analyze', methods=['POST'])
@token_required
@limiter.limit(Config.RATE_LIMIT_ANALYZE)
def analyze_route():
    return analyze_image()

@app.route('/api/user/analyses', methods=['GET'])
@token_required
def analyses_route():
    return get_user_analyses()

@app.route('/api/user/delete-account', methods=['DELETE'])
@token_required
def delete_account_route():
    return delete_account()

@app.route('/api/health', methods=['GET'])
def health_route():
    return health_check()

# Crear tablas de la base de datos
with app.app_context():
    db.create_all()
    app.logger.info('Base de datos inicializada')

if __name__ == '__main__':
    app.logger.info('Iniciando servidor Flask...')
    # Configurar puerto para Railway y desarrollo local
    port = Config.PORT
    # En producción usar un servidor WSGI como Gunicorn
    app.run(debug=False, host='0.0.0.0', port=port)
            
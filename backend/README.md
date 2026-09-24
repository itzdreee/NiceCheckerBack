# Backend Seguro para Análisis de Imágenes

## 🔐 Seguridad Implementada

### Autenticación y Encriptación
1. **bcrypt** - Encriptación de contraseñas con salt único (imposible de desencriptar)
2. **JWT (JSON Web Tokens)** - Tokens de autenticación que no pueden ser falsificados
3. **Sistema de registro/login** - Los usuarios deben registrarse para usar el servicio
4. **Protección de rutas** - Solo usuarios autenticados pueden analizar imágenes
5. **Tokens con expiración** - Los tokens expiran después de 24 horas

### Seguridad de Archivos
1. **Validación de archivos**: Solo se aceptan formatos de imagen seguros (PNG, JPG, JPEG, GIF)
2. **Sanitización de nombres**: `secure_filename()` previene ataques de path traversal
3. **Límite de tamaño**: Máximo 16MB para prevenir ataques de denegación de servicio
4. **Eliminación automática**: Las imágenes se eliminan después del análisis

### Seguridad de Red
1. **CORS configurado**: Solo permite requests desde tu frontend específico
2. **Logging seguro**: Registra actividad sin exponer información sensible
3. **Manejo de errores**: No expone información técnica al cliente
4. **Variables de entorno**: Claves secretas no están en el código

### Base de Datos
1. **SQLite (desarrollo)** / **PostgreSQL (producción recomendado)**
2. **Contraseñas encriptadas** - Nunca se almacenan en texto plano
3. **Registro de actividad** - Auditoría de uso por usuario

## 📚 Librerías de Seguridad y su Función

### bcrypt (Encriptación de contraseñas)
- **Qué hace**: Encripta contraseñas usando un algoritmo de hashing con salt automático
- **Por qué es seguro**: 
  - Cada contraseña tiene un hash único (incluso si son iguales)
  - Diseñado específicamente para contraseñas (lento para prevenir ataques de fuerza bruta)
  - Imposible de desencriptar (solo se puede verificar si una contraseña coincide)
- **Cómo funciona**: `bcrypt.hashpw(password, salt)` y `bcrypt.checkpw(password, hash)`

### PyJWT (Tokens de autenticación)
- **Qué hace**: Crea y verifica tokens JWT (JSON Web Tokens)
- **Por qué es seguro**: 
  - Los tokens están firmados digitalmente (no pueden ser falsificados)
  - Pueden incluir expiración automática
  - No requieren almacenamiento en servidor (stateless)
- **Cómo funciona**: Genera tokens que el cliente envía en cada request

### python-jose (Criptografía adicional)
- **Qué hace**: Proporciona funciones criptográficas adicionales para JWT
- **Por qué es seguro**: Implementación robusta de algoritmos de firma digital

### SQLAlchemy (ORM de base de datos)
- **Qué hace**: Mapeo objeto-relacional para manejar la base de datos de forma segura
- **Por qué es seguro**: Previene inyección SQL al usar consultas parametrizadas

### Flask-SQLAlchemy (Integración con Flask)
- **Qué hace**: Integra SQLAlchemy con Flask de forma segura
- **Por qué es seguro**: Maneja conexiones y transacciones de forma automática

## 🔒 Cómo Funciona la Encriptación

### Registro de Usuario:
1. El usuario envía: `username`, `email`, `password`
2. **bcrypt** genera un salt aleatorio único
3. **bcrypt** hashea la contraseña con el salt: `hash = bcrypt.hashpw(password, salt)`
4. Solo el hash se guarda en la base de datos (la contraseña original nunca se guarda)

### Login:
1. El usuario envía: `username`, `password`
2. Se busca el hash almacenado en la base de datos
3. **bcrypt** verifica: `bcrypt.checkpw(password, hash)`
4. Si coincide, se genera un **JWT token** con expiración de 24 horas

### Análisis de Imágenes:
1. El cliente envía el token en el header: `Authorization: Bearer <token>`
2. El servidor verifica el token con **JWT**
3. Si el token es válido, permite el análisis
4. Cada acción se registra con el nombre de usuario para auditoría

## 📋 Librerías de Análisis de Imágenes

### Flask (Framework Web)
- **Qué hace**: Framework ligero para crear APIs REST
- **Por qué es seguro**: Tiene protección integrada contra ataques comunes

### Werkzeug (Utilidades de seguridad)
- **Qué hace**: Proporciona `secure_filename()` que sanitiza nombres de archivos
- **Por qué es seguro**: Previene ataques de path traversal

### Flask-CORS (Control de accesos)
- **Qué hace**: Controla qué dominios pueden hacer requests a tu API
- **Por qué es seguro**: Previene ataques CSRF

### Pillow (Procesamiento de imágenes)
- **Qué hace**: Manipulación segura de imágenes
- **Por qué es seguro**: Valida formatos de imagen

### exif (Metadatos de imágenes)
- **Qué hace**: Extrae metadatos EXIF (ubicación GPS, fecha, dispositivo)
- **Por qué es útil**: Detecta información de ubicación incrustada en las fotos
- **Análisis realizado**: 
  - Detección de coordenadas GPS
  - Nivel de exposición de ubicación (alto/bajo)
  - Extracción de información del dispositivo

### OpenCV (Visión por computadora)
- **Qué hace**: Detección de objetos, rostros, análisis de imágenes
- **Por qué es útil**: Detecta personas, ropa, exposición del cuerpo
- **Análisis realizado**:
  - Detección de rostros usando Haar Cascade
  - Análisis de piel expuesta usando detección de color HSV
  - Clasificación de exposición corporal (alto/medio/bajo)
  - Conteo de rostros en la imagen

### NumPy (Cálculos numéricos)
- **Qué hace**: Operaciones matemáticas para procesamiento de imágenes
- **Por qué es necesario**: OpenCV y otras librerías de IA dependen de él

### python-dotenv (Variables de entorno)
- **Qué hace**: Carga variables de entorno desde archivo .env
- **Por qué es seguro**: Mantiene claves secretas fuera del código

### Flask-Limiter (Rate limiting)
- **Qué hace**: Limita el número de requests por IP
- **Por qué es seguro**: Previene ataques de fuerza bruta y abuso del servicio
- **Límites configurados**: 200 requests/día, 50/hora por defecto

### email-validator (Validación de emails)
- **Qué hace**: Valida que los emails tengan el formato correcto
- **Por qué es seguro**: Previene registros con emails inválidos o maliciosos

## 📦 Instalación

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual (Windows)
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Copiar archivo de variables de entorno
copy .env.example .env

# Editar .env con tus claves secretas (USA CLAVES DIFERENTES Y SEGURAS)
```

## 🚀 Ejecución

```bash
python app.py
```

El servidor correrá en http://localhost:5000

## 🔌 API Endpoints

### Autenticación
- `POST /api/auth/register` - Registro de nuevo usuario (rate limit: 5/hora)
- `POST /api/auth/login` - Inicio de sesión (retorna token JWT) (rate limit: 10/hora)
- `POST /api/auth/logout` - Cierre de sesión
- `GET /api/auth/me` - Obtener información del usuario actual (requiere token)

### Análisis
- `POST /api/analyze` - Analizar imagen (requiere token JWT) (rate limit: 30/hora)
- `GET /api/user/analyses` - Obtener historial de análisis (requiere token)
- `DELETE /api/user/delete-account` - Eliminar cuenta y datos (requiere token)

### Sistema
- `GET /api/health` - Verificar estado del servidor

## 🧪 Prueba de la API

### 1. Registrar usuario
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"miusuario","email":"test@example.com","password":"MiPassword123"}'
```

### 2. Login (obtener token)
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"miusuario","password":"MiPassword123"}'
```
Guarda el token que recibes en la respuesta.

### 3. Analizar imagen (con token)
```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Authorization: Bearer TU_TOKEN_AQUI" \
  -F "file=@ruta/a/tu/imagen.jpg"
```

### 4. Ver información del usuario
```bash
curl -X GET http://localhost:5000/api/auth/me \
  -H "Authorization: Bearer TU_TOKEN_AQUI"
```

## ⚠️ Consideraciones de Seguridad para Producción

1. **Cambia las claves secretas** en `.env` por claves aleatorias y largas
2. **Usa PostgreSQL** en lugar de SQLite para producción
3. **Implementa rate limiting** para prevenir ataques de fuerza bruta
4. **Usa HTTPS** en producción (nunca HTTP)
5. **Implementa validación de email** (enviar email de confirmación)
6. **Considera 2FA** (autenticación de dos factores) para mayor seguridad
7. **Usa un servidor WSGI** como Gunicorn en lugar de `app.run()`
8. **Implementa backups** de la base de datos regularmente

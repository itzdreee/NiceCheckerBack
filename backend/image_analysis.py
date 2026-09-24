import cv2
import numpy as np
from PIL import Image
import exif
import re
import logging

logger = logging.getLogger(__name__)

def analyze_exif_data(image_path):
    """
    Analiza los metadatos EXIF para detectar ubicación GPS + OCR para texto revelador
    Returns: dict con has_gps, gps_coordinates, location_exposure, location_details
    """
    try:
        location_exposure = 'bajo'
        location_details = []
        has_gps = False
        gps_coordinates = None
        
        # 1. Análisis EXIF tradicional
        with Image.open(image_path) as img:
            exif_data = img._getexif()
            
            if exif_data:
                from PIL.ExifTags import TAGS
                gps_info = None
                
                for tag, value in exif_data.items():
                    tag_name = TAGS.get(tag, tag)
                    if tag_name == 'GPSInfo':
                        gps_info = value
                        break
                
                if gps_info:
                    def convert_to_degrees(value):
                        degrees = value[0]
                        minutes = value[1]
                        seconds = value[2]
                        return degrees + (minutes / 60.0) + (seconds / 3600.0)
                    
                    gps_data = {}
                    for key in gps_info.keys():
                        name = TAGS.get(key, key)
                        gps_data[name] = gps_info[key]
                    
                    if 'GPSLatitude' in gps_data and 'GPSLongitude' in gps_data:
                        lat = convert_to_degrees(gps_data['GPSLatitude'])
                        lon = convert_to_degrees(gps_data['GPSLongitude'])
                        
                        if gps_data.get('GPSLatitudeRef') == 'S':
                            lat = -lat
                        if gps_data.get('GPSLongitudeRef') == 'W':
                            lon = -lon
                        
                        has_gps = True
                        gps_coordinates = f"{lat:.6f}, {lon:.6f}"
                        location_exposure = 'alto'
                        location_details.append('Coordenadas GPS detectadas en metadatos')
        
        # 2. OCR para detectar texto que revele ubicación (simplificado sin Tesseract)
        try:
            img = cv2.imread(image_path)
            if img is not None:
                # Convertir a escala de grises
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                
                # Análisis básico de patrones visuales (sin OCR)
                # Detectar posibles señales o letreros por color
                hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
                
                # Colores comunes en señales
                lower_red = np.array([0, 120, 70])
                upper_red = np.array([10, 255, 255])
                red_mask = cv2.inRange(hsv, lower_red, upper_red)
                
                lower_blue = np.array([100, 120, 70])
                upper_blue = np.array([130, 255, 255])
                blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)
                
                red_pixels = np.count_nonzero(red_mask)
                blue_pixels = np.count_nonzero(blue_mask)
                total_pixels = img.shape[0] * img.shape[1]
                
                # Simular detección de texto sin OCR
                text = ""  # OCR no disponible en versión simplificada
                
                # Palabras clave que pueden indicar ubicación
                location_keywords = [
                    'calle', 'avenida', 'plaza', 'parque', 'colegio', 'escuela',
                    'restaurante', 'hotel', 'motel', 'hospital', 'clinica',
                    'iglesia', 'templo', 'museo', 'teatro', 'cine',
                    'aeropuerto', 'estación', 'metro', 'bus', 'terminal',
                    'centro', 'comercial', 'shopping', 'mall', 'mercado',
                    'universidad', 'instituto', 'biblioteca', 'gimnasio',
                    'piscina', 'playa', 'montaña', 'cerro', 'río', 'lago'
                ]
                
                # Patrones para detectar direcciones
                address_patterns = [
                    r'\d+\s+[A-Za-z]+\s+(calle|avenida|av|c|ave)',
                    r'[A-Za-z]+\s+\d+',
                    r'\d{3,}-\d{3,}',  # Códigos postales
                    r'[A-Z]{2,}\s+\d{4,}'  # Patrones tipo "ABC 1234"
                ]
                
                text_lower = text.lower()
                found_keywords = [kw for kw in location_keywords if kw in text_lower]
                found_addresses = []
                
                for pattern in address_patterns:
                    matches = re.findall(pattern, text_lower, re.IGNORECASE)
                    found_addresses.extend(matches)
                
                if found_keywords or found_addresses:
                    location_exposure = 'alto'
                    if found_keywords:
                        location_details.append(f'Palabras de ubicación detectadas: {", ".join(found_keywords[:3])}')
                    if found_addresses:
                        location_details.append(f'Posibles direcciones detectadas: {len(found_addresses)}')
        
        except Exception as ocr_error:
            logger.warning(f'OCR no disponible: {str(ocr_error)}')
        
        # 3. Análisis visual básico para detectar landmarks conocidos
        try:
            img = cv2.imread(image_path)
            if img is not None:
                # Detectar presencia de texto en la imagen (señales, letreros)
                hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
                
                # Colores comunes en señales de tráfico
                lower_red = np.array([0, 120, 70])
                upper_red = np.array([10, 255, 255])
                red_mask = cv2.inRange(hsv, lower_red, upper_red)
                
                lower_blue = np.array([100, 120, 70])
                upper_blue = np.array([130, 255, 255])
                blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)
                
                red_pixels = np.count_nonzero(red_mask)
                blue_pixels = np.count_nonzero(blue_mask)
                total_pixels = img.shape[0] * img.shape[1]
                
                if (red_pixels / total_pixels) > 0.01 or (blue_pixels / total_pixels) > 0.01:
                    location_details.append('Posibles señales o letreros detectados')
                    if location_exposure == 'bajo':
                        location_exposure = 'medio'
        
        except Exception as visual_error:
            logger.warning(f'Análisis visual no disponible: {str(visual_error)}')
        
        return {
            'has_gps': has_gps,
            'gps_coordinates': gps_coordinates,
            'location_exposure': location_exposure,
            'location_details': location_details
        }
            
    except Exception as e:
        logger.error(f'Error analizando EXIF: {str(e)}')
        return {
            'has_gps': False,
            'gps_coordinates': None,
            'location_exposure': 'desconocido',
            'location_details': ['Error en el análisis']
        }

def analyze_body_exposure(image_path):
    """
    Analiza la imagen para detectar exposición del cuerpo usando OpenCV básico (sin MediaPipe)
    Returns: dict con has_faces, face_count, body_exposure, exposure_details
    """
    try:
        # Cargar imagen con OpenCV
        img = cv2.imread(image_path)
        if img is None:
            return {
                'has_faces': False,
                'face_count': 0,
                'body_exposure': 'desconocido',
                'exposure_details': []
            }
        
        exposure_details = []
        body_exposure = 'bajo'
        face_count = 0
        
        # 1. Detección de rostros con Haar Cascade (OpenCV tradicional)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        face_count = len(faces)
        
        if face_count > 0:
            exposure_details.append(f'{face_count} rostro(s) detectado(s)')
            
            # 2. Análisis de piel expuesta usando detección de color HSV
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            
            # Rangos de piel en HSV (varios tonos)
            lower_skin1 = np.array([0, 20, 70], dtype=np.uint8)
            upper_skin1 = np.array([20, 255, 255], dtype=np.uint8)
            
            lower_skin2 = np.array([160, 20, 70], dtype=np.uint8)
            upper_skin2 = np.array([180, 255, 255], dtype=np.uint8)
            
            # Crear máscaras de piel
            skin_mask1 = cv2.inRange(hsv, lower_skin1, upper_skin1)
            skin_mask2 = cv2.inRange(hsv, lower_skin2, upper_skin2)
            skin_mask = cv2.bitwise_or(skin_mask1, skin_mask2)
            
            # Calcular porcentaje de piel en la imagen
            total_pixels = img.shape[0] * img.shape[1]
            skin_pixels = np.count_nonzero(skin_mask)
            skin_percentage = (skin_pixels / total_pixels) * 100
            
            exposure_details.append(f'Porcentaje de piel expuesta: {skin_percentage:.1f}%')
            
            # 3. Clasificación de exposición basada en múltiples factores
            exposure_score = 0
            
            # Porcentaje de piel
            if skin_percentage > 40:
                exposure_score += 3
                exposure_details.append('Alta exposición de piel detectada')
            elif skin_percentage > 25:
                exposure_score += 2
                exposure_details.append('Exposición de piel moderada')
            elif skin_percentage > 15:
                exposure_score += 1
            
            # Número de rostros
            if face_count > 1:
                exposure_score += 1
                exposure_details.append('Múltiples personas en la foto')
            
            # Clasificación final
            if exposure_score >= 3:
                body_exposure = 'alto'
            elif exposure_score >= 2:
                body_exposure = 'medio'
            else:
                body_exposure = 'bajo'
                exposure_details.append('Nivel de exposición corporal aceptable')
            
            # 4. Análisis adicional de composición
            height, width = img.shape[:2]
            
            # Detectar si la foto es un retrato (persona grande en el frame)
            if face_count > 0:
                # Obtener el rostro más grande
                largest_face = max(faces, key=lambda f: f[2] * f[3])
                face_area = largest_face[2] * largest_face[3]
                image_area = width * height
                face_ratio = face_area / image_area
                
                if face_ratio > 0.15:  # El rostro ocupa más del 15% de la imagen
                    exposure_details.append('Retrato cercano detectado')
                    exposure_score += 1
            
            # Ajustar clasificación final
            if exposure_score >= 4:
                body_exposure = 'alto'
            elif exposure_score >= 2:
                body_exposure = 'medio'
            else:
                body_exposure = 'bajo'
                
        else:
            exposure_details.append('No se detectaron rostros en la imagen')
            body_exposure = 'bajo'
        
        return {
            'has_faces': face_count > 0,
            'face_count': face_count,
            'body_exposure': body_exposure,
            'exposure_details': exposure_details
        }
        
    except Exception as e:
        logger.error(f'Error analizando exposición del cuerpo: {str(e)}')
        return {
            'has_faces': False,
            'face_count': 0,
            'body_exposure': 'desconocido',
            'exposure_details': ['Error en el análisis']
        }

def generate_recommendations(exif_analysis, body_analysis):
    """
    Genera recomendaciones basadas en el análisis con IA
    Returns: list de strings con recomendaciones
    """
    recommendations = []
    
    # Recomendaciones de ubicación
    if exif_analysis['has_gps']:
        recommendations.append('🚨 PELIGRO: Tu foto contiene coordenadas GPS exactas. CUALQUIERA puede saber dónde estabas.')
        recommendations.append('🔧 Solución: Usa "exiftool" o apps similares para eliminar metadatos antes de subir.')
        recommendations.append('📱 En Android/iOS: Desactiva la geolocalización de la cámara antes de tomar fotos.')
    
    if exif_analysis['location_exposure'] == 'alto':
        for detail in exif_analysis.get('location_details', []):
            recommendations.append(f'📍 {detail}')
        recommendations.append('⚠️ Nivel alto de exposición de ubicación detectado.')
    
    elif exif_analysis['location_exposure'] == 'medio':
        recommendations.append('⚠️ Nivel medio de exposición de ubicación. Revisa el contexto antes de compartir.')
    
    # Recomendaciones de exposición corporal
    if body_analysis['body_exposure'] == 'muy_alto':
        recommendations.append('🚨 PELIGRO: Nivel MUY ALTO de exposición corporal. No recomendado para redes públicas.')
        recommendations.append('👙 Considera si realmente quieres que esta foto sea visible para cualquiera.')
        recommendations.append('🔒 Usa configuraciones de privacidad: "Solo amigos" o "Solo yo".')
        recommendations.append('👎 Piensa en cómo podría usarse esta foto en el futuro (bullying, screenshots, etc.).')
    
    elif body_analysis['body_exposure'] == 'alto':
        recommendations.append('⚠️ Nivel ALTO de exposición corporal. Ten precaución.')
        recommendations.append('👥 Considera quién podrá ver esta foto: ¿amigos? ¿familia? ¿extraños?')
        recommendations.append('📱 Revisa las configuraciones de privacidad de la plataforma.')
        recommendations.append('🤔 Piensa: ¿Te sentirías cómodo si tu profesor/familia la ve?')
    
    elif body_analysis['body_exposure'] == 'medio':
        recommendations.append('⚠️ Nivel MEDIO de exposición corporal. Evalúa el contexto.')
        recommendations.append('👥 ¿Es apropiado para la audiencia que la verá?')
        recommendations.append('📱 Considera hacer la foto privada para contactos cercanos.')
    
    elif body_analysis['body_exposure'] == 'bajo':
        recommendations.append('✅ Nivel de exposición corporal aceptable para redes sociales.')
    
    # Recomendaciones específicas basadas en detalles
    for detail in body_analysis.get('exposure_details', []):
        if 'piel' in detail.lower() and '%' in detail:
            percentage = int(''.join(filter(str.isdigit, detail.split('%')[0])))
            if percentage > 30:
                recommendations.append(f'📸 {detail} - Considera si es apropiado.')
    
    if body_analysis['face_count'] > 1:
        recommendations.append(f'👥 Hay {body_analysis["face_count"]} personas en la foto. ¿Tienes su permiso para subirla?')
        recommendations.append('⚖️ Respetar la privacidad de los demás es responsabilidad de todos.')
    
    # Recomendaciones generales
    recommendations.append('💡 RECUERDA: Una vez subida, pierdes el control sobre quién puede ver/guardar/compartir la foto.')
    recommendations.append('🔐 Configura siempre la privacidad máxima posible en tus redes sociales.')
    recommendations.append('🤔 Antes de subir, pregúntate: ¿Querría ver esto mi familia/mi jefe dentro de 5 años?')
    
    return recommendations

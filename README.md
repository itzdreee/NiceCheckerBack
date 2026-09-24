# NiceChecker - Analizador de Privacidad de Fotos con IA

🎯 **NiceChecker** analiza tus fotos antes de subirlas a redes sociales para detectar exposición de ubicación y cuerpo.

## 📁 Estructura del Proyecto

```
Windsurf/
├── Backend/          # API Python/Flask con análisis de imágenes
│   ├── app.py
│   ├── config.py
│   ├── models.py
│   ├── auth.py
│   ├── routes.py
│   ├── image_analysis.py
│   ├── requirements.txt
│   ├── railway.json
│   ├── .env.example
│   ├── .gitignore
│   └── README.md
│
└── Frontend/         # Aplicación React para el usuario
    ├── package.json
    ├── vercel.json
    ├── .env.example
    ├── .env.production
    ├── .gitignore
    ├── README.md
    ├── public/
    │   └── index.html
    └── src/
        ├── index.js
        ├── index.css
        ├── App.js
        └── App.css
```

## 🚀 Deployment

### Backend → Railway
1. Sube la carpeta `Backend/` a GitHub
2. Importa el repo en Railway
3. Railway crea PostgreSQL automáticamente
4. Configura variables de entorno

### Frontend → Vercel
1. Sube la carpeta `Frontend/` a GitHub
2. Conecta con Vercel
3. Configura `REACT_APP_API_URL` con la URL de Railway
4. Deploy automático

## 🎨 Diseño
- **Colores:** Verde agua (#5afac7) + Marrón café (#8B4513) + Blanco
- **Nombre:** NiceChecker
- **Funcionalidad:** Análisis de privacidad de fotos con IA

## 📱 Plataformas
- ✅ Web responsive (móvil y desktop)
- ✅ Backend API REST (compatible con React Native futuro)
- ✅ Base de datos PostgreSQL (Railway)

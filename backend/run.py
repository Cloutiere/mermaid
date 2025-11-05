# backend/run.py
from app import create_app

# Utiliser la fonction d'usine pour créer et configurer l'application
app = create_app()

if __name__ == '__main__':
    # Fla, CORS et db sont initialisés à l'intérieur de create_app()
    app.run(host='0.0.0.0', port=5001, debug=True)
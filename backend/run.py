# backend/run.py
from app import create_app

# Utiliser la fonction d'usine pour créer et configurer l'application.
# Par défaut, create_app utilisera la configuration DevelopmentConfig
app = create_app()

if __name__ == '__main__':
    # La configuration par défaut dans app.config.Config lit les variables d'environnement
    # pour le port, l'hôte et le debug.
    # Ici, nous utilisons les valeurs par défaut spécifiées dans l'énoncé initial 
    # ou les valeurs déduites de la configuration (si elles sont explicitement définies dans app/config.py, 
    # mais ici on utilise la valeur par défaut pour run.py)
    app.run(host='0.0.0.0', port=5001, debug=app.config['DEBUG'])
# backend/run.py
# Version 1.0

import os
from app import create_app

# Récupère le nom de la configuration à partir de la variable d'environnement FLASK_ENV.
# Si FLASK_ENV n'est pas définie, utilise 'development' par défaut.
# Cela permet de sélectionner la configuration appropriée (development, testing, production).
config_name = os.environ.get('FLASK_ENV', 'development')

# Crée l'instance de l'application Flask en utilisant la fonction factory 'create_app'.
# La configuration sélectionnée sera passée à create_app.
app = create_app(config_name)

if __name__ == '__main__':
    # Lance le serveur de développement Flask.
    # L'hôte et le port peuvent être configurés via des variables d'environnement (ex: FLASK_RUN_HOST, FLASK_RUN_PORT)
    # ou directement ici si nécessaire. Pour une utilisation en production, un serveur WSGI comme Gunicorn est recommandé.
    print(f"Démarrage de l'application Flask en mode : {config_name}")
    app.run(host='0.0.0.0', port=5001, debug=True)
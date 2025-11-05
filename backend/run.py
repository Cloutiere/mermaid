from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
import os

app = Flask(__name__)
CORS(app)

# Configuration de la base de données
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Import et initialisation de la base de données
from app.models import db, Project, SubProject, Node, Relationship, ClassDef, LinkType

db.init_app(app)

# Initialisation Flask-Migrate
migrate = Migrate(app, db)

@app.route('/api/health', methods=['GET'])
def health_check():
    return {'status': 'ok', 'message': 'Backend Flask is running'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
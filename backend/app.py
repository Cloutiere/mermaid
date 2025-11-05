"""
Point d'entrée minimal du backend Flask.
À compléter avec votre code applicatif.
"""
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/health', methods=['GET'])
def health_check():
    return {'status': 'ok', 'message': 'Backend Flask is running'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

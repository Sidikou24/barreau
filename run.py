
# run.py (Point d'entrée de l'application)
from app import create_app
import os

app = create_app(os.getenv('FLASK_CONFIG', 'default'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)


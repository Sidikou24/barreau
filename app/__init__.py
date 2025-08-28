
# app/__init__.py (Initialisation de l'application Flask)
from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from app.config import config

# Initialisation des extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # Chargement de la configuration
    app.config.from_object(config[config_name])
    
    # Initialisation des extensions avec l'app
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    
    # Configuration de Flask-Login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))
    
    # Enregistrement des Blueprints
    from app.routes.auth import auth_bp
    from app.routes.batonnier import batonnier_bp
    from app.routes.avocat import avocat_bp
    from app.routes.assistant_comptable import assistant_comptable_bp
    from app.routes.assistant_admin import assistant_admin_bp
    from app.routes.tresorier import tresorier_bp
    from app.routes.secretaire import secretaire_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(batonnier_bp, url_prefix='/batonnier')
    app.register_blueprint(avocat_bp, url_prefix='/avocat')
    app.register_blueprint(assistant_comptable_bp, url_prefix='/assistant-comptable')
    app.register_blueprint(assistant_admin_bp, url_prefix='/assistant-admin')
    app.register_blueprint(tresorier_bp, url_prefix='/tresorier')
    app.register_blueprint(secretaire_bp, url_prefix='/secretaire')
    
    # Route par défaut
    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))
    
    # Import des modèles pour les migrations
    from app.models import user, avocat, droit_plaidoirie, cabinet_avocat, \
                          acte_avocat, assistance_juridique, cotisation, \
                          formation, sanction_disciplinaire
    
    return app


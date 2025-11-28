from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flasgger import Swagger
import logging
from logging.handlers import RotatingFileHandler
import os

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[]
)


def create_app(config_name=None):
    """Application factory pattern"""
    app = Flask(__name__)

    # Load configuration
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    from app.config import get_config
    config_class = get_config(config_name)
    app.config.from_object(config_class)

    # Initialize extensions with app
    db.init_app(app)
    jwt.init_app(app)

    # Configure CORS
    CORS(app,
         resources={r"/api/*": {
             "origins": app.config['CORS_ORIGINS'],
             "methods": app.config['CORS_METHODS'],
             "allow_headers": app.config['CORS_ALLOW_HEADERS'],
             "supports_credentials": True
         }})

    # Configure Rate Limiting
    if app.config['RATELIMIT_ENABLED']:
        limiter.init_app(app)

    # Configure Swagger
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec',
                "route": '/apispec.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/api/docs"
    }

    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": app.config['APP_NAME'],
            "description": "TaskForge API - Sistema de Gestion de Tareas con funciones avanzadas",
            "version": app.config['APP_VERSION'],
            "contact": {
                "name": "API Support",
                "url": "https://github.com/yourusername/taskforge-api"
            }
        },
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "**IMPORTANTE:** Debes incluir 'Bearer ' antes del token.\n\nEjemplo: `Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`\n\nPasos:\n1. Haz login en /auth/login\n2. Copia el 'access_token' de la respuesta\n3. Haz clic en 'Authorize' arriba\n4. Escribe: Bearer <tu_token>\n5. Haz clic en 'Authorize' y luego 'Close'"
            }
        },
        "security": [
            {
                "Bearer": []
            }
        ],
        "basePath": "/api",
        "schemes": ["https"] if app.config['FLASK_ENV'] == 'production' else ["http", "https"]
    }

    Swagger(app, config=swagger_config, template=swagger_template)

    # Setup logging
    setup_logging(app)

    # Register blueprints
    register_blueprints(app)

    # Register error handlers
    register_error_handlers(app)

    # JWT handlers
    register_jwt_handlers(app)

    # Shell context for flask shell command
    @app.shell_context_processor
    def make_shell_context():
        from app.models.user import User, Role
        from app.models.task import Task, TaskStatus, TaskPriority
        from app.models.tag import Tag
        return {
            'db': db,
            'User': User,
            'Role': Role,
            'Task': Task,
            'Tag': Tag,
            'TaskStatus': TaskStatus,
            'TaskPriority': TaskPriority
        }

    return app


def register_blueprints(app):
    """Register all blueprints"""
    from app.routes.health import health_bp
    from app.routes.auth import auth_bp
    from app.routes.users import users_bp
    from app.routes.tasks import tasks_bp
    from app.routes.tags import tags_bp

    # Register blueprints with /api prefix
    app.register_blueprint(health_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(tasks_bp, url_prefix='/api/tasks')
    app.register_blueprint(tags_bp, url_prefix='/api/tags')


def register_error_handlers(app):
    """Register error handlers"""

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 'Peticion Incorrecta',
            'message': str(error)
        }), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'success': False,
            'error': 'No autorizado',
            'message': 'Autenticacion requerida'
        }), 401

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'success': False,
            'error': 'Prohibido',
            'message': 'No tienes permiso para acceder a este recurso'
        }), 403

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 'No Encontrado',
            'message': 'Recurso no encontrado'
        }), 404

    @app.errorhandler(429)
    def ratelimit_handler(error):
        return jsonify({
            'success': False,
            'error': 'Limite de Velocidad Excedido',
            'message': 'Demasiadas peticiones. Por favor intentalo de nuevo mas tarde.'
        }), 429

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Error Interno del Servidor',
            'message': 'Ocurrio un error inesperado'
        }), 500


def register_jwt_handlers(app):
    """Register JWT handlers"""

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'success': False,
            'error': 'Token Expirado',
            'message': 'El token ha expirado'
        }), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'success': False,
            'error': 'Token Invalido',
            'message': 'Fallo la verificacion de firma'
        }), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            'success': False,
            'error': 'Autorizacion Requerida',
            'message': 'La peticion no contiene un token valido'
        }), 401

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'success': False,
            'error': 'Token Revocado',
            'message': 'El token ha sido revocado'
        }), 401


def setup_logging(app):
    """Configure application logging"""
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')

        file_handler = RotatingFileHandler(
            'logs/taskforge.log',
            maxBytes=10240000,
            backupCount=10
        )

        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))

        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('TaskForge API startup')

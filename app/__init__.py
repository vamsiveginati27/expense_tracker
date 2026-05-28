from flask import Flask
from flask_jwt_extended import JWTManager
from mongoengine import connect
from config import Config
from expenses import users_bp


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize MongoDB
    connect(
        host=app.config['MONGODB_URI'],
        connect=False
    )

    # Initialize JWT
    jwt = JWTManager(app)

    # Register blueprints
    from expenses import auth_bp, expenses_bp, users_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(expenses_bp)
    app.register_blueprint(users_bp)

    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health():
        from datetime import datetime
        return {'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}, 200

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'message': 'Endpoint not found'}, 404

    @app.errorhandler(500)
    def internal_error(error):
        return {'message': 'Internal server error'}, 500

    return app

import os
from flask import Flask, render_template, session
from flask_socketio import SocketIO
from config import Config
from models import db

socketio = SocketIO(cors_allowed_origins="*")

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ensure instance directory exists
    instance_dir = os.path.join(app.root_path, 'instance')
    os.makedirs(instance_dir, exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    socketio.init_app(app)

    # Register Blueprints
    from routes.auth import auth_bp
    from routes.student import student_bp
    from routes.vendor import vendor_bp
    from routes.admin import admin_bp
    from routes.orders import orders_bp
    from routes.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(vendor_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(api_bp)

    @app.route('/')
    def landing():
        return render_template('landing.html')

    @app.route('/demo')
    def demo_page():
        return render_template('demo.html')

    # WebSocket events
    @socketio.on('connect')
    def handle_connect():
        pass

    return app

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    print("Starting CanteenFlow AI server on http://127.0.0.1:5000")
    socketio.run(app, debug=True, host='127.0.0.1', port=5000, allow_unsafe_werkzeug=True)

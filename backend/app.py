from flask import Flask
from backend.config import Config
from backend.database import db

def create_app(config_class=Config):
    app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')
    app.config.from_object(config_class)

    db.init_app(app)

    # Register extensions and blueprints
    from backend.websocket_handler import register_extensions
    register_extensions(app)

    from backend.attack_lab import attack_bp
    app.register_blueprint(attack_bp)

    # Register core routes for frontend
    from flask import render_template

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/login.html')
    def login_page():
        return render_template('login.html')

    @app.route('/register.html')
    def register_page():
        return render_template('register.html')

    @app.route('/attack-lab')
    def attack_lab_page():
        return render_template('attack_lab.html')

    @app.route('/key-management')
    def key_management_page():
        return render_template('key_management.html')

    return app

if __name__ == '__main__':
    from backend.websocket_handler import socketio
    app = create_app()
    socketio.run(app, debug=True, port=5000)

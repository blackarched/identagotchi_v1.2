# File: minigotchi/gui.py
import os
from flask import (Flask, Blueprint, render_template, request,
                   send_from_directory, abort)
from flask_wtf import CSRFProtect
import logging

# Application Factory

def create_app(config_path=None):
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config.from_pyfile(config_path or 'config.py')

    # Security Settings
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'change_me')
    CSRFProtect(app)

    # Logging
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s'
    ))
    app.logger.setLevel(logging.INFO)
    app.logger.addHandler(handler)

    # Register Blueprints
    from .routes import main_bp
    app.register_blueprint(main_bp)

    return app


# Entry point for development
if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
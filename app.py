from flask import Flask, render_template
from routes.auth_routes import auth_bp
from routes.admin import admin_bp
from routes.student import student_bp
import os


def create_app():
    app = Flask(__name__)
    app.secret_key = "chave_super_secreta"  # necessária para sessão

    # 🔹 Configurações globais
    app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # 🔹 Registro dos módulos (Blueprints)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(student_bp)

    @app.route('/')
    def index():    
        return render_template('index.html')
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)



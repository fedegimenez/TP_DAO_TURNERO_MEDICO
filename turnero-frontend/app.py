from flask import Flask, redirect, url_for
from flask_wtf.csrf import CSRFProtect

from settings import settings
from blueprints.auth import bp as auth_bp
from blueprints.dashboard import bp as dashboard_bp
from blueprints.patients import bp as patients_bp
from blueprints.doctors import bp as doctors_bp
from blueprints.specialties import bp as specialties_bp
from blueprints.appointments import bp as appointments_bp
from blueprints.reports import bp as reports_bp

csrf = CSRFProtect()


def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config.from_object(settings)
    app.secret_key = settings.SECRET_KEY

    csrf.init_app(app)

    # Blueprints...
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(patients_bp, url_prefix="/pacientes")
    app.register_blueprint(doctors_bp, url_prefix="/medicos")
    app.register_blueprint(specialties_bp, url_prefix="/especialidades")
    app.register_blueprint(appointments_bp, url_prefix="/turnos")
    app.register_blueprint(reports_bp, url_prefix="/reportes")

    @app.get("/")
    def home():
        # ⚠️ Redirige a la vista que sí prepara `resumen`
        return redirect(url_for("dashboard.dashboard_view"))

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=settings.DEBUG, port=5173)

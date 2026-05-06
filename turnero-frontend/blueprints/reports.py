from flask import Blueprint, render_template, request, session
import asyncio
from services.api import api
from utils.auth import login_required

bp = Blueprint("reports", __name__)

@bp.get("/")
@login_required
def index():
    token = session.get("token")
    desde = request.args.get("desde")
    hasta = request.args.get("hasta")
    try:
        por_medico = asyncio.run(api.get("/reportes/turnos-medico", params={"desde": desde, "hasta": hasta}, token=token))
    except Exception:
        por_medico = []
    try:
        por_especialidad = asyncio.run(api.get("/reportes/turnos-especialidad", token=token))
    except Exception:
        por_especialidad = []
    return render_template("reports/index.html", por_medico=por_medico, por_especialidad=por_especialidad)

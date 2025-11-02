from flask import Blueprint, flash, render_template, request, session
import asyncio

from services.api import api

bp = Blueprint("patients", __name__)


def _load_patients(token):
    return asyncio.run(api.get("/pacientes", token=token))


@bp.get("/")
def index():
    token = session.get("token")
    try:
        pacientes = _load_patients(token)
    except Exception as e:
        pacientes = []
        flash(f"Error al cargar pacientes: {e}", "error")
    return render_template("patients/index.html", pacientes=pacientes)


@bp.get("/_table")
def table_partial():
    token = session.get("token")
    pacientes = _load_patients(token)
    return render_template("patients/_table.html", pacientes=pacientes)


@bp.get("/_form")
def form_partial():
    return render_template("patients/_form.html", action="/pacientes/crear", method="post", title="Nuevo paciente")


@bp.get("/<int:pid>/form")
def form_edit(pid: int):
    token = session.get("token")
    paciente = asyncio.run(api.get(f"/pacientes/{pid}", token=token))
    return render_template(
        "patients/_form.html",
        action=f"/pacientes/{pid}/editar",
        method="post",
        title="Editar paciente",
        values=paciente,
        editing=True,
    )


def _payload_from_form(form):
    return {
        "nombre": form.get("nombre", "").strip(),
        "apellido": form.get("apellido", "").strip(),
        "dni": form.get("dni", "").strip(),
        "fecha_nacimiento": form.get("fecha_nacimiento", ""),
        "genero": form.get("genero") or None,
        "direccion": form.get("direccion", ""),
        "telefono": form.get("telefono", ""),
        "email": form.get("email", ""),
        "obra_social": form.get("obra_social", "") or None,
        "nro_afiliado": form.get("nro_afiliado", "") or None,
    }


@bp.post("/crear")
def crear():
    token = session.get("token")
    payload = _payload_from_form(request.form)
    try:
        asyncio.run(api.post("/pacientes", payload, token=token))
        pacientes = _load_patients(token)
        return render_template("patients/_table.html", pacientes=pacientes)
    except Exception as e:
        return (
            render_template(
                "patients/_form.html",
                error=str(e),
                values=payload,
                action="/pacientes/crear",
                method="post",
                title="Nuevo paciente",
            ),
            400,
        )


@bp.post("/<int:pid>/editar")
def editar(pid: int):
    token = session.get("token")
    payload = _payload_from_form(request.form)
    try:
        asyncio.run(api.put(f"/pacientes/{pid}", payload, token=token))
        pacientes = _load_patients(token)
        return render_template("patients/_table.html", pacientes=pacientes)
    except Exception as e:
        return (
            render_template(
                "patients/_form.html",
                error=str(e),
                values=payload | {"id": pid},
                action=f"/pacientes/{pid}/editar",
                method="post",
                title="Editar paciente",
                editing=True,
            ),
            400,
        )


@bp.post("/toggle/<int:pid>")
def toggle(pid: int):
    token = session.get("token")
    activo = request.form.get("activo") == "true"
    try:
        asyncio.run(api.patch(f"/pacientes/{pid}/estado", {"activo": activo}, token=token))
        pacientes = _load_patients(token)
        return render_template("patients/_table.html", pacientes=pacientes)
    except Exception as e:
        return f"Error: {e}", 400


@bp.get("/<int:pid>/historial")
def historial(pid: int):
    token = session.get("token")
    try:
        historial = asyncio.run(api.get(f"/turnos/paciente/{pid}/historial", token=token))
    except Exception as e:
        historial = []
        flash(f"No se pudo obtener historial: {e}", "error")
    return render_template("patients/_history.html", historial=historial)

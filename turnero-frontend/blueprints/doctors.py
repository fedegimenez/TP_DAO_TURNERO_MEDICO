from flask import Blueprint, render_template, session, request
import asyncio

from services.api import api

bp = Blueprint("doctors", __name__)


def _load_doctors(token):
    return asyncio.run(api.get("/medicos", token=token))


def _load_specialties(token):
    return asyncio.run(api.get("/especialidades", token=token))


@bp.get("/")
def index():
    token = session.get("token")
    medicos = _load_doctors(token)
    especialidades = _load_specialties(token)
    return render_template("doctors/index.html", medicos=medicos, especialidades=especialidades)


@bp.get("/_table")
def table_partial():
    token = session.get("token")
    medicos = _load_doctors(token)
    especialidades = _load_specialties(token)
    return render_template("doctors/_table.html", medicos=medicos, especialidades=especialidades)


@bp.get("/_form")
def form_partial():
    token = session.get("token")
    especialidades = _load_specialties(token)
    return render_template(
        "doctors/_form.html",
        action="/medicos/crear",
        values={},
        specialties=especialidades,
        title="Nuevo médico",
    )


@bp.get("/<int:did>/form")
def form_edit(did: int):
    token = session.get("token")
    medico = asyncio.run(api.get(f"/medicos/{did}", token=token))
    especialidades = _load_specialties(token)
    return render_template(
        "doctors/_form.html",
        action=f"/medicos/{did}/editar",
        values=medico,
        specialties=especialidades,
        editing=True,
        title="Editar médico",
    )


def _availability_from_form(form):
    disponibilidad = []
    for dia in range(7):
        if form.get(f"day_{dia}_active"):
            start = form.get(f"day_{dia}_start")
            end = form.get(f"day_{dia}_end")
            slot = form.get(f"day_{dia}_slot") or 30
            if start and end:
                disponibilidad.append(
                    {
                        "day_of_week": dia,
                        "start_time": start,
                        "end_time": end,
                        "slot_minutes": int(slot),
                    }
                )
    return disponibilidad


def _payload_from_form(form, include_dni=True):
    payload = {
        "nombre": form.get("nombre", "").strip(),
        "apellido": form.get("apellido", "").strip(),
        "email": form.get("email") or None,
        "telefono": form.get("telefono") or None,
        "direccion": form.get("direccion") or None,
        "genero": form.get("genero") or None,
        "matricula": form.get("matricula", "").strip(),
    }
    if include_dni:
        payload["dni"] = form.get("dni", "").strip()
    specialties = [int(i) for i in form.getlist("specialty_ids")]
    payload["specialty_ids"] = specialties
    payload["availability"] = _availability_from_form(form)
    return payload


@bp.post("/crear")
def crear():
    token = session.get("token")
    payload = _payload_from_form(request.form, include_dni=True)
    try:
        asyncio.run(api.post("/medicos", payload, token=token))
        medicos = _load_doctors(token)
        especialidades = _load_specialties(token)
        return render_template("doctors/_table.html", medicos=medicos, especialidades=especialidades)
    except Exception as e:
        return (
            render_template(
                "doctors/_form.html",
                error=str(e),
                values=payload,
                specialties=_load_specialties(token),
                action="/medicos/crear",
                title="Nuevo médico",
            ),
            400,
        )


@bp.post("/<int:did>/editar")
def editar(did: int):
    token = session.get("token")
    payload = _payload_from_form(request.form, include_dni=False)
    try:
        asyncio.run(api.put(f"/medicos/{did}", payload, token=token))
        medicos = _load_doctors(token)
        especialidades = _load_specialties(token)
        return render_template("doctors/_table.html", medicos=medicos, especialidades=especialidades)
    except Exception as e:
        return (
            render_template(
                "doctors/_form.html",
                error=str(e),
                values=payload | {"id": did},
                specialties=_load_specialties(token),
                action=f"/medicos/{did}/editar",
                editing=True,
                title="Editar médico",
            ),
            400,
        )


@bp.post("/toggle/<int:did>")
def toggle(did: int):
    token = session.get("token")
    activo = request.form.get("activo") == "true"
    try:
        asyncio.run(api.patch(f"/medicos/{did}/estado", {"activo": activo}, token=token))
        medicos = _load_doctors(token)
        especialidades = _load_specialties(token)
        return render_template("doctors/_table.html", medicos=medicos, especialidades=especialidades)
    except Exception as e:
        return f"Error: {e}", 400

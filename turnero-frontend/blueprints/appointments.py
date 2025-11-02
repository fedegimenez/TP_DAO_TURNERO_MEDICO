from datetime import datetime
from flask import Blueprint, flash, render_template, request, session
import asyncio

from services.api import api

bp = Blueprint("appointments", __name__)


def _api_get(path: str, token: str, params: dict | None = None):
    return asyncio.run(api.get(path, params=params, token=token))


def _load_catalogs(token: str):
    pacientes = _api_get("/pacientes", token)
    medicos = _api_get("/medicos", token)
    especialidades = _api_get("/especialidades", token)
    return pacientes, medicos, especialidades


def _load_turnos(token: str):
    today = datetime.now().strftime("%Y-%m-%dT00:00")
    return _api_get("/turnos", token, params={"desde": today})


def _maps(pacientes, medicos, especialidades):
    return (
        {p["id"]: f"{p['apellido']}, {p['nombre']}" for p in pacientes},
        {m["id"]: f"{m['apellido']}, {m['nombre']}" for m in medicos},
        {e["id"]: e["nombre"] for e in especialidades},
    )


@bp.get("/")
def index():
    token = session.get("token")
    try:
        pacientes, medicos, especialidades = _load_catalogs(token)
        turnos = _load_turnos(token)
    except Exception as exc:
        pacientes = medicos = especialidades = turnos = []
        flash(f"No se pudieron cargar datos de turnos: {exc}", "error")
    return render_template(
        "appointments/index.html",
        pacientes=pacientes,
        medicos=medicos,
        especialidades=especialidades,
        turnos=turnos,
    )


@bp.get("/_form")
def form_partial():
    token = session.get("token")
    pacientes, medicos, especialidades = _load_catalogs(token)
    return render_template(
        "appointments/_form.html",
        pacientes=pacientes,
        medicos=medicos,
        especialidades=especialidades,
        values={},
    )


def _build_payload(form):
    fecha = form.get("fecha")
    hora = form.get("hora")
    if not fecha or not hora:
        raise ValueError("Debes indicar fecha y hora")
    return {
        "paciente_id": int(form.get("paciente_id")),
        "medico_id": int(form.get("medico_id")),
        "especialidad_id": int(form.get("especialidad_id")),
        "fecha": f"{fecha}T{hora}",
        "duracion_min": int(form.get("duracion_min", 30)),
        "receta_url": form.get("receta_url") or None,
    }


@bp.post("/crear")
def crear():
    token = session.get("token")
    pacientes, medicos, especialidades = _load_catalogs(token)
    try:
        payload = _build_payload(request.form)
        asyncio.run(api.post("/turnos", payload, token=token))
        turnos = _load_turnos(token)
        pac_map, med_map, esp_map = _maps(pacientes, medicos, especialidades)
        now_iso = datetime.now().strftime("%Y-%m-%dT%H:%M")
        return render_template(
            "appointments/_form.html",
            pacientes=pacientes,
            medicos=medicos,
            especialidades=especialidades,
            values={},
            success="Turno registrado",
            turnos=turnos,
            pacientes_map=pac_map,
            medicos_map=med_map,
            especialidades_map=esp_map,
            now_iso=now_iso,
        )
    except Exception as exc:
        values = request.form.to_dict()
        return (
            render_template(
                "appointments/_form.html",
                pacientes=pacientes,
                medicos=medicos,
                especialidades=especialidades,
                error=str(exc),
                values=values,
            ),
            400,
        )


@bp.get("/_table")
def table_partial():
    token = session.get("token")
    pacientes, medicos, especialidades = _load_catalogs(token)
    turnos = _load_turnos(token)
    pac_map, med_map, esp_map = _maps(pacientes, medicos, especialidades)
    now_iso = datetime.now().strftime("%Y-%m-%dT%H:%M")
    return render_template(
        "appointments/_table.html",
        turnos=turnos,
        pacientes_map=pac_map,
        medicos_map=med_map,
        especialidades_map=esp_map,
        now_iso=now_iso,
    )


@bp.get("/<int:tid>/form")
def edit_form(tid: int):
    token = session.get("token")
    pacientes, medicos, especialidades = _load_catalogs(token)
    turno = asyncio.run(api.get(f"/turnos/{tid}", token=token))
    values = {
        "id": turno["id"],
        "paciente_id": turno["paciente_id"],
        "medico_id": turno["medico_id"],
        "especialidad_id": turno["especialidad_id"],
        "fecha": turno["fecha"],
        "duracion_min": turno["duracion_min"],
    }
    return render_template(
        "appointments/_edit_form.html",
        pacientes=pacientes,
        medicos=medicos,
        especialidades=especialidades,
        values=values,
    )


@bp.post("/<int:tid>/editar")
def editar(tid: int):
    token = session.get("token")
    pacientes, medicos, especialidades = _load_catalogs(token)
    try:
        payload = _build_payload(request.form)
        asyncio.run(api.put(f"/turnos/{tid}", payload, token=token))
        turnos = _load_turnos(token)
        pac_map, med_map, esp_map = _maps(pacientes, medicos, especialidades)
        now_iso = datetime.now().strftime("%Y-%m-%dT%H:%M")
        values = payload | {"id": tid}
        return render_template(
            "appointments/_edit_form.html",
            pacientes=pacientes,
            medicos=medicos,
            especialidades=especialidades,
            values=values,
            success="Turno actualizado",
            close_modal=True,
            turnos=turnos,
            pacientes_map=pac_map,
            medicos_map=med_map,
            especialidades_map=esp_map,
            now_iso=now_iso,
        )
    except Exception as exc:
        values = request.form.to_dict() | {"id": tid}
        return (
            render_template(
                "appointments/_edit_form.html",
                pacientes=pacientes,
                medicos=medicos,
                especialidades=especialidades,
                values=values,
                error=str(exc),
            ),
            400,
        )


@bp.post("/cancelar/<int:tid>")
def cancelar(tid: int):
    token = session.get("token")
    try:
        asyncio.run(api.post(f"/turnos/{tid}/cancelar", {}, token=token))
        turnos = _load_turnos(token)
        pacientes, medicos, especialidades = _load_catalogs(token)
        pac_map, med_map, esp_map = _maps(pacientes, medicos, especialidades)
        now_iso = datetime.now().strftime("%Y-%m-%dT%H:%M")
        return render_template(
            "appointments/_table.html",
            turnos=turnos,
            pacientes_map=pac_map,
            medicos_map=med_map,
            especialidades_map=esp_map,
            now_iso=now_iso,
        )
    except Exception as exc:
        return f"Error: {exc}", 400


@bp.get("/<int:tid>/consulta-form")
def consulta_form(tid: int):
    token = session.get("token")
    turno = asyncio.run(api.get(f"/turnos/{tid}", token=token))
    return render_template("appointments/_consultation_form.html", turno=turno)


@bp.post("/<int:tid>/consulta")
def registrar_consulta(tid: int):
    token = session.get("token")
    turno = asyncio.run(api.get(f"/turnos/{tid}", token=token))
    payload = {
        "motivo": request.form.get("motivo") or None,
        "observaciones": request.form.get("observaciones") or None,
        "diagnostico": request.form.get("diagnostico") or None,
        "indicaciones": request.form.get("indicaciones") or None,
    }
    receta_items = []
    medicamentos = request.form.getlist("medicamento")
    dosis_list = request.form.getlist("dosis")
    frecuencia_list = request.form.getlist("frecuencia")
    duracion_list = request.form.getlist("duracion")
    indicaciones_list = request.form.getlist("indicaciones_item")
    for idx, med in enumerate(medicamentos):
        med = med.strip()
        if not med:
            continue
        receta_items.append(
            {
                "medicamento": med,
                "dosis": dosis_list[idx] if idx < len(dosis_list) and dosis_list[idx] else None,
                "frecuencia": frecuencia_list[idx] if idx < len(frecuencia_list) and frecuencia_list[idx] else None,
                "duracion": duracion_list[idx] if idx < len(duracion_list) and duracion_list[idx] else None,
                "indicaciones": indicaciones_list[idx] if idx < len(indicaciones_list) and indicaciones_list[idx] else None,
            }
        )
    if receta_items:
        payload["receta"] = {
            "fecha_emision": datetime.now().date().isoformat(),
            "estado": "ACTIVA",
            "items": receta_items,
        }
    try:
        asyncio.run(api.post(f"/turnos/{tid}/consulta", payload, token=token))
        pacientes, medicos, especialidades = _load_catalogs(token)
        turnos = _load_turnos(token)
        pac_map, med_map, esp_map = _maps(pacientes, medicos, especialidades)
        now_iso = datetime.now().strftime("%Y-%m-%dT%H:%M")
        return render_template(
            "appointments/_consultation_form.html",
            close_modal=True,
            success="Consulta registrada",
            turnos=turnos,
            pacientes_map=pac_map,
            medicos_map=med_map,
            especialidades_map=esp_map,
            now_iso=now_iso,
        )
    except Exception as exc:
        return (
            render_template(
                "appointments/_consultation_form.html",
                turno=turno,
                error=str(exc),
            ),
            400,
        )


@bp.get("/recordatorio-form/<int:tid>")
def recordatorio_form(tid: int):
    token = session.get("token")
    turno = asyncio.run(api.get(f"/turnos/{tid}", token=token))
    recordatorios = asyncio.run(api.get(f"/turnos/{tid}/recordatorios", token=token))
    return render_template(
        "appointments/_reminder_form.html",
        turno=turno,
        recordatorios=recordatorios,
    )


@bp.post("/recordatorio/<int:tid>")
def programar_recordatorio(tid: int):
    token = session.get("token")
    canal = request.form.get("canal", "EMAIL")
    fecha = request.form.get("fecha")
    hora = request.form.get("hora")
    if not fecha or not hora:
        turno = asyncio.run(api.get(f"/turnos/{tid}", token=token))
        recordatorios = asyncio.run(api.get(f"/turnos/{tid}/recordatorios", token=token))
        return (
            render_template(
                "appointments/_reminder_form.html",
                turno=turno,
                recordatorios=recordatorios,
                error="Debe indicar fecha y hora",
            ),
            400,
        )
    programado = f"{fecha}T{hora}:00"
    try:
        asyncio.run(
            api.post(
                f"/turnos/{tid}/recordatorios",
                {"canal": canal, "programado_para": programado},
                token=token,
            )
        )
        turno = asyncio.run(api.get(f"/turnos/{tid}", token=token))
        recordatorios = asyncio.run(api.get(f"/turnos/{tid}/recordatorios", token=token))
        return render_template(
            "appointments/_reminder_form.html",
            turno=turno,
            recordatorios=recordatorios,
            success="Recordatorio programado",
        )
    except Exception as exc:
        turno = asyncio.run(api.get(f"/turnos/{tid}", token=token))
        recordatorios = asyncio.run(api.get(f"/turnos/{tid}/recordatorios", token=token))
        return (
            render_template(
                "appointments/_reminder_form.html",
                turno=turno,
                recordatorios=recordatorios,
                error=str(exc),
            ),
            400,
        )


@bp.get("/_grid")
def grid():
    token = session.get("token")
    medico_id = request.args.get("medico_id", type=int)
    fecha = request.args.get("fecha")
    dur = request.args.get("duracion_min", type=int, default=30)
    inicio = request.args.get("inicio", default="09:00")
    fin = request.args.get("fin", default="17:00")

    slots = []
    if medico_id and fecha:
        try:
            slots = _api_get(
                "/turnos/disponibles",
                token,
                params={"medico_id": medico_id, "fecha": fecha, "duracion_min": dur, "inicio": inicio, "fin": fin},
            )
        except Exception as e:
            flash(f"No se pudo obtener disponibilidad: {e}", "error")
    return render_template("appointments/_grid.html", slots=slots, duracion=dur)

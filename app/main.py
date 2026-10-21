from __future__ import annotations

import json
import os
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.database import db_session, init_db
from app.schemas import IncidentCreate, StatusUpdate, TelemetryInput
from app.services.rules_engine import SCENARIOS, evaluate_telemetry
from app.services.triage import triage_incident

load_dotenv()
STATIC_DIR = Path(__file__).parent / "static"
STATUSES = {"registrada","em_triagem","encaminhada","em_atendimento","aguardando_peca","resolvida","reaberta"}

def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def fetch_one(sql: str, params: tuple = ()) -> dict | None:
    with db_session() as con:
        row = con.execute(sql, params).fetchone()
        return dict(row) if row else None

def fetch_all(sql: str, params: tuple = ()) -> list[dict]:
    with db_session() as con:
        return [dict(r) for r in con.execute(sql, params).fetchall()]

def add_event(con, incident_id: int, event_type: str, old: str | None, new: str | None, actor: str, note: str) -> None:
    con.execute("""INSERT INTO incident_events
      (incident_id,event_type,old_status,new_status,actor,note,created_at)
      VALUES (?,?,?,?,?,?,?)""",(incident_id,event_type,old,new,actor,note,now()))

def incident_out(row: dict) -> dict:
    row["suggested_questions"] = json.loads(row.get("suggested_questions") or "[]")
    return row

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="Poço Vivo API", version="0.1.0",
 description="MVP de registro, triagem e acompanhamento de problemas de abastecimento.",
 lifespan=lifespan)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def home() -> str:
    return (STATIC_DIR / "index.html").read_text(encoding="utf-8")

@app.get("/api/health")
def health() -> dict:
    return {"status":"ok","project":"Poço Vivo","version":app.version,"mode":"demo"}

@app.get("/api/communities")
def communities() -> list[dict]:
    return fetch_all("SELECT id,name,municipality,responsible_name,responsible_role,responsible_confirmed FROM communities ORDER BY id")

@app.get("/api/dashboard")
def dashboard() -> dict:
    c = fetch_one("""SELECT COUNT(*) total,
      SUM(CASE WHEN status IN ('registrada','em_triagem') THEN 1 ELSE 0 END) triage,
      SUM(CASE WHEN status IN ('encaminhada','em_atendimento','aguardando_peca','reaberta') THEN 1 ELSE 0 END) open,
      SUM(CASE WHEN status='resolvida' THEN 1 ELSE 0 END) resolved FROM incidents""") or {}
    recent = fetch_all("""SELECT i.*,c.name community_name FROM incidents i JOIN communities c ON c.id=i.community_id ORDER BY i.id DESC LIMIT 8""")
    return {"total":c.get("total") or 0,"triage":c.get("triage") or 0,"open":c.get("open") or 0,"resolved":c.get("resolved") or 0,
            "latest_incidents":[incident_out(x) for x in recent],"demo_mode":True}

@app.get("/api/incidents")
def list_incidents(status: str | None = None, limit: int = Query(100, ge=1, le=300)) -> list[dict]:
    if status and status not in STATUSES:
        raise HTTPException(422,"Status inválido.")
    if status:
        rows = fetch_all("""SELECT i.*,c.name community_name FROM incidents i JOIN communities c ON c.id=i.community_id WHERE i.status=? ORDER BY i.id DESC LIMIT ?""",(status,limit))
    else:
        rows = fetch_all("""SELECT i.*,c.name community_name FROM incidents i JOIN communities c ON c.id=i.community_id ORDER BY i.id DESC LIMIT ?""",(limit,))
    return [incident_out(x) for x in rows]

@app.post("/api/incidents", status_code=201)
def create_incident(payload: IncidentCreate) -> dict:
    community = fetch_one("SELECT * FROM communities WHERE id=?",(payload.community_id,))
    if not community:
        raise HTTPException(404,"Comunidade não encontrada.")
    triage = triage_incident(payload.title,payload.description)
    confirmed = bool(community["responsible_confirmed"] and community["responsible_name"])
    assignee = community["responsible_name"] if confirmed else None
    status = "encaminhada" if confirmed else "em_triagem"
    routing_note = ("Destino inicial sugerido pelo cadastro confirmado; o destinatário ainda precisa aceitar." if confirmed
                    else "Responsável não confirmado no cadastro; requer triagem humana antes do encaminhamento.")
    created = now()
    public_id = f"PV-{datetime.now(timezone.utc):%y%m%d}-{uuid.uuid4().hex[:5].upper()}"
    with db_session() as con:
        cur = con.execute("""INSERT INTO incidents
          (public_id,community_id,title,description,category,priority,triage_source,suggested_questions,
           status,assignee,routing_note,created_at,updated_at)
          VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
          (public_id,payload.community_id,payload.title,payload.description,triage["category"],triage["priority"],
           triage["provider"],json.dumps(triage["questions"],ensure_ascii=False),status,assignee,routing_note,created,created))
        incident_id = cur.lastrowid
        add_event(con,incident_id,"criada",None,status,payload.reporter_alias,
                  f"{triage['summary']} {routing_note}")
    result = fetch_one("""SELECT i.*,c.name community_name FROM incidents i JOIN communities c ON c.id=i.community_id WHERE i.id=?""",(incident_id,))
    result = incident_out(result)
    result["triage_summary"] = triage["summary"]
    return result

@app.get("/api/incidents/{incident_id}")
def get_incident(incident_id: int) -> dict:
    row = fetch_one("""SELECT i.*,c.name community_name,c.municipality FROM incidents i JOIN communities c ON c.id=i.community_id WHERE i.id=?""",(incident_id,))
    if not row:
        raise HTTPException(404,"Ocorrência não encontrada.")
    row = incident_out(row)
    row["events"] = fetch_all("SELECT * FROM incident_events WHERE incident_id=? ORDER BY id",(incident_id,))
    return row

@app.patch("/api/incidents/{incident_id}/status")
def update_status(incident_id: int, payload: StatusUpdate) -> dict:
    incident = fetch_one("SELECT * FROM incidents WHERE id=?",(incident_id,))
    if not incident:
        raise HTTPException(404,"Ocorrência não encontrada.")
    if payload.status == "resolvida" and len(payload.note.strip()) < 8:
        raise HTTPException(422,"Para resolver, registre a providência e a verificação do restabelecimento.")
    t = now()
    with db_session() as con:
        con.execute("UPDATE incidents SET status=?,updated_at=?,closed_at=CASE WHEN ?='resolvida' THEN ? ELSE closed_at END WHERE id=?",
                    (payload.status,t,payload.status,t,incident_id))
        add_event(con,incident_id,"mudança_status",incident["status"],payload.status,payload.actor,payload.note)
    return get_incident(incident_id)

@app.get("/api/telemetry/latest")
def telemetry_latest() -> dict:
    rows = fetch_all("SELECT * FROM telemetry ORDER BY id DESC LIMIT 25")
    return {"items":rows,"count":len(rows)}

@app.get("/api/telemetry/summary")
def telemetry_summary() -> dict:
    row = fetch_one("""SELECT COUNT(*) total,
      SUM(CASE WHEN state='critico' THEN 1 ELSE 0 END) critical,
      SUM(CASE WHEN state='atencao' THEN 1 ELSE 0 END) warning FROM telemetry""") or {}
    return {"total":row.get("total") or 0,"critical":row.get("critical") or 0,"warning":row.get("warning") or 0}

@app.post("/api/telemetry", status_code=201)
def ingest_telemetry(payload: TelemetryInput) -> dict:
    data = payload.model_dump()
    state, message = evaluate_telemetry(data)
    t = now()
    with db_session() as con:
        cur = con.execute("""INSERT INTO telemetry
          (device_id,scenario,source,pump_expected_on,supply_present,motor_current_a,vibration_rms_g,flow_l_min,tank_level_pct,state,message,created_at)
          VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
          (data["device_id"],data["scenario"],data["source"],int(data["pump_expected_on"]),
           None if data["supply_present"] is None else int(data["supply_present"]),data["motor_current_a"],
           data["vibration_rms_g"],data["flow_l_min"],data["tank_level_pct"],state,message,t))
        ident = cur.lastrowid
    return {"id":ident,"state":state,"message":message,"created_at":t,"demo":data["source"]=="simulation"}

@app.post("/api/simulator/{scenario}", status_code=201)
def run_scenario(scenario: str) -> dict:
    if scenario not in SCENARIOS:
        raise HTTPException(404,"Cenário desconhecido.")
    data = SCENARIOS[scenario]
    result = ingest_telemetry(TelemetryInput(device_id="POCO-DEMO-001",scenario=scenario,source="simulation",**data))
    result["scenario"] = scenario
    result["readings"] = data
    return result

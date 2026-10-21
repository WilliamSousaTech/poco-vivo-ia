from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

DEFAULT_DB = "data/pocovivo.db"

def get_db_path() -> Path:
    return Path(os.getenv("POCOVIVO_DB", DEFAULT_DB))

@contextmanager
def db_session() -> Iterator[sqlite3.Connection]:
    path = get_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path, timeout=10)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    try:
        yield con
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()

def init_db() -> None:
    with db_session() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS communities(
          id INTEGER PRIMARY KEY, name TEXT NOT NULL, municipality TEXT NOT NULL,
          responsible_name TEXT, responsible_role TEXT,
          responsible_confirmed INTEGER NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS incidents(
          id INTEGER PRIMARY KEY AUTOINCREMENT, public_id TEXT NOT NULL UNIQUE,
          community_id INTEGER NOT NULL REFERENCES communities(id),
          title TEXT NOT NULL, description TEXT NOT NULL, category TEXT NOT NULL,
          priority TEXT NOT NULL, triage_source TEXT NOT NULL,
          suggested_questions TEXT NOT NULL DEFAULT '[]',
          status TEXT NOT NULL, assignee TEXT, routing_note TEXT NOT NULL,
          created_at TEXT NOT NULL, updated_at TEXT NOT NULL, closed_at TEXT
        );
        CREATE TABLE IF NOT EXISTS incident_events(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          incident_id INTEGER NOT NULL REFERENCES incidents(id) ON DELETE CASCADE,
          event_type TEXT NOT NULL, old_status TEXT, new_status TEXT,
          actor TEXT NOT NULL, note TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS telemetry(
          id INTEGER PRIMARY KEY AUTOINCREMENT, device_id TEXT NOT NULL,
          scenario TEXT NOT NULL, source TEXT NOT NULL, pump_expected_on INTEGER NOT NULL,
          supply_present INTEGER, motor_current_a REAL, vibration_rms_g REAL,
          flow_l_min REAL, tank_level_pct REAL, state TEXT NOT NULL,
          message TEXT NOT NULL, created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_incident_status ON incidents(status);
        CREATE INDEX IF NOT EXISTS idx_event_incident ON incident_events(incident_id);
        CREATE INDEX IF NOT EXISTS idx_telemetry_device ON telemetry(device_id, id DESC);
        """)
        con.execute("""INSERT OR IGNORE INTO communities
          (id,name,municipality,responsible_name,responsible_role,responsible_confirmed)
          VALUES (1,'Povoado São José (demonstração)','Município demonstrativo',
          'Equipe de Abastecimento — exemplo','operador',1)""")
        con.execute("""INSERT OR IGNORE INTO communities
          (id,name,municipality,responsible_name,responsible_role,responsible_confirmed)
          VALUES (2,'Comunidade Boa Vista (demonstração)','Município demonstrativo',
          NULL,NULL,0)""")

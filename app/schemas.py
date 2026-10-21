from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

Category = Literal["sem_abastecimento","falha_bomba","falta_energia","vazamento","outro"]
Priority = Literal["urgente","alta","media","baixa"]
Status = Literal["registrada","em_triagem","encaminhada","em_atendimento","aguardando_peca","resolvida","reaberta"]

class IncidentCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    community_id: int = Field(ge=1)
    title: str = Field(min_length=4, max_length=120)
    description: str = Field(min_length=8, max_length=3000)
    reporter_alias: str = Field(default="Morador(a)", min_length=1, max_length=80)

class StatusUpdate(BaseModel):
    status: Status
    actor: str = Field(default="Equipe demonstrativa", min_length=1, max_length=100)
    note: str = Field(default="", max_length=1500)

class TelemetryInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    device_id: str = Field(min_length=2, max_length=80)
    scenario: str = Field(default="manual", max_length=80)
    source: str = Field(default="simulation", max_length=40)
    pump_expected_on: bool
    supply_present: bool | None = None
    motor_current_a: float | None = Field(default=None, ge=0, le=1000)
    vibration_rms_g: float | None = Field(default=None, ge=0, le=1000)
    flow_l_min: float | None = Field(default=None, ge=0, le=100000)
    tank_level_pct: float | None = Field(default=None, ge=0, le=100)

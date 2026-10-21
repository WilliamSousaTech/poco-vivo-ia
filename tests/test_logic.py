from app.services.triage import local_triage
from app.services.rules_engine import evaluate_telemetry, SCENARIOS

def test_power_loss_is_critical():
    state, _ = evaluate_telemetry(SCENARIOS["power_loss"])
    assert state == "critico"

def test_expected_off_is_not_a_failure():
    state, _ = evaluate_telemetry({"pump_expected_on":False,"supply_present":True,"motor_current_a":0})
    assert state == "normal"

def test_vibration_rule():
    state, _ = evaluate_telemetry(SCENARIOS["irregular"])
    assert state == "atencao"

def test_local_triage_bomba():
    r = local_triage("Poço parou", "A comunidade está sem água desde ontem.")
    assert r["priority"] == "urgente"
    assert r["provider"] == "regras_locais"

def test_local_triage_vazamento():
    assert local_triage("Vazamento", "Um cano quebrou")["category"] == "vazamento"

from typing import Any

def evaluate_telemetry(data: dict[str, Any]) -> tuple[str, str]:
    if not data.get("pump_expected_on"):
        return "normal", "A bomba não deveria estar ligada; parada pode ser normal."
    if data.get("supply_present") is False:
        return "critico", "Sinal de ausência de alimentação enquanto a bomba deveria operar; verificar instalação."
    current = data.get("motor_current_a")
    if data.get("supply_present") is True and current is not None and current <= 0.05:
        return "critico", "Alimentação indicada como presente, sem corrente medida; conferir circuito e medição."
    vib = data.get("vibration_rms_g")
    if vib is not None and vib > 0.45:
        return "atencao", "Vibração acima do limite demonstrativo; comparar com referência do equipamento."
    flow = data.get("flow_l_min")
    if flow is not None and flow <= 0.1:
        return "atencao", "Vazão baixa durante operação esperada; investigar bomba e tubulação."
    if data.get("supply_present") is None and current is None:
        return "desconhecido", "Dados insuficientes para avaliar condição elétrica."
    return "normal", "Nenhuma anomalia prevista nas regras demonstrativas foi detectada."

SCENARIOS = {
 "normal": dict(pump_expected_on=True,supply_present=True,motor_current_a=2.1,vibration_rms_g=0.08,flow_l_min=8.4,tank_level_pct=64.0),
 "power_loss": dict(pump_expected_on=True,supply_present=False,motor_current_a=0.0,vibration_rms_g=0.0,flow_l_min=0.0,tank_level_pct=39.0),
 "motor_stopped": dict(pump_expected_on=True,supply_present=True,motor_current_a=0.0,vibration_rms_g=0.0,flow_l_min=0.0,tank_level_pct=27.0),
 "irregular": dict(pump_expected_on=True,supply_present=True,motor_current_a=3.8,vibration_rms_g=0.72,flow_l_min=2.0,tank_level_pct=23.0),
 "offline": dict(pump_expected_on=True,supply_present=None,motor_current_a=None,vibration_rms_g=None,flow_l_min=None,tank_level_pct=None),
}

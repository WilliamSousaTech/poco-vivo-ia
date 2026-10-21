from __future__ import annotations

import json
import os
import re
from typing import Any

CATEGORIES = {"sem_abastecimento","falha_bomba","falta_energia","vazamento","outro"}
PRIORITIES = {"urgente","alta","media","baixa"}

def local_triage(title: str, description: str) -> dict[str, Any]:
    text = f"{title} {description}".lower()
    if any(x in text for x in ("vazamento","cano quebrado","tubulação rompida","tubulacao rompida")):
        category, priority = "vazamento", "alta"
    elif any(x in text for x in ("energia","sem luz","falta de luz","alimentação elétrica","alimentacao eletrica")):
        category, priority = "falta_energia", "alta"
    elif any(x in text for x in ("bomba","motor","poço parou","poco parou","não liga","nao liga","sem corrente")):
        category, priority = "falha_bomba", "alta"
    elif any(x in text for x in ("sem água","sem agua","sem abastecimento","comunidade toda")):
        category, priority = "sem_abastecimento", "urgente"
    else:
        category, priority = "outro", "media"
    if any(x in text for x in ("sem água","sem agua","sem abastecimento","poço parou","poco parou","bomba parou")):
        priority = "urgente"
    return {
        "category": category,
        "priority": priority,
        "questions": [
            "Desde quando o problema acontece?",
            "A comunidade está totalmente sem água ou o abastecimento está reduzido?"
        ],
        "summary": "Sugestão por regras locais; confirme os fatos com a comunidade.",
        "provider": "regras_locais",
    }

def _extract_json(text: str) -> dict[str, Any]:
    match = re.search(r"\{.*\}", text, re.S)
    if not match:
        raise ValueError("Resposta da IA sem objeto JSON.")
    return json.loads(match.group(0))

def triage_incident(title: str, description: str) -> dict[str, Any]:
    key, model = os.getenv("OPENAI_API_KEY","").strip(), os.getenv("OPENAI_MODEL","").strip()
    if not key or not model:
        return local_triage(title, description)
    try:
        from openai import OpenAI
        client = OpenAI(api_key=key, timeout=12, max_retries=1)
        response = client.responses.create(
            model=model,
            input=[
              {"role":"system","content":
               "Você auxilia triagem de problemas de abastecimento comunitário. Não diagnostique causa técnica como fato. Não invente responsável nem prazo. Responda somente JSON com category, priority, questions, summary. category: sem_abastecimento, falha_bomba, falta_energia, vazamento, outro. priority: urgente, alta, media, baixa. Sugira e não tome decisões definitivas."},
              {"role":"user","content":json.dumps({"title":title[:120],"description":description[:3000]},ensure_ascii=False)}
            ],
        )
        data = _extract_json(response.output_text)
        if data.get("category") not in CATEGORIES or data.get("priority") not in PRIORITIES:
            return local_triage(title, description)
        questions = data.get("questions", [])
        if not isinstance(questions, list):
            questions = []
        return {
          "category":data["category"], "priority":data["priority"],
          "questions":[str(q)[:240] for q in questions[:4]],
          "summary":str(data.get("summary","Sugestão da IA a ser revisada."))[:500],
          "provider":"openai"
        }
    except Exception:
        result = local_triage(title, description)
        result["provider"] = "regras_locais_fallback"
        result["summary"] = "IA externa indisponível; usado fallback por regras locais."
        return result

from campuscare.logic_engine import analyze_case


def test_logic_engine_detects_router_down():
    case = {
        "room_name": "Lab_1",
        "room_type": "laboratorio",
        "device": "router_laboratorio",
        "symptom": "connessione_assente",
        "event_in_minutes": 20,
        "users_involved": 72,
        "exam_or_lecture": 1,
        "temperature": 26.0,
        "network_load": 0.88,
    }

    result = analyze_case(case)

    assert result.fault == "router_down"
    assert result.intervention == "riavvio_o_sostituzione_router"
    assert result.rule_priority in {"alta", "critica"}
    assert len(result.explanations) > 0


def test_logic_engine_default_case():
    case = {
        "room_name": "Aula_A",
        "room_type": "aula",
        "device": "lim",
        "symptom": "connessione_lenta",
        "event_in_minutes": 180,
        "users_involved": 10,
        "exam_or_lecture": 0,
        "temperature": 22.0,
        "network_load": 0.2,
    }

    result = analyze_case(case)

    assert result.fault == "nessun_guasto_critico"
    assert result.intervention == "monitoraggio"
    assert result.rule_priority in {"bassa", "media"}
    assert len(result.explanations) > 0
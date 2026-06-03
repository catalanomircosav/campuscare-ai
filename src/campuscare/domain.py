"""Definizione del dominio di CampusCare AI.

Questo modulo contiene il vocabolario controllato del sistema:
ambienti, dispositivi, sintomi, guasti, interventi, tecnici e coordinate.

Tutti gli altri moduli devono usare questi valori, così il progetto resta coerente.
"""

from __future__ import annotations


ROOM_TYPES = [
    "aula",
    "laboratorio",
    "biblioteca",
    "ufficio",
]


DEVICES = [
    "proiettore",
    "pc_docente",
    "rete_wifi",
    "router_laboratorio",
    "lim",
    "climatizzatore",
    "impianto_audio",
    "presa_elettrica",
]


SYMPTOMS = [
    "non_si_accende",
    "nessun_segnale",
    "connessione_assente",
    "connessione_lenta",
    "audio_assente",
    "temperatura_alta",
    "immagine_distorta",
    "riavvii_frequenti",
    "odore_bruciato",
]


FAULTS = [
    "cavo_hdmi_guasto",
    "input_configurato_male",
    "router_down",
    "sovraccarico_rete",
    "alimentazione_guasta",
    "climatizzazione_guasta",
    "impianto_audio_guasto",
    "hardware_pc_guasto",
    "nessun_guasto_critico",
]

FAULT_COMPETENCE = {
    "cavo_hdmi_guasto": "audiovisivo",
    "input_configurato_male": "audiovisivo",
    "router_down": "rete",
    "sovraccarico_rete": "rete",
    "alimentazione_guasta": "elettrico",
    "climatizzazione_guasta": "impianti",
    "impianto_audio_guasto": "audiovisivo",
    "hardware_pc_guasto": "informatica",
    "nessun_guasto_critico": "informatica",
}

INTERVENTIONS = {
    "cavo_hdmi_guasto": "sostituzione_cavo_hdmi",
    "input_configurato_male": "riconfigurazione_dispositivo",
    "router_down": "riavvio_o_sostituzione_router",
    "sovraccarico_rete": "analisi_rete",
    "alimentazione_guasta": "intervento_elettrico",
    "climatizzazione_guasta": "intervento_climatizzazione",
    "impianto_audio_guasto": "controllo_impianto_audio",
    "hardware_pc_guasto": "diagnosi_pc_docente",
    "nessun_guasto_critico": "monitoraggio",
}


PRIORITIES = [
    "bassa",
    "media",
    "alta",
    "critica",
]


DEVICE_COMPETENCE = {
    "proiettore": "audiovisivo",
    "pc_docente": "informatica",
    "rete_wifi": "rete",
    "router_laboratorio": "rete",
    "lim": "audiovisivo",
    "climatizzatore": "impianti",
    "impianto_audio": "audiovisivo",
    "presa_elettrica": "elettrico",
}


TECHNICIANS = [
    {
        "name": "tecnico_it",
        "skills": {"informatica", "rete", "audiovisivo"},
        "available": True,
        "position": (0, 0),
    },
    {
        "name": "tecnico_rete",
        "skills": {"rete", "informatica"},
        "available": True,
        "position": (7, 2),
    },
    {
        "name": "manutentore_elettrico",
        "skills": {"elettrico"},
        "available": True,
        "position": (2, 8),
    },
    {
        "name": "manutentore_impianti",
        "skills": {"impianti", "elettrico"},
        "available": True,
        "position": (8, 8),
    },
]


ROOM_COORDINATES = {
    "Aula_A": (1, 2),
    "Aula_B": (4, 1),
    "Lab_1": (8, 2),
    "Lab_2": (8, 6),
    "Biblioteca": (3, 7),
    "Ufficio_Segreteria": (0, 8),
}


ROOM_TYPE_BY_NAME = {
    "Aula_A": "aula",
    "Aula_B": "aula",
    "Lab_1": "laboratorio",
    "Lab_2": "laboratorio",
    "Biblioteca": "biblioteca",
    "Ufficio_Segreteria": "ufficio",
}
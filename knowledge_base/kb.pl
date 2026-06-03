% CampusCare AI - Knowledge Base Prolog
% File generato automaticamente da src/campuscare/prolog_export.py

% Ambienti
ambiente(aula_a, aula).
ambiente(aula_b, aula).
ambiente(biblioteca, biblioteca).
ambiente(lab_1, laboratorio).
ambiente(lab_2, laboratorio).
ambiente(ufficio_segreteria, ufficio).

% Dispositivi
dispositivo(climatizzatore).
dispositivo(impianto_audio).
dispositivo(lim).
dispositivo(pc_docente).
dispositivo(presa_elettrica).
dispositivo(proiettore).
dispositivo(rete_wifi).
dispositivo(router_laboratorio).

% Sintomi
sintomo(audio_assente).
sintomo(connessione_assente).
sintomo(connessione_lenta).
sintomo(immagine_distorta).
sintomo(nessun_segnale).
sintomo(non_si_accende).
sintomo(odore_bruciato).
sintomo(riavvii_frequenti).
sintomo(temperatura_alta).

% Diagnosi simboliche: diagnosi(Dispositivo, Sintomo, Guasto).
diagnosi(climatizzatore, non_si_accende, alimentazione_guasta).
diagnosi(climatizzatore, temperatura_alta, climatizzazione_guasta).
diagnosi(impianto_audio, audio_assente, impianto_audio_guasto).
diagnosi(impianto_audio, non_si_accende, alimentazione_guasta).
diagnosi(lim, nessun_segnale, input_configurato_male).
diagnosi(lim, non_si_accende, alimentazione_guasta).
diagnosi(pc_docente, connessione_assente, router_down).
diagnosi(pc_docente, connessione_lenta, sovraccarico_rete).
diagnosi(pc_docente, non_si_accende, alimentazione_guasta).
diagnosi(pc_docente, riavvii_frequenti, hardware_pc_guasto).
diagnosi(presa_elettrica, non_si_accende, alimentazione_guasta).
diagnosi(presa_elettrica, odore_bruciato, alimentazione_guasta).
diagnosi(proiettore, immagine_distorta, input_configurato_male).
diagnosi(proiettore, nessun_segnale, cavo_hdmi_guasto).
diagnosi(proiettore, non_si_accende, alimentazione_guasta).
diagnosi(rete_wifi, connessione_assente, router_down).
diagnosi(rete_wifi, connessione_lenta, sovraccarico_rete).
diagnosi(router_laboratorio, connessione_assente, router_down).
diagnosi(router_laboratorio, connessione_lenta, sovraccarico_rete).

% Interventi: intervento(Guasto, Intervento).
intervento(alimentazione_guasta, intervento_elettrico).
intervento(cavo_hdmi_guasto, sostituzione_cavo_hdmi).
intervento(climatizzazione_guasta, intervento_climatizzazione).
intervento(hardware_pc_guasto, diagnosi_pc_docente).
intervento(impianto_audio_guasto, controllo_impianto_audio).
intervento(input_configurato_male, riconfigurazione_dispositivo).
intervento(nessun_guasto_critico, monitoraggio).
intervento(router_down, riavvio_o_sostituzione_router).
intervento(sovraccarico_rete, analisi_rete).

% Competenze richieste dai dispositivi.
competenza_dispositivo(climatizzatore, impianti).
competenza_dispositivo(impianto_audio, audiovisivo).
competenza_dispositivo(lim, audiovisivo).
competenza_dispositivo(pc_docente, informatica).
competenza_dispositivo(presa_elettrica, elettrico).
competenza_dispositivo(proiettore, audiovisivo).
competenza_dispositivo(rete_wifi, rete).
competenza_dispositivo(router_laboratorio, rete).

% Competenze richieste dai guasti.
competenza_guasto(alimentazione_guasta, elettrico).
competenza_guasto(cavo_hdmi_guasto, audiovisivo).
competenza_guasto(climatizzazione_guasta, impianti).
competenza_guasto(hardware_pc_guasto, informatica).
competenza_guasto(impianto_audio_guasto, audiovisivo).
competenza_guasto(input_configurato_male, audiovisivo).
competenza_guasto(nessun_guasto_critico, informatica).
competenza_guasto(router_down, rete).
competenza_guasto(sovraccarico_rete, rete).

% Tecnici e competenze.
disponibile(tecnico_it).
competenza_tecnico(tecnico_it, audiovisivo).
competenza_tecnico(tecnico_it, informatica).
competenza_tecnico(tecnico_it, rete).
disponibile(tecnico_rete).
competenza_tecnico(tecnico_rete, informatica).
competenza_tecnico(tecnico_rete, rete).
disponibile(manutentore_elettrico).
competenza_tecnico(manutentore_elettrico, elettrico).
disponibile(manutentore_impianti).
competenza_tecnico(manutentore_impianti, elettrico).
competenza_tecnico(manutentore_impianti, impianti).

% Regole derivate.
puo_intervenire(Tecnico, Guasto) :-
    competenza_guasto(Guasto, Competenza),
    competenza_tecnico(Tecnico, Competenza),
    disponibile(Tecnico).

cura_per(Dispositivo, Sintomo, Intervento) :-
    diagnosi(Dispositivo, Sintomo, Guasto),
    intervento(Guasto, Intervento).

tecnico_per(Dispositivo, Sintomo, Tecnico) :-
    diagnosi(Dispositivo, Sintomo, Guasto),
    puo_intervenire(Tecnico, Guasto).

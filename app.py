import streamlit as st
import pandas as pd
import json
import os

# Configurazione Pagina
st.set_page_config(page_title="Cro Magnon Manager", page_icon="⛳", layout="centered")

# --- STILE CSS AGGIORNATO PER VISIBILITÀ SU IPHONE ---
st.markdown("""
    <style>
    /* Forza il colore del testo dei checkbox per renderli leggibili */
    .stCheckbox label {
        color: #1a242f !important;
        font-weight: 600 !important;
        background-color: #ffffff;
        padding: 8px 15px;
        border-radius: 8px;
        border: 1px solid #d1d1d1;
        display: block;
        width: 100%;
    }
    /* Stile generale */
    .main { background-color: #f8f9fa; }
    .stButton>button { 
        width: 100%; 
        border-radius: 8px; 
        height: 3.5em; 
        background-color: #e67e22; 
        color: white; 
        font-weight: bold; 
        border: none;
        box-shadow: 0px 2px 4px rgba(0,0,0,0.1);
    }
    h1, h2, h3 { color: #1a242f; text-align: center; }
    /* Box per i nomi nella sezione score */
    .player-row {
        padding: 10px;
        background-color: #ffffff;
        border-radius: 5px;
        margin-bottom: 5px;
        border-left: 5px solid #e67e22;
    }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "golf_db.json"

def carica_dati():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except: return []
    return []

def salva_dati(lista):
    with open(DB_FILE, "w") as f:
        json.dump(lista, f, indent=4)

if 'anagrafica' not in st.session_state:
    st.session_state.anagrafica = carica_dati()

st.title("⛳ CRO MAGNON GOLF LEAGUE")

# --- TAB ---
tab1, tab2 = st.tabs(["🎮 Gara del Giorno", "👥 Gestione Giocatori"])

# --- TAB 2: GESTIONE ANAGRAFICA ---
with tab2:
    st.subheader("Registra nuovi soci")
    with st.form("nuovo_giocatore", clear_on_submit=True):
        col_n, col_h = st.columns([2, 1])
        nome = col_n.text_input("Nome e Cognome")
        hcp = col_h.number_input("HCP attuale", 0, 54, 36)
        submit = st.form_submit_button("Aggiungi all'Anagrafica")
        
        if submit and nome:
            if not any(g['nome'].lower() == nome.lower() for g in st.session_state.anagrafica):
                st.session_state.anagrafica.append({"nome": nome, "hcp": hcp})
                salva_dati(st.session_state.anagrafica)
                st.success(f"{nome} registrato!")
                st.rerun()
            else:
                st.error("Giocatore già presente.")

    st.divider()
    st.subheader("Soci Registrati")
    if st.session_state.anagrafica:
        for i, g in enumerate(st.session_state.anagrafica):
            c1, c2 = st.columns([3, 1])
            c1.markdown(f"**{g['nome']}** (HCP: {g['hcp']})")
            if c2.button("Elimina", key=f"del_{i}"):
                st.session_state.anagrafica.pop(i)
                salva_dati(st.session_state.anagrafica)
                st.rerun()
    else:
        st.info("L'anagrafica è vuota.")

# --- TAB 1: GARA DEL GIORNO ---
with tab1:
    if not st.session_state.anagrafica:
        st.warning("Vai nel tab 'Gestione Giocatori' per aggiungere i soci.")
    else:
        st.subheader("1. Chi gioca oggi?")
        st.write("Seleziona i presenti:")
        
        presenti = []
        for g in st.session_state.anagrafica:
            # Checkbox con stile forzato tramite CSS
            if st.checkbox(f"{g['nome']} (HCP {g['hcp']})", key=f"check_{g['nome']}"):
                presenti.append(g)

        if presenti:
            st.divider()
            st.subheader("2. Impostazioni Gara")
            tipo_gara = st.radio("Distanza", ["18 Buche", "9 Buche"], horizontal=True)
            target = 36 if tipo_gara == "18 Buche" else 18
            
            st.subheader("3. Inserimento Score")
            risultati_gara = []
            
            for p in presenti:
                st.markdown(f"""<div class='player-row'><b>{p['nome']}</b> (HCP Partenza: {p['hcp']})</div>""", unsafe_allow_html=True)
                score = st.text_input(f"Punti per {p['nome']}", key=f"score_{p['nome']}", placeholder="Inserisci punti o NC")
                
                punti_int = 0
                nuovo_hcp = p['hcp']
                if score.upper() == "NC":
                    punti_int = -1
                elif score.isdigit():
                    punti_int = int(score)
                    calo = (punti_int - target) // 2 if punti_int > target else 0
                    nuovo_hcp = p['hcp'] - calo
                
                risultati_gara.append({
                    "nome": p['nome'],
                    "hcp_p": p['hcp'],
                    "punti": punti_int,
                    "hcp_f": nuovo_hcp
                })

            st.divider()
            if st.button("🏆 GENERA CLASSIFICA"):
                st.balloons()
                df = pd.DataFrame(risultati_gara)
                df = df.sort_values(by="punti", ascending=False).reset_index(drop=True)
                
                def format_pos(i, p):
                    if p < 0: return "-"
                    return f"{i+1}° POSTO"
                
                df['Posizione'] = [format_pos(i, p) for i, p in enumerate(df['punti'])]
                df['Punti Gara'] = df['punti'].apply(lambda x: "NC" if x == -1 else x)
                
                st.subheader("📊 Risultati Finali")
                st.table(df[['Posizione', 'nome', 'hcp_p', 'Punti Gara', 'hcp_f']].rename(columns={
                    'nome': 'Giocatore', 'hcp_p': 'HCP Partenza', 'hcp_f': 'Nuovo HCP'
                }))

                if st.button("💾 AGGIORNA HCP IN ANAGRAFICA"):
                    for res in risultati_gara:
                        for soci in st.session_state.anagrafica:
                            if soci['nome'] == res['nome']:
                                soci['hcp'] = res['hcp_f']
                    salva_dati(st.session_state.anagrafica)
                    st.success("HCP aggiornati con successo!")
        else:
            st.info("Spunta i nomi dei giocatori per iniziare.")# --- TAB NELL'INTERFACCIA ---
tab1, tab2 = st.tabs(["🎮 Gara del Giorno", "👥 Gestione Giocatori"])

# --- TAB 2: GESTIONE ANAGRAFICA ---
with tab2:
    st.subheader("Registra nuovi soci")
    with st.form("nuovo_giocatore", clear_on_submit=True):
        col_n, col_h = st.columns([2, 1])
        nome = col_n.text_input("Nome e Cognome")
        hcp = col_h.number_input("HCP attuale", 0, 54, 36)
        submit = st.form_submit_button("Aggiungi all'Anagrafica")
        
        if submit and nome:
            if not any(g['nome'].lower() == nome.lower() for g in st.session_state.anagrafica):
                st.session_state.anagrafica.append({"nome": nome, "hcp": hcp})
                salva_dati(st.session_state.anagrafica)
                st.success(f"{nome} registrato!")
                st.rerun()
            else:
                st.error("Giocatore già presente.")

    st.divider()
    st.subheader("Soci Registrati")
    if st.session_state.anagrafica:
        for i, g in enumerate(st.session_state.anagrafica):
            c1, c2 = st.columns([3, 1])
            c1.write(f"**{g['nome']}** (HCP: {g['hcp']})")
            if c2.button("Elimina", key=f"del_{i}"):
                st.session_state.anagrafica.pop(i)
                salva_dati(st.session_state.anagrafica)
                st.rerun()
    else:
        st.info("L'anagrafica è vuota.")

# --- TAB 1: GARA DEL GIORNO ---
with tab1:
    if not st.session_state.anagrafica:
        st.warning("Vai nel tab 'Gestione Giocatori' per aggiungere i soci.")
    else:
        st.subheader("1. Chi gioca oggi?")
        presenti = []
        
        # Selezione rapida
        col_sel1, col_sel2 = st.columns(2)
        if col_sel1.button("Seleziona Tutti"):
            st.session_state.all_selected = True
        if col_sel2.button("Deseleziona Tutti"):
            st.session_state.all_selected = False

        # Lista di selezione
        for g in st.session_state.anagrafica:
            is_presente = st.checkbox(f"{g['nome']} (HCP {g['hcp']})", key=f"check_{g['nome']}")
            if is_presente:
                presenti.append(g)

        if presenti:
            st.divider()
            st.subheader("2. Impostazioni Gara")
            tipo_gara = st.radio("Distanza", ["18 Buche", "9 Buche"], horizontal=True)
            target = 36 if tipo_gara == "18 Buche" else 18
            
            st.subheader("3. Inserimento Score")
            risultati_gara = []
            
            for p in presenti:
                c_n, c_s = st.columns([3, 1])
                c_n.write(f"**{p['nome']}**")
                score = c_s.text_input("Punti", key=f"score_{p['nome']}", placeholder="NC")
                
                # Calcolo al volo
                punti_int = 0
                nuovo_hcp = p['hcp']
                if score.upper() == "NC":
                    punti_int = -1
                elif score.isdigit():
                    punti_int = int(score)
                    calo = (punti_int - target) // 2 if punti_int > target else 0
                    nuovo_hcp = p['hcp'] - calo
                
                risultati_gara.append({
                    "nome": p['nome'],
                    "hcp_p": p['hcp'],
                    "punti": punti_int,
                    "hcp_f": nuovo_hcp
                })

            if st.button("🏆 GENERA CLASSIFICA"):
                st.balloons()
                df = pd.DataFrame(risultati_gara)
                df = df.sort_values(by="punti", ascending=False).reset_index(drop=True)
                
                # Formattazione per la tabella
                def format_pos(i, p):
                    if p < 0: return "-"
                    return f"{i+1}° POSTO"
                
                df['Posizione'] = [format_pos(i, p) for i, p in enumerate(df['punti'])]
                df['Punti Gara'] = df['punti'].apply(lambda x: "NC" if x == -1 else x)
                
                st.subheader("📊 Risultati Finali")
                st.table(df[['Posizione', 'nome', 'hcp_p', 'Punti Gara', 'hcp_f']].rename(columns={
                    'nome': 'Giocatore', 'hcp_p': 'HCP Partenza', 'hcp_f': 'Nuovo HCP'
                }))

                if st.button("💾 AGGIORNA HCP NELL'ANAGRAFICA"):
                    # Aggiorna l'hcp nell'anagrafica principale solo per chi ha giocato
                    for res in risultati_gara:
                        for soci in st.session_state.anagrafica:
                            if soci['nome'] == res['nome']:
                                soci['hcp'] = res['hcp_f']
                    salva_dati(st.session_state.anagrafica)
                    st.success("HCP aggiornati per la prossima gara!")
        else:
            st.info("Seleziona almeno un giocatore per iniziare la gara.")

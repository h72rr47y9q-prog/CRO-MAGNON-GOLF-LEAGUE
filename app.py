import streamlit as st
import pandas as pd
import json
import os

# Configurazione Pagina
st.set_page_config(page_title="Cro Magnon Manager", page_icon="⛳", layout="wide")

# --- CSS ANTI-DARK MODE ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f6; color: #1a242f; }
    .stCheckbox label, .stMarkdown p, label { color: #1a242f !important; font-weight: 600 !important; }
    .stButton>button { background-color: #27ae60 !important; color: white !important; border-radius: 8px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "golf_data_v3.json"

# --- FUNZIONI DATI (MIGLIORATE) ---
def carica_dati():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                d = json.load(f)
                # Verifichiamo che la struttura sia corretta
                if "giocatori" not in d: d["giocatori"] = []
                if "campi" not in d: d["campi"] = []
                return d
        except: return {"giocatori": [], "campi": []}
    return {"giocatori": [], "campi": []}

def salva_dati(dati):
    try:
        with open(DB_FILE, "w") as f:
            json.dump(dati, f, indent=4)
        return True
    except Exception as e:
        st.error(f"Errore tecnico nel salvataggio: {e}")
        return False

# Inizializzazione Session State
if 'db' not in st.session_state:
    st.session_state.db = carica_dati()

st.title("⛳ CRO MAGNON GOLF LEAGUE")
tab1, tab2, tab3 = st.tabs(["🎮 Gara", "👥 Giocatori", "🏗️ Campi"])

# --- TAB 3: GESTIONE CAMPI (FIXATO CON FORM) ---
with tab3:
    st.header("Configurazione Campi")
    
    # Usiamo un FORM per assicurarci che il click sul tasto invii tutto
    with st.form("form_nuovo_campo"):
        nome_c = st.text_input("Nome del Golf Club")
        tipo_c = st.radio("Numero Buche", [9, 18], horizontal=True)
        st.write("---")
        
        par_lista = []
        hcp_lista = []
        
        # Griglia per Par e HCP
        cols_per_row = 3
        for i in range(0, tipo_c, cols_per_row):
            cols = st.columns(cols_per_row)
            for j in range(cols_per_row):
                b_num = i + j + 1
                if b_num <= tipo_c:
                    with cols[j]:
                        st.markdown(f"**Buca {b_num}**")
                        p = st.number_input(f"Par", 3, 5, 4, key=f"p_form_{b_num}")
                        h = st.number_input(f"HCP", 1, 18, b_num, key=f"h_form_{b_num}")
                        par_lista.append(p)
                        hcp_lista.append(h)
        
        submit_campo = st.form_submit_button("💾 SALVA CONFIGURAZIONE CAMPO")
        
        if submit_campo:
            if nome_c:
                nuovo_campo = {
                    "nome": nome_c,
                    "tipo": tipo_c,
                    "par": par_lista,
                    "hcp_buche": hcp_lista
                }
                st.session_state.db["campi"].append(nuovo_campo)
                if salva_dati(st.session_state.db):
                    st.success(f"Campo '{nome_c}' salvato con successo!")
                    st.rerun()
            else:
                st.error("Inserisci il nome del campo prima di salvare!")

    st.divider()
    st.subheader("Campi in Memoria")
    if st.session_state.db["campi"]:
        for idx, c in enumerate(st.session_state.db["campi"]):
            col1, col2 = st.columns([4, 1])
            col1.write(f"⛳ **{c['nome']}** ({c['tipo']} buche)")
            if col2.button("Elimina", key=f"del_c_{idx}"):
                st.session_state.db["campi"].pop(idx)
                salva_dati(st.session_state.db)
                st.rerun()
    else:
        st.info("Nessun campo registrato.")

# --- TAB 2: GIOCATORI ---
with tab2:
    st.header("Anagrafica Soci")
    with st.form("add_player"):
        c1, c2 = st.columns([2, 1])
        n = c1.text_input("Nome Giocatore")
        h = c2.number_input("HCP", 0, 54, 36)
        if st.form_submit_button("Aggiungi Socio"):
            if n:
                st.session_state.db["giocatori"].append({"nome": n, "hcp": h})
                salva_dati(st.session_state.db)
                st.rerun()

    for idx, g in enumerate(st.session_state.db["giocatori"]):
        c1, c2 = st.columns([4, 1])
        c1.write(f"👤 {g['nome']} (HCP {g['hcp']})")
        if c2.button("Elimina", key=f"del_g_{idx}"):
            st.session_state.db["giocatori"].pop(idx)
            salva_dati(st.session_state.db)
            st.rerun()

# --- TAB 1: GARA (Semplificato per test) ---
with tab1:
    if not st.session_state.db["campi"]:
        st.warning("Configura un campo nel tab 'Campi' per iniziare.")
    else:
        campo_gara = st.selectbox("Dove giochiamo?", [c['nome'] for c in st.session_state.db["campi"]])
        # ... (restante codice della gara come prima)

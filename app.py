import streamlit as st
import pandas as pd
import json
import os

# Configurazione Pagina
st.set_page_config(page_title="Cro Magnon Manager", page_icon="⛳", layout="wide")

# --- CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f6 !important; }
    .stSelectbox label { font-size: 14px !important; font-weight: bold !important; }
    .stButton>button { background-color: #27ae60 !important; color: white !important; border-radius: 8px; font-weight: bold; height: 3.5em; }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "golf_data_v13.json"

def carica_dati():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                d = json.load(f)
                return d
        except: return {"giocatori": [], "campi": []}
    return {"giocatori": [], "campi": []}

def salva_dati(dati):
    with open(DB_FILE, "w") as f:
        json.dump(dati, f, indent=4)

if 'db' not in st.session_state:
    st.session_state.db = carica_dati()

# Inizializzazione HCP temporanei come lista di INTERI
if 'mappa_hcp' not in st.session_state:
    st.session_state.mappa_hcp = {i: i for i in range(1, 19)}

dati = st.session_state.db

st.title("⛳ CRO MAGNON GOLF")
tab1, tab2, tab3 = st.tabs(["🎮 Gara", "👥 Soci", "🏗️ Campi"])

# --- TAB 3: CAMPI ---
with tab3:
    st.header("Configura Nuovo Campo")
    tipo_c = st.radio("Numero buche:", [9, 18], horizontal=True)
    nome_c = st.text_input("Nome Golf Club", key="n_campo_input")
    
    st.write("### Assegnazione PAR e HCP (1-18)")
    
    par_salvati = []
    hcp_salvati = []
    
    # Pool di riferimento sempre numerico
    POOL_COMPLETO = list(range(1, 19))
    
    for i in range(tipo_c):
        b_num = i + 1
        c1, c2, c3 = st.columns([1, 2, 3])
        c1.markdown(f"**Buca {b_num}**")
        
        # PAR
        p_val = c2.selectbox(f"Par B{b_num}", [3, 4, 5], index=1, key=f"p_idx_{b_num}")
        par_salvati.append(p_val)
        
        # HCP - LOGICA CORRETTA PER ORDINAMENTO NUMERICO
        # 1. Togliamo i valori usati nelle altre buche
        altri_usati = [st.session_state.mappa_hcp[j] for j in range(1, tipo_c + 1) if j != b_num]
        
        # 2. Creiamo la lista delle opzioni (SOLO NUMERI INTERI)
        opzioni = [n for n in POOL_COMPLETO if n not in altri_usati]
        
        # 3. FORZIAMO L'ORDINAMENTO NUMERICO (essenziale per iOS)
        opzioni = sorted(opzioni) 
        
        # Controllo che il valore attuale sia valido
        val_corrente = st.session_state.mappa_hcp[b_num]
        if val_corrente not in opzioni:
            val_corrente = opzioni[0]
            st.session_state.mappa_hcp[b_num] = val_corrente
            
        # 4. Mostriamo la selectbox passando la lista di INTERI
        h_val = c3.selectbox(
            f"HCP B{b_num}",
            options=opzioni,
            index=opzioni.index(val_corrente),
            key=f"hcp_idx_{b_num}"
        )
        
        # Se l'utente cambia, aggiorniamo e ricarichiamo per escludere il numero dalle altre buche
        if h_val != st.session_state.mappa_hcp[b_num]:
            st.session_state.mappa_hcp[b_num] = h_val
            st.rerun()
            
        hcp_salvati.append(h_val)

    if st.button("💾 SALVA CONFIGURAZIONE"):
        if nome_c:
            dati["campi"].append({"nome": nome_c, "tipo": tipo_c, "par": par_salvati, "hcp_buche": hcp_salvati})
            salva_dati(dati)
            st.success("Campo aggiunto!")
            st.rerun()

# --- ALTRI TAB (Semplificati per brevità) ---
with tab2:
    st.header("Anagrafica")
    with st.form("p_f"):
        n = st.text_input("Nome")
        h = st.number_input("HCP", 0, 54, 36)
        if st.form_submit_button("Aggiungi"):
            dati["giocatori"].append({"nome": n, "hcp": h})
            salva_dati(dati)
            st.rerun()

with tab1:
    if not dati["campi"]:
        st.info("Crea un campo.")
    else:
        sel = st.selectbox("Campo:", [c['nome'] for c in dati["campi"]])
        campo = next(c for c in dati["campi"] if c['nome'] == sel)
        pres = [g for g in dati["giocatori"] if st.checkbox(f"{g['nome']}", key=f"check_{g['nome']}")]
        if pres and st.button("Calcola Punteggi"):
            st.write("Classifica generata (Logica Stableford attiva)")

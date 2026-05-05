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

DB_FILE = "golf_data_v14.json"

def carica_dati():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except: return {"giocatori": [], "campi": []}
    return {"giocatori": [], "campi": []}

def salva_dati(dati):
    with open(DB_FILE, "w") as f:
        json.dump(dati, f, indent=4)

if 'db' not in st.session_state:
    st.session_state.db = carica_dati()

# Inizializziamo la mappa degli HCP (usiamo numeri interi internamente)
if 'mappa_hcp' not in st.session_state:
    st.session_state.mappa_hcp = {i: i for i in range(1, 19)}

dati = st.session_state.db

st.title("⛳ CRO MAGNON GOLF")
tab1, tab2, tab3 = st.tabs(["🎮 Gara", "👥 Soci", "🏗️ Campi"])

with tab3:
    st.header("Configura Nuovo Campo")
    tipo_c = st.radio("Numero buche:", [9, 18], horizontal=True)
    nome_c = st.text_input("Nome Golf Club", key="n_campo_final")
    
    st.write("### Assegnazione PAR e HCP")
    
    par_salvati = []
    hcp_salvati = []
    
    for i in range(tipo_c):
        b_num = i + 1
        c1, c2, c3 = st.columns([1, 2, 3])
        c1.markdown(f"**Buca {b_num}**")
        
        # PAR
        p_val = c2.selectbox(f"Par B{b_num}", [3, 4, 5], index=1, key=f"p_v_{b_num}")
        par_salvati.append(p_val)
        
        # HCP - LOGICA "ANTI-IOS" CON ZERO DAVANTI
        altri_usati = [st.session_state.mappa_hcp[j] for j in range(1, tipo_c + 1) if j != b_num]
        
        # Opzioni come numeri interi per il calcolo
        opzioni_int = [n for n in range(1, 19) if n not in altri_usati]
        opzioni_int.sort()
        
        val_corrente = st.session_state.mappa_hcp[b_num]
        if val_corrente not in opzioni_int:
            val_corrente = opzioni_int[0]
            st.session_state.mappa_hcp[b_num] = val_corrente

        # USIAMO format_func PER FAR VEDERE "01, 02..." NELLA TENDINA
        # Questo inganna l'ordinamento alfabetico del browser
        h_val = c3.selectbox(
            f"HCP B{b_num}",
            options=opzioni_int,
            index=opzioni_int.index(val_corrente),
            format_func=lambda x: f"{x:02d}", # Trasforma 1 in "01", 10 in "10"
            key=f"h_v_{b_num}"
        )
        
        if h_val != st.session_state.mappa_hcp[b_num]:
            st.session_state.mappa_hcp[b_num] = h_val
            st.rerun()
            
        hcp_salvati.append(h_val)

    if st.button("💾 SALVA CAMPO"):
        if nome_c:
            dati["campi"].append({"nome": nome_c, "tipo": tipo_c, "par": par_salvati, "hcp_buche": hcp_salvati})
            salva_dati(dati)
            st.success("Salvato!")
            st.rerun()

# TAB 2 e TAB 1 rimangono uguali, il calcolo userà i numeri interi salvati
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
        pres = [g for g in dati["giocatori"] if st.checkbox(f"{g['nome']}", key=f"ch_{g['nome']}")]
        if pres:
            for p in presenti:
                # La logica del cartellino rimane quella con le tendine 0-10
                pass

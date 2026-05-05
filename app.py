import streamlit as st
import pandas as pd
import json
import os

# Configurazione Pagina
st.set_page_config(page_title="Cro Magnon Manager", page_icon="⛳", layout="wide")

# --- CSS PULITO PER MOBILE ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f6 !important; }
    .stNumberInput label { font-size: 14px !important; font-weight: bold !important; color: #1a242f !important; }
    .stButton>button { 
        background-color: #27ae60 !important; 
        color: white !important; 
        border-radius: 8px; 
        font-weight: bold; 
        height: 3.5em; 
        width: 100%;
    }
    .stExpander { border-radius: 12px !important; border: 1px solid #d1d1d1 !important; }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "golf_data_v15.json"

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

dati = st.session_state.db

st.title("⛳ CRO MAGNON GOLF")
tab1, tab2, tab3 = st.tabs(["🎮 Gara", "👥 Soci", "🏗️ Campi"])

# --- TAB 3: CAMPI (SCRITTURA MANUALE) ---
with tab3:
    st.header("Nuovo Campo")
    tipo_c = st.radio("Buche:", [9, 18], horizontal=True)
    nome_c = st.text_input("Nome Golf Club")
    
    st.write("### Configura Buca per Buca")
    
    par_input = []
    hcp_input = []
    
    for i in range(tipo_c):
        b = i + 1
        c1, c2, c3 = st.columns([1, 2, 2])
        c1.markdown(f"**B{b}**")
        # PAR: Numero da scrivere
        p = c2.number_input(f"Par B{b}", 3, 5, 4, key=f"p_in_{b}")
        par_input.append(p)
        # HCP: Numero da scrivere (senza vincoli o sparizioni)
        h = c3.number_input(f"HCP B{b}", 1, 18, b, key=f"h_in_{b}")
        hcp_input.append(h)

    if st.button("💾 SALVA CAMPO"):
        if nome_c:
            dati["campi"].append({"nome": nome_c, "tipo": tipo_c, "par": par_input, "hcp_buche": hcp_input})
            salva_dati(dati)
            st.success("Campo registrato!")
            st.rerun()

# --- TAB 2: SOCI ---
with tab2:
    st.header("Anagrafica")
    with st.form("add_player"):
        n = st.text_input("Nome")
        h = st.number_input("HCP", 0, 54, 36)
        if st.form_submit_button("Aggiungi"):
            dati["giocatori"].append({"nome": n, "hcp": h})
            salva_dati(dati)
            st.rerun()
    
    for idx, g in enumerate(dati["giocatori"]):
        c1, c2 = st.columns([4, 1])
        c1.write(f"👤 {g['nome']} (HCP {g['hcp']})")
        if c2.button("Elimina", key=f"del_{idx}"):
            dati["giocatori"].pop(idx)
            salva_dati(dati)
            st.rerun()

# --- TAB 1: GARA ---
with tab1:
    if not dati["campi"]:
        st.info("Configura un campo prima.")
    else:
        campo_nome = st.selectbox("Seleziona Campo:", [c['nome'] for c in dati["campi"]])
        campo = next(c for c in dati["campi"] if c['nome'] == campo_nome)
        
        st.subheader("Giocatori in campo:")
        scelti = [g for g in dati["giocatori"] if st.checkbox(f"{g['nome']}", key=f"g_{g['nome']}")]

        if scelti:
            risultati_finale = []
            for p in scelti:
                with st.expander(f"Cartellino: {p['nome']}"):
                    colpi_buca = []
                    # Inserimento colpi buca per buca
                    for i in range(0, campo["tipo"], 3):
                        cols = st.columns(3)
                        for j in range(3):
                            idx = i + j
                            if idx < campo["tipo"]:
                                val = cols[j].number_input(f"Buca {idx+1}", 0, 20, 0, key=f"score_{p['nome']}_{idx}")
                                colpi_buca.append(val)
                    
                    # Calcolo Stableford
                    punti_stb = 0
                    hcp_g = p['hcp']
                    for k in range(campo["tipo"]):
                        colpi = colpi_buca[k]
                        if colpi > 0:
                            par_b = campo['par'][k]
                            hcp_b = campo['hcp_buche'][k]
                            # Calcolo colpi ricevuti per buca
                            ricevuti = (hcp_g // campo["tipo"]) + (1 if hcp_b <= (hcp_g % campo["tipo"]) else 0)
                            punti_stb += max(0, 2 + par_b - (colpi - ricevuti))
                    
                    st.write(f"**Punti Totali: {int(punti_stb)}**")
                    target = 36 if campo["tipo"] == 18 else 18
                    calo = (punti_stb - target) // 2 if punti_stb > target else 0
                    risultati_finale.append({"Giocatore": p['nome'], "Punti": int(punti_stb), "HCP Fine": int(p['hcp'] - calo)})

            if st.button("🏆 CALCOLA CLASSIFICA"):
                df = pd.DataFrame(risultati_finale).sort_values(by="Punti", ascending=False).reset_index(drop=True)
                st.table(df)

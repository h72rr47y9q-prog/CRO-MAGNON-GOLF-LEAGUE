import streamlit as st
import pandas as pd
import json
import os

# Configurazione Pagina
st.set_page_config(page_title="Cro Magnon Manager", page_icon="⛳", layout="wide")

# --- CSS OTTIMIZZATO ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f6 !important; color: #1a242f !important; }
    .stMarkdown p, label, .stSelectbox label { color: #1a242f !important; font-weight: 600 !important; }
    .stButton>button { background-color: #27ae60 !important; color: white !important; border-radius: 8px; font-weight: bold; border: none; height: 3.5em; }
    .stExpander { background-color: white !important; border: 1px solid #d1d1d1 !important; border-radius: 12px !important; margin-bottom: 10px !important; }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "golf_data_v9.json"

def carica_dati():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                d = json.load(f)
                if "giocatori" not in d: d["giocatori"] = []
                if "campi" not in d: d["campi"] = []
                return d
        except: return {"giocatori": [], "campi": []}
    return {"giocatori": [], "campi": []}

def salva_dati(dati):
    with open(DB_FILE, "w") as f:
        json.dump(dati, f, indent=4)

if 'db' not in st.session_state:
    st.session_state.db = carica_dati()

# Inizializzazione HCP temporanei per la creazione del campo
if 'hcp_temp' not in st.session_state:
    st.session_state.hcp_temp = {i: i for i in range(1, 19)}

dati = st.session_state.db

st.title("⛳ CRO MAGNON GOLF")
tab1, tab2, tab3 = st.tabs(["🎮 Gara", "👥 Soci", "🏗️ Campi"])

# --- TAB 3: CAMPI (CON HCP DINAMICI) ---
with tab3:
    st.header("Configura Nuovo Campo")
    tipo_c = st.radio("Numero buche:", [9, 18], horizontal=True)
    
    with st.form("form_campo"):
        nome_c = st.text_input("Nome Golf Club")
        par_lista = []
        hcp_lista = []
        
        st.write("Assegna PAR e HCP (ogni numero HCP è unico):")
        
        for b in range(1, tipo_c + 1):
            col_b, col_p, col_h = st.columns([1, 2, 3])
            col_b.markdown(f"**B{b}**")
            
            # PAR con selectbox
            p_val = col_p.selectbox(f"Par B{b}", [3, 4, 5], index=1, key=f"setup_p_{b}", label_visibility="collapsed")
            par_lista.append(p_val)
            
            # HCP con logica di sparizione
            # Calcoliamo quali hcp sono stati usati nelle ALTRE buche
            usati_altrove = [st.session_state.hcp_temp[i] for i in range(1, tipo_c + 1) if i != b]
            opzioni_hcp = [i for i in range(1, 19) if i not in usati_altrove]
            
            # Se il valore attuale non è tra le opzioni (per cambio tipo campo), resettiamo
            if st.session_state.hcp_temp[b] not in opzioni_hcp:
                st.session_state.hcp_temp[b] = opzioni_hcp[0]
            
            h_val = col_h.selectbox(
                f"HCP B{b}", 
                options=opzioni_hcp,
                index=opzioni_hcp.index(st.session_state.hcp_temp[b]),
                key=f"setup_h_{b}",
                label_visibility="collapsed"
            )
            st.session_state.hcp_temp[b] = h_val
            hcp_lista.append(h_val)

        if st.form_submit_button("💾 Salva Campo"):
            if nome_c:
                dati["campi"].append({"nome": nome_c, "tipo": tipo_c, "par": par_lista, "hcp_buche": hcp_lista})
                salva_dati(dati)
                st.success(f"Campo {nome_c} salvato correttamente!")
                st.rerun()

# --- TAB 2: GIOCATORI ---
with tab2:
    st.header("Gestione Soci")
    with st.form("add_p"):
        n = st.text_input("Nome")
        h = st.number_input("HCP", 0, 54, 36)
        if st.form_submit_button("Aggiungi"):
            if n:
                dati["giocatori"].append({"nome": n, "hcp": h})
                salva_dati(dati)
                st.rerun()
    for idx, g in enumerate(dati["giocatori"]):
        c1, c2 = st.columns([4, 1])
        c1.write(f"👤 {g['nome']} (HCP {g['hcp']})")
        if c2.button("Elimina", key=f"del_g_{idx}"):
            dati["giocatori"].pop(idx)
            salva_dati(dati)
            st.rerun()

# --- TAB 1: GARA ---
with tab1:
    if not dati["campi"]:
        st.info("Configura un campo per iniziare.")
    else:
        campo_scelto = st.selectbox("Seleziona Campo:", [c['nome'] for c in dati["campi"]])
        campo = next(c for c in dati["campi"] if c['nome'] == campo_scelto)
        
        st.subheader("Chi gioca oggi?")
        presenti = [g for g in dati["giocatori"] if st.checkbox(f"{g['nome']}", key=f"pres_{g['nome']}")]

        if presenti:
            st.divider()
            risultati_gara = []

            for p in presenti:
                with st.expander(f"📝 {p['nome']} (HCP {p['hcp']})"):
                    metodo = st.radio(f"Input per {p['nome']}", ["Tendina", "Manuale"], horizontal=True, key=f"m_{p['nome']}")
                    punti_giocatore = 0
                    
                    if metodo == "Manuale":
                        punti_giocatore = st.number_input("Punti Stableford", 0, 60, 0, key=f"man_{p['nome']}")
                    else:
                        colpi = []
                        for i in range(0, campo["tipo"], 3):
                            cols = st.columns(3)
                            for j in range(3):
                                b_idx = i + j
                                if b_idx < campo["tipo"]:
                                    val = cols[j].selectbox(
                                        f"Buca {b_idx+1}", 
                                        options=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                                        format_func=lambda x: f"B{b_idx+1}: {x}" if x > 0 else f"B{b_idx+1}: -",
                                        key=f"score_{p['nome']}_{b_idx}"
                                    )
                                    colpi.append(val)
                        
                        # Calcolo Stableford
                        hcp_g = p['hcp']
                        for idx in range(campo["tipo"]):
                            l = colpi[idx]
                            if l > 0:
                                par, diff = campo['par'][idx], campo['hcp_buche'][idx]
                                ricevuti = (hcp_g // campo["tipo"]) + (1 if diff <= (hcp_g % campo["tipo"]) else 0)
                                punti_giocatore += max(0, 2 + par - (l - ricevuti))
                    
                    st.write(f"**Punti totali: {int(punti_giocatore)}**")
                    target = 36 if campo["tipo"] == 18 else 18
                    calo = (punti_giocatore - target) // 2 if punti_giocatore > target else 0
                    risultati_gara.append({"Giocatore": p['nome'], "Punti": int(punti_giocatore), "Nuovo HCP": int(p['hcp'] - calo)})

            if st.button("🏆 VEDI CLASSIFICA"):
                df = pd.DataFrame(risultati_gara).sort_values(by="Punti", ascending=False).reset_index(drop=True)
                df.insert(0, 'Pos', [f"{i+1}°" for i in range(len(df))])
                st.table(df)

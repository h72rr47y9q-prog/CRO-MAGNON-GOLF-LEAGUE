import streamlit as st
import pandas as pd
import json
import os

# Configurazione Pagina
st.set_page_config(page_title="Cro Magnon Manager", page_icon="⛳", layout="wide")

# --- CSS ANTI-DARK MODE (FORZA COLORI CHIARI) ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f6 !important; color: #1a242f !important; }
    .stMarkdown p, label, .stSelectbox label, .stCheckbox label { color: #1a242f !important; font-weight: 600 !important; }
    .stButton>button { background-color: #27ae60 !important; color: white !important; border-radius: 8px; font-weight: bold; border: none; height: 3em; width: 100%; }
    .stExpander { background-color: white !important; border: 1px solid #d1d1d1 !important; border-radius: 10px; }
    div[data-testid="stForm"] { background-color: white !important; padding: 20px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "golf_data_v4.json"

# --- FUNZIONI DATI ---
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

dati = st.session_state.db

st.title("⛳ CRO MAGNON GOLF LEAGUE")
tab1, tab2, tab3 = st.tabs(["🎮 Gara del Giorno", "👥 Giocatori", "🏗️ Campi"])

# --- TAB 3: GESTIONE CAMPI (FIX BUG 18 BUCHE) ---
with tab3:
    st.header("Configurazione Campi")
    
    # La scelta del tipo deve stare FUORI dal form per aggiornare la UI
    tipo_c = st.radio("Seleziona numero buche per il nuovo campo:", [9, 18], horizontal=True)
    
    with st.form("form_nuovo_campo"):
        nome_c = st.text_input("Nome del Golf Club")
        st.write(f"Configurazione per {tipo_c} buche:")
        
        par_lista = []
        hcp_lista = []
        
        # Generiamo la griglia dinamica
        cols_per_row = 3
        for i in range(0, tipo_c, cols_per_row):
            cols = st.columns(cols_per_row)
            for j in range(cols_per_row):
                b_num = i + j + 1
                if b_num <= tipo_c:
                    with cols[j]:
                        st.markdown(f"**Buca {b_num}**")
                        p = st.number_input(f"Par", 3, 5, 4, key=f"p_f_{b_num}")
                        h = st.number_input(f"HCP", 1, 18, b_num, key=f"h_f_{b_num}")
                        par_lista.append(p)
                        hcp_lista.append(h)
        
        if st.form_submit_button("💾 SALVA CAMPO"):
            if nome_c:
                dati["campi"].append({"nome": nome_c, "tipo": tipo_c, "par": par_lista, "hcp_buche": hcp_lista})
                salva_dati(dati)
                st.success(f"Campo '{nome_c}' salvato!")
                st.rerun()

    st.divider()
    for idx, c in enumerate(dati["campi"]):
        c1, c2 = st.columns([4, 1])
        c1.write(f"⛳ {c['nome']} ({c['tipo']} buche)")
        if c2.button("Elimina", key=f"del_c_{idx}"):
            dati["campi"].pop(idx)
            salva_dati(dati)
            st.rerun()

# --- TAB 2: GIOCATORI ---
with tab2:
    st.header("Anagrafica Soci")
    with st.form("add_p"):
        c1, c2 = st.columns([2, 1])
        n = c1.text_input("Nome")
        h = c2.number_input("HCP", 0, 54, 36)
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

# --- TAB 1: GARA DEL GIORNO (FIX BUG VISUALIZZAZIONE) ---
with tab1:
    if not dati["campi"] or not dati["giocatori"]:
        st.warning("Configura prima Campi e Giocatori!")
    else:
        st.subheader("1. Setup Gara")
        nome_campo_scelto = st.selectbox("Seleziona il campo di oggi:", [c['nome'] for c in dati["campi"]])
        campo = next(c for c in dati["campi"] if c['nome'] == nome_campo_scelto)
        
        st.subheader("2. Chi gioca?")
        giocatori_presenti = []
        for g in dati["giocatori"]:
            if st.checkbox(f"{g['nome']} (HCP {g['hcp']})", key=f"pres_{g['nome']}"):
                giocatori_presenti.append(g)

        if giocatori_presenti:
            st.divider()
            st.subheader("3. Inserimento Scorecard")
            risultati_gara = []

            for p in giocatori_presenti:
                with st.expander(f"Cartellino: {p['nome']}", expanded=False):
                    colpi_buca = []
                    # Griglia inserimento colpi (3 per riga)
                    for i in range(0, campo["tipo"], 3):
                        cols = st.columns(3)
                        for j in range(3):
                            b_idx = i + j
                            if b_idx < campo["tipo"]:
                                with cols[j]:
                                    c = st.number_input(f"Buca {b_idx+1} (Par {campo['par'][b_idx]})", 0, 15, 0, key=f"s_{p['nome']}_{b_idx}")
                                    colpi_buca.append(c)
                    
                    # Calcolo Stableford
                    punti_stb = 0
                    hcp_g = p['hcp']
                    for b_idx in range(campo["tipo"]):
                        lordo = colpi_buca[b_idx]
                        if lordo == 0: continue
                        
                        par = campo['par'][b_idx]
                        diff = campo['hcp_buche'][b_idx]
                        
                        ricevuti = hcp_g // campo["tipo"]
                        if diff <= (hcp_g % campo["tipo"]): ricevuti += 1
                        
                        punti_b = max(0, 2 + par - (lordo - ricevuti))
                        punti_stb += punti_b
                    
                    st.info(f"Punti Stableford calcolati: {int(punti_stb)}")
                    
                    target = 36 if campo["tipo"] == 18 else 18
                    calo = (punti_stb - target) // 2 if punti_stb > target else 0
                    risultati_gara.append({
                        "Giocatore": p['nome'], "HCP Partenza": p['hcp'],
                        "Punti": int(punti_stb), "Nuovo HCP": int(p['hcp'] - calo)
                    })

            st.divider()
            if st.button("🏆 CALCOLA CLASSIFICA"):
                df_res = pd.DataFrame(risultati_gara).sort_values(by="Punti", ascending=False).reset_index(drop=True)
                df_res.insert(0, 'Pos', [f"{i+1}°" for i in range(len(df_res))])
                st.table(df_res)
                
                if st.button("💾 Conferma e Aggiorna Anagrafica"):
                    for r in risultati_gara:
                        for soci in dati["giocatori"]:
                            if soci["nome"] == r["Giocatore"]:
                                soci["hcp"] = r["Nuovo HCP"]
                    salva_dati(dati)
                    st.success("HCP salvati!")

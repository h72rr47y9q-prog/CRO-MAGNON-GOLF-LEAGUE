import streamlit as st
import pandas as pd
import json
import os

# Configurazione Pagina
st.set_page_config(page_title="Cro Magnon Manager", page_icon="⛳", layout="wide")

# --- CSS ANTI-DARK MODE ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f6 !important; color: #1a242f !important; }
    .stMarkdown p, label, .stSelectbox label, .stCheckbox label { color: #1a242f !important; font-weight: 600 !important; }
    .stButton>button { background-color: #27ae60 !important; color: white !important; border-radius: 8px; font-weight: bold; border: none; height: 3em; width: 100%; }
    .stExpander { background-color: white !important; border: 1px solid #d1d1d1 !important; border-radius: 10px; margin-bottom: 10px; }
    div[data-testid="stForm"] { background-color: white !important; padding: 20px; border-radius: 10px; border: 1px solid #d1d1d1; }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "golf_data_v6.json"

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

# --- TAB 3: CAMPI ---
with tab3:
    st.header("Configurazione Campi")
    tipo_c = st.radio("Seleziona numero buche:", [9, 18], horizontal=True)
    with st.form("form_campo"):
        nome_c = st.text_input("Nome Golf Club")
        par_lista, hcp_lista = [], []
        for i in range(0, tipo_c, 3):
            cols = st.columns(3)
            for j in range(3):
                b = i + j + 1
                if b <= tipo_c:
                    with cols[j]:
                        st.markdown(f"**Buca {b}**")
                        par_lista.append(st.number_input(f"Par", 3, 5, 4, key=f"p_{b}"))
                        hcp_lista.append(st.number_input(f"HCP", 1, 18, b, key=f"h_{b}"))
        if st.form_submit_button("Salva Campo"):
            if nome_c:
                dati["campi"].append({"nome": nome_c, "tipo": tipo_c, "par": par_lista, "hcp_buche": hcp_lista})
                salva_dati(dati)
                st.rerun()

    for idx, c in enumerate(dati["campi"]):
        col1, col2 = st.columns([4, 1])
        col1.write(f"⛳ {c['nome']} ({c['tipo']} buche)")
        if col2.button("Elimina", key=f"del_c_{idx}"):
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
        col1, col2 = st.columns([4, 1])
        col1.write(f"👤 {g['nome']} (HCP {g['hcp']})")
        if col2.button("Elimina", key=f"del_g_{idx}"):
            dati["giocatori"].pop(idx)
            salva_dati(dati)
            st.rerun()

# --- TAB 1: GARA DEL GIORNO ---
with tab1:
    if not dati["campi"] or not dati["giocatori"]:
        st.info("Configura prima Campi e Giocatori!")
    else:
        st.subheader("1. Setup Gara")
        n_campo = st.selectbox("Seleziona campo:", [c['nome'] for c in dati["campi"]])
        campo = next(c for c in dati["campi"] if c['nome'] == n_campo)
        
        st.subheader("2. Seleziona i presenti")
        presenti = []
        for g in dati["giocatori"]:
            if st.checkbox(f"{g['nome']} (HCP {g['hcp']})", key=f"pr_{g['nome']}"):
                presenti.append(g)

        if presenti:
            st.divider()
            st.subheader("3. Inserimento Risultati")
            risultati_gara = []

            # Visualizzazione diretta senza suddivisione in voli
            for p in presenti:
                with st.expander(f"Giocatore: {p['nome']} (HCP {p['hcp']})"):
                    metodo = st.radio(f"Metodo per {p['nome']}:", ["Punti Totali (Manuale)", "Scorecard Completa"], horizontal=True, key=f"met_{p['nome']}")
                    
                    punti_finali = 0
                    
                    if metodo == "Punti Totali (Manuale)":
                        punti_finali = st.number_input("Punti Stableford totali:", 0, 60, 0, key=f"man_{p['nome']}")
                    else:
                        colpi_lordi = []
                        for row in range(0, campo["tipo"], 3):
                            cols = st.columns(3)
                            for j in range(3):
                                b_idx = row + j
                                if b_idx < campo["tipo"]:
                                    with cols[j]:
                                        c = st.number_input(f"Buca {b_idx+1} (Par {campo['par'][b_idx]})", 0, 15, 0, key=f"b_{p['nome']}_{b_idx}")
                                        colpi_lordi.append(c)
                        
                        # Calcolo Stableford
                        hcp_g = p['hcp']
                        for b_idx in range(campo["tipo"]):
                            l = colpi_lordi[b_idx]
                            if l > 0:
                                par, diff = campo['par'][b_idx], campo['hcp_buche'][b_idx]
                                ricevuti = (hcp_g // campo["tipo"]) + (1 if diff <= (hcp_g % campo["tipo"]) else 0)
                                punti_finali += max(0, 2 + par - (l - ricevuti))
                    
                    st.write(f"**Punti calcolati: {int(punti_finali)}**")
                    
                    # Logica calcolo nuovo HCP
                    target = 36 if campo["tipo"] == 18 else 18
                    # Se punti > target, l'HCP scende di 1 ogni 2 punti extra (approssimato)
                    calo = (punti_finali - target) // 2 if punti_finali > target else 0
                    risultati_gara.append({
                        "Giocatore": p['nome'], "HCP": p['hcp'],
                        "Punti": int(punti_finali), "Nuovo HCP": int(p['hcp'] - calo)
                    })

            st.divider()
            if st.button("🏆 VEDI CLASSIFICA FINALE"):
                st.balloons()
                df = pd.DataFrame(risultati_gara).sort_values(by="Punti", ascending=False).reset_index(drop=True)
                df.insert(0, 'Pos', [f"{i+1}°" for i in range(len(df))])
                st.table(df)
                
                if st.button("💾 Conferma e Salva Nuovi HCP"):
                    for r in risultati_gara:
                        for s in dati["giocatori"]:
                            if s["nome"] == r["Giocatore"]: s["hcp"] = r["Nuovo HCP"]
                    salva_dati(dati)
                    st.success("HCP aggiornati con successo!")

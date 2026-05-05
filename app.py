import streamlit as st
import pandas as pd
import json
import os

# Configurazione Pagina
st.set_page_config(page_title="Cro Magnon Manager", page_icon="⛳", layout="wide")

# --- CSS OTTIMIZZATO PER MOBILE ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f6 !important; color: #1a242f !important; }
    .stMarkdown p, label, .stSelectbox label { color: #1a242f !important; font-weight: 600 !important; }
    /* Bottone Classifica */
    .stButton>button { 
        background-color: #27ae60 !important; 
        color: white !important; 
        border-radius: 8px; 
        font-weight: bold; 
        border: none; 
        height: 3.5em; 
        margin-top: 20px;
    }
    /* Stile per i box dei giocatori */
    .stExpander { 
        background-color: white !important; 
        border: 1px solid #d1d1d1 !important; 
        border-radius: 12px !important; 
        margin-bottom: 15px !important; 
    }
    /* Riduciamo lo spazio tra le selectbox */
    div[data-testid="column"] { padding: 0px 5px !important; }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "golf_data_v8.json"

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

st.title("⛳ CRO MAGNON GOLF")
tab1, tab2, tab3 = st.tabs(["🎮 Gara", "👥 Soci", "🏗️ Campi"])

# --- TAB 3: CAMPI ---
with tab3:
    st.header("Nuovo Campo")
    tipo_c = st.radio("Buche:", [9, 18], horizontal=True)
    with st.form("form_campo"):
        nome_c = st.text_input("Nome Golf Club")
        par_lista, hcp_lista = [], []
        # Qui usiamo un layout compatto per inserire i dati del campo
        for b in range(1, tipo_c + 1):
            cols = st.columns([1, 2, 2])
            cols[0].markdown(f"**B{b}**")
            par_lista.append(cols[1].selectbox(f"Par B{b}", [3, 4, 5], index=1, key=f"p_{b}", label_visibility="collapsed"))
            hcp_lista.append(cols[2].number_input(f"HCP B{b}", 1, 18, b, key=f"h_{b}", label_visibility="collapsed"))
        
        if st.form_submit_button("Salva Campo"):
            if nome_c:
                dati["campi"].append({"nome": nome_c, "tipo": tipo_c, "par": par_lista, "hcp_buche": hcp_lista})
                salva_dati(dati)
                st.rerun()

# --- TAB 2: GIOCATORI ---
with tab2:
    st.header("Anagrafica")
    with st.form("add_p"):
        n = st.text_input("Nome Giocatore")
        h = st.number_input("HCP", 0, 54, 36)
        if st.form_submit_button("Aggiungi"):
            if n:
                dati["giocatori"].append({"nome": n, "hcp": h})
                salva_dati(dati)
                st.rerun()
    for idx, g in enumerate(dati["giocatori"]):
        col1, col2 = st.columns([3, 1])
        col1.write(f"👤 {g['nome']} (HCP {g['hcp']})")
        if col2.button("X", key=f"del_g_{idx}"):
            dati["giocatori"].pop(idx)
            salva_dati(dati)
            st.rerun()

# --- TAB 1: GARA (MOBILE FRIENDLY CON SELECTBOX) ---
with tab1:
    if not dati["campi"]:
        st.info("Configura un campo per iniziare.")
    else:
        campo_scelto = st.selectbox("Dove si gioca?", [c['nome'] for c in dati["campi"]])
        campo = next(c for c in dati["campi"] if c['nome'] == campo_scelto)
        
        st.subheader("Chi partecipa?")
        presenti = [g for g in dati["giocatori"] if st.checkbox(f"{g['nome']}", key=f"pres_{g['nome']}")]

        if presenti:
            st.divider()
            risultati_gara = []

            for p in presenti:
                with st.expander(f"📝 {p['nome']} (HCP {p['hcp']})", expanded=False):
                    metodo = st.radio(f"Input per {p['nome']}", ["Tendina buca per buca", "Punti totali manuali"], horizontal=True, key=f"m_{p['nome']}")
                    
                    punti_giocatore = 0
                    
                    if metodo == "Punti totali manuali":
                        punti_giocatore = st.number_input("Inserisci Punti Stableford", 0, 60, 0, key=f"man_{p['nome']}")
                    else:
                        colpi_inseriti = []
                        # Generiamo le tendine in un layout a 3 colonne per non allungare troppo la pagina
                        for i in range(0, campo["tipo"], 3):
                            cols = st.columns(3)
                            for j in range(3):
                                b_idx = i + j
                                if b_idx < campo["tipo"]:
                                    with cols[j]:
                                        # Menu a tendina da 0 a 10 (0 significa buca non giocata o X)
                                        valore = st.selectbox(
                                            f"Buca {b_idx+1}", 
                                            options=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 
                                            format_func=lambda x: f"B{b_idx+1}: {x}" if x > 0 else f"B{b_idx+1}: -",
                                            key=f"sb_{p['nome']}_{b_idx}"
                                        )
                                        colpi_inseriti.append(valore)
                        
                        # Calcolo Stableford
                        hcp_g = p['hcp']
                        for idx in range(campo["tipo"]):
                            l = colpi_inseriti[idx]
                            if l > 0:
                                par = campo['par'][idx]
                                diff = campo['hcp_buche'][idx]
                                ricevuti = (hcp_g // campo["tipo"]) + (1 if diff <= (hcp_g % campo["tipo"]) else 0)
                                punti_giocatore += max(0, 2 + par - (l - ricevuti))
                    
                    st.write(f"**Punti totali: {int(punti_giocatore)}**")
                    
                    target = 36 if campo["tipo"] == 18 else 18
                    calo = (punti_giocatore - target) // 2 if punti_giocatore > target else 0
                    risultati_gara.append({
                        "Giocatore": p['nome'], 
                        "Punti": int(punti_giocatore), 
                        "Nuovo HCP": int(p['hcp'] - calo)
                    })

            if st.button("🏆 VEDI CLASSIFICA"):
                st.balloons()
                df = pd.DataFrame(risultati_gara).sort_values(by="Punti", ascending=False).reset_index(drop=True)
                df.insert(0, 'Pos', [f"{i+1}°" for i in range(len(df))])
                st.table(df)

import streamlit as st
import pandas as pd
import json
import os

# Configurazione Pagina
st.set_page_config(page_title="Cro Magnon Manager", page_icon="⛳", layout="wide")

# --- CSS AVANZATO PER EFFETTO SCORECARD ---
st.markdown("""
    <style>
    /* Sfondo e font generale */
    .stApp { background-color: #e8ecef !important; color: #1a242f !important; }
    
    /* Stile celle Scorecard */
    .score-cell {
        border: 1px solid #000 !important;
        background-color: #ffffff;
        text-align: center;
        padding: 5px;
        font-weight: bold;
    }
    .header-cell {
        background-color: #27ae60 !important;
        color: white !important;
        border: 1px solid #000 !important;
        text-align: center;
        font-weight: bold;
        padding: 5px;
    }
    .label-cell {
        background-color: #f1f1f1 !important;
        border: 1px solid #000 !important;
        font-weight: bold;
        padding: 5px;
    }

    /* Rimpiccioliamo gli input per farli stare nella griglia */
    div[data-testid="stNumberInput"] div[data-baseweb="input"] {
        background-color: transparent !important;
        border: none !important;
    }
    div[data-testid="stNumberInput"] input {
        text-align: center !important;
        font-size: 18px !important;
        font-weight: bold !important;
        padding: 0px !important;
    }
    
    /* Nascondiamo le etichette degli input nella griglia per pulizia */
    div[data-testid="stNumberInput"] label { display: none !important; }

    /* Bottoni */
    .stButton>button { 
        background-color: #27ae60 !important; 
        color: white !important; 
        border-radius: 4px; 
        font-weight: bold; 
        border: 2px solid #1e8449;
    }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "golf_data_v7.json"

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
tab1, tab2, tab3 = st.tabs(["🎮 Gara del Giorno", "👥 Giocatori", "🏗️ Configura Campi"])

# --- TAB 3: CONFIGURAZIONE CAMPI (LOOK SCORECARD) ---
with tab3:
    st.header("Configurazione Nuovo Campo")
    tipo_c = st.radio("Dimensione:", [9, 18], horizontal=True)
    
    with st.container():
        st.markdown("### Anteprima Cartellino")
        nome_c = st.text_input("Nome del Golf Club")
        
        # Header buche
        cols = st.columns([2] + [1] * 9 + [1.5]) # Prima colonna larga, poi 9 strette, poi totale
        cols[0].markdown("<div class='header-cell'>BUCA</div>", unsafe_allow_html=True)
        for i in range(1, 10):
            cols[i].markdown(f"<div class='header-cell'>{i}</div>", unsafe_allow_html=True)
        cols[10].markdown("<div class='header-cell'>OUT</div>", unsafe_allow_html=True)

        # Riga PAR (Prime 9)
        p_row1 = st.columns([2] + [1] * 9 + [1.5])
        p_row1[0].markdown("<div class='label-cell'>PAR</div>", unsafe_allow_html=True)
        par_lista = []
        for i in range(9):
            with p_row1[i+1]:
                par_lista.append(st.number_input("", 3, 5, 4, key=f"cp_{i}"))
        p_row1[10].markdown(f"<div class='score-cell'>{sum(par_lista[:9])}</div>", unsafe_allow_html=True)

        # Riga HCP (Prime 9)
        h_row1 = st.columns([2] + [1] * 9 + [1.5])
        h_row1[0].markdown("<div class='label-cell'>HCP</div>", unsafe_allow_html=True)
        hcp_lista = []
        for i in range(9):
            with h_row1[i+1]:
                hcp_lista.append(st.number_input("", 1, 18, i+1, key=f"ch_{i}"))
        h_row1[10].markdown("<div class='score-cell'>-</div>", unsafe_allow_html=True)

        # Se 18 buche, aggiungiamo la seconda parte
        if tipo_c == 18:
            st.write("")
            cols2 = st.columns([2] + [1] * 9 + [1.5])
            cols2[0].markdown("<div class='header-cell'>BUCA</div>", unsafe_allow_html=True)
            for i in range(10, 19):
                cols2[i-9].markdown(f"<div class='header-cell'>{i}</div>", unsafe_allow_html=True)
            cols2[10].markdown("<div class='header-cell'>IN</div>", unsafe_allow_html=True)

            p_row2 = st.columns([2] + [1] * 9 + [1.5])
            p_row2[0].markdown("<div class='label-cell'>PAR</div>", unsafe_allow_html=True)
            for i in range(9, 18):
                with p_row2[i-8]:
                    par_lista.append(st.number_input("", 3, 5, 4, key=f"cp_{i}"))
            p_row2[10].markdown(f"<div class='score-cell'>{sum(par_lista[9:])}</div>", unsafe_allow_html=True)

            h_row2 = st.columns([2] + [1] * 9 + [1.5])
            h_row2[0].markdown("<div class='label-cell'>HCP</div>", unsafe_allow_html=True)
            for i in range(9, 18):
                with h_row2[i-8]:
                    hcp_lista.append(st.number_input("", 1, 18, i+1, key=f"ch_{i}"))
            h_row2[10].markdown("<div class='score-cell'>-</div>", unsafe_allow_html=True)

        st.write("")
        if st.button("💾 SALVA CONFIGURAZIONE CAMPO"):
            if nome_c:
                dati["campi"].append({"nome": nome_c, "tipo": tipo_c, "par": par_lista, "hcp_buche": hcp_lista})
                salva_dati(dati)
                st.success("Campo salvato!")
                st.rerun()

# --- TAB 1: GARA DEL GIORNO (SCORECARD REALE) ---
with tab1:
    if not dati["campi"]:
        st.info("Crea un campo nel tab Configura Campi.")
    else:
        n_campo = st.selectbox("Seleziona campo:", [c['nome'] for c in dati["campi"]])
        campo = next(c for c in dati["campi"] if c['nome'] == n_campo)
        
        st.subheader("Giocatori al tee di partenza")
        presenti = [g for g in dati["giocatori"] if st.checkbox(f"{g['nome']} (HCP {g['hcp']})", key=f"p_{g['nome']}")]

        if presenti:
            st.divider()
            risultati_gara = []

            for p in presenti:
                st.markdown(f"### 📋 Cartellino: {p['nome']}")
                metodo = st.radio(f"Modalità {p['nome']}", ["Scorecard", "Manuale"], horizontal=True, key=f"m_{p['nome']}")
                
                punti_finali = 0
                
                if metodo == "Manuale":
                    punti_finali = st.number_input("Punti Stableford:", 0, 60, 0, key=f"man_{p['nome']}")
                else:
                    # --- DISEGNO SCORECARD ---
                    # Header
                    h_cols = st.columns([2] + [1]*9 + [1.5])
                    h_cols[0].markdown("<div class='header-cell'>BUCA</div>", unsafe_allow_html=True)
                    for i in range(1, 10): h_cols[i].markdown(f"<div class='header-cell'>{i}</div>", unsafe_allow_html=True)
                    h_cols[10].markdown("<div class='header-cell'>OUT</div>", unsafe_allow_html=True)
                    
                    # Riga Colpi (Prime 9)
                    s_cols1 = st.columns([2] + [1]*9 + [1.5])
                    s_cols1[0].markdown("<div class='label-cell'>COLPI</div>", unsafe_allow_html=True)
                    colpi = []
                    for i in range(9):
                        with s_cols1[i+1]:
                            colpi.append(st.number_input("", 0, 15, 0, key=f"score_{p['nome']}_{i}"))
                    s_cols1[10].markdown(f"<div class='score-cell'>{sum(colpi[:9])}</div>", unsafe_allow_html=True)

                    if campo["tipo"] == 18:
                        # Header (10-18)
                        h_cols2 = st.columns([2] + [1]*9 + [1.5])
                        h_cols2[0].markdown("<div class='header-cell'>BUCA</div>", unsafe_allow_html=True)
                        for i in range(10, 19): h_cols2[i-9].markdown(f"<div class='header-cell'>{i}</div>", unsafe_allow_html=True)
                        h_cols2[10].markdown("<div class='header-cell'>IN</div>", unsafe_allow_html=True)
                        
                        # Riga Colpi (10-18)
                        s_cols2 = st.columns([2] + [1]*9 + [1.5])
                        s_cols2[0].markdown("<div class='label-cell'>COLPI</div>", unsafe_allow_html=True)
                        for i in range(9, 18):
                            with s_cols2[i-8]:
                                colpi.append(st.number_input("", 0, 15, 0, key=f"score_{p['nome']}_{i}"))
                        s_cols2[10].markdown(f"<div class='score-cell'>{sum(colpi[9:])}</div>", unsafe_allow_html=True)

                    # Calcolo Stableford
                    hcp_g = p['hcp']
                    for b_idx in range(campo["tipo"]):
                        l = colpi[b_idx]
                        if l > 0:
                            par, diff = campo['par'][b_idx], campo['hcp_buche'][b_idx]
                            ricevuti = (hcp_g // campo["tipo"]) + (1 if diff <= (hcp_g % campo["tipo"]) else 0)
                            punti_finali += max(0, 2 + par - (l - ricevuti))
                
                st.success(f"Punti Stableford Totali: {int(punti_finali)}")
                target = 36 if campo["tipo"] == 18 else 18
                calo = (punti_finali - target) // 2 if punti_finali > target else 0
                risultati_gara.append({"Giocatore": p['nome'], "HCP": p['hcp'], "Punti": int(punti_finali), "Nuovo HCP": int(p['hcp'] - calo)})
                st.divider()

            if st.button("🏆 CALCOLA CLASSIFICA"):
                df = pd.DataFrame(risultati_gara).sort_values(by="Punti", ascending=False).reset_index(drop=True)
                df.insert(0, 'Pos', [f"{i+1}°" for i in range(len(df))])
                st.table(df)

# --- TAB 2: GIOCATORI (RIMASTO UGUALE) ---
with tab2:
    st.header("Anagrafica Soci")
    with st.form("add_p"):
        c1, c2 = st.columns([2, 1])
        n = c1.text_input("Nome")
        h = c2.number_input("HCP", 0, 54, 36)
        if st.form_submit_button("Aggiungi Socio"):
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

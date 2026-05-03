import streamlit as st
import pandas as pd
import json
import os

# Configurazione Pagina
st.set_page_config(page_title="Cro Magnon Manager", page_icon="⛳", layout="wide")

# --- CSS DEFINITIVO ANTI-DARK MODE & STILE GOLF ---
st.markdown("""
    <style>
    /* Forziamo lo sfondo chiaro e testo scuro su tutta l'app */
    .stApp { background-color: #f0f2f1; color: #1a242f; }
    
    /* Box Giocatori e Campi */
    .stCheckbox label, .stMarkdown p, .stHeader h2, .stHeader h3, label {
        color: #1a242f !important;
        font-weight: 600 !important;
    }
    
    /* Input e Form */
    .stTextInput input, .stNumberInput input {
        background-color: white !important;
        color: #1a242f !important;
        border: 1px solid #27ae60 !important;
    }

    /* Bottoni */
    .stButton>button {
        background-color: #27ae60 !important;
        color: white !important;
        border-radius: 10px;
        font-weight: bold;
        border: none;
        height: 3em;
    }
    
    /* Tabelle */
    .styled-table { border-collapse: collapse; width: 100%; background: white; border-radius: 10px; overflow: hidden; }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "golf_data_v2.json"

# --- FUNZIONI DATI ---
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

st.title("⛳ CRO MAGNON GOLF LEAGUE")

tab1, tab2, tab3 = st.tabs(["🎮 Gara", "👥 Giocatori", "🏗️ Gestione Campi"])

# --- TAB 3: GESTIONE CAMPI ---
with tab3:
    st.header("Configurazione Campi")
    with st.expander("➕ Aggiungi un nuovo campo"):
        nome_campo = st.text_input("Nome del Golf Club")
        tipo_campo = st.radio("Tipo", [9, 18], horizontal=True)
        
        st.write("Inserisci Par e HCP (Indice Difficoltà) per ogni buca:")
        col_par, col_hcp = st.columns(2)
        
        par_lista = []
        hcp_lista = []
        
        for i in range(1, tipo_campo + 1):
            with col_par:
                par_lista.append(st.number_input(f"Buca {i} - Par", 3, 5, 4, key=f"par_{i}"))
            with col_hcp:
                hcp_lista.append(st.number_input(f"Buca {i} - HCP", 1, 18, i, key=f"hcp_{i}"))
        
        if st.button("Salva Campo"):
            if nome_campo:
                dati["campi"].append({
                    "nome": nome_campo,
                    "tipo": tipo_campo,
                    "par": par_lista,
                    "hcp_buche": hcp_lista
                })
                salva_dati(dati)
                st.success(f"Campo {nome_campo} salvato!")
                st.rerun()

# --- TAB 2: GIOCATORI ---
with tab2:
    st.header("Anagrafica Soci")
    with st.form("add_player"):
        n = st.text_input("Nome")
        h = st.number_input("HCP", 0, 54, 36)
        if st.form_submit_button("Aggiungi"):
            dati["giocatori"].append({"nome": n, "hcp": h})
            salva_dati(dati)
            st.rerun()
    
    for i, g in enumerate(dati["giocatori"]):
        c1, c2 = st.columns([4,1])
        c1.write(f"**{g['nome']}** (HCP: {g['hcp']})")
        if c2.button("Elimina", key=f"del_p_{i}"):
            dati["giocatori"].pop(i)
            salva_dati(dati)
            st.rerun()

# --- TAB 1: GARA ---
with tab1:
    if not dati["campi"] or not dati["giocatori"]:
        st.info("Configura prima almeno un Campo e un Giocatore nei tab a fianco.")
    else:
        st.header("Partenza Gara")
        campo_scelto = st.selectbox("Dove si gioca?", [c["nome"] for c in dati["campi"]])
        info_campo = next(c for c in dati["campi"] if c["nome"] == campo_scelto)
        
        st.subheader("Seleziona Giocatori")
        presenti = []
        for g in dati["giocatori"]:
            if st.checkbox(f"{g['nome']} (HCP {g['hcp']})", key=f"play_{g['nome']}"):
                presenti.append(g)

        if presenti:
            st.divider()
            st.subheader("Inserimento Colpi per Buca")
            classifica_finale = []

            for p in presenti:
                with st.expander(f"Scorecard: {p['nome']}"):
                    colpi_buca = []
                    for b in range(1, info_campo["tipo"] + 1):
                        c = st.number_input(f"Buca {b} (Par {info_campo['par'][b-1]})", 0, 15, 0, key=f"sc_{p['nome']}_{b}")
                        colpi_buca.append(c)
                    
                    # --- CALCOLO STABLEFORD ---
                    punti_totali = 0
                    hcp_giocatore = p['hcp']
                    
                    for b_idx in range(info_campo["tipo"]):
                        score = colpi_buca[b_idx]
                        if score == 0: continue # Buca X o non finita
                        
                        par_buca = info_campo['par'][b_idx]
                        hcp_buca = info_campo['hcp_buche'][b_idx]
                        
                        # Calcolo colpi ricevuti sulla buca
                        base_strokes = hcp_giocatore // info_campo["tipo"]
                        extra_stroke = 1 if hcp_buca <= (hcp_giocatore % info_campo["tipo"]) else 0
                        colpi_ricevuti = base_strokes + extra_stroke
                        
                        # Punti Stableford: 2 + (Par - (Colpi - Ricevuti))
                        punti_buca = max(0, 2 + par_buca - (score - colpi_ricevuti))
                        punti_totali += punti_buca
                    
                    st.metric(f"Punti Stableford di {p['nome']}", int(punti_totali))
                    
                    # Calcolo Nuovo HCP (semplificato su target 36)
                    target = 36 if info_campo["tipo"] == 18 else 18
                    calo = (punti_totali - target) // 2 if punti_totali > target else 0
                    nuovo_hcp = p['hcp'] - calo
                    
                    classifica_finale.append({
                        "Giocatore": p['nome'],
                        "HCP Partenza": p['hcp'],
                        "Punti": int(punti_totali),
                        "Nuovo HCP": int(nuovo_hcp)
                    })

            if st.button("🏆 VEDI CLASSIFICA FINALE"):
                df = pd.DataFrame(classifica_finale).sort_values(by="Punti", ascending=False).reset_index(drop=True)
                df.insert(0, 'Pos', [f"{i+1}°" for i in range(len(df))])
                st.table(df)
                
                if st.button("💾 Conferma e Aggiorna HCP"):
                    for res in classifica_finale:
                        for g in dati["giocatori"]:
                            if g["nome"] == res["Giocatore"]:
                                g["hcp"] = res["Nuovo HCP"]
                    salva_dati(dati)
                    st.success("HCP aggiornati!")

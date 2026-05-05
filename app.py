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

DB_FILE = "golf_data_v12.json"

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

# Inizializziamo una lista fissa di 18 elementi per gli HCP scelti
if 'hcp_scelti' not in st.session_state:
    st.session_state.hcp_scelti = [i for i in range(1, 19)]

dati = st.session_state.db

st.title("⛳ CRO MAGNON GOLF")
tab1, tab2, tab3 = st.tabs(["🎮 Gara", "👥 Soci", "🏗️ Campi"])

# --- TAB 3: CAMPI ---
with tab3:
    st.header("Configura Nuovo Campo")
    tipo_c = st.radio("Numero buche:", [9, 18], horizontal=True)
    nome_c = st.text_input("Nome Golf Club", key="n_campo")
    
    st.write("### Assegnazione PAR e HCP (1-18)")
    
    par_definitivi = []
    hcp_definitivi = []
    
    for i in range(tipo_c):
        buca_num = i + 1
        col1, col2, col3 = st.columns([1, 2, 3])
        
        col1.markdown(f"**Buca {buca_num}**")
        
        # PAR
        p = col2.selectbox(f"Par B{buca_num}", [3, 4, 5], index=1, key=f"par_b_{buca_num}")
        par_definitivi.append(p)
        
        # HCP (Logica di esclusione)
        # Troviamo quali sono gli HCP usati dalle ALTRE buche
        altri_hcp = [st.session_state.hcp_scelti[j] for j in range(tipo_c) if i != j]
        
        # Le opzioni sono TUTTI i numeri da 1 a 18 che non sono negli altri hcp
        opzioni = [n for n in range(1, 19) if n not in altri_hcp]
        opzioni.sort() # Garantisce l'ordine 1, 2, 3... 18
        
        # Se il valore attuale per questa buca non è più disponibile, resettalo al primo libero
        valore_attuale = st.session_state.hcp_scelti[i]
        if valore_attuale not in opzioni:
            valore_attuale = opzioni[0]
            st.session_state.hcp_scelti[i] = valore_attuale
            
        # Selectbox con l'elenco ordinato
        h = col3.selectbox(
            f"HCP B{buca_num}",
            options=opzioni,
            index=opzioni.index(valore_attuale),
            key=f"hcp_b_{buca_num}"
        )
        
        # Aggiorna lo stato se l'utente cambia valore
        if h != st.session_state.hcp_scelti[i]:
            st.session_state.hcp_scelti[i] = h
            st.rerun()
            
        hcp_definitivi.append(h)

    if st.button("💾 SALVA CAMPO"):
        if nome_c:
            dati["campi"].append({"nome": nome_c, "tipo": tipo_c, "par": par_definitivi, "hcp_buche": hcp_definitivi})
            salva_dati(dati)
            st.success("Campo Salvato!")
            st.rerun()

# --- TAB 2 e TAB 1 (Invariati ma ottimizzati per coerenza) ---
with tab2:
    st.header("Soci")
    with st.form("p_form"):
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
        if c2.button("X", key=f"del_{idx}"):
            dati["giocatori"].pop(idx)
            salva_dati(dati)
            st.rerun()

with tab1:
    if not dati["campi"]:
        st.info("Configura un campo.")
    else:
        c_nome = st.selectbox("Campo:", [c['nome'] for c in dati["campi"]])
        campo = next(c for c in dati["campi"] if c['nome'] == c_nome)
        presenti = [g for g in dati["giocatori"] if st.checkbox(f"{g['nome']}", key=f"p_{g['nome']}")]

        if presenti:
            risultati = []
            for p in presenti:
                with st.expander(f"Segna: {p['nome']}"):
                    colpi = []
                    for i in range(0, campo["tipo"], 3):
                        cols = st.columns(3)
                        for j in range(3):
                            idx = i + j
                            if idx < campo["tipo"]:
                                s = cols[j].selectbox(f"B{idx+1}", range(11), format_func=lambda x: f"B{idx+1}: {x}" if x>0 else "-", key=f"s_{p['nome']}_{idx}")
                                colpi.append(s)
                    
                    # Calcolo Stableford
                    pts = 0
                    for k in range(campo["tipo"]):
                        if colpi[k] > 0:
                            h_buca = campo['hcp_buche'][k]
                            r = (p['hcp'] // campo["tipo"]) + (1 if h_buca <= (p['hcp'] % campo["tipo"]) else 0)
                            pts += max(0, 2 + campo['par'][k] - (colpi[k] - r))
                    
                    st.write(f"Punti: {int(pts)}")
                    target = 36 if campo["tipo"] == 18 else 18
                    calo = (pts - target) // 2 if pts > target else 0
                    risultati.append({"Giocatore": p['nome'], "Punti": int(pts), "Nuovo HCP": int(p['hcp'] - calo)})

            if st.button("🏆 Classifica"):
                df = pd.DataFrame(risultati).sort_values(by="Punti", ascending=False).reset_index(drop=True)
                st.table(df)

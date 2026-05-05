import streamlit as st
import pandas as pd
import json
import os

# Configurazione Pagina
st.set_page_config(page_title="Cro Magnon Manager", page_icon="⛳", layout="wide")

# --- CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f6 !important; color: #1a242f !important; }
    .stButton>button { background-color: #27ae60 !important; color: white !important; border-radius: 8px; font-weight: bold; height: 3.5em; width: 100%; }
    .stExpander { background-color: white !important; border: 1px solid #d1d1d1 !important; border-radius: 12px !important; }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "golf_data_v11.json"

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

# Inizializzazione degli HCP temporanei (18 posizioni predefinite)
if 'temp_hcp_map' not in st.session_state:
    st.session_state.temp_hcp_map = {i: i for i in range(1, 19)}

dati = st.session_state.db

st.title("⛳ CRO MAGNON GOLF")
tab1, tab2, tab3 = st.tabs(["🎮 Gara", "👥 Soci", "🏗️ Campi"])

# --- TAB 3: CAMPI (LOGICA HCP ESCLUSIVA) ---
with tab3:
    st.header("Configura Nuovo Campo")
    tipo_c = st.radio("Seleziona buche:", [9, 18], horizontal=True)
    
    # Campo di testo per il nome FUORI dal form per non resettare tutto ad ogni invio
    nome_c = st.text_input("Nome Golf Club", key="nome_campo_input")
    
    st.write("### Assegnazione PAR e HCP")
    st.caption("Nota: Se selezioni un HCP, questo non sarà più disponibile per le altre buche.")
    
    par_finali = []
    hcp_finali = []
    
    # Creiamo la griglia di selezione
    for b in range(1, tipo_c + 1):
        col_b, col_p, col_h = st.columns([1, 2, 3])
        col_b.markdown(f"**Buca {b}**")
        
        # 1. Selezione PAR
        p_val = col_p.selectbox(f"Par B{b}", [3, 4, 5], index=1, key=f"p_sel_{b}")
        par_finali.append(p_val)
        
        # 2. Selezione HCP con esclusione
        # Calcoliamo i numeri già presi dalle ALTRE buche
        presi_da_altri = [st.session_state.temp_hcp_map[i] for i in range(1, tipo_c + 1) if i != b]
        # Le opzioni per questa buca sono i numeri da 1 a 18 MENO quelli presi dagli altri
        opzioni_rimaste = [n for n in range(1, 19) if n not in presi_da_altri]
        opzioni_rimaste.sort() # Forza l'ordine 1, 2, 3...
        
        # Se il valore salvato per questa buca non è tra le opzioni (es. un altro l'ha "rubato"),
        # prendiamo il primo disponibile
        if st.session_state.temp_hcp_map[b] not in opzioni_rimaste:
            st.session_state.temp_hcp_map[b] = opzioni_rimaste[0]
            
        idx_attuale = opzioni_rimaste.index(st.session_state.temp_hcp_map[b])
        
        h_val = col_h.selectbox(
            f"HCP B{b}", 
            options=opzioni_rimaste,
            index=idx_attuale,
            key=f"h_sel_{b}"
        )
        
        # Aggiorniamo lo stato globale appena l'utente cambia la tendina
        if h_val != st.session_state.temp_hcp_map[b]:
            st.session_state.temp_hcp_map[b] = h_val
            st.rerun()
            
        hcp_finali.append(h_val)

    if st.button("💾 SALVA CAMPO DEFINITIVAMENTE"):
        if nome_c:
            dati["campi"].append({
                "nome": nome_c, 
                "tipo": tipo_c, 
                "par": par_finali, 
                "hcp_buche": hcp_finali
            })
            salva_dati(dati)
            st.success(f"Campo {nome_c} aggiunto alla lista!")
            st.rerun()
        else:
            st.error("Inserisci il nome del Golf Club!")

# --- TAB 2: GIOCATORI ---
with tab2:
    st.header("Anagrafica")
    with st.form("new_player"):
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
        st.info("Configura un campo nel tab 'Campi'.")
    else:
        campo_scelto = st.selectbox("Dove si gioca?", [c['nome'] for c in dati["campi"]])
        campo = next(c for c in dati["campi"] if c['nome'] == campo_scelto)
        
        st.subheader("Seleziona i presenti")
        presenti = [g for g in dati["giocatori"] if st.checkbox(f"{g['nome']}", key=f"pr_{g['nome']}")]

        if presenti:
            st.divider()
            risultati = []
            for p in presenti:
                with st.expander(f"Cartellino: {p['nome']} (HCP {p['hcp']})"):
                    metodo = st.radio("Metodo:", ["Tendina", "Manuale"], horizontal=True, key=f"m_{p['nome']}")
                    pts = 0
                    if metodo == "Manuale":
                        pts = st.number_input("Punti Stableford", 0, 60, 0, key=f"man_{p['nome']}")
                    else:
                        scores = []
                        for i in range(0, campo["tipo"], 3):
                            cols = st.columns(3)
                            for j in range(3):
                                b_idx = i + j
                                if b_idx < campo["tipo"]:
                                    s = cols[j].selectbox(f"B{b_idx+1}", [0,1,2,3,4,5,6,7,8,9,10], format_func=lambda x: f"B{b_idx+1}: {x}" if x>0 else "-", key=f"sc_{p['nome']}_{b_idx}")
                                    scores.append(s)
                        
                        # Calcolo
                        for idx in range(campo["tipo"]):
                            if scores[idx] > 0:
                                p_val, h_val = campo['par'][idx], campo['hcp_buche'][idx]
                                r = (p['hcp'] // campo["tipo"]) + (1 if h_val <= (p['hcp'] % campo["tipo"]) else 0)
                                pts += max(0, 2 + p_val - (scores[idx] - r))
                    
                    st.write(f"**Punti: {int(pts)}**")
                    target = 36 if campo["tipo"] == 18 else 18
                    calo = (pts - target) // 2 if pts > target else 0
                    risultati.append({"Giocatore": p['nome'], "Punti": int(pts), "Nuovo HCP": int(p['hcp'] - calo)})

            if st.button("🏆 MOSTRA CLASSIFICA"):
                df = pd.DataFrame(risultati).sort_values(by="Punti", ascending=False).reset_index(drop=True)
                df.insert(0, 'Pos', [f"{i+1}°" for i in range(len(df))])
                st.table(df)

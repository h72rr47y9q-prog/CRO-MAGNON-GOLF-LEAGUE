import streamlit as st
import pandas as pd
import json
import os

# Configurazione Pagina
st.set_page_config(page_title="Cro Magnon Manager", page_icon="⛳", layout="centered")

# --- STILE CSS PER EVITARE TESTO BIANCO ---
st.markdown("""
    <style>
    .stCheckbox label {
        color: #1a242f !important;
        font-weight: 600 !important;
        background-color: #ffffff;
        padding: 10px;
        border-radius: 8px;
        border: 1px solid #d1d1d1;
    }
    .stMarkdown p { color: #1a242f !important; }
    .stButton>button { 
        background-color: #e67e22; 
        color: white; 
        font-weight: bold; 
    }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "golf_db.json"

# Funzioni gestione dati con gestione errori
def carica_dati():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except:
            return []
    return []

def salva_dati(lista):
    try:
        with open(DB_FILE, "w") as f:
            json.dump(lista, f, indent=4)
    except Exception as e:
        st.error(f"Errore nel salvataggio: {e}")

# Inizializzazione dati
if 'anagrafica' not in st.session_state:
    st.session_state.anagrafica = carica_dati()

st.title("⛳ CRO MAGNON GOLF LEAGUE")

tab1, tab2 = st.tabs(["🎮 Gara del Giorno", "👥 Gestione Giocatori"])

# --- TAB 2: GESTIONE ANAGRAFICA ---
with tab2:
    st.subheader("Registra nuovi soci")
    with st.form("nuovo_giocatore", clear_on_submit=True):
        nome = st.text_input("Nome e Cognome")
        hcp = st.number_input("HCP attuale", 0, 54, 36)
        if st.form_submit_button("Aggiungi all'Anagrafica"):
            if nome:
                st.session_state.anagrafica.append({"nome": nome, "hcp": hcp})
                salva_dati(st.session_state.anagrafica)
                st.success(f"{nome} aggiunto!")
                st.rerun()

    st.divider()
    if st.session_state.anagrafica:
        for i, g in enumerate(st.session_state.anagrafica):
            c1, c2 = st.columns([3, 1])
            c1.write(f"**{g['nome']}** (HCP: {g['hcp']})")
            if c2.button("Elimina", key=f"del_{i}"):
                st.session_state.anagrafica.pop(i)
                salva_dati(st.session_state.anagrafica)
                st.rerun()

# --- TAB 1: GARA DEL GIORNO ---
with tab1:
    if not st.session_state.anagrafica:
        st.info("Aggiungi i giocatori nel tab 'Gestione Giocatori'.")
    else:
        st.subheader("Seleziona i presenti")
        presenti_nomi = []
        for g in st.session_state.anagrafica:
            if st.checkbox(f"{g['nome']} (HCP {g['hcp']})", key=f"ch_{g['nome']}"):
                presenti_nomi.append(g['nome'])

        if presenti_nomi:
            st.divider()
            tipo_gara = st.radio("Distanza", ["18 Buche", "9 Buche"], horizontal=True)
            target = 36 if tipo_gara == "18 Buche" else 18
            
            risultati_temp = []
            for nome_p in presenti_nomi:
                # Recupera l'hcp originale
                hcp_orig = next(item['hcp'] for item in st.session_state.anagrafica if item['nome'] == nome_p)
                
                score = st.text_input(f"Punti per {nome_p}", key=f"sc_{nome_p}", placeholder="NC")
                
                punti_f = 0
                hcp_f = hcp_orig
                if score.upper() == "NC":
                    punti_f = -1
                elif score.isdigit():
                    punti_f = int(score)
                    calo = (punti_f - target) // 2 if punti_f > target else 0
                    hcp_f = hcp_orig - calo
                
                risultati_temp.append({
                    "Giocatore": nome_p,
                    "HCP Partenza": hcp_orig,
                    "Punti": punti_f,
                    "Nuovo HCP": hcp_f
                })

            if st.button("🏆 GENERA CLASSIFICA"):
                res_df = pd.DataFrame(risultati_temp)
                res_df = res_df.sort_values(by="Punti", ascending=False).reset_index(drop=True)
                
                # Formattazione classifica
                res_df.insert(0, 'Posizione', [f"{i+1}° POSTO" if p >= 0 else "-" for i, p in enumerate(res_df['Punti'])])
                res_df['Punti'] = res_df['Punti'].apply(lambda x: "NC" if x == -1 else x)
                
                st.subheader("📊 Risultati")
                st.table(res_df)

                if st.button("💾 AGGIORNA HCP DEFINITIVAMENTE"):
                    for r in risultati_temp:
                        for g in st.session_state.anagrafica:
                            if g['nome'] == r['Giocatore']:
                                g['hcp'] = r['Nuovo HCP']
                    salva_dati(st.session_state.anagrafica)
                    st.success("HCP aggiornati in anagrafica!")

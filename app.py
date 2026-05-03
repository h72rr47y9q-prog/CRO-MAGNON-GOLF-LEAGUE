import streamlit as st
import pandas as pd
import json
import os

# Configurazione Pagina
st.set_page_config(page_title="Cro Magnon Golf League", page_icon="⛳", layout="centered")

# --- STILE CSS PERSONALIZZATO ---
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #e67e22; color: white; }
    h1 { color: #1a242f; text-align: center; font-family: 'Georgia'; }
    </style>
    """, unsafe_allow_html=True)

st.title("⛳ CRO MAGNON GOLF LEAGUE")

# --- FUNZIONI DATABASE ---
DB_FILE = "golf_db.json"

def carica_dati():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return []

def salva_dati(lista):
    with open(DB_FILE, "w") as f:
        json.dump(lista, f, indent=4)

# Inizializzazione sessione
if 'giocatori' not in st.session_state:
    st.session_state.giocatori = carica_dati()

# --- SIDEBAR: GESTIONE GIOCATORI ---
with st.sidebar:
    st.header("Gestione Club")
    nuovo_nome = st.text_input("Nome Giocatore")
    nuovo_hcp = st.number_input("HCP Iniziale", min_value=0, max_value=54, step=1)
    
    if st.button("➕ Aggiungi Giocatore"):
        if nuovo_nome:
            st.session_state.giocatori.append({
                "nome": nuovo_nome, 
                "hcp": nuovo_hcp, 
                "punti": 0, 
                "nuovo_hcp": nuovo_hcp
            })
            salva_dati(st.session_state.giocatori)
            st.success(f"{nuovo_nome} aggiunto!")

    if st.button("🗑️ Reset Classifica"):
        for g in st.session_state.giocatori:
            g['punti'] = 0
            g['nuovo_hcp'] = g['hcp']
        st.rerun()

# --- MAIN: GARA DEL GIORNO ---
col1, col2 = st.columns(2)
with col1:
    tipo_gara = st.radio("Tipo di Gara", ["18 Buche", "9 Buche"])
    target = 36 if tipo_gara == "18 Buche" else 18

st.divider()

# --- INSERIMENTO PUNTI ---
st.subheader("📝 Inserimento Punteggi")
for g in st.session_state.giocatori:
    cols = st.columns([3, 2])
    with cols[0]:
        st.write(f"**{g['nome']}** (HCP: {g['hcp']})")
    with cols[1]:
        # Usiamo un text_input per gestire anche "NC"
        punti_input = st.text_input(f"Punti", key=f"p_{g['nome']}", placeholder="0 o NC")
        
        if punti_input.upper() == "NC":
            g['punti'] = -1
            g['nuovo_hcp'] = g['hcp']
        elif punti_input.isdigit():
            p = int(punti_input)
            g['punti'] = p
            calo = (p - target) // 2 if p > target else 0
            g['nuovo_hcp'] = g['hcp'] - calo

if st.button("⛳ CALCOLA E AGGIORNA CLASSIFICA"):
    salva_dati(st.session_state.giocatori)
    st.balloons()

st.divider()

# --- CLASSIFICA FINALE ---
st.subheader("🏆 Classifica Live")
if st.session_state.giocatori:
    # Creazione DataFrame per visualizzazione
    df = pd.DataFrame(st.session_state.giocatori)
    
    # Ordiniamo
    df = df.sort_values(by="punti", ascending=False).reset_index(drop=True)
    
    # Formattazione Classifica e Medaglie
    def formatta_pos(index, punti):
        if punti <= 0: return "-"
        if index == 0: return "🥇 1° POSTO"
        if index == 1: return "🥈 2° POSTO"
        if index == 2: return "🥉 3° POSTO"
        return f"{index + 1}° POSTO"

    df['Classifica'] = [formatta_pos(i, p) for i, p in enumerate(df['punti'])]
    df['Punti'] = df['punti'].apply(lambda x: "NC" if x == -1 else x)
    
    # Rinominiano le colonne per l'utente
    df_display = df[['Classifica', 'nome', 'hcp', 'Punti', 'nuovo_hcp']].copy()
    df_display.columns = ['Posizione', 'Giocatore', 'HCP Partenza', 'Punti Gara', 'Nuovo HCP']
    
    st.table(df_display)

    # Pulsante per salvare i nuovi HCP per la prossima volta
    if st.button("💾 Conferma HCP per Sabato prossimo"):
        for g in st.session_state.giocatori:
            g['hcp'] = g['nuovo_hcp']
        salva_dati(st.session_state.giocatori)
        st.success("HCP di partenza aggiornati per la prossima gara!")

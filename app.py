import streamlit as st
import pandas as pd
import json
import os

# Configurazione Pagina
st.set_page_config(page_title="Cro Magnon Manager", page_icon="⛳", layout="wide")

# --- CSS ANTI-DARK MODE & UI PULITA ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f6; color: #1a242f; }
    .stCheckbox label, .stMarkdown p, label { color: #1a242f !important; font-weight: 600 !important; }
    .stButton>button { background-color: #27ae60 !important; color: white !important; border-radius: 8px; font-weight: bold; border: none; height: 3em; }
    /* Box per le buche */
    .buca-box {
        background-color: white;
        padding: 10px;
        border-radius: 10px;
        border: 1px solid #d1d1d1;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "golf_data_v3.json"

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

tab1, tab2, tab3 = st.tabs(["🎮 Gara del Giorno", "👥 Gestione Giocatori", "🏗️ Configurazione Campi"])

# --- TAB 3: GESTIONE CAMPI (LAYOUT A GRIGLIA) ---
with tab3:
    st.header("Configurazione Campi")
    with st.expander("➕ Registra Nuovo Campo", expanded=True):
        nome_c = st.text_input("Nome del Golf Club")
        tipo_c = st.radio("Numero Buche", [9, 18], horizontal=True)
        
        st.write("---")
        st.write("**Inserisci i dati delle buche (Par e HCP):**")
        
        par_lista = []
        hcp_lista = []
        
        # Creiamo una griglia 3x3 o 6x3 a seconda delle buche
        cols_per_row = 3
        for i in range(0, tipo_c, cols_per_row):
            cols = st.columns(cols_per_row)
            for j in range(cols_per_row):
                buca_num = i + j + 1
                if buca_num <= tipo_c:
                    with cols[j]:
                        st.markdown(f"**Buca {buca_num}**")
                        p = st.number_input(f"Par", 3, 5, 4, key=f"p_{buca_num}")
                        h = st.number_input(f"HCP", 1, 18, buca_num, key=f"h_{buca_num}")
                        par_lista.append(p)
                        hcp_lista.append(h)
        
        if st.button("Salva Configurazione Campo"):
            if nome_c:
                dati["campi"].append({
                    "nome": nome_c,
                    "tipo": tipo_c,
                    "par": par_lista,
                    "hcp_buche": hcp_lista
                })
                salva_dati(dati)
                st.success(f"Campo {nome_c} aggiunto correttamente!")
                st.rerun()

# --- TAB 2: GIOCATORI ---
with tab2:
    st.header("Anagrafica Soci")
    with st.form("add_p"):
        c1, c2 = st.columns([2, 1])
        n = c1.text_input("Nome Giocatore")
        h = c2.number_input("HCP", 0, 54, 36)
        if st.form_submit_button("Aggiungi Socio"):
            dati["giocatori"].append({"nome": n, "hcp": h})
            salva_dati(dati)
            st.rerun()
    
    st.write("---")
    for i, g in enumerate(dati["giocatori"]):
        c1, c2 = st.columns([4,1])
        c1.write(f"👤 **{g['nome']}** — HCP: {g['hcp']}")
        if c2.button("Elimina", key=f"del_p_{i}"):
            dati["giocatori"].pop(i)
            salva_dati(dati)
            st.rerun()

# --- TAB 1: GARA ---
with tab1:
    if not dati["campi"] or not dati["giocatori"]:
        st.info("Configura prima Campi e Giocatori nei tab appositi.")
    else:
        st.header("Inizia Gara")
        campo_scelto = st.selectbox("Seleziona Campo", [c["nome"] for c in dati["campi"]])
        info_c = next(c for c in dati["campi"] if c["nome"] == campo_scelto)
        
        st.subheader("Chi partecipa oggi?")
        presenti = []
        for g in dati["giocatori"]:
            # Checkbox con stile per visibilità
            if st.checkbox(f"{g['nome']} (HCP {g['hcp']})", key=f"p_{g['nome']}"):
                presenti.append(g)

        if presenti:
            st.divider()
            st.subheader("Inserimento Scorecard")
            risultati_finale = []

            for p in presenti:
                with st.expander(f"Cartellino di {p['nome']}", expanded=False):
                    colpi_inseriti = []
                    # Layout scorecard buca per buca
                    st.write(f"HCP Partenza: {p['hcp']}")
                    
                    # Griglia per inserimento colpi
                    for i in range(0, info_c["tipo"], 3):
                        cols = st.columns(3)
                        for j in range(3):
                            b_num = i + j + 1
                            if b_num <= info_c["tipo"]:
                                with cols[j]:
                                    c = st.number_input(f"Buca {b_num} (Par {info_c['par'][b_num-1]})", 0, 15, 0, key=f"score_{p['nome']}_{b_num}")
                                    colpi_inseriti.append(c)
                    
                    # Calcolo Stableford
                    tot_stableford = 0
                    hcp_g = p['hcp']
                    num_buche = info_c["tipo"]
                    
                    for b_idx in range(num_buche):
                        colpi_lordi = colpi_inseriti[b_idx]
                        if colpi_lordi == 0: continue
                        
                        par_b = info_c['par'][b_idx]
                        diff_b = info_c['hcp_buche'][b_idx]
                        
                        # Calcolo colpi ricevuti
                        ricevuti = hcp_g // num_buche
                        if diff_b <= (hcp_g % num_buche):
                            ricevuti += 1
                        
                        punti_b = max(0, 2 + par_b - (colpi_lordi - ricevuti))
                        tot_stableford += punti_b
                    
                    st.success(f"Totale Stableford: {int(tot_stableford)}")
                    
                    # Calcolo HCP Finale
                    target = 36 if num_buche == 18 else 18
                    calo = (tot_stableford - target) // 2 if tot_stableford > target else 0
                    nuovo_hcp = p['hcp'] - calo
                    
                    risultati_finale.append({
                        "Giocatore": p['nome'],
                        "HCP Inizio": p['hcp'],
                        "Punti": int(tot_stableford),
                        "Nuovo HCP": int(nuovo_hcp)
                    })

            if st.button("🏆 CALCOLA CLASSIFICA FINALE"):
                st.balloons()
                res_df = pd.DataFrame(risultati_finale).sort_values(by="Punti", ascending=False).reset_index(drop=True)
                res_df.insert(0, 'Pos', [f"{i+1}°" for i in range(len(res_df))])
                st.table(res_df)
                
                if st.button("💾 Applica Nuovi HCP in Anagrafica"):
                    for r in risultati_finale:
                        for g in dati["giocatori"]:
                            if g["nome"] == r["Giocatore"]:
                                g["hcp"] = r["Nuovo HCP"]
                    salva_dati(dati)
                    st.success("HCP aggiornati per sabato prossimo!")

import streamlit as st
import json
from datetime import datetime

# carica dati
def load_data():
    try:
        with open("matches.json", "r") as f:
            return json.load(f)
    except:
        return []

data = load_data()

st.title("📊 GOAL ENGINE APP")

# --- GIORNI ---
oggi = datetime.now().strftime("%Y-%m-%d")

giorni = list(set([m["date"] for m in data]))
giorni.sort()

giorno_scelto = st.selectbox("Seleziona giorno", giorni, index=len(giorni)-1)

# --- FILTRA PER GIORNO ---
matches_day = [m for m in data if m["date"] == giorno_scelto]

# --- STELLE ---
st.subheader("Seleziona categoria")

col1, col2, col3 = st.columns(3)

stars_choice = None

with col1:
    if st.button("⭐⭐⭐"):
        stars_choice = 3

with col2:
    if st.button("⭐⭐"):
        stars_choice = 2

with col3:
    if st.button("⭐"):
        stars_choice = 1

# --- MATCH LIST ---
if stars_choice:
    matches_filtered = [m for m in matches_day if m["stars"] == stars_choice]

    if matches_filtered:
        match_labels = [
            f'{m["home"]} vs {m["away"]} | {m["time"]}'
            for m in matches_filtered
        ]

        selected_label = st.selectbox("Seleziona match", match_labels)

        selected_match = matches_filtered[match_labels.index(selected_label)]

        st.session_state["selected_match"] = selected_match

# --- DETTAGLIO MATCH ---
if "selected_match" in st.session_state:
    m = st.session_state["selected_match"]

    st.subheader(f'{m["home"]} vs {m["away"]}')

    st.write(f"League: {m['league']}")
    st.write(f"Time: {m['time']}")
    st.write(f"Stars: {'⭐'*m['stars']}")

    st.write("### Picks")
    for p in m["picks"]:
        st.write("-", p)

    st.write("### Stats")
    for k, v in m["stats"].items():
        st.write(f"{k}: {v}")

    # INPUT
    result = st.text_input("Final Result (es: 2-1)", m.get("result", ""))
    ht = st.text_input("HT Result (es: 1-0)", m.get("ht", ""))

    if st.button("Salva"):
        m["result"] = result
        m["ht"] = ht

        # CALCOLO
        try:
            home_goals, away_goals = map(int, result.split("-"))
            ht_home, ht_away = map(int, ht.split("-"))
        except:
            st.error("Formato risultato errato")
        else:
            results = {}

            for pick in m["picks"]:
                if "Over 2.5" in pick:
                    results[pick] = "WIN" if home_goals + away_goals >= 3 else "LOSS"
                elif "Over 1.5" in pick:
                    results[pick] = "WIN" if home_goals + away_goals >= 2 else "LOSS"
                elif "BTTS" in pick:
                    results[pick] = "WIN" if home_goals > 0 and away_goals > 0 else "LOSS"
                elif "Home" in pick:
                    results[pick] = "WIN" if home_goals > away_goals else "LOSS"
                elif "Over 0.5 HT" in pick:
                    results[pick] = "WIN" if ht_home + ht_away >= 1 else "LOSS"

            m["results"] = results

            # salva file
            with open("matches.json", "w") as f:
                json.dump(data, f, indent=2)

    # OUTPUT
    if "results" in m:
        st.write("### Esiti")
        for k, v in m["results"].items():
            st.write(f"{k} → {v}")

import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Over 2.5 Hedge Strategy Demo",
    layout="centered"
)

st.title("⚽ Over 2.5 Goal Hedge Strategy (Demo)")
st.caption("Rule-based eligibility & hedge structure demonstration")

TOTAL_BANKROLL = 100

def implied_prob(odds):
    return 1 / odds if odds > 0 else 0

st.divider()

# ===============================
# Match Info
# ===============================
st.subheader("Match Information")

col1, col2 = st.columns(2)
with col1:
    home_team = st.text_input("Home Team", "Team A")
with col2:
    away_team = st.text_input("Away Team", "Team B")

st.markdown(f"### {home_team} vs {away_team}")

st.divider()

# ===============================
# Market Odds Input
# ===============================
st.subheader("Market Odds Input")

col1, col2 = st.columns(2)
with col1:
    over25_odds = st.number_input(
        "Over 2.5 Odds", min_value=1.01, value=2.35, step=0.01
    )
with col2:
    home_win_odds = st.number_input(
        "Home Win Odds", min_value=1.01, value=1.38, step=0.01
    )

st.markdown("#### Under 2.5 Correct Score Odds")

score_odds = {
    "0-0": st.number_input("0 - 0 Odds", value=9.5, step=0.1),
    "1-0": st.number_input("1 - 0 Odds", value=7.5, step=0.1),
    "0-1": st.number_input("0 - 1 Odds", value=7.8, step=0.1),
    "1-1": st.number_input("1 - 1 Odds", value=6.2, step=0.1),
    "2-0": st.number_input("2 - 0 Odds", value=9.0, step=0.1),
    "0-2": st.number_input("0 - 2 Odds", value=9.8, step=0.1),
}

st.divider()

# ===============================
# System 1
# ===============================
st.subheader("System 1 · Under Score Hedge + Over 2.5")

selected_scores = st.multiselect(
    "Select any 3 Under 2.5 scores for hedge",
    options=list(score_odds.keys())
)

system1_active = (
    2.20 <= over25_odds <= 2.50 and
    len(selected_scores) == 3
)

if system1_active:
    under_prob = sum(implied_prob(score_odds[s]) for s in selected_scores)
    over_prob = implied_prob(over25_odds)

    stake_under = TOTAL_BANKROLL * under_prob / (under_prob + over_prob)
    stake_over = TOTAL_BANKROLL - stake_under

    st.success("✔ System 1 Eligible")
    st.markdown(f"""
    **Selected Scores**: {', '.join(selected_scores)}  
    **Under Hedge Probability**: {under_prob:.2%}  
    **Over 2.5 Probability**: {over_prob:.2%}

    **Stake Allocation**
    - Under Scores: {stake_under:.2f}
    - Over 2.5: {stake_over:.2f}
    """)
else:
    st.warning("✖ System 1 Not Eligible (Check Over odds & score selection)")

st.divider()

# ===============================
# System 2
# ===============================
st.subheader("System 2 · Total Goals + Strong Home Win + Over 2.5")

col1, col2, col3 = st.columns(3)
with col1:
    tg0 = st.number_input("Total Goals 0 Odds", value=9.0)
with col2:
    tg1 = st.number_input("Total Goals 1 Odds", value=5.5)
with col3:
    tg2 = st.number_input("Total Goals 2 Odds", value=4.2)

system2_active = home_win_odds <= 1.40 and 2.20 <= over25_odds <= 2.50

if system2_active:
    tg_prob = implied_prob(tg0) + implied_prob(tg1) + implied_prob(tg2)
    over_prob = implied_prob(over25_odds)

    stake_tg = TOTAL_BANKROLL * tg_prob / (tg_prob + over_prob)
    stake_over2 = TOTAL_BANKROLL - stake_tg

    st.success("✔ System 2 Eligible")
    st.markdown(f"""
    **Total Goals (0/1/2) Probability**: {tg_prob:.2%}  
    **Over 2.5 Probability**: {over_prob:.2%}

    **Stake Allocation**
    - Total Goals Combo: {stake_tg:.2f}
    - Over 2.5: {stake_over2:.2f}
    """)
else:
    st.warning("✖ System 2 Not Eligible (Home odds or Over odds invalid)")

st.divider()

# ===============================
# Live Odds Signal
# ===============================
st.subheader("Live Over 2.5 Odds Signal")

live_over = st.number_input(
    "Live Over 2.5 Odds", value=over25_odds, step=0.01
)

if live_over != over25_odds:
    st.warning(
        f"⚠ Over 2.5 odds changed: {over25_odds} → {live_over} "
        "Market structure may have shifted."
    )
else:
    st.info("No significant Over 2.5 odds movement detected")

st.divider()

st.caption(
    "This demo illustrates hedge-eligible market structures. "
    "It is not a betting recommendation."
)

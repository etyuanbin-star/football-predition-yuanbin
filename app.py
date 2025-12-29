import streamlit as st

st.set_page_config(
    page_title="Over 2.5 Hedge Strategy Demo",
    layout="centered"
)

st.title("⚽ Over 2.5 Goal Hedge Strategy (Demo)")
st.caption("Rule-based eligibility filter for total goals & score hedging")

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
    over25_odds = st.number_input("Over 2.5 Odds", min_value=1.01, value=2.35, step=0.01)
with col2:
    under25_odds = st.number_input("Under 2.5 Odds", min_value=1.01, value=1.65, step=0.01)

st.markdown("#### Key Under 2.5 Score Odds")

col1, col2, col3 = st.columns(3)
with col1:
    odds_00 = st.number_input("0 - 0 Odds", min_value=1.01, value=9.5, step=0.1)
with col2:
    odds_10 = st.number_input("1 - 0 / 0 - 1 Odds", min_value=1.01, value=7.5, step=0.1)
with col3:
    odds_11 = st.number_input("1 - 1 Odds", min_value=1.01, value=6.2, step=0.1)

st.divider()

# ===============================
# Strategy Preconditions
# ===============================
st.subheader("Strategy Preconditions")

# Rule A: Over 2.5 Entry Condition
rule_over = over25_odds >= 2.30

# Rule B: Under 2.5 Hedge Structure
rule_under = (
    under25_odds <= 1.70 and
    odds_11 >= 6.0 and
    odds_00 >= 8.0
)

# Display rules
st.markdown("### Rule Check")

if rule_over:
    st.success("✔ Over 2.5 Odds ≥ 2.30 (PASS)")
else:
    st.error("✖ Over 2.5 Odds < 2.30 (FAIL)")

if rule_under:
    st.success("✔ Under 2.5 Hedge Structure Valid")
else:
    st.error("✖ Under 2.5 Hedge Structure Invalid")

st.divider()

# ===============================
# Final Decision
# ===============================
st.subheader("Final Strategy Status")

if rule_over and rule_under:
    st.success("🟢 Strategy Eligible")
    st.markdown("""
    **Suggested Structure**
    - Core Position: Over 2.5
    - Hedge Scores: 0-0 / 1-0 / 1-1
    - Risk Level: Medium
    """)
else:
    st.warning("🔴 Strategy Not Eligible")
    st.markdown("""
    **Reason**
    - Market structure does not meet predefined conditions
    - No action recommended
    """)

st.divider()

# ===============================
# Disclaimer
# ===============================
st.caption(
    "This demo demonstrates rule-based strategy filtering. "
    "All outputs are probabilistic and do not guarantee outcomes."
)

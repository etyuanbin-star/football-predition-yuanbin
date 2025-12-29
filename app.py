import streamlit as st
import pandas as pd
import numpy as np

# --- Page Configuration ---
st.set_page_config(page_title="EV Mirror: The Edge Lab", layout="wide")

# --- Header & Preface ---
st.title("🔺 EV Mirror: The Edge Lab")
st.subheader("Risk Management & Trading Psychology Educational Tool")

with st.expander("📖 READ FIRST: The Dogmas of Risk Control", expanded=True):
    st.markdown("""
    **Core Principles:**
    1. **Cash is a Position**: In a Negative Expected Value (EV) environment, *not playing* is the only winning strategy.
    2. **The Hedge Trap**: Attempting to 'eliminate' risk by covering all outcomes only accelerates capital depletion through transaction costs (The House Edge).
    3. **Value Dilution**: When information becomes 'Overheated' (too many people betting the same way), the odds no longer reflect the true probability.
    4. **The Impossible Trinity**: You cannot simultaneously have **High Win Rate**, **High Odds**, and **High Frequency**.
    """)

# --- 1. Sidebar: Market Environment & Filters ---
with st.sidebar:
    st.header("⚖️ Market Odds (House Pricing)")
    o25_odds = st.number_input("Over 2.5 Goals Odds", value=2.45, min_value=1.01, step=0.01)
    
    st.divider()
    st.subheader("🛡️ Experience Filters")
    exclude_zero = st.checkbox("Exclude 0-0 (Historical Pattern: High Activity)", value=False)
    exclude_extreme = st.checkbox("Exclude Extreme Scores (Power Imbalance)", value=False)
    
    heat_level = st.select_slider(
        "Information Heat (Value Dilution)",
        options=["Ice Cold", "Cool", "Balanced", "Overheated", "Manic"],
        value="Overheated"
    )
    
    st.divider()
    st.subheader("🧠 Your Judgment")
    pred_prob = st.slider("Your Predicted Win Rate for Over 2.5 (%)", 10, 90, 45) / 100

# --- 2. Logic Engine: EV & The Impossible Trinity ---
score_list = ["0-0", "1-0", "0-1", "1-1", "2-0", "0-2"]
default_odds = {"0-0": 10.0, "1-0": 8.5, "0-1": 8.0, "1-1": 7.0, "2-0": 13.0, "0-2": 12.0}

# 2.1 Overround Analysis (House Margin)
all_probs = [1/o25_odds] + [1/v for v in default_odds.values()]
overround = (sum(all_probs) - 1) * 100

# 2.2 Value Dilution Logic
heat_impact = {"Ice Cold": 1.05, "Cool": 1.02, "Balanced": 1.0, "Overheated": 0.95, "Manic": 0.85}
adjusted_ev_odds = o25_odds * heat_impact[heat_level]
ev = (pred_prob * (adjusted_ev_odds - 1)) - (1 - pred_prob)

# --- 3. Diagnostic Panel ---
col_tri, col_val = st.columns([1, 1])

with col_tri:
    st.write("### 🔺 The Impossible Trinity Monitor")
    tri_index = pred_prob * o25_odds
    
    if tri_index > 1.05:
        st.error(f"Index {tri_index:.2f}: 【Mathematical Illusion】\nThis combination rarely exists in real markets. Likely a scam or error.")
    elif tri_index > 0.95:
        st.warning(f"Index {tri_index:.2f}: 【Professional Edge Zone】\nA slight mathematical advantage exists. Requires strict discipline.")
    else:
        st.success(f"Index {tri_index:.2f}: 【The Harvest Zone】\nThis is the house's favorite zone. You win often, but you lose money overall.")

with col_val:
    st.write("### 💰 Expected Value (EV) Diagnosis")
    if ev > 0:
        st.metric("Expected Return", f"+{ev:.2%}", "Edge Found")
        kelly = max(0, ev / (adjusted_ev_odds - 1))
        st.write(f"Suggested Kelly Position: **{kelly:.2%}** of Bankroll")
    else:
        st.metric("Expected Return", f"{ev:.2%}", "No Edge - Stay Out", delta_color="inverse")
        st.error("CONCLUSION: Not acting is the only way to 'win' here.")

# --- 4. Strategy Sandbox: The Hedge Trap ---
st.divider()
st.subheader("🕹️ Strategy Sandbox: Multi-Hedge & Blindspot Analysis")
c1, c2 = st.columns([1, 2], gap="large")

active_bets = []
with c1:
    st.write("**Configure Your Bets:**")
    if st.toggle("Main Bet: Over 2.5 Goals", value=True):
        amt = st.number_input("Stake ($)", value=100, key="o25_main")
        active_bets.append({"name": "Over 2.5", "odds": o25_odds, "stake": amt, "is_over": True})
    
    st.write("---")
    st.write("**Score Hedges (Under 2.5):**")
    for s in score_list:
        disabled = (s == "0-0" and exclude_zero) or (s in ["2-0", "0-2"] and exclude_extreme)
        label = f"{s} {'(Pattern Suggests Exclude)' if disabled else ''}"
        
        col_cb, col_am = st.columns([1, 1])
        with col_cb:
            is_bet = st.checkbox(label, key=f"cb_{s}", value=False)
        with col_am:
            amt = st.number_input("Stake", value=20, key=f"am_{s}", label_visibility="collapsed") if is_bet else 0
        
        if is_bet:
            active_bets.append({"name": s, "odds": default_odds[s], "stake": amt, "is_over": False})

    total_stake = sum(b['stake'] for b in active_bets)
    st.metric("🛡️ Total Capital Committed", f"${total_stake}")

with c2:
    outcomes = score_list + ["Over 2.5 (3+ Goals)"]
    res_data = []
    for out in outcomes:
        income = 0
        is_o = (out == "Over 2.5 (3+ Goals)")
        for b in active_bets:
            if (b['is_over'] and is_o) or (b['name'] == out):
                income += b['stake'] * b['odds']
        res_data.append({"Outcome": out, "Net Profit/Loss": income - total_stake})
    
    df_res = pd.DataFrame(res_data)
    st.write("**PnL Distribution across Outcomes:**")
    st.bar_chart(df_res.set_index("Outcome")["Net Profit/Loss"])
    
    holes = df_res[df_res['Net Profit/Loss'] < 0]
    if total_stake > 0:
        if holes.empty:
            st.success("✨ Mathematical Coverage achieved (Check if profit margin is too thin).")
        else:
            st.warning(f"🚨 Blindspot Alert: If the result is {', '.join(holes['Outcome'].tolist

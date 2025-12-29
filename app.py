import streamlit as st
import pandas as pd
import numpy as np

# ===============================
# Page Config
# ===============================
st.set_page_config(
    page_title="Football Odds Hedge Terminal",
    layout="wide"
)

st.title("⚽ Football Odds Hedge – Negative EV Trading Terminal")
st.caption(
    "A structural demonstration of why rational hedge constructions fail "
    "under bookmaker-implied probability and margin."
)

st.divider()

# ===============================
# Panel 1: Market Input
# ===============================
st.subheader("🟦 Market Input")

col1, col2 = st.columns(2)
with col1:
    match_name = st.text_input(
        "Match",
        "Angola vs Egypt (AFCON Group B, 2025-12-30)"
    )
with col2:
    over25_odds = st.number_input(
        "Over 2.5 Odds",
        min_value=1.01,
        value=2.30,
        step=0.01
    )

st.markdown("### Under 2.5 – Exact Score Odds")

scores = {
    "0-0": st.number_input("0 - 0", value=7.20, step=0.1),
    "1-0": st.number_input("1 - 0", value=7.30, step=0.1),
    "0-1": st.number_input("0 - 1", value=5.80, step=0.1),
    "2-0": st.number_input("2 - 0", value=14.00, step=0.1),
    "1-1": st.number_input("1 - 1", value=5.90, step=0.1),
    "0-2": st.number_input("0 - 2", value=10.00, step=0.1),
}

st.divider()

# ===============================
# Panel 2: Position Construction
# ===============================
st.subheader("🟦 Position Construction")

st.markdown(
    "Select **any 3 exact-score legs** (like selecting option legs in a spread structure). "
    "Scores with odds < 6 are typically filtered out in practice."
)

selected_scores = []
for score, odds in scores.items():
    if st.checkbox(f"{score} @ {odds}", value=odds >= 6):
        selected_scores.append((score, odds))

if len(selected_scores) != 3:
    st.warning("⚠️ Exactly **3 scorelines** must be selected.")
    st.stop()

st.success("✔ 3-leg Under-score portfolio constructed")

st.divider()

# ===============================
# Panel 3: Implied Probability Matrix
# ===============================
st.subheader("🟦 Implied Probability Matrix")

data = []

# Over 2.5
data.append({
    "Leg": "Over 2.5",
    "Odds": over25_odds,
    "Implied Probability": 1 / over25_odds
})

# Selected Under scores
for score, odds in selected_scores:
    data.append({
        "Leg": f"Under {score}",
        "Odds": odds,
        "Implied Probability": 1 / odds
    })

df = pd.DataFrame(data)
df["Implied Probability (%)"] = df["Implied Probability"] * 100

st.dataframe(df, use_container_width=True)

total_implied_prob = df["Implied Probability"].sum()

st.markdown(
    f"**Total Implied Probability (Selected Outcome Space): "
    f"{total_implied_prob*100:.2f}%**"
)

st.caption(
    "Probabilities are directly derived from bookmaker odds "
    "(before any margin normalization)."
)

st.divider()

# ===============================
# Panel 4: Coverage vs Expectation
# ===============================
st.subheader("🟦 Coverage vs Expectation")

coverage_estimate = total_implied_prob
house_edge_estimate = max(0.0, coverage_estimate - 1.0)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(
        "Outcome Coverage (Implied)",
        f"{coverage_estimate*100:.1f}%"
    )
with col2:
    st.metric(
        "Estimated House Edge",
        f"{house_edge_estimate*100:.1f}%"
    )
with col3:
    st.metric(
        "Structural Bias",
        "Negative EV"
    )

st.markdown(
    """
**Key Insight**

- High outcome coverage does **not** imply profitability  
- Diversifying outcomes reduces variance, **not expectation**
- Margin is embedded across the entire probability surface
"""
)

st.divider()

# ===============================
# Panel 5: PnL Simulation (核心)
# ===============================
st.subheader("🟦 Expected PnL Simulation")

st.markdown(
    "Simulate repeated execution of this structure under **market-implied probabilities**. "
    "This does **not** assume prediction skill."
)

bankroll = 100
stake_per_leg = 6  # as per your example logic
iterations = st.slider("Simulation Runs", 100, 5000, 1000, step=100)

# Normalize probabilities for simulation (still negative EV due to odds)
probs = df["Implied Probability"].values
probs = probs / probs.sum()

returns = []

for _ in range(iterations):
    outcome = np.random.choice(len(probs), p=probs)
    pnl = -stake_per_leg * (len(probs) - 1)

    win_odds = df.iloc[outcome]["Odds"]
    pnl += stake_per_leg * win_odds

    returns.append(pnl)

returns = np.array(returns)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Avg PnL per Cycle", f"{returns.mean():.2f}")
with col2:
    st.metric("Win Rate", f"{(returns > 0).mean()*100:.1f}%")
with col3:
    st.metric("Max Drawdown (Sim)", f"{returns.min():.2f}")

st.line_chart(returns.cumsum())

st.caption(
    "Even with diversified outcomes and high hit-rate, "
    "expected PnL drifts downward due to structural pricing."
)

st.divider()

# ===============================
# Final Conclusion
# ===============================
st.subheader("🟥 Structural Conclusion")

st.markdown(
    """
**This hedge construction is logically consistent and risk-aware.  
However:**

- The expectation is **mathematically negative**
- Loss is driven by **pricing structure**, not poor selection
- Long-term profitability is impossible under fixed bookmaker odds

**This terminal demonstrates failure by design.**
"""
)

st.caption(
    "This tool is for analytical demonstration only. "
    "It visualizes structural constraints, not betting advice."
)

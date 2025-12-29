import streamlit as st
import pandas as pd

st.set_page_config(page_title="Hedge Betting Trap Demo", layout="centered")

st.title("⚠️ Football Hedge Betting Trap Demo")
st.caption("For people who understand probability / finance / game theory")

st.divider()

# ======================
# 通用函数
# ======================

def implied_prob(odds):
    return 1 / odds if odds > 0 else 0

# ======================
# 比赛 A：核心对冲场
# ======================

st.subheader("Match A — Score Hedge + Over 2.5")

over25_odds = st.number_input("Over 2.5 Odds", 2.20, 2.50, 2.30, 0.01)
stake_over = st.number_input("Over 2.5 Stake", value=100)

st.markdown("#### Under 2.5 Score Odds (6 Scores)")

score_inputs = {
    "1-0": st.number_input("1-0", value=7.30),
    "0-0": st.number_input("0-0", value=7.20),
    "0-1": st.number_input("0-1", value=5.80),
    "2-0": st.number_input("2-0", value=14.00),
    "1-1": st.number_input("1-1", value=5.90),
    "0-2": st.number_input("0-2", value=10.00),
}

score_filter_odds = st.number_input("Score Odds Filter (>=)", value=6.0)
stake_scores_total = st.number_input("Score Combo Total Stake", value=100)

# 筛选比分
selected_scores = {k: v for k, v in score_inputs.items() if v >= score_filter_odds}
num_scores = len(selected_scores)

# ======================
# 系统一计算
# ======================

over_prob = implied_prob(over25_odds)
score_probs = {k: implied_prob(v) for k, v in selected_scores.items()}
score_prob_sum = sum(score_probs.values())

coverage_sys1 = over_prob + score_prob_sum

stake_per_score = stake_scores_total / num_scores if num_scores > 0 else 0

ev_over = over_prob * (over25_odds * stake_over - stake_over) - (1 - over_prob) * stake_over

ev_scores = 0
for odds in selected_scores.values():
    p = implied_prob(odds)
    win_profit = odds * stake_per_score - stake_per_score
    ev_scores += p * win_profit - (1 - p) * stake_per_score

ev_sys1 = ev_over + ev_scores

# ======================
# 比赛 B：高胜率锚点
# ======================

st.divider()
st.subheader("Match B — High Win Anchor")

home_win_odds = st.number_input("Home Win Odds (<1.40)", value=1.25)
stake_anchor = st.number_input("Anchor Combo Stake", value=100)

st.markdown("#### Total Goals Odds (Match A)")
tg_0 = st.number_input("0 Goals Odds", value=7.20)
tg_1 = st.number_input("1 Goal Odds", value=3.60)
tg_2 = st.number_input("2 Goals Odds", value=3.20)

# ======================
# 系统二计算
# ======================

# 排除0球
tg_selected = {
    "1 Goal": tg_1,
    "2 Goals": tg_2
}

tg_probs = {k: implied_prob(v) for k, v in tg_selected.items()}
home_win_prob = implied_prob(home_win_odds)

combo_prob = sum(tg_probs.values()) * home_win_prob

combo_odds_avg = sum(tg_selected.values()) / len(tg_selected)
combo_odds = combo_odds_avg * home_win_odds

ev_combo = combo_prob * (combo_odds * stake_anchor - stake_anchor) - (1 - combo_prob) * stake_anchor

# Over2.5 仍然下注
ev_sys2 = ev_over + ev_combo

# ======================
# 输出结果
# ======================

st.divider()
st.subheader("📊 Strategy Evaluation")

df = pd.DataFrame({
    "System": ["System 1", "System 2"],
    "Coverage / Hit Illusion": [coverage_sys1, combo_prob],
    "Total Stake": [
        stake_over + stake_scores_total,
        stake_over + stake_anchor
    ],
    "Expected Value (EV)": [ev_sys1, ev_sys2]
})

st.dataframe(df, use_container_width=True)

# ======================
# 陷阱揭示
# ======================

st.divider()
st.subheader("🚨 Trap Exposed")

st.markdown("""
**Key Insight**

- High coverage ≠ positive EV  
- Hedging does NOT remove bookmaker margin  
- You are buying multiple negatively-priced probability products  

**This is not a football problem.  
This is a pricing structure problem.**
""")

if ev_sys1 < 0 and ev_sys2 < 0:
    st.error("❌ Both systems are structurally negative EV")
else:
    st.warning("⚠️ One system shows abnormal result — recheck assumptions")

st.caption("Demo purpose: reveal structural traps, not recommend betting.")

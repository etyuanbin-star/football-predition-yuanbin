import streamlit as st
import pandas as pd

# ======================
# 核心逻辑层 (Logic)
# ======================

def calculate_implied_prob(odds):
    """计算隐含概率，处理赔率为0的极端情况"""
    return 1 / odds if odds > 0 else 0

def calculate_ev(prob, odds, stake):
    """计算期望值 EV = (Win_Prob * Profit) - (Loss_Prob * Stake)"""
    if odds <= 0 or stake <= 0:
        return 0.0
    profit = (odds * stake) - stake
    return (prob * profit) - ((1 - prob) * stake)

# ======================
# 配置与样式
# ======================
st.set_page_config(page_title="Hedge Betting Trap Demo", layout="wide")

st.title("⚠️ Football Hedge Betting Trap Demo")
st.caption("Insight: Pricing structure usually favors the bookmaker regardless of hedging.")

# ======================
# 输入区域 (UI - Sidebar or Columns)
# ======================
with st.sidebar:
    st.header("⚙️ Global Parameters")
    stake_over = st.number_input("Over 2.5 Stake", value=100, step=10)
    stake_scores_total = st.number_input("Score Combo Total Stake", value=100, step=10)
    stake_anchor = st.number_input("Anchor Combo Stake", value=100, step=10)
    
st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Match A: Score Hedge + Over 2.5")
    over25_odds = st.number_input("Over 2.5 Odds", 2.0, 5.0, 2.30, 0.05)
    
    st.markdown("**Under 2.5 Score Odds (Select to Hedge)**")
    # 使用表格布局输入，更美观
    input_cols = st.columns(3)
    score_data = [("1-0", 7.30), ("0-0", 7.20), ("0-1", 5.80), ("2-0", 14.0), ("1-1", 5.90), ("0-2", 10.0)]
    
    selected_scores = {}
    for i, (score, default_val) in enumerate(score_data):
        with input_cols[i % 3]:
            val = st.number_input(score, value=default_val, key=f"score_{score}")
            selected_scores[score] = val

    score_filter_odds = st.slider("Min Odds to Include in Hedge", 1.0, 10.0, 6.0)

with col2:
    st.subheader("Match B: High Win Anchor")
    home_win_odds = st.number_input("Match B Home Win Odds (Anchor)", 1.05, 2.0, 1.25, 0.01)
    
    st.markdown("**Match A - Goal Distribution Odds**")
    tg_0 = st.number_input("0 Goals Odds", value=7.20)
    tg_1 = st.number_input("1 Goal Odds", value=3.60)
    tg_2 = st.number_input("2 Goals Odds", value=3.20)

# ======================
# 计算层 (Calculation)
# ======================

# 系统 1 计算
valid_scores = {k: v for k, v in selected_scores.items() if v >= score_filter_odds}
over_prob = calculate_implied_prob(over25_odds)
scores_prob_sum = sum(calculate_implied_prob(v) for v in valid_scores.values())

ev_over = calculate_ev(over_prob, over25_odds, stake_over)
ev_scores = 0
if valid_scores:
    s_per_score = stake_scores_total / len(valid_scores)
    for o in valid_scores.values():
        p = calculate_implied_prob(o)
        ev_scores += calculate_ev(p, o, s_per_score)

sys1_ev_total = ev_over + ev_scores
sys1_coverage = over_prob + scores_prob_sum

# 系统 2 计算 (Match A 1-2 Goals + Match B Win)
tg_selected = {"1G": tg_1, "2G": tg_2}
tg_prob_sum = sum(calculate_implied_prob(v) for v in tg_selected.values())
home_win_prob = calculate_implied_prob(home_win_odds)

# 串关赔率计算 (乘法原则)
combo_odds = (sum(tg_selected.values()) / 2) * home_win_odds 
combo_prob = tg_prob_sum * home_win_prob
ev_combo = calculate_ev(combo_prob, combo_odds, stake_anchor)

sys2_ev_total = ev_over + ev_combo

# ======================
# 结果展示层 (Results)
# ======================
st.divider()
st.subheader("📊 Strategy Evaluation")

res_df = pd.DataFrame({
    "Strategy": ["System 1 (Wide Hedge)", "System 2 (Parlay Anchor)"],
    "Hit Illusion (Prob)": [f"{sys1_coverage:.2%}", f"{combo_prob:.2%}"],
    "Total Stake ($)": [stake_over + stake_scores_total, stake_over + stake_anchor],
    "Total EV ($)": [round(sys1_ev_total, 2), round(sys2_ev_total, 2)]
})

# 突出显示 EV 列
def color_ev(val):
    color = 'red' if val < 0 else 'green'
    return f'color: {color}; font-weight: bold'

st.table(res_df.style.applymap(color_ev, subset=['Total EV ($)']))

# 增加可视化对比
st.bar_chart(res_df.set_index("Strategy")["Total EV ($)"])

# ======================
# 陷阱揭示与总结
# ======================
st.subheader("🚨 Why the House Always Wins")

with st.expander("Click to see the mathematical trap"):
    st.write("""
    1. **Margin Stacking**: Each time you add a selection to a 'hedge', you are paying the bookmaker's margin again.
    2. **Probability Illusion**: A $90\%$ coverage sounds safe, but if the combined EV is $-5\%$, you are simply losing money $5\%$ faster.
    3. **The Anchor Trap**: Match B (the 'banker') adds risk without adding relative value if its odds already reflect its true probability.
    """)

if sys1_ev_total < 0 and sys2_ev_total < 0:
    st.error(f"Financial Verdict: Both systems lead to an expected loss of approximately ${abs(min(sys1_ev_total, sys2_ev_total)):.2f} per cycle.")

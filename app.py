import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ======================
# 1. 核心计算引擎 (Logic Layer)
# ======================
class BettingEngine:
    @staticmethod
    def get_implied_prob(odds):
        return 1 / odds if odds > 0 else 0

    @staticmethod
    def calculate_ev(prob, odds, stake):
        if odds <= 0 or stake <= 0: return 0.0
        return (prob * (odds * stake - stake)) - ((1 - prob) * stake)

    @staticmethod
    def run_monte_carlo(win_prob, odds, stake, initial_bankroll=10000, rounds=500):
        """模拟长期资金曲线"""
        # 生成基于伯努利分布的随机结果 (1为赢, 0为输)
        results = np.random.choice([1, 0], size=rounds, p=[win_prob, 1 - win_prob])
        
        bankroll_history = [initial_bankroll]
        current_balance = initial_bankroll
        
        for win in results:
            if win:
                current_balance += (odds * stake - stake)
            else:
                current_balance -= stake
            bankroll_history.append(current_balance)
            
        return bankroll_history

# ======================
# 2. 页面配置与样式
# ======================
st.set_page_config(page_title="Hedge Trap Analysis", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

st.title("⚠️ Football Hedge Betting Trap Demo")
st.caption("Deep Dive into Pricing Structures and Expected Value (EV)")

# ======================
# 3. 侧边栏及全局参数
# ======================
with st.sidebar:
    st.header("💰 Investment Setup")
    init_bankroll = st.number_input("Starting Bankroll ($)", value=10000)
    sim_rounds = st.slider("Simulation Rounds", 100, 2000, 1000)
    st.divider()
    st.info("This tool demonstrates why high coverage doesn't guarantee profit due to bookmaker margins.")

# ======================
# 4. 主界面：输入区域
# ======================
col1, col2 = st.columns(2)

with col1:
    st.subheader("Match A: Score Hedge + Over 2.5")
    o25_odds = st.number_input("Over 2.5 Odds", 1.5, 5.0, 2.30)
    o25_stake = st.number_input("Over 2.5 Stake ($)", value=100)
    
    st.markdown("**Under 2.5 Scores (Hedge)**")
    # 使用简洁的列布局输入比分赔率
    sc_cols = st.columns(3)
    score_odds = {
        "1-0": sc_cols[0].number_input("1-0", value=7.3),
        "0-0": sc_cols[1].number_input("0-0", value=7.2),
        "0-1": sc_cols[2].number_input("0-1", value=5.8),
        "2-0": sc_cols[0].number_input("2-0", value=14.0),
        "1-1": sc_cols[1].number_input("1-1", value=5.9),
        "0-2": sc_cols[2].number_input("0-2", value=10.0),
    }
    score_filter = st.slider("Include Odds >= ", 1.0, 15.0, 6.0)
    score_total_stake = st.number_input("Score Total Stake ($)", value=100)

with col2:
    st.subheader("Match B: High Win Anchor")
    mB_win_odds = st.number_input("Match B Home Win Odds", 1.1, 2.0, 1.25)
    mB_stake = st.number_input("Anchor Combo Stake ($)", value=100)
    
    st.markdown("**Match A Goal Distribution (for Combo)**")
    tg0 = st.number_input("0 Goals Odds", value=7.20)
    tg1 = st.number_input("1 Goal Odds", value=3.60)
    tg2 = st.number_input("2 Goals Odds", value=3.20)

# ======================
# 5. 计算逻辑
# ======================
engine = BettingEngine()

# --- System 1 Calculations ---
active_scores = {k: v for k, v in score_odds.items() if v >= score_filter}
num_active = len(active_scores)
prob_o25 = engine.get_implied_prob(o25_odds)
prob_scores = sum(engine.get_implied_prob(v) for v in active_scores.values())

sys1_coverage = prob_o25 + prob_scores
sys1_total_stake = o25_stake + score_total_stake

ev_o25 = engine.calculate_ev(prob_o25, o25_odds, o25_stake)
ev_scores = 0
if num_active > 0:
    stake_per_s = score_total_stake / num_active
    for o in active_scores.values():
        ev_scores += engine.calculate_ev(engine.get_implied_prob(o), o, stake_per_s)
sys1_ev = ev_o25 + ev_scores

# --- System 2 Calculations ---
prob_tg = sum(engine.get_implied_prob(v) for v in [tg1, tg2])
prob_mB = engine.get_implied_prob(mB_win_odds)
combo_prob = prob_tg * prob_mB
combo_odds = ( (tg1 + tg2)/2 ) * mB_win_odds # 简化组合赔率模型

sys2_ev = ev_o25 + engine.calculate_ev(combo_prob, combo_odds, mB_stake)
sys2_total_stake = o25_stake + mB_stake

# ======================
# 6. 结果展示与模拟图表
# ======================
st.divider()
st.subheader("📊 Performance Analysis")

# 数据看板
res_col1, res_col2, res_col3 = st.columns(3)
res_col1.metric("System 1 EV", f"${sys1_ev:.2f}", delta=f"{sys1_ev/(sys1_total_stake):.2%}", delta_color="normal")
res_col2.metric("System 2 EV", f"${sys2_ev:.2f}", delta=f"{sys2_ev/(sys2_total_stake):.2%}", delta_color="normal")
res_col3.metric("Max Coverage", f"{sys1_coverage:.1%}")

# 蒙特卡洛模拟图表
st.markdown("### 📉 Projected Capital Decay (Monte Carlo)")
sim_data = engine.run_monte_carlo(sys1_coverage, 1.0, sys1_total_stake * (1 + sys1_ev/sys1_total_stake), init_bankroll, sim_rounds)

fig = go.Figure()
fig.add_trace(go.Scatter(y=sim_data, mode='lines', name='Total Balance', line=dict(color='#EF553B', width=2)))
fig.update_layout(
    hovermode="x unified",
    template="plotly_white",
    xaxis_title="Bets Placed",
    yaxis_title="Bankroll ($)",
    showlegend=False,
    margin=dict(l=20, r=20, t=40, b=20)
)
st.plotly_chart(fig, use_container_width=True)



# ======================
# 7. 陷阱教育 (The "Why")
# ======================
st.divider()
exp1 = st.expander("🔍 Why does this graph go down even with high coverage?")
exp1.write("""
1. **The Overround (Margin)**: Every odds provided by a bookmaker has a built-in fee. When you 'hedge', you aren't removing risk; you are multiplying fees.
2. **Probability vs. Price**: You might hit your bet 90% of the time, but if you are paid at odds that only represent 85% probability, you lose in the long run.
3. **Compound Negative EV**: Combining Match A and Match B (System 2) often compounds the house edge.
""")

if sys1_ev < 0:
    st.error(f"Financial Summary: System 1 has a structural loss of {abs(sys1_ev/sys1_total_stake):.2%} per bet.")

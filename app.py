import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# --- 页面配置 ---
st.set_page_config(page_title="交易风险控制实验室", layout="wide")

st.title("🛡️ 交易与投资：风险控制实验室 (教材版)")
st.subheader("核心教义：不具备数学优势的交易，不操作才是真正的‘赢’。")

# --- 1. 教学侧边栏：风险参数 ---
with st.sidebar:
    st.header("📉 市场环境模拟")
    st.info("将博彩赔率理解为交易的‘盈亏比’。")
    
    win_payout = st.number_input("潜在回报倍数 (盈亏比+1)", value=2.10, step=0.1)
    est_win_rate = st.slider("你的交易胜率预测 (%)", 5, 95, 45) / 100
    
    st.divider()
    st.subheader("💸 交易摩擦 (抽水)")
    fee_rate = st.slider("交易手续费/点差/抽水 (%)", 0.0, 15.0, 5.0) / 100

# --- 2. 逻辑引擎：期望值 (EV) 评估 ---
# 真实的赔率需要扣除摩擦成本
real_payout = win_payout * (1 - fee_rate)
ev = (est_win_rate * (real_payout - 1)) - (1 - est_win_rate)

# --- 3. 核心教材模块：资产曲线对比 ---
st.subheader("📈 策略演习：操作 vs. 不操作")

col_metric, col_chart = st.columns([1, 2])

with col_metric:
    st.write("### 诊断报告")
    if ev > 0:
        st.success(f"当前期望值: +{ev:.2f}\n这是一个具备‘统计学优势’的交易。")
        st.write("👉 **建议**：可以按照凯利公式轻仓入场。")
    else:
        st.error(f"当前期望值: {ev:.2f}\n这是一个‘负和博弈’。")
        st.write("👉 **硬核教义**：此时任何入场动作都是在消耗本金。**不操作（空仓）产生的收益是 0%，优于损失。**")

    # 凯利判据建议
    kelly_f = max(0, ev / (real_payout - 1))
    st.metric("建议单次风险仓位", f"{kelly_f:.2%}")

with col_chart:
    # 模拟 100 场
    rounds = 100
    # 操作组
    ops_results = np.random.choice([real_payout-1, -1], size=rounds, p=[est_win_rate, 1-est_win_rate])
    ops_curve = 10000 * np.cumprod(1 + ops_results * 0.05) # 假设每次押 5%
    # 不操作组
    no_ops_curve = np.full(rounds + 1, 10000)
    
    sim_df = pd.DataFrame({
        "交易场次": np.arange(rounds + 1),
        "频繁操作 (负EV)": np.insert(ops_curve, 0, 10000),
        "不操作 (空仓赢家)": no_ops_curve
    })
    
    fig = px.line(sim_df, x="交易场次", y=["频繁操作 (负EV)", "不操作 (空仓赢家)"], 
                  title="资产规模演变对比", color_discrete_map={"频繁操作 (负EV)": "#FF4B4B", "不操作 (空仓赢家)": "#00C853"})
    st.plotly_chart(fig, use_container_width=True)

# --- 4. 深度教育：投资者的三条铁律 ---
st.divider()
st.subheader("📚 风险控制教材：交易者必读")

t1, t2, t3 = st.tabs(["1. 成本陷阱", "2. 对冲的真相", "3. 胜率的谎言"])

with t1:
    st.markdown("""
    ### 摩擦成本是隐形杀手
    在博彩中这叫“抽水”，在交易中这叫“点差”和“手续费”。
    * 如果你的盈亏比不足以覆盖手续费，你的交易模型从出生那一刻起就是必败的。
    * **教材案例**：你以为你在玩 50% 胜率的游戏，但扣除 5% 抽水后，你的真实胜率需求需要达到 53% 才能保本。
    """)

with t2:
    st.markdown("""
    ### 过度对冲 = 慢性自杀
    很多交易者喜欢在亏损时做对冲单。
    * **真相**：对冲本质上是在锁定亏损的同时，支付两份手续费。
    * 在我们的足球模型中，买入大球的同时买入所有小球比分，就是一种**代价极其昂贵的对冲**，它让你的期望值降到了最低。
    """)

with t3:
    st.markdown("""
    ### 频率越高，优势越薄
    * 庄家（市场）最喜欢高频交易者。
    * 真正的赢家（如巴菲特）会放弃 99% 的平庸机会，只在不可能三角最稳固时出手。
    * **记住**：你不需要参与每一场波动，正如你不需要下注每一场球赛。
    """)

# --- 5. 交互式风险警示 ---
if st.button("🔴 点击获取终极警示"):
    st.warning("⚠️ **投资警示**：在所有负期望值的系统中，唯一的获胜策略就是‘离场’。这个工具不是为了教你如何下注，而是为了让你看清风险，学会在没有优势时保护你的本金。")

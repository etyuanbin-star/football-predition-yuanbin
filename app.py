import streamlit as st
import pandas as pd
import numpy as np

# --- 页面配置 ---
st.set_page_config(page_title="胜算实验室：期望值之镜", layout="wide")

# --- 核心样式与前言 ---
st.title("🔺 胜算实验室：期望值之镜 (EV Mirror)")
st.subheader("—— 交易与投资风险控制教育工具")

with st.expander("📖 点击阅读：致博弈者的风险教义", expanded=True):
    st.markdown("""
    **核心教义：**
    1. **不操作即获利**：在负期望值（Negative EV）环境下，空仓是唯一盈利的策略。
    2. **对冲陷阱**：试图通过增加投注项来“消灭”风险，本质上是在加速支付手续费（抽水）。
    3. **信息稀释**：当一个机会被大众熟知（过热），其赔率已不再匹配其真实的发生概率。
    4. **不可能三角**：你无法在同一场博弈中同时占有：高胜率、高赔率、高频率。
    """)

# --- 1. 侧边栏：市场环境与经验过滤 ---
with st.sidebar:
    st.header("⚖️ 庄家定价 (市场环境)")
    o25_odds = st.number_input("大球 (Over 2.5) 赔率", value=2.45, min_value=1.01, step=0.01)
    
    st.divider()
    st.subheader("🛡️ 经验过滤器 (逻辑筛选)")
    exclude_zero = st.checkbox("排除 0-0 (历史规律：近期交锋活跃)", value=False)
    exclude_extreme = st.checkbox("排除偏门比分 (规律排除：实力悬殊)", value=False)
    
    heat_level = st.select_slider(
        "当前信息热度 (价值稀释度)",
        options=["极低", "偏低", "平衡", "过热", "狂热"],
        value="过热"
    )
    
    st.divider()
    st.subheader("🧠 你的核心判断")
    pred_prob = st.slider("你预测的大球真实胜率 (%)", 10, 90, 45) / 100

# --- 2. 逻辑计算引擎 ---
score_list = ["0-0", "1-0", "0-1", "1-1", "2-0", "0-2"]
default_odds = {"0-0": 10.0, "1-0": 8.5, "0-1": 8.0, "1-1": 7.0, "2-0": 13.0, "0-2": 12.0}

# 2.1 抽水率分析
all_probs = [1/o25_odds] + [1/v for v in default_odds.values()]
overround = (sum(all_probs) - 1) * 100

# 2.2 价值稀释逻辑
heat_impact = {"极低": 1.05, "偏低": 1.02, "平衡": 1.0, "过热": 0.95, "狂热": 0.85}
adjusted_ev_odds = o25_odds * heat_impact[heat_level]
ev = (pred_prob * (adjusted_ev_odds - 1)) - (1 - pred_prob)

# --- 3. 教学面板：不可能三角监测 ---
col_tri, col_val = st.columns([1, 1])

with col_tri:
    st.write("### 🔺 不可能三角状态")
    # 胜率 * 赔率 指数
    tri_index = pred_prob * o25_odds
    if tri_index > 1.05:
        st.error(f"指数 {tri_index:.2f}：【数学幻觉】\n高概率+高赔率在现实中极少共存。")
    elif tri_index > 0.95:
        st.warning(f"指数 {tri_index:.2f}：【价值边缘】\n勉强存在博弈空间，但容错率极低。")
    else:
        st.success(f"指数 {tri_index:.2f}：【庄家收割区】\n这是最稳健的亏损模型。")

with col_val:
    st.write("### 💰 期望值 (EV) 诊断")
    if ev > 0:
        st.metric("预期收益率", f"+{ev:.2%}", "具备入场价值")
        kelly = max(0, ev / (adjusted_ev_odds - 1))
        st.write(f"建议单次风险仓位: **{kelly:.2%}**")
    else:
        st.metric("预期收益率", f"{ev:.2%}", "建议空仓 (不操作)", delta_color="inverse")
        st.error("结论：不操作才是真正的‘赢’。")

# --- 4. 自由沙盘：对冲陷阱演示 ---
st.divider()
st.subheader("🕹️ 策略沙盘：自由对冲与盲区监测")
c1, c2 = st.columns([1, 2], gap="large")

active_bets = []
with c1:
    st.write("**配置你的下注组合：**")
    if st.toggle("投注：全场大球", value=True):
        amt = st.number_input("金额 ($)", value=100, key="o25_main")
        active_bets.append({"name": "大球项", "odds": o25_odds, "stake": amt, "is_over": True})
    
    st.write("---")
    st.write("**选择对冲比分：**")
    for s in score_list:
        # 历史规律自动排除逻辑
        disabled = (s == "0-0" and exclude_zero) or (s in ["2-0", "0-2"] and exclude_extreme)
        label = f"{s} {'(规律建议排除)' if disabled else ''}"
        
        col_cb, col_am = st.columns([1, 1])
        with col_cb:
            is_bet = st.checkbox(label, key=f"cb_{s}", value=False if disabled else False)
        with col_am:
            amt = st.number_input("金额", value=20, key=f"am_{s}", label_visibility="collapsed") if is_bet else 0
        
        if is_bet:
            active_bets.append({"name": s, "odds": default_odds[s], "stake": amt, "is_over": False})

    total_stake = sum(b['stake'] for b in active_bets)
    st.metric("🛡️ 总投入成本", f"${total_stake}")

with c2:
    # 计算盈亏数据
    outcomes = score_list + ["3球及以上(大球)"]
    res_data = []
    for out in outcomes:
        income = 0
        is_o = (out == "3球及以上(大球)")
        for b in active_bets:
            if (b['is_over'] and is_o) or (b['name'] == out):
                income += b['stake'] * b['odds']
        res_data.append({"结果": out, "净盈亏": income - total_stake})
    
    df_res = pd.DataFrame(res_data)
    
    # 原生图表展示
    st.write("**不同赛果下的利润/亏损分布：**")
    st.bar_chart(df_res.set_index("结果")["净盈亏"])
    
    # 盲区预警
    holes = df_res[df_res['净盈亏'] < 0]
    if total_stake > 0:
        if holes.empty:
            st.success("✨ 理论全覆盖：你实现了数学对冲（请检查利润是否微薄到无法抵御波动）。")
        else:
            st.warning(f"🚨 盲区预警：如果结果是 {', '.join(holes['结果'].tolist())}，你将产生亏损。")

# --- 5. 交易者教材：资产曲线模拟 ---
st.divider()
st.subheader("📉 风险教育：频繁对冲 vs. 守拙空仓")
rounds = 50
ops_curve = [10000]
no_ops_curve = [10000]

# 模拟50次交易结果
for _ in range(rounds):
    # 模拟真实市场波动 (基于EV)
    change = np.random.choice([ev, -0.1]) # 简化模型
    ops_curve.append(ops_curve[-1] * (1 + change))
    no_ops_curve.append(10000)

chart_df = pd.DataFrame({
    "尝试场次": np.arange(rounds + 1),
    "频繁操作/过度对冲": ops_curve,
    "不操作 (空仓赢家)": no_ops_curve
})
st.line_chart(chart_df.set_index("尝试场次"))
st.caption("注：在负 EV 系统中，那根绿色的直线（不操作）就是战胜 90% 玩家的终极神技。")

# --- 6. 结语 ---
st.markdown("---")
st.center_text = st.markdown("<h3 style='text-align: center; color: gray;'>在这个实验室里，你输得越多，在现实中就赢回了越多。</h3>", unsafe_allow_html=True)

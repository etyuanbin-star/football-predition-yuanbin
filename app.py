import streamlit as st
import pandas as pd
import numpy as np

# --- 页面配置 ---
st.set_page_config(page_title="胜算实验室：期望值之镜", layout="wide")

# --- 标题与前言 ---
st.title("🔺 胜算实验室：期望值之镜 (EV Mirror)")
st.subheader("—— 交易风险控制与博弈心理教育工具")

with st.expander("📖 必读：风险控制的核心教义", expanded=True):
    st.markdown("""
    **核心原则：**
    1. **不操作也是一种仓位**：在负期望值（Negative EV）环境下，离场观望是唯一获利的策略。
    2. **对冲陷阱**：试图通过覆盖所有结果来“消除”风险，本质上是加速向庄家支付手续费。
    3. **价值稀释**：当一个机会由于热度过高而变得“众所周知”，其赔率通常已无法覆盖其真实风险。
    4. **不可能三角**：你无法在同一场交易中同时获得：**高胜率、高赔率、高频率**。
    """)

# --- 1. 侧边栏：市场环境与过滤器 ---
with st.sidebar:
    st.header("⚖️ 市场环境 (庄家定价)")
    o25_odds = st.number_input("全场大球 (Over 2.5) 实时赔率", value=2.45, min_value=1.01, step=0.01)
    
    st.divider()
    st.subheader("🛡️ 经验过滤器 (逻辑降噪)")
    exclude_zero = st.checkbox("排除 0-0 (近期交锋无白卷)", value=False)
    exclude_extreme = st.checkbox("排除偏门比分 (实力悬殊)", value=False)
    
    heat_level = st.select_slider(
        "当前市场热度 (价值稀释度)",
        options=["极低", "偏低", "平衡", "过热", "狂热"],
        value="过热"
    )
    
    st.divider()
    st.subheader("🧠 你的主观判断")
    pred_prob = st.slider("你预测的大球真实概率 (%)", 10, 90, 45) / 100

# --- 2. 逻辑引擎：期望值计算 ---
# 默认赔率参考值（仅作为初始显示）
default_odds_map = {"0-0": 10.0, "1-0": 8.5, "0-1": 8.0, "1-1": 7.0, "2-0": 13.0, "0-2": 12.0}

heat_impact = {"极低": 1.05, "偏低": 1.02, "平衡": 1.0, "过热": 0.95, "狂热": 0.85}
adjusted_odds = o25_odds * heat_impact[heat_level]
ev = (pred_prob * (adjusted_odds - 1)) - (1 - pred_prob)

# --- 3. 诊断面板 ---
col_tri, col_val = st.columns([1, 1])

with col_tri:
    st.write("### 🔺 不可能三角监测")
    tri_index = pred_prob * o25_odds
    if tri_index > 1.05:
        st.error(f"指数 {tri_index:.2f}：【数学幻觉】\n此概率配此赔率在现实中极少共存。")
    elif tri_index > 0.95:
        st.warning(f"指数 {tri_index:.2f}：【专业博弈区】\n存在微弱数学优势。")
    else:
        st.success(f"指数 {tri_index:.2f}：【庄家收割区】\n长期操作必输。")

with col_val:
    st.write("### 💰 期望值 (EV) 诊断")
    if ev > 0:
        st.metric("预期收益率", f"+{ev:.2%}", "发现入场优势")
        kelly = max(0, ev / (adjusted_odds - 1))
        st.write(f"建议最大仓位: **{kelly:.2%}**")
    else:
        st.metric("预期收益率", f"{ev:.2%}", "无优势 - 建议空仓", delta_color="inverse")
        st.error("结论：不操作才是真正的‘赢’。")

# --- 4. 策略沙盘：支持自定义赔率输入 ---
st.divider()
st.subheader("🕹️ 策略沙盘：自定义对冲与盲区分析")
c1, c2 = st.columns([1, 2], gap="large")

active_bets = []
score_list = ["0-0", "1-0", "0-1", "1-1", "2-0", "0-2"]

with c1:
    st.write("**1. 核心仓位设置：**")
    if st.toggle("投入：全场大球", value=True):
        amt = st.number_input("大球投入金额 ($)", value=100, key="o25_main")
        active_bets.append({"name": "大球", "odds": o25_odds, "stake": amt, "is_over": True})
    
    st.write("---")
    st.write("**2. 比分对冲设置 (可调赔率)：**")
    
    # 表头说明
    head_c1, head_c2, head_c3 = st.columns([1, 1.2, 1.2])
    head_c2.caption("输入金额 ($)")
    head_c3.caption("实时赔率")

    for s in score_list:
        disabled = (s == "0-0" and exclude_zero) or (s in ["2-0", "0-2"] and exclude_extreme)
        
        col_cb, col_am, col_od = st.columns([1, 1.2, 1.2])
        
        with col_cb:
            is_bet = st.checkbox(s, key=f"cb_{s}", disabled=disabled)
        
        with col_am:
            # 只有勾选后才允许输入金额
            stake = st.number_input("金额", value=20.0, step=1.0, key=f"am_{s}", label_visibility="collapsed") if is_bet else 0.0
        
        with col_od:
            # 只有勾选后才允许输入该场次的特定赔率
            current_odds = st.number_input("赔率", value=default_odds_map[s], step=0.1, key=f"od_{s}", label_visibility="collapsed") if is_bet else 0.0
        
        if is_bet:
            active_bets.append({"name": s, "odds": current_odds, "stake": stake, "is_over": False})

    total_stake = sum(b['stake'] for b in active_bets)
    st.metric("🛡️ 当前总投入本金", f"${total_stake:.2f}")

with c2:
    over_label = "大球 (3球+)"
    outcomes = score_list + [over_label]
    res_data = []
    
    for out in outcomes:
        income = 0
        is_o = (out == over_label)
        for b in active_bets:
            # 如果赛果匹配或者是大球项赢了
            if (b['is_over'] and is_o) or (b['name'] == out):
                income += b['stake'] * b['odds']
        res_data.append({"赛果": out, "净盈亏": income - total_stake})
    
    df_res = pd.DataFrame(res_data)
    st.write("**多维度盈亏分布图 (PnL Chart)：**")
    st.bar_chart(df_res.set_index("赛果")["净盈亏"])
    
    # 盲区预警逻辑
    holes = df_res[df_res['净盈亏'] < 0]
    if total_stake > 0:
        if holes.empty:
            st.success("✨ 理论全覆盖：你通过自定义赔率计算实现了全面对冲。")
        else:
            hole_str = ", ".join(holes['赛果'].tolist())
            st.warning(f"🚨 盲区警报：若赛果为 {hole_str}，你将产生亏损。")

# --- 5. 教育模块：资产曲线 ---
st.divider()
st.subheader("📉 资产演变模拟：频繁操作 vs. 观望")
rounds = 50
ops_curve = [10000.0]
no_ops_curve = [10000.0]

for _ in range(rounds):
    risk = 0.05
    win = np.random.random() < pred_prob
    outcome = risk * (adjusted_odds - 1) if win else -risk
    ops_curve.append(ops_curve[-1] * (1 + outcome))
    no_ops_curve.append(10000.0)

chart_df = pd.DataFrame({"场次": np.arange(rounds + 1), "频繁操作": ops_curve, "空仓观望": no_ops_curve})
st.line_chart(chart_df.set_index("场次"))

# --- 6. 页脚 ---
st.markdown("---")
st.markdown("<h3 style='text-align: center; color: gray;'>在这个实验室里输得越多，现实中就赢回越多。</h3>", unsafe_allow_html=True)

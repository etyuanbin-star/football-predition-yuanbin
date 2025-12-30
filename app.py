import streamlit as st
import pandas as pd
import numpy as np

# --- 页面配置 ---
st.set_page_config(page_title="胜算实验室：期望值之镜", layout="wide")

# --- 1. 顶部：品牌与核心教义 ---
st.title("🔺 胜算实验室：期望值之镜 (EV Mirror)")
st.subheader("—— 足球博弈逻辑与风险控制实验室")

# 嵌入你提到的“最高先觉概率”逻辑说明
with st.expander("🔬 为什么选择 [大球 + 3组比分] 的组合？（逻辑白皮书）", expanded=True):
    st.markdown("""
    在足球投注领域，这种策略被认为是**‘先觉概率’最高**的模型之一，原因在于它完美处理了物理空间的‘点’与‘面’：
    
    * **空间的极致拆解**：足球进球总数只有“大”和“小”两个世界。大球（Over 2.5）一单就覆盖了所有 3 球及以上的**无限可能性**。
    * **高概率盲区的精准打击**：小球世界（Under 2.5）其实只有 6 种精确比分。通过选择其中最可能的 3 组，你实际上用极小的‘保险费’锁定了小球世界里 **70%-80%** 的发生概率。
    * **赔率杠杆效应**：大球是主攻（面），比分是对冲（点）。比分的高赔率（通常 8x-12x）允许你用总本金的 **15%-20%** 就能在进球荒时收回全部本金。
    
    **结论：** 这种组合是在‘全覆盖’与‘高盈亏比’之间能找到的最优平衡点。
    """)

# --- 2. 侧边栏：参数输入 ---
with st.sidebar:
    st.header("⚖️ 实时盘口输入")
    o25_odds = st.number_input("全场大球 (Over 2.5) 赔率", value=2.45, min_value=1.01, step=0.01)
    
    st.divider()
    st.subheader("🛡️ 逻辑过滤器")
    exclude_zero = st.checkbox("排除 0-0 (近期进攻欲望强)", value=False)
    exclude_extreme = st.checkbox("排除 2-0/0-2 (实力均衡)", value=False)
    
    heat_level = st.select_slider(
        "市场热度 (热度越高，赔率越虚)",
        options=["极低", "偏低", "平衡", "过热", "狂热"],
        value="平衡"
    )
    
    st.divider()
    st.subheader("🧠 胜算预测")
    pred_prob = st.slider("你预测的大球真实胜率 (%)", 10, 90, 45) / 100

# --- 3. 逻辑引擎 ---
heat_impact = {"极低": 1.05, "偏低": 1.02, "平衡": 1.0, "过热": 0.95, "狂热": 0.85}
adjusted_odds = o25_odds * heat_impact[heat_level]
ev = (pred_prob * (adjusted_odds - 1)) - (1 - pred_prob)

# --- 4. 诊断面板 ---
col_tri, col_val = st.columns([1, 1])
with col_tri:
    st.write("### 🔺 不可能三角监测")
    tri_index = pred_prob * o25_odds
    if tri_index > 1.05:
        st.error(f"指数 {tri_index:.2f}：【数学幻觉】\n小心！此赔率与胜率组合在现实中几乎不存在。")
    elif tri_index > 0.95:
        st.warning(f"指数 {tri_index:.2f}：【专业博弈区】\n具备微弱优势，适合作为教材案例。")
    else:
        st.success(f"指数 {tri_index:.2f}：【庄家抽水区】\n长期操作本金将温水煮青蛙。")

with col_val:
    st.write("### 💰 期望值 (EV) 诊断")
    if ev > 0:
        st.metric("预期收益率", f"+{ev:.2%}", "具备入场价值")
    else:
        st.metric("预期收益率", f"{ev:.2%}", "无优势 - 不玩才是赢", delta_color="inverse")

# --- 5. 策略沙盘：支持自定义赔率 ---
st.divider()
st.subheader("🕹️ 策略沙盘：自定义对冲与盲区分析")
c1, c2 = st.columns([1, 2], gap="large")

active_bets = []
score_list = ["0-0", "1-0", "0-1", "1-1", "2-0", "0-2"]
default_odds_map = {"0-0": 10.0, "1-0": 8.5, "0-1": 8.0, "1-1": 7.0, "2-0": 13.0, "0-2": 12.0}

with c1:
    st.write("**配置仓位与实时赔率：**")
    if st.toggle("核心腿：全场大球", value=True):
        amt = st.number_input("大球金额 ($)", value=100.0, key="o25_main")
        active_bets.append({"name": "大球", "odds": o25_odds, "stake": amt, "is_over": True})
    
    st.write("---")
    # 表头说明
    hc1, hc2, hc3 = st.columns([1, 1.2, 1.2])
    hc2.caption("投入金额")
    hc3.caption("实时赔率")

    for s in score_list:
        # 自动过滤逻辑
        is_disabled = (s == "0-0" and exclude_zero) or (s in ["2-0", "0-2"] and exclude_extreme)
        
        col_cb, col_am, col_od = st.columns([1, 1.2, 1.2])
        with col_cb:
            is_bet = st.checkbox(s, key=f"cb_{s}", disabled=is_disabled)
        with col_am:
            stake = st.number_input("金额", value=20.0, step=1.0, key=f"am_{s}", label_visibility="collapsed") if is_bet else 0.0
        with col_od:
            odds = st.number_input("赔率", value=default_odds_map[s], step=0.1, key=f"od_{s}", label_visibility="collapsed") if is_bet else 0.0
        
        if is_bet:
            active_bets.append({"name": s, "odds": odds, "stake": stake, "is_over": False})

    total_stake = sum(b['stake'] for b in active_bets)
    st.metric("🛡️ 总投入本金", f"${total_stake:.2f}")

with c2:
    over_label = "大球 (3球+)"
    outcomes = score_list + [over_label]
    res_data = []
    for out in outcomes:
        income = 0
        is_o = (out == over_label)
        for b in active_bets:
            if (b['is_over'] and is_o) or (b['name'] == out):
                income += b['stake'] * b['odds']
        res_data.append({"赛果": out, "净盈亏": income - total_stake})
    
    df_res = pd.DataFrame(res_data)
    st.bar_chart(df_res.set_index("赛果")["净盈亏"])
    
    holes = df_res[df_res['净盈亏'] < 0]
    if total_stake > 0:
        if holes.empty:
            st.success("✨ 完美对冲：当前组合已覆盖所有核心物理概率。")
        else:
            lost_str = ", ".join(holes['赛果'].tolist())
            st.warning(f"🚨 风险盲区：若赛果为 {lost_str}，你将产生亏损。")

# --- 6. 资产曲线 ---
st.divider()
st.subheader("📉 风险教育：资产长期演变模拟")
rounds = 50
ops_curve = [10000.0]
no_ops_curve = [10000.0]

for _ in range(rounds):
    risk = 0.05
    win = np.random.random() < pred_prob
    outcome = risk * (adjusted_odds - 1) if win else -risk
    ops_curve.append(ops_curve[-1] * (1 + outcome))
    no_ops_curve.append(10000.0)

chart_df = pd.DataFrame({"场次": np.arange(rounds + 1), "频繁操作 (负EV)": ops_curve, "空仓观望": no_ops_curve})
st.line_chart(chart_df.set_index("场次"))
st.caption("在所有负期望值博弈中，绿色的直线（不做任何交易）就是通往赢家的终极捷径。")

# --- 7. 页脚 ---
st.markdown("---")
st.markdown("<h3 style='text-align: center; color: gray;'>这个实验室不教你如何赢钱，它教你如何在没有优势时保护本金。</h3>", unsafe_allow_html=True)

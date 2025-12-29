import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="足球投注模拟沙盘", layout="wide")

st.title("🎲 足球投注策略：自由模拟沙盘")
st.markdown("在这个实验室里，你可以**自由组合**投注项。拖动滑块或勾选选项，右侧图表会实时告诉你这是“赚钱方案”还是“爆仓陷阱”。")

# --- 1. 庄家赔率设置 (侧边栏) ---
with st.sidebar:
    st.header("⚖️ 市场环境(赔率)")
    o25_odds = st.number_input("全场大球 (Over 2.5) 赔率", value=2.25, step=0.05)
    st.divider()
    st.subheader("比分赔率 (Under 2.5)")
    score_list = ["0-0", "1-0", "0-1", "1-1", "2-0", "0-2"]
    default_odds = [10.0, 8.0, 7.5, 6.5, 12.0, 11.0]
    scores_config = {s: st.number_input(f"{s} 赔率", value=d) for s, d in zip(score_list, default_odds)}

# --- 2. 自由投注操作区 ---
col_input, col_viz = st.columns([1, 1], gap="large")
active_bets = []

with col_input:
    st.subheader("🕹️ 自由配置你的投注单")
    
    # 大球投注
    with st.container(border=True):
        c1, c2 = st.columns([1, 2])
        if c1.toggle("投注：全场大球", value=True):
            amt = c2.slider("大球投入金额 ($)", 0, 1000, 100)
            if amt > 0:
                active_bets.append({"name": "大球结果", "odds": o25_odds, "stake": amt, "is_over": True})

    # 比分投注矩阵
    st.write("**具体比分对冲方案：**")
    grid = st.columns(2)
    for i, s in enumerate(score_list):
        with grid[i % 2]:
            with st.container(border=True):
                if st.checkbox(f"投注 {s}", key=f"cb_{s}"):
                    amt = st.number_input(f"金额", value=50, step=10, key=f"amt_{s}")
                    active_bets.append({"name": s, "odds": scores_config[s], "stake": amt, "is_over": False})

    total_stake = sum(b['stake'] for b in active_bets)
    st.metric("总计投入本金", f"${total_stake}")

# --- 3. 实时盈亏逻辑 ---
outcomes = score_list + ["大球(3球+)"]
results = []

for out in outcomes:
    income = 0
    is_out_over = (out == "大球(3球+)")
    for bet in active_bets:
        if (bet['is_over'] and is_out_over) or (bet['name'] == out):
            income += bet['stake'] * bet['odds']
    results.append({"赛果": out, "净盈亏": income - total_stake})

df = pd.DataFrame(results)

# --- 4. 视觉反馈 ---
with col_viz:
    st.subheader("📊 实时盈亏反馈")
    if total_stake > 0:
        # 使用 Plotly 制作精美条形图
        fig = px.bar(df, x="赛果", y="净盈亏", color="净盈亏",
                     color_continuous_scale=["#FF4B4B", "#00C853"],
                     text_auto='.2f')
        fig.add_hline(y=0, line_dash="dash", line_color="black")
        st.plotly_chart(fig, use_container_width=True)
        
        # 风险报告
        loss_cases = df[df['净盈亏'] < 0]
        if loss_cases.empty:
            st.success("✅ 这是一个完美对冲！无论结果如何你都盈利。")
        else:
            st.warning(f"⚠️ 警告：当前有 {len(loss_cases)} 种结果会导致亏损。")
            st.table(df.set_index("赛果"))
    else:
        st.info("请在左侧开始你的投注组合。")

# --- 5. 压力测试 ---
st.divider()
if total_stake > 0:
    st.subheader("🌊 连续投注 100 场模拟")
    sim = 10000 + np.cumsum(np.random.choice(df['净盈亏'], size=100))
    st.line_chart(bankroll := sim)
    st.caption("注：模拟展示了在包含庄家抽水的负 EV 情况下，资金的衰减过程。")

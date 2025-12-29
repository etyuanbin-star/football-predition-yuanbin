import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# --- 页面样式优化 ---
st.set_page_config(page_title="足球策略实验场", layout="wide")

st.title("🕹️ 足球投注策略：沙盘实验室")
st.markdown("这里没有固定的方案。你可以随意**排列组合**，看看数学逻辑如何拆解你的对冲策略。")

# --- 1. 环境设定（侧边栏） ---
with st.sidebar:
    st.header("📊 庄家赔率环境")
    st.caption("调整这里的赔率，模拟不同博彩公司的抽水情况")
    o25_odds = st.number_input("全场大球 (Over 2.5) 赔率", value=2.25, step=0.05)
    
    st.divider()
    st.subheader("比分赔率设定")
    score_list = ["0-0", "1-0", "0-1", "1-1", "2-0", "0-2"]
    default_odds = [10.0, 8.0, 7.5, 6.5, 12.0, 11.0]
    scores_config = {}
    for score, d_odds in zip(score_list, default_odds):
        scores_config[score] = st.number_input(f"{score} 赔率", value=d_odds, step=0.1)

# --- 2. 核心操作区 ---
col_input, col_viz = st.columns([2, 3], gap="large")

active_bets = []

with col_input:
    st.subheader("📝 你的投注单")
    st.write("勾选并输入你想在每个选项上投入的金额：")
    
    # 大球投注卡片
    with st.container(border=True):
        c1, c2 = st.columns([1, 1])
        is_o25 = c1.toggle("投注：全场大球", value=True)
        o25_stake = c2.number_input("投入 ($)", value=100, step=10, key="o25_s") if is_o25 else 0
        if is_o25: active_bets.append({"name": "大球结果", "odds": o25_odds, "stake": o25_stake, "is_over": True})

    # 比分投注矩阵
    st.write("投注：具体小球比分")
    score_grid = st.columns(2)
    for i, score in enumerate(score_list):
        with score_grid[i % 2]:
            with st.container(border=True):
                is_bet = st.checkbox(f"投 {score}", key=f"bet_{score}")
                s_stake = st.number_input(f"金额", value=50, step=10, key=f"s_{score}") if is_bet else 0
                if is_bet: 
                    active_bets.append({"name": score, "odds": scores_config[score], "stake": s_stake, "is_over": False})

    total_cost = sum(b['stake'] for b in active_bets)
    st.metric("总计投入金额", f"${total_cost}")

# --- 3. 实时分析计算 ---
# 模拟可能的赛果
possible_outcomes = score_list + ["大球(3球及以上)"]
analysis_data = []

for outcome in possible_outcomes:
    income = 0
    is_outcome_over = (outcome == "大球(3球及以上)")
    
    for bet in active_bets:
        if bet['is_over'] and is_outcome_over:
            income += bet['stake'] * bet['odds']
        elif bet['name'] == outcome:
            income += bet['stake'] * bet['odds']
            
    net_profit = income - total_cost
    analysis_data.append({"赛果": outcome, "净盈亏": net_profit})

df_analysis = pd.DataFrame(analysis_data)

# --- 4. 视觉反馈中心 ---
with col_viz:
    st.subheader("📊 策略实时盈亏预测")
    
    # 盈利图表
    fig = px.bar(
        df_analysis, 
        x="赛果", 
        y="净盈亏", 
        color="净盈亏",
        color_continuous_scale=["#FF4B4B", "#00C853"], # 亏损红，盈利绿
        text_auto='.2f'
    )
    fig.add_hline(y=0, line_dash="dash", line_color="black", line_width=2)
    fig.update_layout(height=450, margin=dict(t=20))
    st.plotly_chart(fig, use_container_width=True)
    

    # 漏洞提醒系统
    holes = df_analysis[df_analysis['净盈亏'] <= -total_cost]
    if not holes.empty and total_cost > 0:
        st.error(f"🚨 **存在盲区：** 如果比赛结果是 **{', '.join(holes['赛果'].tolist())}**，你将损失全部投入。")
    elif total_cost > 0:
        avg_ev = df_analysis['净盈亏'].mean()
        if avg_ev < 0:
            st.warning(f"📉 **庄家陷阱：** 虽然你覆盖了所有结果，但平均每场仍会亏损 **${abs(avg_ev):.2f}**。")
        else:
            st.success("💎 **理论盈利：** 当前配置在数学上有正收益（通常在真实赔率下很难实现）。")

# --- 5. 压力测试（可玩性增强） ---
st.divider()
if total_cost > 0:
    st.subheader("🌊 连续投注模拟")
    st.write("假设按照你现在的配置，连续玩 100 场（随机生成真实赛果）：")
    
    # 基于结果分布的简单模拟
    sim_results = np.random.choice(df_analysis['净盈亏'], size=100)
    bankroll = 10000 + np.cumsum(sim_results)
    
    st.line_chart(bankroll)
    st.caption("注：起始资金为 $10,000。此图展示了‘高覆盖率’策略下，本金在抽水环境中的消耗过程。")

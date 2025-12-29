import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# --- 页面配置 ---
st.set_page_config(page_title="博彩决策沙盘", layout="wide")

st.title("🎮 足球策略自由沙盘")
st.markdown("这里没有标准答案。请自由组合你的投注，看看在数学逻辑下，你的策略能否离场获利。")

# --- 1. 环境设定（侧边栏） ---
with st.sidebar:
    st.header("🎲 庄家赔率设置")
    st.caption("设置市场真实的赔率环境")
    o25_odds = st.number_input("全场大球 (Over 2.5) 赔率", value=2.25, step=0.05)
    
    st.divider()
    st.subheader("比分赔率 (Under 2.5)")
    # 预设常见比分
    score_list = ["0-0", "1-0", "0-1", "1-1", "2-0", "0-2"]
    default_odds = [10.0, 8.0, 7.5, 6.5, 12.0, 11.0]
    scores_config = {}
    for score, d_odds in zip(score_list, default_odds):
        scores_config[score] = st.number_input(f"{score} 赔率", value=d_odds, step=0.1)

# --- 2. 玩家投注操作区 ---
st.subheader("🕹️ 自由投注面板")

col_input, col_viz = st.columns([1, 1], gap="large")

with col_input:
    st.write("**选择你的投注单：**")
    active_bets = []
    
    # 大球选项卡片化
    with st.container(border=True):
        c1, c2 = st.columns([1, 2])
        is_o25 = c1.toggle("投注大球", value=True)
        o25_stake = c2.number_input("投入金额 ($)", value=100, step=10, key="o25_s") if is_o25 else 0
        if is_o25: active_bets.append({"name": "大球(3+)", "odds": o25_odds, "stake": o25_stake, "is_over": True})

    # 比分选项
    st.write("**具体比分组合：**")
    score_grid = st.columns(2)
    for i, score in enumerate(score_list):
        with score_grid[i % 2]:
            with st.container(border=True):
                is_bet = st.checkbox(f"投注 {score}", key=f"bet_{score}")
                s_stake = st.number_input(f"金额", value=50, step=10, key=f"s_{score}") if is_bet else 0
                if is_bet: active_bets.append({"name": score, "odds": scores_config[score], "stake": s_stake, "is_over": False})

    total_cost = sum(b['stake'] for b in active_bets)
    st.metric("总成本 (Total Stake)", f"${total_cost}")

# --- 3. 实时盈亏模拟计算 ---
# 模拟所有可能的赛果
possible_outcomes = score_list + ["大球结果(2-1, 1-2, 3-0等)"]
analysis_data = []

for outcome in possible_outcomes:
    income = 0
    is_outcome_over = (outcome == "大球结果(2-1, 1-2, 3-0等)")
    
    for bet in active_bets:
        if bet['is_over'] and is_outcome_over:
            income += bet['stake'] * bet['odds']
        elif bet['name'] == outcome:
            income += bet['stake'] * bet['odds']
            
    net_profit = income - total_cost
    analysis_data.append({"赛果": outcome, "净盈亏": net_profit})

df_analysis = pd.DataFrame(analysis_data)

# --- 4. 可视化反馈 ---
with col_viz:
    st.write("### 📊 盈亏实时分析")
    
    # 绘制直观的条形图
    fig = px.bar(
        df_analysis, 
        x="赛果", 
        y="净盈亏", 
        color="净盈亏",
        color_continuous_scale=["#FF4B4B", "#00C853"], # 负值红，正值绿
        text_auto='.2f'
    )
    
    # 增加零位基准线
    fig.add_hline(y=0, line_dash="dash", line_color="black", line_width=2)
    fig.update_layout(showlegend=False, height=450)
    
    st.plotly_chart(fig, use_container_width=True)
    

    # 策略漏洞提醒
    holes = df_analysis[df_analysis['净盈亏'] <= -total_cost]
    if not holes.empty and total_cost > 0:
        st.error(f"⚠️ 策略盲区：如果踢出 {', '.join(holes['赛果'].tolist())}，你将损失全部本金！")
    elif total_cost > 0:
        avg_return = df_analysis['净盈亏'].mean()
        if avg_return < 0:
            st.warning(f"📉 结构性陷阱：虽然你覆盖了所有结果，但平均每场依然亏损 ${abs(avg_return):.2f}")
        else:
            st.success("💎 发现套利机会？（通常现实中庄家赔率不会允许这种情况）")

# --- 5. 沉浸式模拟 ---
st.divider()
if total_cost > 0:
    st.subheader("🌊 压力测试：连续投注 100 场的结果")
    # 简单模拟 100 场结果
    sim_results = np.random.choice(df_analysis['净盈亏'], size=100)
    bankroll = 1000 + np.cumsum(sim_results)
    
    st.line_chart(bankroll)
    st.caption("注：此模拟假设每种结果发生的概率与赔率反相关（即含庄家抽水的真实环境）。")

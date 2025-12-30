import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# 页面配置
st.set_page_config(
    page_title="胜算实验室：足球投注风控系统",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 自定义CSS样式 ---
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1.5rem;
        background: linear-gradient(90deg, #1e3c72, #2a5298);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .strategy-box {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .positive { color: #28a745; font-weight: bold; }
    .negative { color: #dc3545; font-weight: bold; }
    .neutral { color: #6c757d; font-weight: bold; }
    .metric-card {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# --- 应用标题 ---
st.markdown('<div class="main-header"><h1>🔺 胜算实验室：足球投注风控系统</h1><p>可视化分析足球投注策略的风险与收益</p></div>', unsafe_allow_html=True)

# --- 侧边栏配置 ---
with st.sidebar:
    st.header("⚙️ 系统配置")
    
    # 选择策略
    st.subheader("🎯 选择策略")
    strategy = st.radio(
        "选择分析策略",
        ["策略1: 比分精准对冲", "策略2: 总进球+稳胆对冲"],
        index=1
    )
    
    st.markdown("---")
    
    # 通用参数
    st.subheader("💰 通用参数")
    total_investment = st.number_input("总投入资金 (元)", min_value=100, max_value=10000, value=200, step=100)
    
    st.markdown("---")
    
    # 主比赛设置
    st.subheader("⚽ 主比赛设置")
    main_team_a = st.text_input("主队", value="安哥拉")
    main_team_b = st.text_input("客队", value="埃及")
    
    if strategy == "策略1: 比分精准对冲":
        # 策略1参数
        st.subheader("🎯 策略1设置")
        over25_stake = st.number_input("大球投注金额 (元)", min_value=50, max_value=5000, value=100, step=50)
        hedge_stake = total_investment - over25_stake
        
        # 比分选项
        st.write("选择比分对冲选项:")
        score_options = ["0-0", "1-0", "0-1", "1-1", "2-0", "0-2", "2-1", "1-2", "2-2"]
        selected_scores = []
        for score in score_options:
            if st.checkbox(score, value=(score in ["1-0", "0-1", "1-1", "2-0", "0-2"]), key=f"score_{score}"):
                selected_scores.append(score)
        
    else:  # 策略2
        # 策略2参数
        st.subheader("🎯 策略2设置")
        over25_stake = st.number_input("大球投注金额 (元)", min_value=50, max_value=5000, value=100, step=50)
        hedge_stake = total_investment - over25_stake
        
        # 总进球选项
        st.write("选择总进球选项:")
        goal_options = ["0球", "1球", "2球"]
        selected_goals = []
        for goal in goal_options:
            if st.checkbox(goal, value=(goal in ["1球", "2球"]), key=f"goal_{goal}"):
                selected_goals.append(goal)
        
        # 稳胆比赛设置
        st.subheader("🏆 稳胆比赛设置")
        strong_team_a = st.text_input("稳胆主队", value="布赖代合作", key="strong_a")
        strong_team_b = st.text_input("稳胆客队", value="欧奈宰尹马", key="strong_b")
    
    st.markdown("---")
    
    # 赔率设置
    st.subheader("📈 赔率设置")
    over25_odds = st.number_input("大球赔率", min_value=1.01, max_value=10.0, value=2.30, step=0.05)
    
    if strategy == "策略1: 比分精准对冲":
        score_odds = {}
        st.write("设置比分赔率:")
        for score in selected_scores:
            default_odds = {"0-0": 10.0, "1-0": 8.5, "0-1": 8.0, "1-1": 7.0, "2-0": 13.0, "0-2": 12.0, "2-1": 15.0, "1-2": 14.0, "2-2": 20.0}
            score_odds[score] = st.number_input(f"{score}赔率", min_value=1.01, max_value=50.0, value=default_odds.get(score, 10.0), step=0.1, key=f"odds_{score}")
    else:
        goal_odds = {}
        st.write("设置总进球赔率:")
        for goal in selected_goals:
            default_odds = {"0球": 7.20, "1球": 3.60, "2球": 3.20}
            goal_odds[goal] = st.number_input(f"{goal}赔率", min_value=1.01, max_value=50.0, value=default_odds.get(goal, 5.0), step=0.1, key=f"odds_{goal}")
        strong_odds = st.number_input("稳胆主胜赔率", min_value=1.01, max_value=5.0, value=1.25, step=0.05)

# --- 风险警示 ---
st.markdown("""
<div class="warning-box">
⚠️ <strong>风险警示</strong>
<p>本工具旨在展示投注策略的数学模型，<strong>严禁用于非法博彩</strong>。</p>
<ul>
<li>稳胆场次爆冷会导致对冲系统全面溃缩。</li>
<li>未覆盖的赛果（如0-0或特定高分）将导致本金全损。</li>
</ul>
</div>
""", unsafe_allow_html=True)

# --- 计算函数 ---
def calculate_strategy1():
    scenarios = []
    stake_per_score = hedge_stake / len(selected_scores) if selected_scores else 0
    possible_outcomes = ["0-0", "1-0", "0-1", "1-1", "2-0", "0-2", "2-1", "1-2", "2-2", "其他大球"]
    
    for outcome in possible_outcomes:
        income = 0
        if outcome == "其他大球":
            income = over25_stake * over25_odds
        elif outcome in selected_scores:
            income = stake_per_score * score_odds.get(outcome, 0)
            
        net_profit = income - total_investment
        status = "盈利" if net_profit > 0 else ("保本" if net_profit == 0 else "亏损")
        scenarios.append({"赛果": outcome, "总收入": round(income, 2), "净盈亏": round(net_profit, 2), "状态": status})
    return pd.DataFrame(scenarios)

def calculate_strategy2():
    scenarios = []
    stake_per_goal = hedge_stake / len(selected_goals) if selected_goals else 0
    goal_outcomes = ["0球", "1球", "2球", "3+球"]
    strong_outcomes = ["主胜", "平局", "客胜"]
    
    for goals in goal_outcomes:
        for strong in strong_outcomes:
            income = 0
            if goals == "3+球":
                income += over25_stake * over25_odds
            if strong == "主胜" and goals in selected_goals:
                income += stake_per_goal * (goal_odds.get(goals, 0) * strong_odds)
                
            net_profit = income - total_investment
            roi = (net_profit / total_investment) * 100
            status = "盈利" if net_profit > 0 else ("保本" if net_profit == 0 else "亏损")
            scenarios.append({"总进球": goals, "稳胆结果": strong, "净盈亏": round(net_profit, 2), "收益率": round(roi, 2), "状态": status})
    return pd.DataFrame(scenarios)

# --- 数据展示 ---
if strategy == "策略1: 比分精准对冲":
    df_scenarios = calculate_strategy1()
    st.header("📊 关键指标")
    col1, col2, col3 = st.columns(3)
    col1.metric("总投入", f"{total_investment}元")
    col2.metric("最大盈利", f"{df_scenarios['净盈亏'].max()}元")
    col3.metric("盈利情景数", f"{len(df_scenarios[df_scenarios['净盈亏'] > 0])}/{len(df_scenarios)}")

    fig = go.Figure(go.Bar(x=df_scenarios["赛果"], y=df_scenarios["净盈亏"], marker_color=['#4ECDC4' if x > 0 else '#FF6B6B' for x in df_scenarios["净盈亏"]]))
    st.plotly_chart(fig, use_container_width=True)
else:
    df_scenarios = calculate_strategy2()
    st.header("📊 关键指标")
    col1, col2, col3 = st.columns(3)
    col1.metric("总投入", f"{total_investment}元")
    col2.metric("最大盈利", f"{df_scenarios['净盈亏'].max()}元")
    col3.metric("双重损失风险数", f"{len(df_scenarios[df_scenarios['净盈亏'] <= -total_investment])}个情景")

    fig = go.Figure()
    for g in df_scenarios["总进球"].unique():
        sub = df_scenarios[df_scenarios["总进球"] == g]
        fig.add_trace(go.Bar(x=sub["稳胆结果"], y=sub["净盈亏"], name=g))
    fig.update_layout(barmode='group', title="策略2盈亏分布")
    st.plotly_chart(fig, use_container_width=True)

# 详细表格
st.subheader("📋 详细数据分析")
def color_status(val):
    color = '#d4edda' if val == "盈利" else ('#f8d7da' if val == "亏损" else '#fff3cd')
    return f'background-color: {color}'

st.dataframe(df_scenarios.style.applymap(color_status, subset=['状态']), use_container_width=True)

st.markdown("---")
st.caption("胜算实验室 v2.0 | 仅供风控概念学习使用")

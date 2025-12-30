import streamlit as st
import pandas as pd
import numpy as np
import random

# 页面配置
st.set_page_config(
    page_title="胜算实验室：足球投注风控教育系统",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 样式 ---
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #1e3c72, #2a5298);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .positive {
        color: #28a745;
        font-weight: bold;
    }
    .negative {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- 标题 ---
st.markdown('<div class="main-header"><h1>🔺 胜算实验室：足球投注风控系统</h1></div>', unsafe_allow_html=True)
st.caption("教育工具：可视化展示庄家数学优势 | 仅供学习风控概念使用")

# --- 侧边栏 ---
with st.sidebar:
    st.header("⚙️ 参数配置")
    
    # 核心大球项
    st.subheader("⚖️ 核心大球项 (Over 2.5)")
    o25_odds = st.number_input("大球赔率", value=2.30, step=0.01, min_value=1.01, max_value=100.0)
    o25_stake = st.number_input("大球金额 ($)", value=100.0, step=1.0, min_value=0.0)
    
    st.divider()
    
    # 策略选择
    st.subheader("🎯 策略选择")
    mode = st.radio("执行策略", ["策略 1：比分精准对冲", "策略 2：总进球对冲"])
    
    st.divider()
    
    # 风险参数
    st.subheader("🧠 风险参数")
    pred_prob = st.slider("预测大球概率 (%)", 10, 90, 45) / 100
    
    st.divider()
    
    # 模拟设置
    show_simulation = st.checkbox("启用长期模拟", value=False)
    if show_simulation:
        sim_runs = st.slider("模拟次数", 100, 5000, 1000)
        initial_bankroll = st.number_input("初始资金 ($)", value=1000.0, min_value=100.0)

# --- 风险警示 ---
st.markdown("""
<div class="warning-box">
⚠️ <strong>风险警示：</strong>体育投注是负期望值游戏。庄家通过数学优势确保长期盈利。
本工具旨在教育用户理解风险，<strong>不鼓励任何形式的赌博行为</strong>。
</div>
""", unsafe_allow_html=True)

# --- 核心逻辑 ---
st.divider()
st.header("📊 核心对冲策略分析")

col_strategy, col_results = st.columns([1.5, 2], gap="large")
active_bets = []

if mode == "策略 1：比分精准对冲":
    with col_strategy:
        st.subheader("🎯 比分精准对冲策略")
        
        # 比分对冲设置
        scores = ["0-0", "1-0", "0-1", "1-1", "2-0", "0-2"]
        default_odds = {"0-0": 10.0, "1-0": 8.5, "0-1": 8.0, "1-1": 7.0, "2-0": 13.0, "0-2": 12.0}
        
        st.write("设置比分对冲项")
        
        for s in scores:
            col1, col2, col3 = st.columns([1, 1.5, 1.5])
            with col1:
                is_on = st.checkbox(s, key=f"s1_{s}", value=(s in ["1-0", "0-1", "1-1"]))
            with col2:
                s_amt = st.number_input(f"金额", value=15.0 if s in ["1-0", "0-1", "1-1"] else 10.0, 
                                       key=f"s1_am_{s}", label_visibility="collapsed") if is_on else 0.0
            with col3:
                s_odd = st.number_input(f"赔率", value=default_odds[s], 
                                       key=f"s1_od_{s}", label_visibility="collapsed") if is_on else 0.0
            
            if is_on: 
                active_bets.append({"item": s, "odd": s_odd, "stake": s_amt, "type": "比分对冲"})
        
        # 添加大球主投注
        active_bets.append({"item": "3球+", "odd": o25_odds, "stake": o25_stake, "type": "主投注"})
        
        # 计算总投入
        total_cost = sum(b['stake'] for b in active_bets)
        st.metric("💰 总投入", f"${total_cost:.2f}")

    with col_results:
        st.subheader("📈 模拟盈亏分析")
        
        # 7种可能结果
        outcomes = ["0-0", "1-0", "0-1", "1-1", "2-0", "0-2", "3球+"]
        results = []
        
        for outcome in outcomes:
            income = 0
            for bet in active_bets:
                if bet["item"] == outcome:
                    income += bet["stake"] * bet["odd"]
            
            net_profit = income - total_cost
            
            results.append({
                "模拟赛果": outcome,
                "总收入": round(income, 2),
                "总投入": round(total_cost, 2),
                "净盈亏": round(net_profit, 2),
                "状态": "盈利" if net_profit > 0 else ("保本" if net_profit == 0 else "亏损")
            })
        
        df_results = pd.DataFrame(results)
        
        # 使用 Streamlit 内置条形图
        st.write("##### 盈亏条形图")
        chart_data = df_results.set_index("模拟赛果")["净盈亏"]
        st.bar_chart(chart_data)
        
        # 详细数据表
        st.write("##### 详细盈亏表")
        
        # 自定义显示带颜色的表格
        def color_profit(val):
            if val > 0:
                return 'background-color: #d4edda; color: #155724;'
            elif val < 0:
                return 'background-color: #f8d7da; color: #721c24;'
            else:
                return 'background-color: #fff3cd; color: #856404;'
        
        # 显示表格
        styled_df = df_results.style.applymap(color_profit, subset=['净盈亏'])
        st.dataframe(styled_df, hide_index=True, use_container_width=True)
        
        # 总结统计
        profitable = sum(1 for r in results if r['净盈亏'] > 0)
        breakeven = sum(1 for r in results if r['净盈亏'] == 0)
        losing = sum(1 for r in results if r['净盈亏'] < 0)
        
        st.info(f"""
        **策略分析总结：**
        - 覆盖赛果: {len(outcomes)} 种
        - 盈利赛果: {profitable} 种 ({profitable/len(outcomes)*100:.1f}%)
        - 保本赛果: {breakeven} 种
        - 亏损赛果: {losing} 种 ({losing/len(outcomes)*100:.1f}%)
        """)

else:  # 策略 2：总进球复式对冲
    with col_strategy:
        st.subheader("🎯 总进球复式对冲策略")
        
        # 稳胆设置
        strong_win = st.number_input("稳胆赔率", value=1.35, step=0.01)
        multi_stake = st.number_input("复式对冲总投入 ($)", value=100.0, step=1.0)
        
        # 总进球对冲设置
        totals = ["0球", "1球", "2球"]
        img_odds = {"0球": 7.20, "1球": 3.55, "2球": 3.00}
        
        st.write("设置总进球对冲")
        selected = []
        
        for g in totals:
            col1, col2 = st.columns([1, 2])
            with col1:
                is_on = st.checkbox(g, key=f"s2_{g}", value=(g != "0球"))
            with col2:
                g_odd = st.number_input(f"赔率", value=img_odds[g], 
                                       key=f"s2_od_{g}", label_visibility="collapsed") if is_on else 0.0
            
            if is_on: 
                selected.append({"name": g, "odd": g_odd})
        
        # 计算分摊金额
        if selected:
            share = multi_stake / len(selected)
            for item in selected:
                active_bets.append({
                    "item": item['name'], 
                    "odd": item['odd'] * strong_win, 
                    "stake": share,
                    "type": "总进球对冲"
                })
        
        # 添加大球主投注
        active_bets.append({"item": "3球+", "odd": o25_odds, "stake": o25_stake, "type": "主投注"})
        
        # 计算总投入
        total_cost = sum(b['stake'] for b in active_bets)
        st.metric("💰 总投入", f"${total_cost:.2f}")

    with col_results:
        st.subheader("📈 模拟盈亏分析")
        
        # 4种可能结果
        outcomes = ["0球", "1球", "2球", "3球+"]
        results = []
        
        for outcome in outcomes:
            income = 0
            for bet in active_bets:
                if bet["item"] == outcome:
                    income += bet["stake"] * bet["odd"]
            
            net_profit = income - total_cost
            
            results.append({
                "模拟赛果": outcome,
                "总收入": round(income, 2),
                "总投入": round(total_cost, 2),
                "净盈亏": round(net_profit, 2),
                "状态": "盈利" if net_profit > 0 else ("保本" if net_profit == 0 else "亏损")
            })
        
        df_results = pd.DataFrame(results)
        
        # 使用 Streamlit 内置条形图
        st.write("##### 盈亏条形图")
        chart_data = df_results.set_index("模拟赛果")["净盈亏"]
        st.bar_chart(chart_data)
        
        # 详细数据表
        st.write("##### 详细盈亏表")
        
        # 自定义显示带颜色的表格
        def color_profit(val):
            if val > 0:
                return 'background-color: #d4edda; color: #155724;'
            elif val < 0:
                return 'background-color: #f8d7da; color: #721c24;'
            else:
                return 'background-color: #fff3cd; color: #856404;'
        
        # 显示表格
        styled_df = df_results.style.applymap(color_profit, subset=['净盈亏'])
        st.dataframe(styled_df, hide_index=True, use_container_width=True)

# --- 数学期望计算 ---
st.divider()
st.header("📉 数学期望分析")

# 计算策略的数学期望
if mode == "策略 1：比分精准对冲":
    prob_3plus = pred_prob
    prob_each_other = (1 - pred_prob) / 6 if len(active_bets) > 1 else 0
    
    ev = 0
    for result in results:
        if result["模拟赛果"] == "3球+":
            ev += result["净盈亏"] * prob_3plus
        else:
            ev += result["净盈亏"] * prob_each_other
else:
    prob_3plus = pred_prob
    prob_each_other = (1 - pred_prob) / 3 if len(active_bets) > 1 else 0
    
    ev = 0
    for result in results:
        if result["模拟赛果"] == "3球+":
            ev += result["净盈亏"] * prob_3plus
        else:
            ev += result["净盈亏"] * prob_each_other

# 显示EV分析
col1, col2 = st.columns(2)
with col1:
    st.metric("策略期望值 (EV)", f"${ev:.2f}", 
              delta="正向" if ev > 0 else "负向",
              delta_color="normal" if ev <= 0 else "inverse")

with col2:
    # 简单大球投注EV
    simple_ev = (pred_prob * o25_odds - 1) * o25_stake
    st.metric("简单大球投注EV", f"${simple_ev:.2f}")

# EV解释
if ev > 0:
    st.success(f"✅ **理论上有长期盈利可能** | 每次投注期望收益: ${ev:.2f}")
else:
    st.error(f"❌ **负期望值策略** | 每次投注期望损失: ${abs(ev):.2f}")

# --- 庄家优势解析 ---
st.divider()
st.header("🏢 庄家数学优势")

# 计算庄家优势
implied_prob = 1 / o25_odds
overround = (1/implied_prob - 1) * 100

st.markdown(f"""
**赔率分析：**
- 大球赔率: {o25_odds:.2f}
- 赔率隐含概率: {implied_prob*100:.1f}%
- 庄家优势 (Overround): {overround:.2f}%

**你的预测 vs 市场：**
- 你的预测概率: {pred_prob*100:.1f}%
- 市场隐含概率: {implied_prob*100:.1f}%
- 概率差值: {(pred_prob - implied_prob)*100:+.1f}%

**数学原理：**

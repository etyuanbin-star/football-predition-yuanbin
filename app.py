
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random

# 页面配置
st.set_page_config(
    page_title="胜算实验室：足球投注风控教育系统",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 导入自定义模块（如果拆分的话）
# 这里我们先写一个完整但更简洁的版本

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
    if st.checkbox("启用长期模拟"):
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
        
        # 可视化
        fig, ax = plt.subplots(figsize=(10, 5))
        colors = ['#dc3545' if x < 0 else '#28a745' for x in df_results['净盈亏']]
        bars = ax.bar(df_results['模拟赛果'], df_results['净盈亏'], color=colors)
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax.set_xlabel('比赛结果')
        ax.set_ylabel('净盈亏 ($)')
        ax.set_title('各结果净盈亏分析')
        ax.tick_params(axis='x', rotation=45)
        
        # 添加数值标签
        for bar, value in zip(bars, df_results['净盈亏']):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'${value:+.0f}', ha='center', va='bottom' if height > 0 else 'top',
                   fontsize=9)
        
        plt.tight_layout()
        st.pyplot(fig)
        
        # 详细数据表
        st.dataframe(df_results, hide_index=True, use_container_width=True)

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
        
        # 可视化
        fig, ax = plt.subplots(figsize=(8, 5))
        colors = ['#dc3545' if x < 0 else '#28a745' for x in df_results['净盈亏']]
        bars = ax.bar(df_results['模拟赛果'], df_results['净盈亏'], color=colors)
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax.set_xlabel('比赛结果')
        ax.set_ylabel('净盈亏 ($)')
        ax.set_title('各结果净盈亏分析')
        
        # 添加数值标签
        for bar, value in zip(bars, df_results['净盈亏']):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'${value:+.0f}', ha='center', va='bottom' if height > 0 else 'top',
                   fontsize=10)
        
        plt.tight_layout()
        st.pyplot(fig)
        
        # 详细数据表
        st.dataframe(df_results, hide_index=True, use_container_width=True)

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
""")

# --- 长期模拟 ---
if 'sim_runs' in locals() and sim_runs:
    st.divider()
    st.header("📈 长期资金曲线模拟")
    
    # 模拟参数
    n_simulations = 50
    n_bets = min(sim_runs, 1000)
    starting_bankroll = initial_bankroll
    
    # 简化模拟
    all_paths = []
    
    for sim in range(n_simulations):
        bankroll = starting_bankroll
        path = [bankroll]
        
        for bet in range(n_bets):
            # 基于期望值模拟
            if ev > 0:
                bankroll += ev * random.uniform(0.5, 1.5)
            else:
                bankroll += ev * random.uniform(0.8, 1.2)
            
            if bankroll <= 0:
                bankroll = 0
            
            path.append(max(0, bankroll))
        
        all_paths.append(path)
    
    # 可视化
    fig, ax = plt.subplots(figsize=(12, 6))
    
    for i, path in enumerate(all_paths[:10]):  # 只显示前10条
        alpha = 0.3
        linewidth = 1
        ax.plot(path, alpha=alpha, linewidth=linewidth, color='blue')
    
    # 平均路径
    if all_paths:
        avg_path = np.mean(all_paths, axis=0)
        ax.plot(avg_path, 'r-', linewidth=2, label='平均路径', alpha=0.8)
    
    ax.axhline(y=starting_bankroll, color='green', linestyle='--', alpha=0.5, label='初始资金')
    ax.axhline(y=starting_bankroll/2, color='orange', linestyle='--', alpha=0.5, label='50%亏损线')
    ax.axhline(y=0, color='red', linestyle='-', alpha=0.3, label='破产线')
    
    ax.set_xlabel('投注次数')
    ax.set_ylabel('资金余额 ($)')
    ax.set_title(f'长期资金曲线模拟 ({n_simulations}条路径)')
    ax.legend(loc='upper left', fontsize=8)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    st.pyplot(fig)
    
    # 统计
    if all_paths:
        final_balances = [path[-1] for path in all_paths]
        bankruptcy_count = sum(1 for b in final_balances if b <= 0)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("平均最终资金", f"${np.mean(final_balances):.0f}")
        with col2:
            st.metric("破产概率", f"{bankruptcy_count/n_simulations*100:.1f}%")
        with col3:
            profitable_rate = sum(1 for b in final_balances if b > starting_bankroll) / n_simulations * 100
            st.metric("盈利路径比例", f"{profitable_rate:.1f}%")

# --- 健康建议 ---
st.divider()
st.header("💡 健康投注建议")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### ✅ 健康原则
    
    1. **预算控制**
    - 月投注预算 ≤ 娱乐预算的10%
    - 单场投注 ≤ 总预算的5%
    - 永不借贷投注
    
    2. **记录分析**
    - 记录每笔投注
    - 每月复盘决策
    - 设置止损止盈线
    
    3. **正确心态**
    - 视投注为娱乐消费
    - 接受损失是体验的一部分
    - 享受比赛本身
    """)

with col2:
    st.markdown("""
    ### ⚠️ 必须避免
    
    1. **追注行为**
    - "已经输这么多，必须追回来"
    - 情绪化决策
    - 忽视资金管理
    
    2. **认知偏差**
    - "我连胜3场，我有技巧"
    - "连开5次大，下次必小"
    - 为失败找外部借口
    
    3. **不切实际期望**
    - 视投注为投资
    - 追求"财务自由"
    - 高估预测能力
    """)

# --- 最终警示 ---
st.divider()
st.markdown("""
<div style='text-align: center; padding: 1.5rem; background-color: #f8d7da; border-radius: 10px;'>
<h3 style='color: #721c24;'>⚠️ 重要提醒</h3>
<p style='color: #721c24;'>
<strong>体育投注不是投资，而是娱乐消费。</strong><br>
庄家通过数学优势确保长期盈利，你的"技巧"无法改变数学现实。<br><br>
<strong>如果你或你认识的人有赌博问题，请寻求帮助：</strong><br>
• 全国戒赌热线：1-800-522-4700<br>
• 设置自我排除<br>
• 与专业人士交谈
</p>
</div>
""", unsafe_allow_html=True)

# --- 脚注 ---
st.caption("""
*本工具仅用于教育目的，展示赌博的数学原理和风险。不鼓励任何形式的赌博行为。*  
*所有计算基于概率理论，实际结果可能因多种因素而异。*  
*如果你需要赌博问题帮助，请联系专业机构。*
""")

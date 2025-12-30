import streamlit as st
import pandas as pd
import numpy as np
import random

# 页面配置 - 使用缓存优化
st.set_page_config(
    page_title="胜算实验室：足球投注风控系统",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 缓存优化函数 ---
@st.cache_data(ttl=300)  # 缓存5分钟
def calculate_results(active_bets, outcomes, total_cost):
    """缓存计算结果"""
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
    return results

@st.cache_data(ttl=300)
def simulate_paths(ev, n_simulations, n_bets, starting_bankroll):
    """缓存模拟结果"""
    simulation_data = []
    
    for sim in range(min(n_simulations, 50)):  # 限制最多50条路径
        bankroll = starting_bankroll
        path = []
        
        for bet in range(min(n_bets, 200)):  # 限制最多200次投注
            # 简化模拟逻辑
            bankroll += ev * random.uniform(0.8, 1.2)
            if bankroll <= 0:
                bankroll = 0
                break
            path.append(max(0, bankroll))
        
        # 只记录关键点，减少数据量
        for i, value in enumerate(path):
            if i % 10 == 0 or i == len(path) - 1:  # 每10次记录一次
                simulation_data.append({
                    "模拟路径": sim + 1,
                    "投注次数": i + 1,
                    "资金余额": value
                })
    
    return simulation_data

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
    /* 优化表格样式 */
    .dataframe {
        font-size: 0.9em;
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
        sim_runs = st.slider("模拟次数", 100, 2000, 500)  # 减少最大模拟次数
        initial_bankroll = st.number_input("初始资金 ($)", value=1000.0, min_value=100.0)
        
    # 性能选项
    st.divider()
    st.subheader("⚡ 性能选项")
    use_simple_charts = st.checkbox("使用简化图表", value=True, 
                                    help="简化图表显示以加快渲染速度")

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
        
        # 使用会话状态存储复选框状态，避免重复渲染
        if 'checkbox_states' not in st.session_state:
            st.session_state.checkbox_states = {s: (s in ["1-0", "0-1", "1-1"]) for s in scores}
        
        for s in scores:
            col1, col2, col3 = st.columns([1, 1.5, 1.5])
            with col1:
                is_on = st.checkbox(s, key=f"s1_{s}", value=st.session_state.checkbox_states[s])
                st.session_state.checkbox_states[s] = is_on
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
        
        # 使用缓存函数计算结果
        results = calculate_results(active_bets, outcomes, total_cost)
        
        df_results = pd.DataFrame(results)
        
        # 图表显示
        if use_simple_charts:
            st.write("##### 盈亏条形图（简化）")
            # 简化图表数据
            chart_df = df_results[["模拟赛果", "净盈亏"]].set_index("模拟赛果")
            st.bar_chart(chart_df)
        else:
            # 更详细的图表显示
            st.write("##### 盈亏分析")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("最大盈利", f"${df_results['净盈亏'].max():.0f}")
            with col2:
                st.metric("最大亏损", f"${df_results['净盈亏'].min():.0f}")
        
        # 详细数据表 - 只显示关键列
        st.write("##### 详细盈亏表")
        
        # 简化表格显示
        display_df = df_results[["模拟赛果", "净盈亏", "状态"]].copy()
        display_df["净盈亏"] = display_df["净盈亏"].apply(lambda x: f"${x:+.2f}")
        
        # 使用st.dataframe而不是st.table，性能更好
        st.dataframe(display_df, hide_index=True, use_container_width=True, height=300)
        
        # 快速统计
        profitable = sum(1 for r in results if r['净盈亏'] > 0)
        st.info(f"""
        **快速分析：**
        - 覆盖赛果: {len(outcomes)} 种
        - 盈利赛果: {profitable} 种
        - 保本率: {profitable/len(outcomes)*100:.1f}%
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
        
        # 使用缓存函数计算结果
        results = calculate_results(active_bets, outcomes, total_cost)
        
        df_results = pd.DataFrame(results)
        
        # 图表显示
        if use_simple_charts:
            st.write("##### 盈亏条形图（简化）")
            chart_df = df_results[["模拟赛果", "净盈亏"]].set_index("模拟赛果")
            st.bar_chart(chart_df)
        else:
            st.write("##### 盈亏分析")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("最大盈利", f"${df_results['净盈亏'].max():.0f}")
            with col2:
                st.metric("最大亏损", f"${df_results['净盈亏'].min():.0f}")
        
        # 详细数据表
        st.write("##### 详细盈亏表")
        display_df = df_results[["模拟赛果", "净盈亏", "状态"]].copy()
        display_df["净盈亏"] = display_df["净盈亏"].apply(lambda x: f"${x:+.2f}")
        st.dataframe(display_df, hide_index=True, use_container_width=True, height=200)

# --- 数学期望计算 ---
st.divider()
st.header("📉 数学期望分析")

# 计算策略的数学期望
if mode == "策略 1：比分精准对冲":
    prob_3plus = pred_prob
    prob_each_other = (1 - pred_prob) / 6 if len(active_bets) > 1 else 0
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
    ev_color = "normal" if ev <= 0 else "inverse"
    ev_delta = "正向" if ev > 0 else "负向"
    st.metric("策略期望值 (EV)", f"${ev:.2f}", delta=ev_delta, delta_color=ev_color)

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

# 使用列布局减少垂直空间
col1, col2 = st.columns(2)
with col1:
    st.markdown(f"""
    **赔率分析：**
    - 大球赔率: {o25_odds:.2f}
    - 隐含概率: {implied_prob*100:.1f}%
    - 庄家优势: {overround:.2f}%
    """)

with col2:
    st.markdown(f"""
    **预测对比：**
    - 你的预测: {pred_prob*100:.1f}%
    - 市场概率: {implied_prob*100:.1f}%
    - 差值: {(pred_prob - implied_prob)*100:+.1f}%
    """)

# --- 长期模拟（优化版）---
if show_simulation:
    st.divider()
    st.header("📈 长期资金曲线模拟")
    
    # 添加进度指示器
    with st.spinner('正在模拟中...'):
        # 使用缓存函数进行模拟
        simulation_data = simulate_paths(ev, 30, sim_runs, initial_bankroll)  # 限制30条路径
        
        if simulation_data:
            sim_df = pd.DataFrame(simulation_data)
            
            # 快速统计
            final_balances = sim_df.groupby("模拟路径")["资金余额"].last()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                avg_balance = final_balances.mean()
                st.metric("平均最终资金", f"${avg_balance:.0f}")
            
            with col2:
                bankruptcy_count = sum(1 for b in final_balances if b <= 0)
                bankruptcy_rate = bankruptcy_count / len(final_balances) * 100
                st.metric("破产概率", f"{bankruptcy_rate:.1f}%")
            
            with col3:
                profitable_count = sum(1 for b in final_balances if b > initial_bankroll)
                profitable_rate = profitable_count / len(final_balances) * 100
                st.metric("盈利路径比例", f"{profitable_rate:.1f}%")
            
            # 简化图表显示
            st.write("##### 资金曲线示例（前5条路径）")
            
            # 选择前5条路径显示
            top_paths = sim_df[sim_df["模拟路径"] <= 5]
            if not top_paths.empty:
                # 创建透视表用于图表
                pivot_df = top_paths.pivot(index="投注次数", columns="模拟路径", values="资金余额")
                st.line_chart(pivot_df)
            
            # 简化分布显示
            st.write("##### 最终资金分布")
            
            # 计算分布
            bins = [0, initial_bankroll/2, initial_bankroll, initial_bankroll*1.5, float('inf')]
            labels = ["严重亏损", "中度亏损", "轻微亏损/盈利", "大幅盈利"]
            
            final_balances_list = list(final_balances)
            distribution = pd.cut(final_balances_list, bins=bins, labels=labels).value_counts().sort_index()
            
            dist_df = pd.DataFrame({
                "资金状态": distribution.index,
                "路径数量": distribution.values
            }).set_index("资金状态")
            
            st.bar_chart(dist_df)

# --- 健康建议（简化版）---
st.divider()
st.header("💡 健康投注建议")

# 使用展开器减少初始显示内容
with st.expander("查看健康投注原则", expanded=False):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### ✅ 健康原则
        
        1. **预算控制**
        - 月投注预算 ≤ 娱乐预算的10%
        - 单场投注 ≤ 总预算的5%
        - 永不借贷投注
        """)
    
    with col2:
        st.markdown("""
        ### ⚠️ 必须避免
        
        1. **追注行为**
        - "已经输这么多，必须追回来"
        - 情绪化决策
        - 忽视资金管理
        """)

# --- 最终警示 ---
st.divider()
st.markdown("""
<div style='text-align: center; padding: 1rem; background-color: #f8d7da; border-radius: 10px;'>
<h4 style='color: #721c24;'>⚠️ 重要提醒</h4>
<p style='color: #721c24; font-size: 0.9rem;'>
<strong>体育投注不是投资，而是娱乐消费。</strong><br>
庄家通过数学优势确保长期盈利。<br>
如果你或你认识的人有赌博问题，请寻求专业帮助。
</p>
</div>
""", unsafe_allow_html=True)

# --- 性能提示 ---
if st.checkbox("显示性能提示", value=False):
    st.info("""
    **性能优化提示：**
    1. 使用"简化图表"选项减少渲染时间
    2. 减少模拟次数到500-1000次
    3. 避免频繁切换策略和参数
    4. 如仍然缓慢，请刷新页面重新开始
    """)

# --- 脚注 ---
st.caption("""
*本工具仅用于教育目的，展示赌博的数学原理和风险。不鼓励任何形式的赌博行为。*  
*所有计算基于概率理论，实际结果可能因多种因素而异。*
""")

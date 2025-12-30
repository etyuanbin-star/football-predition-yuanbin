import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import random

# 设置页面配置
st.set_page_config(
    page_title="胜算实验室：足球投注风控教育系统",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 样式自定义 ---
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
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
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
    .stMetric {
        background-color: #f8f9fa;
        padding: 0.5rem;
        border-radius: 10px;
        border: 1px solid #dee2e6;
    }
</style>
""", unsafe_allow_html=True)

# --- 主标题 ---
st.markdown('<div class="main-header"><h1>🔺 胜算实验室：足球投注风控与教育系统</h1></div>', unsafe_allow_html=True)
st.caption("""
📊 教育工具：可视化展示庄家数学优势 | 基于真实负EV博弈理论 | 仅供学习风控概念使用
""")

# --- 侧边栏配置 ---
with st.sidebar:
    st.header("⚙️ 核心参数配置")
    
    # 核心大球项
    st.subheader("⚖️ 核心大球项 (Over 2.5)")
    o25_odds = st.number_input("大球 (3球+) 赔率", value=2.30, step=0.01, min_value=1.01, max_value=100.0)
    o25_stake = st.number_input("大球投入金额 ($)", value=100.0, step=1.0, min_value=0.0)
    
    st.divider()
    
    # 策略选择
    st.subheader("🎯 策略选择")
    mode = st.radio(
        "执行策略",
        ["策略 1：比分精准对冲", "策略 2：总进球复式对冲"],
        captions=["对冲6个具体比分", "对冲总进球区间"]
    )
    
    # 风险参数
    st.subheader("🧠 风险参数")
    pred_prob = st.slider("你预测的大球概率 (%)", 10, 90, 45, help="你的主观预测概率") / 100
    
    # 真实市场概率（用于对比）
    true_prob = st.slider("市场隐含概率 (%)", 10, 90, 43, 
                         help="根据赔率反算的真实概率（通常比你预测低）") / 100
    
    st.divider()
    
    # 教育模式
    st.subheader("🎓 教育功能")
    show_math = st.checkbox("显示数学原理", value=True)
    show_psychology = st.checkbox("显示心理陷阱", value=True)
    show_simulation = st.checkbox("启用长期模拟", value=True)
    
    if show_simulation:
        sim_runs = st.slider("模拟次数", 100, 10000, 1000)
        initial_bankroll = st.number_input("初始资金 ($)", value=1000.0, min_value=100.0)

# --- 风险警示 ---
st.markdown("""
<div class="warning-box">
⚠️ <strong>风险警示：</strong>体育投注本质是负期望值(负EV)游戏。庄家通过数学优势确保长期盈利。
本工具旨在教育用户理解风险，<strong>不鼓励任何形式的赌博行为</strong>。
</div>
""", unsafe_allow_html=True)

# --- 核心计算逻辑 ---
st.divider()
st.header("📊 核心对冲策略分析")

col_strategy, col_results = st.columns([1.5, 2], gap="large")
active_bets = []

if mode == "策略 1：比分精准对冲":
    with col_strategy:
        st.subheader("🎯 比分精准对冲策略")
        
        # 教育说明
        st.markdown("""
        **策略原理：**
        1. 主投：大球(3球+)
        2. 对冲：6个常见小比分
        3. 目标：降低大球不中的风险
        """)
        
        # 比分对冲设置
        scores = ["0-0", "1-0", "0-1", "1-1", "2-0", "0-2"]
        default_odds = {
            "0-0": 10.0, "1-0": 8.5, "0-1": 8.0, 
            "1-1": 7.0, "2-0": 13.0, "0-2": 12.0
        }
        
        st.write("##### 设置比分对冲项")
        
        for s in scores:
            col1, col2, col3 = st.columns([1, 1.5, 1.5])
            with col1:
                is_on = st.checkbox(s, key=f"s1_{s}", value=(s in ["1-0", "0-1", "1-1"]))
            with col2:
                s_amt = st.number_input(
                    f"金额", 
                    value=15.0 if s in ["1-0", "0-1", "1-1"] else 10.0, 
                    key=f"s1_am_{s}", 
                    label_visibility="collapsed"
                ) if is_on else 0.0
            with col3:
                s_odd = st.number_input(
                    f"赔率", 
                    value=default_odds[s], 
                    key=f"s1_od_{s}", 
                    label_visibility="collapsed"
                ) if is_on else 0.0
            
            if is_on: 
                active_bets.append({
                    "item": s, 
                    "odd": s_odd, 
                    "stake": s_amt,
                    "type": "比分对冲"
                })
        
        # 添加大球主投注
        active_bets.append({
            "item": "3球+", 
            "odd": o25_odds, 
            "stake": o25_stake,
            "type": "主投注"
        })
        
        # 计算总投入和回报
        total_cost = sum(b['stake'] for b in active_bets)
        total_potential = sum(b['stake'] * b['odd'] for b in active_bets)
        
        # 显示财务摘要
        st.divider()
        st.write("##### 💰 财务摘要")
        
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("总投入", f"${total_cost:.2f}")
        with col_b:
            st.metric("潜在回报", f"${total_potential:.2f}")
        with col_c:
            edge = (total_potential/total_cost - 1) * 100 if total_cost > 0 else 0
            st.metric("盈亏边缘", f"{edge:.1f}%", 
                     delta="正向" if edge > 0 else "负向",
                     delta_color="normal")

    with col_results:
        st.subheader("📈 模拟盈亏分析")
        
        # 定义7种可能结果
        outcomes = ["0-0", "1-0", "0-1", "1-1", "2-0", "0-2", "3球+"]
        results = []
        
        for outcome in outcomes:
            income = 0
            winning_bets = []
            
            for bet in active_bets:
                if bet["item"] == outcome:
                    win_amount = bet["stake"] * bet["odd"]
                    income += win_amount
                    winning_bets.append({
                        "投注项": bet["item"],
                        "中奖金额": win_amount,
                        "投入": bet["stake"]
                    })
            
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
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        # 条形图
        colors = ['#dc3545' if x < 0 else '#28a745' for x in df_results['净盈亏']]
        bars = ax1.bar(df_results['模拟赛果'], df_results['净盈亏'], color=colors)
        ax1.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax1.set_xlabel('比赛结果')
        ax1.set_ylabel('净盈亏 ($)')
        ax1.set_title('各结果净盈亏分析')
        ax1.tick_params(axis='x', rotation=45)
        
        # 添加数值标签
        for bar, value in zip(bars, df_results['净盈亏']):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'${value:+.0f}', ha='center', va='bottom' if height > 0 else 'top',
                    fontsize=9)
        
        # 盈亏分布饼图
        profitable = sum(1 for r in results if r['净盈亏'] > 0)
        breakeven = sum(1 for r in results if r['净盈亏'] == 0)
        losing = sum(1 for r in results if r['净盈亏'] < 0)
        
        sizes = [profitable, breakeven, losing]
        labels = [f'盈利\n{profitable}种', f'保本\n{breakeven}种', f'亏损\n{losing}种']
        colors_pie = ['#28a745', '#ffc107', '#dc3545']
        
        ax2.pie(sizes, labels=labels, colors=colors_pie, autopct='%1.0f%%', startangle=90)
        ax2.set_title('结果分布统计')
        
        plt.tight_layout()
        st.pyplot(fig)
        
        # 详细数据表
        st.write("##### 📋 详细盈亏表")
        st.dataframe(
            df_results.style.apply(
                lambda x: ['background-color: #d4edda' if v > 0 else 
                          ('background-color: #fff3cd' if v == 0 else 
                           'background-color: #f8d7da') for v in x],
                subset=['净盈亏']
            ),
            hide_index=True,
            use_container_width=True
        )
        
        # 策略分析
        st.markdown(f"""
        <div class="info-box">
        <strong>策略分析：</strong><br>
        • 覆盖结果: {len(outcomes)} 种<br>
        • 盈利结果: {profitable} 种 ({profitable/len(outcomes)*100:.1f}%)<br>
        • 保本结果: {breakeven} 种<br>
        • 亏损结果: {losing} 种 ({losing/len(outcomes)*100:.1f}%)
        </div>
        """, unsafe_allow_html=True)

else:  # 策略 2：总进球复式对冲
    with col_strategy:
        st.subheader("🎯 总进球复式对冲策略")
        
        # 教育说明
        st.markdown("""
        **策略原理：**
        1. 主投：大球(3球+)
        2. 对冲：0球、1球、2球复式投注
        3. 结合稳胆增加回报
        """)
        
        # 稳胆设置
        strong_win = st.number_input("稳胆赔率 (可选)", value=1.35, step=0.01, 
                                    help="与其他投注结合的稳胆选项")
        multi_stake = st.number_input("复式对冲总投入 ($)", value=100.0, step=1.0, min_value=0.0)
        
        # 总进球对冲设置
        totals = ["0球", "1球", "2球"]
        img_odds = {"0球": 7.20, "1球": 3.55, "2球": 3.00}
        
        st.write("##### 设置总进球对冲")
        selected = []
        
        for g in totals:
            col1, col2 = st.columns([1, 2])
            with col1:
                is_on = st.checkbox(g, key=f"s2_{g}", value=(g != "0球"))
            with col2:
                g_odd = st.number_input(
                    f"赔率", 
                    value=img_odds[g], 
                    key=f"s2_od_{g}", 
                    label_visibility="collapsed"
                ) if is_on else 0.0
            
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
        active_bets.append({
            "item": "3球+", 
            "odd": o25_odds, 
            "stake": o25_stake,
            "type": "主投注"
        })
        
        # 计算总投入和回报
        total_cost = sum(b['stake'] for b in active_bets)
        total_potential = sum(b['stake'] * b['odd'] for b in active_bets)
        
        # 显示财务摘要
        st.divider()
        st.write("##### 💰 财务摘要")
        
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("总投入", f"${total_cost:.2f}")
        with col_b:
            st.metric("潜在回报", f"${total_potential:.2f}")
        with col_c:
            edge = (total_potential/total_cost - 1) * 100 if total_cost > 0 else 0
            st.metric("盈亏边缘", f"{edge:.1f}%", 
                     delta="正向" if edge > 0 else "负向",
                     delta_color="normal")

    with col_results:
        st.subheader("📈 模拟盈亏分析")
        
        # 定义4种可能结果
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
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        # 条形图
        colors = ['#dc3545' if x < 0 else '#28a745' for x in df_results['净盈亏']]
        bars = ax1.bar(df_results['模拟赛果'], df_results['净盈亏'], color=colors)
        ax1.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax1.set_xlabel('比赛结果')
        ax1.set_ylabel('净盈亏 ($)')
        ax1.set_title('各结果净盈亏分析')
        
        # 添加数值标签
        for bar, value in zip(bars, df_results['净盈亏']):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'${value:+.0f}', ha='center', va='bottom' if height > 0 else 'top',
                    fontsize=10)
        
        # 投资组合构成图
        bet_types = {}
        for bet in active_bets:
            bet_type = bet['type']
            bet_types[bet_type] = bet_types.get(bet_type, 0) + bet['stake']
        
        if bet_types:
            labels = list(bet_types.keys())
            sizes = list(bet_types.values())
            colors_port = ['#6f42c1', '#20c997', '#fd7e14', '#e83e8c']
            
            ax2.pie(sizes, labels=labels, colors=colors_port[:len(labels)], 
                   autopct='%1.1f%%', startangle=90)
            ax2.set_title('资金分配构成')
        
        plt.tight_layout()
        st.pyplot(fig)
        
        # 详细数据表
        st.write("##### 📋 详细盈亏表")
        st.dataframe(
            df_results.style.apply(
                lambda x: ['background-color: #d4edda' if v > 0 else 
                          ('background-color: #fff3cd' if v == 0 else 
                           'background-color: #f8d7da') for v in x],
                subset=['净盈亏']
            ),
            hide_index=True,
            use_container_width=True
        )

# --- 预期价值计算 ---
st.divider()
st.header("📉 数学期望分析")

col_ev, col_math = st.columns([1, 1])

with col_ev:
    # 计算策略的数学期望
    if mode == "策略 1：比分精准对冲":
        # 策略1：7种结果
        prob_3plus = pred_prob
        prob_each_other = (1 - pred_prob) / 6
        
        ev = 0
        for result in results:
            if result["模拟赛果"] == "3球+":
                ev += result["净盈亏"] * prob_3plus
            else:
                ev += result["净盈亏"] * prob_each_other
    else:
        # 策略2：4种结果
        prob_3plus = pred_prob
        prob_each_other = (1 - pred_prob) / 3
        
        ev = 0
        for result in results:
            if result["模拟赛果"] == "3球+":
                ev += result["净盈亏"] * prob_3plus
            else:
                ev += result["净盈亏"] * prob_each_other
    
    # 计算市场公平价值
    market_ev = (true_prob * o25_odds - 1) * o25_stake
    
    # 显示EV分析
    st.subheader("🎲 数学期望分析")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            "策略期望值 (EV)",
            f"${ev:.2f}",
            delta="正向" if ev > 0 else "负向",
            delta_color="normal" if ev <= 0 else "inverse"
        )
    
    with col2:
        st.metric(
            "简单大球投注EV",
            f"${market_ev:.2f}",
            delta="对冲策略提升" if ev > market_ev else "无提升",
            delta_color="normal"
        )
    
    # EV解释
    if ev > 0:
        st.success(f"""
        ✅ **理论上有长期盈利可能**
        每次投注平均期望收益: ${ev:.2f}
        但请注意：这基于你的主观预测概率 ({pred_prob*100:.0f}%)，实际概率可能更低。
        """)
    else:
        st.error(f"""
        ❌ **负期望值策略**
        每次投注平均期望损失: ${abs(ev):.2f}
        长期执行必然亏损，平均每${total_cost:.0f}投入损失${abs(ev):.2f}。
        """)

with col_math:
    if show_math:
        st.subheader("🧮 庄家数学优势")
        
        # 计算庄家优势
        implied_prob = 1 / o25_odds  # 赔率隐含的概率
        overround = (1/implied_prob - 1) * 100  # 庄家优势百分比
        
        st.markdown(f"""
        **赔率分析：**
        - 大球赔率: {o25_odds:.2f}
        - 赔率隐含概率: {implied_prob*100:.1f}%
        - 庄家优势 (Overround): {overround:.2f}%
        
        **你的预测 vs 市场：**
        - 你的预测概率: {pred_prob*100:.1f}%
        - 市场隐含概率: {implied_prob*100:.1f}%
        - 概率差值: {(pred_prob - implied_prob)*100:+.1f}%
        
        **简单投注盈亏计算：**
        ```
        期望值 = (概率 × 赔率 - 1) × 投注额
              = ({pred_prob:.3f} × {o25_odds:.2f} - 1) × ${o25_stake:.0f}
              = ${market_ev:.2f}
        ```
        """)

# --- 长期模拟 ---
if show_simulation and 'sim_runs' in locals():
    st.divider()
    st.header("📈 长期资金曲线模拟")
    
    # 模拟参数
    n_simulations = 100  # 路径数量
    n_bets = sim_runs    # 每路径投注次数
    starting_bankroll = initial_bankroll
    
    # 基于用户预测准确率（假设比真实概率略高）
    accuracy = pred_prob * 0.9  # 实际准确率通常低于预测
    
    # 生成多条资金曲线
    all_paths = []
    bankruptcy_count = 0
    
    for sim in range(n_simulations):
        bankroll = starting_bankroll
        path = [bankroll]
        
        for bet in range(n_bets):
            # 模拟投注结果，基于预测准确率
            if random.random() < accuracy:
                # 赢 - 获得净盈亏的期望值
                if ev > 0:
                    bankroll += ev + random.uniform(-ev*0.5, ev*0.5)
                else:
                    # 即使预测准确，由于赔率劣势，可能仍然亏损
                    bankroll += random.uniform(ev*2, abs(ev)*0.5)
            else:
                # 输 - 损失总投入
                bankroll -= total_cost * random.uniform(0.8, 1.2)
            
            # 破产检查
            if bankroll <= 0:
                bankroll = 0
                bankruptcy_count += 1
            
            path.append(max(0, bankroll))
        
        all_paths.append(path)
    
    # 可视化
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    
    # 1. 多条资金曲线
    ax1 = axes[0]
    for i, path in enumerate(all_paths[:20]):  # 只显示前20条
        alpha = 0.3 if i > 0 else 0.8
        linewidth = 2 if i == 0 else 0.8
        ax1.plot(path, alpha=alpha, linewidth=linewidth, color='blue')
    
    # 平均路径
    avg_path = np.mean(all_paths, axis=0)
    ax1.plot(avg_path, 'r-', linewidth=3, label='平均路径', alpha=0.8)
    
    ax1.axhline(y=starting_bankroll, color='green', linestyle='--', alpha=0.5, label='初始资金')
    ax1.axhline(y=starting_bankroll/2, color='orange', linestyle='--', alpha=0.5, label='50%亏损线')
    ax1.axhline(y=0, color='red', linestyle='-', alpha=0.3, label='破产线')
    
    ax1.set_xlabel('投注次数')
    ax1.set_ylabel('资金余额 ($)')
    ax1.set_title('长期资金曲线模拟 (20条路径)')
    ax1.legend(loc='upper left', fontsize=8)
    ax1.grid(True, alpha=0.3)
    
    # 2. 最终资金分布
    ax2 = axes[1]
    final_balances = [path[-1] for path in all_paths]
    
    bins = np.linspace(0, max(final_balances) * 1.1, 30)
    ax2.hist(final_balances, bins=bins, edgecolor='black', alpha=0.7, color='skyblue')
    ax2.axvline(x=starting_bankroll, color='green', linestyle='--', linewidth=2, label='初始资金')
    ax2.axvline(x=np.median(final_balances), color='red', linestyle='--', linewidth=2, label='中位数')
    
    ax2.set_xlabel('最终资金 ($)')
    ax2.set_ylabel('频次')
    ax2.set_title(f'最终资金分布 (n={n_simulations})')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. 破产时间分布
    ax3 = axes[2]
    
    bankruptcy_times = []
    for path in all_paths:
        for i, balance in enumerate(path):
            if balance <= 0:
                bankruptcy_times.append(i)
                break
        else:
            bankruptcy_times.append(n_bets + 1)  # 未破产
    
    if bankruptcy_times:
        ax3.hist([t for t in bankruptcy_times if t <= n_bets], 
                bins=30, edgecolor='black', alpha=0.7, color='coral')
        ax3.set_xlabel('破产发生时间 (投注次数)')
        ax3.set_ylabel('频次')
        ax3.set_title(f'破产时间分布 ({bankruptcy_count}/{n_simulations}破产)')
        ax3.grid(True, alpha=0.3)
    
    plt.tight_layout()
    st.pyplot(fig)
    
    # 统计摘要
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("平均最终资金", f"${np.mean(final_balances):.0f}",
                 delta=f"{np.mean(final_balances)-starting_bankroll:+.0f}")
    
    with col2:
        st.metric("中位数资金", f"${np.median(final_balances):.0f}")
    
    with col3:
        bankruptcy_rate = bankruptcy_count / n_simulations * 100
        st.metric("破产概率", f"{bankruptcy_rate:.1f}%")
    
    with col4:
        profitable_rate = sum(1 for b in final_balances if b > starting_bankroll) / n_simulations * 100
        st.metric("盈利路径比例", f"{profitable_rate:.1f}%")
    
    st.markdown(f"""
    <div class="warning-box">
    <strong>模拟结论：</strong><br>
    在{sim_runs}次投注的{100}条模拟路径中，有{bankruptcy_count}条路径发生破产。
    即使有{profitable_rate:.1f}%的路径最终盈利，但<strong>{bankruptcy_rate:.1f}%的破产风险</strong>意味着这不是可持续的策略。
    </div>
    """, unsafe_allow_html=True)

# --- 庄家优势解析 ---
if show_math:
    st.divider()
    st.header("🏢 庄家商业模式解析")
    
    tab1, tab2, tab3 = st.tabs(["数学优势", "数据优势", "行为操纵"])
    
    with tab1:
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.markdown("""
            ### 📊 隐含概率超额
            
            **典型足球比赛赔率：**
            - 主胜: 2.00 (隐含概率 50%)
            - 平局: 3.50 (隐含概率 28.6%)
            - 客胜: 4.00 (隐含概率 25%)
            
            **总计：103.6%**
            
            **庄家优势：3.6%**
            > 这意味着每$100投注，庄家期望盈利$3.6
            """)
        
        with col_b:
            st.markdown("""
            ### 🎲 数学期望计算
            
            **你的真实胜率需求：**
            ```
            收支平衡胜率 = 1 / 赔率
            
            对于2.00赔率：需要50%胜率
            对于1.90赔率：需要52.6%胜率
            对于1.80赔率：需要55.6%胜率
            ```
            
            **现实：**
            - 职业赌徒胜率：约55-58%
            - 普通玩家胜率：约45-52%
            - 庄家确保：<strong>所有人都输在数学上</strong>
            """)
    
    with tab2:
        st.markdown("""
        ### 💡 信息不对称优势
        
        | 庄家优势 | 你的劣势 |
        |----------|----------|
        | ✅ 实时伤病信息 | ❌ 延迟的公开新闻 |
        | ✅ 内部交易数据 | ❌ 不完整的历史数据 |
        | ✅ 全球投注分布 | ❌ 有限的个人视角 |
        | ✅ 精算师团队24/7 | ❌ 业余时间分析 |
        | ✅ 历史大数据 | ❌ 选择性记忆 |
        
        **关键洞察：**
        > 庄家不预测比赛结果，他们预测投注者的行为。
        """)
    
    with tab3:
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.markdown("""
            ### 🧠 认知偏差利用
            
            **赌徒谬误：**
            > "连开5次大，下次必开小"
            
            **确认偏误：**
            > 只记住赢的比赛，为失败找借口
            
            **控制幻觉：**
            > "我研究了数据，这次一定中"
            
            **沉没成本：**
            > "已经输这么多，必须追回来"
            """)
        
        with col_b:
            st.markdown("""
            ### 🎭 心理操控技巧
            
            **诱盘 (Odds Luring)：**
            - 故意设置"太好"的赔率
            - 吸引玩家投注"错误"的一方
            
            **赶盘 (Odds Driving)：**
            - 快速调整赔率制造恐慌
            - 引导大众投注方向
            
            **滚球陷阱：**
            - 利用直播情绪波动
            - 设置临时"诱人"赔率
            
            **高赔诱惑：**
            - 放大极小概率事件
            - 制造"一夜暴富"幻觉
            """)

# --- 心理陷阱分析 ---
if show_psychology:
    st.divider()
    st.header("🧠 常见投注心理陷阱")
    
    # 创建交互式心理测试
    st.write("##### 自我评估：你是否有这些心理倾向？")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        trap1 = st.checkbox("我经常在输钱后加大投注")
        trap2 = st.checkbox("我相信连胜/连败的模式")
    
    with col2:
        trap3 = st.checkbox("我为失败找外部原因（裁判、运气）")
        trap4 = st.checkbox("我只记得赢钱的时候")
    
    with col3:
        # 修正这里：将双引号改为单引号，或使用转义字符
        
        trap6 = st.checkbox("我用赌博来逃避压力")
    
    if any([trap1, trap2, trap3, trap4, trap5, trap6]):
        trap_count = sum([trap1, trap2, trap3, trap4, trap5, trap6])
        st.warning(f"""
        ⚠️ **检测到{trap_count}种危险心理倾向**
        
        这些是庄家最希望看到的玩家特征。每个倾向都会：
        - ✅ 增加你的投注频率
        - ✅ 提高你的平均投注额
        - ✅ 降低你的决策质量
        - ✅ 延长你的游戏时间
        
        **庄家盈利公式：**
        ```
        利润 = 投注额 × 时间 × 庄家优势
        ```
        你的每个心理弱点都在增加公式的前两项。
        """)

# --- 健康建议与替代方案 ---
st.divider()
st.header("💡 健康投注理念与替代方案")

col_advice, col_alternatives = st.columns(2)

with col_advice:
    st.subheader("✅ 健康投注原则")
    
    st.markdown("""
    **如果选择投注（仅限合法地区）：**
    
    1. **预算原则**
    ```
    月投注预算 ≤ 娱乐预算的10%
    单场投注 ≤ 总预算的5%
    永不借贷投注
    ```
    
    2. **记录原则**
    - 记录每笔投注：金额、理由、结果
    - 每月复盘：识别情绪化决策
    - 设置止损止盈线并严格执行
    
    3. **心态原则**
    - 视投注为娱乐消费，而非投资
    - 接受损失是体验的一部分
    - 享受比赛本身，而非赌博
    """)
    
    # 资金管理计算器
    st.write("##### 💰 健康资金管理计算器")
    monthly_income = st.number_input("你的月收入 ($)", value=5000.0, step=100.0)
    
    safe_budget = monthly_income * 0.01  # 1%原则
    weekly_limit = safe_budget / 4
    per_bet_limit = weekly_limit * 0.2
    
    st.info(f"""
    **建议投注限制：**
    - 月投注上限: **${safe_budget:.0f}** (收入的1%)
    - 周投注上限: **${weekly_limit:.0f}**
    - 单场投注上限: **${per_bet_limit:.0f}**
    - 单日损失上限: **${weekly_limit:.0f}**
    """)

with col_alternatives:
    st.subheader("🎮 健康替代方案")
    
    alternatives = [
        {
            "name": "范特西足球",
            "description": "考验真实足球知识和管理能力",
            "skills": ["数据分析", "阵容管理", "战术理解"],
            "cost": "免费或小额报名费"
        },
        {
            "name": "足球经理游戏",
            "description": "无金钱风险的策略游戏",
            "skills": ["长期规划", "财政管理", "球员发展"],
            "cost": "一次性游戏购买"
        },
        {
            "name": "体育数据分析",
            "description": "学习Python/R分析真实足球数据",
            "skills": ["编程", "统计学", "数据可视化"],
            "cost": "免费在线课程"
        },
        {
            "name": "足球分析博客/播客",
            "description": "将研究能力转化为内容创作",
            "skills": ["写作", "分析", "公众演讲"],
            "cost": "时间投入，潜在收入"
        },
        {
            "name": "正规足球博彩",
            "description": "如体育彩票（合法前提下）",
            "skills": ["风险控制", "概率计算"],
            "cost": "小额娱乐预算"
        }
    ]
    
    for alt in alternatives:
        with st.expander(f"**{alt['name']}**"):
            st.markdown(f"""
            **描述：** {alt['description']}
            
            **培养技能：** {', '.join(alt['skills'])}
            
            **成本/收益：** {alt['cost']}
            """)

# --- 学习总结 ---
st.divider()
st.header("📚 核心学习要点")

col_summary1, col_summary2 = st.columns(2)

with col_summary1:
    st.markdown("""
    ### 🎓 数学现实
    
    1. **负期望值游戏**
    - 庄家数学优势确保长期盈利
    - 你的"技巧"无法改变数学现实
    
    2. **概率的残酷**
    - 55%胜率在1.90赔率下仍然亏损
    - 你需要>52.6%胜率才能在1.90赔率下保本
    
    3. **大数定律**
    - 短期可能赢钱
    - 长期必然输给庄家优势
    """)

with col_summary2:
    st.markdown("""
    ### 🧭 实用建议
    
    1. **如果选择投注**
    - 设定严格的资金上限（收入的1%）
    - 记录和分析每笔投注
    - 视作娱乐消费，而非赚钱手段
    
    2. **如果希望停止**
    - 使用自我排除工具
    - 寻求专业帮助
    - 寻找健康的替代活动
    
    3. **最佳选择**
    - 享受足球本身
    - 参与无金钱风险的足球活动
    - 将分析能力用于建设性用途
    """)

# --- 最终警示 ---
st.divider()
st.markdown("""
<div style='text-align: center; padding: 2rem; background-color: #f8d7da; border-radius: 10px;'>
<h3 style='color: #721c24;'>⚠️ 重要提醒</h3>
<p style='color: #721c24; font-size: 1.1rem;'>
<strong>体育投注不是投资，而是娱乐消费。</strong><br>
庄家设计的所有游戏都具有数学优势，确保他们长期盈利。<br>
本工具展示的"对冲策略"虽然降低风险，但无法消除庄家优势。<br>
<br>
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

# --- 交互式学习问答 ---
st.divider()
with st.expander("🤔 互动问答：测试你的理解"):
    st.write("##### 选择正确答案")
    
    q1 = st.radio(
        "1. 庄家的主要盈利来源是什么？",
        ["A. 预测比赛结果比玩家更准", 
         "B. 设置赔率确保数学优势（Overround）", 
         "C. 操纵比赛结果", 
         "D. 依赖运气"]
    )
    
    q2 = st.radio(
        "2. 如果你的长期胜率是55%，赔率是1.90，你的期望值是？",
        ["A. 正期望值，会长期盈利", 
         "B. 负期望值，会长期亏损", 
         "C. 零期望值，长期保本", 
         "D. 无法确定"]
    )
    
    q3 = st.radio(
        "3. 最健康的投注态度是什么？",
        ["A. 视为投资，追求财务自由", 
         "B. 视为娱乐，设定严格预算", 
         "C. 视为技巧游戏，不断练习提高", 
         "D. 视为社交活动，随朋友下注"]
    )
    
    if st.button("提交答案"):
        correct = 0
        if q1 == "B. 设置赔率确保数学优势（Overround）":
            correct += 1
            st.success("✅ 正确！庄家不预测结果，他们通过数学确保盈利。")
        else:
            st.error("❌ 错误。庄家核心优势是数学，不是预测能力。")
        
        if q2 == "A. 正期望值，会长期盈利":
            correct += 1
            st.success("✅ 正确！55% × 1.90 - 1 = 4.5%，是正期望值。")
        else:
            st.error("❌ 错误。0.55 × 1.90 - 1 = 0.045，是正期望值。")
        
        if q3 == "B. 视为娱乐，设定严格预算":
            correct += 1
            st.success("✅ 正确！健康的态度是控制风险，享受过程。")
        else:
            st.error("❌ 错误。投注应视为娱乐消费，不是投资或社交压力。")
        
        st.info(f"得分：{correct}/3 - {['需要更多学习', '理解基本概念', '掌握核心原理'][correct]}")

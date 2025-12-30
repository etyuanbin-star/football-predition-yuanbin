import streamlit as st
import pandas as pd
import numpy as np
import random

# --- 1. 页面配置 ---
st.set_page_config(page_title="胜算实验室：点对点逻辑修正", layout="wide")

st.title("🔺 胜算实验室：全功能风控系统")
st.caption("核心功能：策略模拟 + EV计算 + 蒙特卡洛实验")

# --- 2. 侧边栏输入 ---
with st.sidebar:
    st.header("⚖️ 核心大球项 (O2.5)")
    o25_odds = st.number_input("大球 (3球+) 赔率", value=2.30, step=0.01)
    o25_stake = st.number_input("大球投入金额", value=100.0, step=1.0)
    
    st.divider()
    st.header("🧠 风险参数")
    pred_prob = st.slider("你预测的大球概率 (%)", 10, 90, 45) / 100
    
    st.divider()
    mode = st.radio("请选择执行策略：", ["策略 1：比分精准流", "策略 2：总进球复式流"])
    
    st.divider()
    st.header("🎲 蒙特卡洛实验")
    show_monte_carlo = st.checkbox("启用蒙特卡洛模拟", value=True)
    
    if show_monte_carlo:
        sim_trials = st.slider("模拟试验次数", 100, 10000, 1000)
        sim_bets = st.slider("每次试验投注次数", 10, 500, 100)
        initial_capital = st.number_input("初始资金", value=1000.0)

# --- 3. 逻辑处理核心 ---
st.divider()
col_in, col_out = st.columns([1.6, 2], gap="large")

active_bets = [] 

if mode == "策略 1：比分精准流":
    with col_in:
        st.write("### 🕹️ 设定比分对冲 (点对点校验)")
        # 强制 6 种比分
        scores = ["0-0", "1-0", "0-1", "1-1", "2-0", "0-2"]
        default_odds = {"0-0": 10.0, "1-0": 8.5, "0-1": 8.0, "1-1": 7.0, "2-0": 13.0, "0-2": 12.0}
        
        for s in scores:
            c1, c2, c3 = st.columns([1, 1.2, 1.2])
            with c1: is_on = st.checkbox(s, key=f"s1_{s}")
            with c2: s_amt = st.number_input(f"金额", value=10.0, key=f"s1_am_{s}", label_visibility="collapsed") if is_on else 0.0
            with c3: s_odd = st.number_input(f"赔率", value=default_odds[s], key=f"s1_od_{s}", label_visibility="collapsed") if is_on else 0.0
            if is_on: 
                active_bets.append({"item": s, "odd": s_odd, "stake": s_amt})
        
        active_bets.append({"item": "3球+", "odd": o25_odds, "stake": o25_stake})
        total_cost = sum(b['stake'] for b in active_bets)
        st.metric("💰 方案实际总投入", f"${total_cost:.2f}")

    with col_out:
        st.write("### 📊 模拟盈亏校验 (点对点比分组合图)")
        
        # --- 关键修正点：这里的横坐标必须是具体比分 ---
        s1_outcomes = ["0-0", "1-0", "0-1", "1-1", "2-0", "0-2", "3球+"]
        res_list = []
        
        for out in s1_outcomes:
            # 只有当投注项的名字完全等于模拟赛果的名字时才计入收益
            income = sum(b['stake'] * b['odd'] for b in active_bets if b['item'] == out)
            res_list.append({"模拟赛果": out, "净盈亏": round(income - total_cost, 2)})
        
        df_s1 = pd.DataFrame(res_list)
        
        # 强制指定渲染，不给程序任何模糊空间
        st.bar_chart(df_s1.set_index("模拟赛果")["净盈亏"])
        st.table(df_s1)

else:
    with col_in:
        st.write("### 🕹️ 设定总进球对冲")
        strong_win = st.number_input("稳胆赔率", value=1.35)
        multi_stake = st.number_input("复式对冲总投入", value=100.0)
        
        totals = ["0球", "1球", "2球"]
        img_odds = {"0球": 7.20, "1球": 3.55, "2球": 3.00}
        
        selected = []
        for g in totals:
            c1, c2 = st.columns([1, 2])
            with c1: is_on = st.checkbox(g, key=f"s2_{g}", value=(g != "0球"))
            with c2: g_odd = st.number_input(f"赔率", value=img_odds[g], key=f"s2_od_{g}", label_visibility="collapsed") if is_on else 0.0
            if is_on: selected.append({"name": g, "odd": g_odd})
        
        if selected:
            share = multi_stake / len(selected)
            for item in selected:
                active_bets.append({"item": item['name'], "odd": item['odd'] * strong_win, "stake": share})
        
        active_bets.append({"item": "3球+", "odd": o25_odds, "stake": o25_stake})
        total_cost = sum(b['stake'] for b in active_bets)
        st.metric("💰 方案实际总投入", f"${total_cost:.2f}")

    with col_out:
        st.write("### 📊 模拟盈亏校验 (总进球区间图)")
        s2_outcomes = ["0球", "1球", "2球", "3球+"]
        res_list = []
        for out in s2_outcomes:
            income = sum(b['stake'] * b['odd'] for b in active_bets if b['item'] == out)
            res_list.append({"模拟赛果": out, "净盈亏": round(income - total_cost, 2)})
        
        df_s2 = pd.DataFrame(res_list)
        st.bar_chart(df_s2.set_index("模拟赛果")["净盈亏"])
        st.table(df_s2)

# --- 4. EV计算 ---
st.divider()
st.header("📉 数学期望分析")

# 计算EV
if mode == "策略 1：比分精准流":
    current_df = df_s1
    # 策略1：3球+概率 = pred_prob，每个具体比分平分剩余概率
    prob_per_score = (1 - pred_prob) / 6
    
    ev = 0
    for _, row in current_df.iterrows():
        if row["模拟赛果"] == "3球+":
            ev += row["净盈亏"] * pred_prob
        else:
            ev += row["净盈亏"] * prob_per_score
else:
    current_df = df_s2
    # 策略2：3球+概率 = pred_prob，每个总进球区间平分剩余概率
    prob_per_total = (1 - pred_prob) / 3
    
    ev = 0
    for _, row in current_df.iterrows():
        if row["模拟赛果"] == "3球+":
            ev += row["净盈亏"] * pred_prob
        else:
            ev += row["净盈亏"] * prob_per_total

# 显示EV
col1, col2 = st.columns(2)
with col1:
    st.metric("策略期望值 (EV)", f"${ev:.2f}", 
              delta="正向" if ev > 0 else "负向",
              delta_color="normal" if ev <= 0 else "inverse")

with col2:
    # 简单大球投注的EV
    simple_ev = (pred_prob * o25_odds - 1) * o25_stake
    st.metric("单纯大球投注EV", f"${simple_ev:.2f}")

# EV解释
if ev > 0:
    st.success(f"✅ **理论上有长期盈利可能** | 每次投注期望收益: ${ev:.2f}")
else:
    st.error(f"❌ **负向期望值策略** | 每次投注期望损失: ${abs(ev):.2f}")

# --- 5. 蒙特卡洛实验 ---
if show_monte_carlo and 'sim_trials' in locals():
    st.divider()
    st.header("🎲 蒙特卡洛模拟实验")
    
    st.write(f"模拟设置：{sim_trials}次试验 × {sim_bets}次投注")
    
    # 存储结果
    all_final_balances = []
    all_profitable_trials = []
    
    # 进度条
    progress_bar = st.progress(0)
    
    for trial in range(sim_trials):
        # 更新进度
        if trial % 100 == 0:
            progress_bar.progress(min((trial + 1) / sim_trials, 1.0))
        
        # 初始资金
        capital = initial_capital
        
        # 执行多次投注
        for bet in range(sim_bets):
            # 模拟投注结果
            # 基于预测概率判断是否大球
            is_over25 = random.random() < pred_prob
            
            if is_over25:
                # 大球赢
                capital += o25_stake * (o25_odds - 1)
            else:
                # 大球输
                capital -= o25_stake
            
            # 如果资金为负，则破产
            if capital <= 0:
                capital = 0
                break
        
        all_final_balances.append(capital)
        all_profitable_trials.append(capital > initial_capital)
    
    # 完成进度
    progress_bar.progress(1.0)
    
    # 计算统计
    avg_final = np.mean(all_final_balances)
    median_final = np.median(all_final_balances)
    bankruptcy_count = sum(1 for b in all_final_balances if b <= 0)
    bankruptcy_rate = bankruptcy_count / sim_trials * 100
    profitable_count = sum(all_profitable_trials)
    profitable_rate = profitable_count / sim_trials * 100
    
    # 显示结果
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("平均最终资金", f"${avg_final:.0f}", 
                  delta=f"{avg_final-initial_capital:+.0f}")
    
    with col2:
        st.metric("破产概率", f"{bankruptcy_rate:.1f}%")
    
    with col3:
        st.metric("盈利试验比例", f"{profitable_rate:.1f}%")
    
    with col4:
        st.metric("中位数资金", f"${median_final:.0f}")
    
    # 资金分布直方图
    st.write("##### 📊 最终资金分布")
    
    # 创建分布数据
    bins = 10
    hist_data = np.histogram(all_final_balances, bins=bins)
    
    # 创建DataFrame
    bin_edges = hist_data[1]
    bin_counts = hist_data[0]
    
    bin_labels = []
    for i in range(len(bin_edges)-1):
        if i == 0:
            bin_labels.append(f"${int(bin_edges[i])}-${int(bin_edges[i+1])}")
        else:
            bin_labels.append(f"${int(bin_edges[i])}-${int(bin_edges[i+1])}")
    
    dist_df = pd.DataFrame({
        "资金范围": bin_labels,
        "试验数量": bin_counts
    })
    
    # 显示图表
    st.bar_chart(dist_df.set_index("资金范围"))
    
    # 风险分析
    st.write("##### ⚠️ 风险分析")
    
    if bankruptcy_rate > 30:
        st.error(f"❌ **极高破产风险** ({bankruptcy_rate:.1f}%) - 强烈不建议执行")
    elif bankruptcy_rate > 20:
        st.warning(f"⚠️ **高破产风险** ({bankruptcy_rate:.1f}%) - 需要谨慎操作")
    elif bankruptcy_rate > 10:
        st.info(f"ℹ️ **中等破产风险** ({bankruptcy_rate:.1f}%) - 建议优化策略")
    else:
        st.success(f"✅ **低破产风险** ({bankruptcy_rate:.1f}%) - 风险可控")
    
    # 实验结论
    st.write("##### 💡 实验结论")
    
    if ev > 0 and profitable_rate > 50 and bankruptcy_rate < 15:
        st.success("""
        **策略表现良好**:
        1. 正向期望值 (EV > 0)
        2. 多数试验盈利
        3. 破产风险较低
        
        理论上，长期执行此策略可能盈利。
        """)
    elif ev <= 0:
        st.error("""
        **策略存在根本问题**:
        1. 负向期望值 (EV ≤ 0)
        2. 长期执行必然亏损
        3. 建议重新设计策略
        """)
    else:
        st.warning("""
        **策略表现不稳定**:
        1. 虽然有正向期望值
        2. 但盈利比例或破产风险不理想
        3. 需要进一步优化
        """)

# --- 6. 教育总结 ---
st.divider()
st.header("📚 核心教育总结")

col_summary1, col_summary2 = st.columns(2)

with col_summary1:
    st.markdown("""
    ### 🎓 数学原理
    
    1. **期望值 (EV) 公式**
    ```
    EV = Σ(概率ᵢ × 收益ᵢ) - 总投入
    
    盈利条件：EV > 0
    亏损条件：EV < 0
    ```
    
    2. **庄家优势**
    ```
    庄家赔率 = 1 / (真实概率 + 优势)
    
    优势通常为3-5%
    这意味着：你的长期胜率需要>52.6%才能保本
    ```
    
    3. **大数定律**
    - 短期可能赢钱（运气）
    - 长期必然输给庄家优势
    - 你无法战胜数学
    """)

with col_summary2:
    st.markdown("""
    ### 💡 实用建议
    
    1. **如果选择投注**
    - 设定严格的资金上限
    - 记录每笔投注并分析
    - 视作娱乐消费，而非投资
    
    2. **对冲策略的本质**
    - 降低风险的同时降低潜在收益
    - 无法消除庄家固有的数学优势
    - 只是在不同的亏损方式之间选择
    
    3. **最佳选择**
    - 享受足球比赛本身
    - 参与无金钱风险的足球活动
    - 将分析能力用于建设性用途
    """)

# --- 7. 最终免责声明 ---
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

# --- 8. 脚注 ---
st.caption("""
*本工具仅用于教育目的，展示赌博的数学原理和风险。不鼓励任何形式的赌博行为。*  
*所有计算基于概率理论，实际结果可能因多种因素而异。*  
*如果你需要赌博问题帮助，请联系专业机构。*
""")

import streamlit as st
import pandas as pd

# --- 1. 页面配置 ---
st.set_page_config(page_title="胜算实验室：点对点逻辑修正版", layout="wide")

st.title("🔺 胜算实验室：全功能风控系统")
st.caption("逻辑修正：比分流 6 种组合独立结算 | 风险生存白皮书 | 复式本金修正")

# --- 2. 逻辑白皮书 ---
with st.expander("📖 胜算实验室：核心策略白皮书", expanded=True):
    st.markdown("""
    ### 🛡️ 核心思想：结构化风险转移与生存博弈
    本系统建立在承认“庄家优势”的前提下，通过数学手段将盲目博弈转化为理性的风险管理。

    #### **1. 策略 A：比分流 (精准点对点防御)**
    - **逻辑**：针对 0-2 球区间内最可能出现的 6 种具体比分进行独立防御。
    - **风控核心**：每一个比分都是独立的赛果。**未勾选的比分即使进球数相同，也视为防御真空区。**
    - **目标**：不求小球盈利，只求大球失败时精准回收本金。

    #### **2. 策略 B：复式串关流 (杠杆防御)**
    - **逻辑**：利用“低赔稳胆”拉高 0, 1, 2 球的回报率。
    - **计算**：总本金 = 大球本金 + 复式总投入（不重复计算单注）。

    #### **3. EV 引擎：风险量化与生存**
    - **博弈本质**：长期博弈中玩家无法赢过庄家抽水。
    - **功能**：计算 EV 旨在提醒你当前对冲成本是否过高，量化“失血速度”，延长生存周期。
    """)

# --- 3. 侧边栏：核心输入 ---
with st.sidebar:
    st.header("⚖️ 核心大球项 (O2.5)")
    o25_odds = st.number_input("大球 (3球+) 赔率", value=2.30, step=0.01)
    o25_stake = st.number_input("大球投入金额", value=100.0, step=1.0)
    
    st.divider()
    st.header("🧠 风险预测")
    pred_prob = st.slider("你预测的大球概率 (%)", 10, 90, 45) / 100
    
    st.divider()
    mode = st.radio("请选择策略模式：", ["策略 1：比分精准流", "策略 2：总进球复式流"])

# --- 4. 主输入区：逻辑配置 ---
st.divider()
col_in, col_out = st.columns([1.6, 2], gap="large")

# 存储所有有效注单
active_bets = []
# 始终加入大球
active_bets.append({"项目": "3球+", "赔率": o25_odds, "金额": o25_stake})

with col_in:
    if mode == "策略 1：比分精准流":
        st.write("### 🕹️ 设定比分对冲 (独立校验)")
        scores = ["0-0", "1-0", "0-1", "1-1", "2-0", "0-2"]
        default_odds = {"0-0": 10.0, "1-0": 8.5, "0-1": 8.0, "1-1": 7.0, "2-0": 13.0, "0-2": 12.0}
        
        for s in scores:
            c1, c2, c3 = st.columns([1, 1.2, 1.2])
            with c1: is_on = st.checkbox(s, key=f"s1_{s}")
            with c2: s_amt = st.number_input(f"金额", value=33.0, key=f"s1_am_{s}", label_visibility="collapsed") if is_on else 0.0
            with c3: s_odd = st.number_input(f"赔率", value=default_odds[s], key=f"s1_od_{s}", label_visibility="collapsed") if is_on else 0.0
            if is_on: 
                active_bets.append({"项目": s, "赔率": s_odd, "金额": s_amt})
    
    else:
        st.write("### 🕹️ 设定总进球复式")
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
                active_bets.append({"项目": item['name'], "赔率": item['odd'] * strong_win, "金额": share})

    total_cost = sum(b['金额'] for b in active_bets)
    st.metric("💰 方案实际总投入", f"${total_cost:.2f}")

# --- 5. 盈亏模拟：彻底剥离判定逻辑 ---
with col_out:
    st.write("### 📊 模拟盈亏校验")
    
    # 判定赛果维度
    if mode == "策略 1：比分精准流":
        test_outcomes = ["0-0", "1-0", "0-1", "1-1", "2-0", "0-2", "3球+"]
    else:
        test_outcomes = ["0球", "1球", "2球", "3球+"]
    
    res_data = []
    for out in test_outcomes:
        income = 0
        for b in active_bets:
            # 【核心修正】：严格匹配！只有下注项目完全等于模拟赛果才算中奖
            # 策略1下，下注0-1，赛果1-0，不匹配，收入为0。
            if b['项目'] == out:
                income += b['金额'] * b['赔率']
        
        res_data.append({"模拟赛果": out, "净盈亏": round(income - total_cost, 2)})

    df = pd.DataFrame(res_data)
    st.bar_chart(df.set_index("模拟赛果")["净盈亏"])
    st.table(df)
    
    # EV 监控仪
    st.divider()
    st.subheader("⚠️ EV 风险监控仪")
    # 模拟概率分布
    other_prob = (1 - pred_prob) / (len(test_outcomes) - 1)
    ev = sum(row['净盈亏'] * (pred_prob if row['模拟赛果'] == "3球+" else other_prob) for _, row in df.iterrows())
    
    st.metric("方案单场预期 EV", f"${ev:.2f}")
    if ev < 0:
        st.warning(f"量化警示：当前博弈失血速度为每场 ${abs(ev):.2f}。")
    else:
        st.success("博弈价值：当前组合具备理论生存空间。")

import streamlit as st
import pandas as pd

# --- 1. 页面配置 ---
st.set_page_config(page_title="胜算实验室：逻辑解耦终极版", layout="wide")

st.title("🔺 胜算实验室：全功能风控系统")
st.caption("核心修正：策略1与策略2逻辑完全物理隔离，比分流由6个组合独立结算")

# --- 2. 逻辑白皮书 (体现您的思想) ---
with st.expander("📖 胜算实验室：核心策略白皮书", expanded=True):
    st.markdown("""
    ### 🛡️ 核心思想：结构化风险转移与生存博弈
    本系统建立在承认“庄家优势”的前提下，通过数学手段将盲目博弈转化为理性的风险管理。

    #### **1. 策略 A：比分流 (精准点对点防御)**
    - **核心逻辑**：针对 0-2 球区间内最可能出现的 **6 种具体比分**进行独立防御。
    - **结算维度**：每一个比分都是唯一的。**如果赛果是 1-0 而你只买了 0-1，判定为对冲失败。**
    - **目标**：不求在防御区盈利，只求大球失败时精确回收本金，延长博弈生命。

    #### **2. 策略 B：复式串关流 (杠杆生存)**
    - **核心逻辑**：利用“低赔稳胆”拉高 0, 1, 2 球的回报率。
    - **成本控制**：总本金 = 大球本金 + 复式总投入（不重复计算单项金额）。

    #### **3. EV 引擎：量化失血速度**
    - **博弈本质**：玩家无法在概率上赢过庄家。
    - **功能设定**：EV 旨在量化对冲成本，提醒你何时“防守过头”导致主攻项失去意义。
    """)

# --- 3. 侧边栏：核心数据 ---
with st.sidebar:
    st.header("⚖️ 核心大球项 (O2.5)")
    o25_odds = st.number_input("大球 (3球+) 赔率", value=2.30, step=0.01)
    o25_stake = st.number_input("大球投入金额", value=100.0, step=1.0)
    
    st.divider()
    st.header("🧠 风险参数")
    pred_prob = st.slider("你预测的大球概率 (%)", 10, 90, 45) / 100
    
    st.divider()
    mode = st.radio("请选择执行策略：", ["策略 1：比分精准流", "策略 2：总进球复式流"])

# --- 4. 逻辑处理区 (完全解耦) ---
st.divider()
col_in, col_out = st.columns([1.6, 2], gap="large")

# 初始化数据
active_bets = []
test_outcomes = []

# --- 物理隔离逻辑 A：比分流 ---
if mode == "策略 1：比分精准流":
    with col_in:
        st.write("### 🕹️ 设定比分对冲 (6 种组合校验)")
        scores = ["0-0", "1-0", "0-1", "1-1", "2-0", "0-2"]
        default_odds = {"0-0": 10.0, "1-0": 8.5, "0-1": 8.0, "1-1": 7.0, "2-0": 13.0, "0-2": 12.0}
        
        for s in scores:
            c1, c2, c3 = st.columns([1, 1.2, 1.2])
            with c1: is_on = st.checkbox(s, key=f"s1_{s}")
            with c2: s_amt = st.number_input(f"金额", value=33.0, key=f"s1_am_{s}", label_visibility="collapsed") if is_on else 0.0
            with c3: s_odd = st.number_input(f"赔率", value=default_odds[s], key=f"s1_od_{s}", label_visibility="collapsed") if is_on else 0.0
            if is_on: 
                active_bets.append({"item": s, "odd": s_odd, "stake": s_amt})
        
        active_bets.append({"item": "3球+", "odd": o25_odds, "stake": o25_stake})
        total_cost = sum(b['stake'] for b in active_bets)
        st.metric("💰 策略1总投入", f"${total_cost:.2f}")

    with col_out:
        st.write("### 📊 比分流：点对点盈亏校验")
        test_outcomes = ["0-0", "1-0", "0-1", "1-1", "2-0", "0-2", "3球+"]
        res_list = []
        for out in test_outcomes:
            income = sum(b['stake'] * b['odd'] for b in active_bets if b['item'] == out)
            res_list.append({"模拟赛果": out, "净盈亏": round(income - total_cost, 2)})
        
        df = pd.DataFrame(res_list)
        st.bar_chart(df.set_index("模拟赛果")["净盈亏"])
        st.table(df)

# --- 物理隔离逻辑 B：总进球流 ---
else:
    with col_in:
        st.write("### 🕹️ 设定总进球对冲 (复式串关)")
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
        st.metric("💰 策略2总投入", f"${total_cost:.2f}")

    with col_out:
        st.write("### 📊 总进球流：区间盈亏校验")
        test_outcomes = ["0球", "1球", "2球", "3球+"]
        res_list = []
        for out in test_outcomes:
            income = sum(b['stake'] * b['odd'] for b in active_bets if b['item'] == out)
            res_list.append({"模拟赛果": out, "净盈亏": round(income - total_cost, 2)})
        
        df = pd.DataFrame(res_list)
        st.bar_chart(df.set_index("模拟赛果")["净盈亏"])
        st.table(df)

# --- 5. 统一 EV 监控 ---
st.divider()
st.subheader("⚠️ EV 风险监控仪")
other_prob = (1 - pred_prob) / (len(test_outcomes) - 1)
ev_val = sum(row['净盈亏'] * (pred_prob if row['模拟赛果'] == "3球+" else other_prob) for _, row in df.iterrows())

c1, c2 = st.columns(2)
with c1:
    st.metric("方案预期 EV", f"${ev_val:.2f}")
with c2:
    if ev_val < 0:
        st.warning(f"量化提醒：该方案处于失血状态，每场平均损耗 ${abs(ev_val):.2f}。")
    else:
        st.success("博弈价值：当前组合具备理论生存空间。")

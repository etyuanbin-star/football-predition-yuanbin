import streamlit as st
import pandas as pd

# --- 1. 页面配置 ---
st.set_page_config(page_title="胜算实验室：比分点对点校验版", layout="wide")

st.title("🔺 胜算实验室：全功能风控系统")

# --- 2. 逻辑白皮书 (体现您的博弈思想) ---
with st.expander("📖 胜算实验室：核心策略白皮书", expanded=True):
    st.markdown("""
    ### 🛡️ 核心思想：结构化风险转移与生存博弈
    本系统建立在承认“庄家优势”的前提下，通过数学手段将盲目博弈转化为理性的风险管理。

    #### **1. 策略 A：比分流 (精准防御)**
    - **逻辑**：针对 0-2 球区间内最可能出现的 6 种比分进行点对点防御。
    - **风控核心**：不追求在小球区盈利，而是通过精准投入，确保大球失败时，本金能最大程度回收。

    #### **2. 策略 B：复式串关流 (杠杆生存)**
    - **逻辑**：利用“低赔稳胆”拉高 0, 1, 2 球的回报率，降低对冲成本。

    #### **3. 风险监控：承认玩家无法赢过庄家**
    - **博弈本质**：长期博弈中，由于抽水存在，玩家无法赢过庄家。
    - **EV 意义**：计算 EV 不是为了预测盈利，而是量化“失血速度”。 如果 EV 严重为负，说明对冲成本已侵蚀生存空间，系统将强制发出警告。
    """)

# --- 3. 侧边栏配置 ---
with st.sidebar:
    st.header("⚖️ 核心大球项 (O2.5)")
    o25_odds = st.number_input("大球 (3球+) 赔率", value=2.30, step=0.01)
    o25_stake = st.number_input("大球投入金额", value=100.0, step=1.0)
    
    st.divider()
    st.header("🧠 风险参数")
    pred_prob = st.slider("你预测的大球概率 (%)", 10, 90, 45) / 100
    
    st.divider()
    mode = st.radio("请选择策略模式：", ["策略 1：比分精准流", "策略 2：总进球复式流"])

# --- 4. 主输入区 ---
st.divider()
col_in, col_out = st.columns([1.5, 2], gap="large")

active_bets = []
# 始终加入大球主攻项
active_bets.append({"项目": "3球+", "赔率": o25_odds, "金额": o25_stake, "分类": "主攻"})

with col_in:
    if mode == "策略 1：比分精准流":
        st.write("### 🕹️ 设定比分对冲 (点对点校验)")
        scores = ["0-0", "1-0", "0-1", "1-1", "2-0", "0-2"]
        default_odds = {"0-0": 10.0, "1-0": 8.5, "0-1": 8.0, "1-1": 7.0, "2-0": 13.0, "0-2": 12.0}
        
        for s in scores:
            c1, c2, c3 = st.columns([1, 1.2, 1.2])
            with c1: is_on = st.checkbox(s, key=f"s1_{s}", value=False)
            # 用户可以自行输入每个比分的金额和赔率
            with c2: s_amt = st.number_input(f"{s}金额", value=33.0, key=f"s1_am_{s}", label_visibility="collapsed") if is_on else 0.0
            with c3: s_odd = st.number_input(f"{s}赔率", value=default_odds[s], key=f"s1_od_{s}", label_visibility="collapsed") if is_on else 0.0
            if is_on: active_bets.append({"项目": s, "赔率": s_odd, "金额": s_amt, "分类": "对冲"})
    
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
            # 支持自行输入总进球赔率
            with c2: g_odd = st.number_input(f"{g}赔率", value=img_odds[g], key=f"s2_od_{g}", label_visibility="collapsed") if is_on else 0.0
            if is_on: selected.append({"name": g, "odd": g_odd})
        
        if selected:
            share = multi_stake / len(selected)
            for item in selected:
                active_bets.append({"项目": item['name'], "赔率": item['odd'] * strong_win, "金额": share, "分类": "对冲"})

    total_cost = sum(b['金额'] for b in active_bets)
    st.metric("💰 方案实际总投入 (Total Stake)", f"${total_cost:.2f}")

# --- 5. 盈亏模拟与 EV 监控 ---
with col_out:
    st.write("### 📊 模拟盈亏校验")
    
    # 核心修正：比分流下，模拟每个具体比分的盈亏，而不是总进球
    if mode == "策略 1：比分精准流":
        test_outcomes = ["0-0", "1-0", "0-1", "1-1", "2-0", "0-2", "3球+"]
    else:
        test_outcomes = ["0球", "1球", "2球", "3球+"]
    
    res_data = []
    for out in test_outcomes:
        income = 0
        for b in active_bets:
            # 只有当赛果完全匹配下注项目时才算回款
            if b['项目'] == out:
                income += b['金额'] * b['赔率']
        
        res_data.append({"模拟赛果": out, "净盈亏": round(income - total_cost, 2)})

    df = pd.DataFrame(res_data)
    
    # 柱状图直观显示哪些比分没被覆盖（会出现负柱）
    st.bar_chart(df.set_index("模拟赛果")["净盈亏"])
    st.table(df)
    
    # EV 风险监控
    st.divider()
    st.subheader("⚠️ 风险监控与 EV")
    # 计算平均分配给非大球项的概率
    other_prob = (1 - pred_prob) / (len(test_outcomes) - 1)
    ev = sum(row['净盈亏'] * (pred_prob if row['模拟赛果'] == "3球+" else other_prob) for _, row in df.iterrows())
    
    st.metric("方案单场 EV (量化失血速度)", f"${ev:.2f}")
    if ev < 0:
        st.warning(f"提醒：当前对冲配置下，每场博弈理论损失 ${abs(ev):.2f}。请优化赔率或注单。")
    else:
        st.success("理想状态：该组合具备数学上的生存价值。")

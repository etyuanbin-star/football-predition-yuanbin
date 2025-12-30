import streamlit as st
import pandas as pd

# --- 1. 页面配置 ---
st.set_page_config(page_title="胜算实验室：点对点逻辑修正", layout="wide")

st.title("🔺 胜算实验室：全功能风控系统")
st.caption("核心修正：比分流 6 种组合独立结算，严禁共用总进球逻辑")

# --- 2. 核心思想白皮书 ---
with st.expander("📖 胜算实验室：核心策略白皮书", expanded=True):
    st.markdown("""
    ### 🛡️ 核心思想：结构化风险转移与生存博弈
    本系统建立在承认“庄家优势”的前提下，通过数学手段将盲目博弈转化为理性的风险管理。

    #### **1. 策略 A：比分流 (精准点对点防御)**
    - **核心逻辑**：针对 0-2 球区间内最可能出现的 **6 种具体比分**进行独立防御。
    - **结算维度**：每一个比分都是唯一的独立赛果。**未勾选的比分即便总进球数相同，也视为防御真空区。**
    - **风险本质**：不求在防御区盈利，只求大球失败时精确回收本金，延长生存周期。

    #### **2. 策略 B：复式串关流 (杠杆生存)**
    - **核心逻辑**：利用“低赔稳胆”拉高 0, 1, 2 球区间的回报。
    - **成本控制**：总本金 = 大球本金 + 复式总投入。

    #### **3. 风险监控：承认玩家无法赢过庄家**
    - **博弈本质**：长期博弈中玩家无法赢过庄家。
    - **EV 意义**：量化对冲成本导致的“失血速度”，提醒玩家不要过度防守。
    """)

# --- 3. 侧边栏输入 ---
with st.sidebar:
    st.header("⚖️ 核心大球项 (O2.5)")
    o25_odds = st.number_input("大球 (3球+) 赔率", value=2.30, step=0.01)
    o25_stake = st.number_input("大球投入金额", value=100.0, step=1.0)
    
    st.divider()
    st.header("🧠 风险参数")
    pred_prob = st.slider("你预测的大球概率 (%)", 10, 90, 45) / 100
    
    st.divider()
    mode = st.radio("请选择执行策略：", ["策略 1：比分精准流", "策略 2：总进球复式流"])

# --- 4. 逻辑处理区 ---
st.divider()
col_in, col_out = st.columns([1.6, 2], gap="large")

active_bets = [] # 存储有效注单

if mode == "策略 1：比分精准流":
    with col_in:
        st.write("### 🕹️ 设定比分对冲 (点对点校验)")
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
        st.write("### 📊 模拟盈亏校验 (6 组独立结算)")
        # 核心：这里的 outcomes 必须是具体的比分组合
        test_outcomes = ["0-0", "1-0", "0-1", "1-1", "2-0", "0-2", "3球+"]
        res_list = []
        for out in test_outcomes:
            # 只有项目完全一致时才算中奖，实现点对点精准校验
            income = sum(b['stake'] * b['odd'] for b in active_bets if b['item'] == out)
            res_list.append({"模拟赛果": out, "净盈亏": round(income - total_cost, 2)})
        
        df = pd.DataFrame(res_list)
        st.bar_chart(df.set_index("模拟赛果")["净盈亏"])
        st.table(df)

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
        st.write("### 📊 模拟盈亏校验 (总进球区间)")
        test_outcomes = ["0球", "1球", "2球", "3球+"]
        res_list = []
        for out in test_outcomes:
            income = sum(b['stake'] * b['odd'] for b in active_bets if b['item'] == out)
            res_list.append({"模拟赛果": out, "净盈亏": round(income - total_cost, 2)})
        
        df = pd.DataFrame(res_list)
        st.bar_chart(df.set_index("模拟赛果")["净盈亏"])
        st.table(df)

# --- 5. 统一风险监控 ---
st.divider()
other_prob = (1 - pred_prob) / (len(test_outcomes) - 1)
ev_val = sum(row['净盈亏'] * (pred_prob if row['模拟赛果'] == "3球+" else other_prob) for _, row in df.iterrows())
st.subheader(f"⚠️ 风险监控仪：方案预期 EV 为 ${ev_val:.2f}")

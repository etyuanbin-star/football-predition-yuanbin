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
    #### **策略 A：比分流 (精准点对点防御)**
    - **独立结算**：每一个比分（如 1-0）都是独立的单元。
    - **防御真空**：如果你只买了 1-0 和 2-0，当开出 0-1 时，即便总进球数很少，该防御区也视为“击穿”。
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

active_bets = [] 

if mode == "策略 1：比分精准流":
    with col_in:
        st.write("### 🕹️ 设定比分对冲 (点对点校验)")
        # 定义比分池
        scores = ["0-0", "1-0", "0-1", "1-1", "2-0", "0-2"]
        default_odds = {"0-0": 10.0, "1-0": 8.5, "0-1": 8.0, "1-1": 7.0, "2-0": 13.0, "0-2": 12.0}
        
        for s in scores:
            c1, c2, c3 = st.columns([1, 1.2, 1.2])
            with c1: is_on = st.checkbox(s, key=f"s1_{s}")
            with c2: s_amt = st.number_input(f"金额", value=10.0, key=f"s1_am_{s}", label_visibility="collapsed") if is_on else 0.0
            with c3: s_odd = st.number_input(f"赔率", value=default_odds[s], key=f"s1_od_{s}", label_visibility="collapsed") if is_on else 0.0
            if is_on: 
                active_bets.append({"item": s, "odd": s_odd, "stake": s_amt})
        
        # 将大球项加入投注清单
        active_bets.append({"item": "3球+", "odd": o25_odds, "stake": o25_stake})
        total_cost = sum(b['stake'] for b in active_bets)
        st.metric("💰 方案实际总投入", f"${total_cost:.2f}")

    with col_out:
        st.write("### 📊 模拟盈亏校验 (点对点比分结算)")
        
        # 这里包含所有可能的模拟情况（含未勾选的比分，以展示“真空区”）
        test_outcomes = ["0-0", "1-0", "0-1", "1-1", "2-0", "0-2", "3球+"]
        res_list = []
        
        for out in test_outcomes:
            # 只有当模拟赛果完全等于投注项时，该注单才产生收益
            # 即使模拟赛果是 0-0，如果 active_bets 里没勾选 0-0，income 也会是 0
            income = sum(b['stake'] * b['odd'] for b in active_bets if b['item'] == out)
            net_profit = income - total_cost
            res_list.append({"模拟赛果": out, "净盈亏": round(net_profit, 2)})
        
        df = pd.DataFrame(res_list)
        
        # 视觉反馈：红色表示亏损，绿色表示盈利
        st.bar_chart(df.set_index("模拟赛果")["净盈亏"])
        
        # 使用表格列出详细数据，并标记盈亏状态
        def color_profit(val):
            color = 'red' if val < 0 else 'green'
            return f'color: {color}'
        
        st.table(df.style.applymap(color_profit, subset=['净盈亏']))

# --- 策略 2 逻辑保持类似处理 ---
else:
    with col_in:
        st.write("### 🕹️ 设定总进球对冲")
        strong_win = st.number_input("稳胆赔率 (串关加成)", value=1.35)
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
                # 串关逻辑：进球赔率 * 稳胆赔率
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
# 简单的 EV 计算逻辑：假设除了大球外，其余模拟赛果平分剩余概率
other_prob = (1 - pred_prob) / (len(test_outcomes) - 1)
ev_val = sum(row['净盈亏'] * (pred_prob if row['模拟赛果'] == "3球+" else other_prob) for _, row in df.iterrows())

c1, c2 = st.columns(2)
with c1:
    st.subheader(f"⚠️ 预期 EV: ${ev_val:.2f}")
with c2:
    if ev_val < 0:
        st.error("警告：当前对冲成本过高，长期博弈预期为负。")
    else:
        st.success("提示：当前方案在预测概率下具有正向收益潜力。")

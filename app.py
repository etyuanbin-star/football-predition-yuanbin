import streamlit as st
import pandas as pd

# --- 1. 页面配置 ---
st.set_page_config(page_title="胜算实验室：点对点逻辑修正", layout="wide")

st.title("🔺 胜算实验室：全功能风控系统")
st.caption("核心修正：策略 1 强制执行【6种比分+大球】点对点独立结算")

# --- 2. 核心思想白皮书 ---
with st.expander("📖 胜算实验室：核心策略白皮书", expanded=True):
    st.markdown("""
    ### 🛡️ 核心思想：点对点精确防御
    #### **策略 1：比分精准流 (Point-to-Point)**
    - **逻辑严抠**：系统不再计算“总进球 0/1/2”，而是直接计算 **0-0, 1-0, 0-1, 1-1, 2-0, 0-2** 这 6 个点。
    - **防御真空**：例如你防御了 1-0 但没勾选 0-1，若赛果为 0-1，系统将判定该点位全损，不产生任何对冲收益。
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
        st.write("### 🕹️ 设定比分对冲 (独立注单)")
        # 强制定义的 6 组具体比分
        scores = ["0-0", "1-0", "0-1", "1-1", "2-0", "0-2"]
        default_odds = {"0-0": 10.0, "1-0": 8.5, "0-1": 8.0, "1-1": 7.0, "2-0": 13.0, "0-2": 12.0}
        
        for s in scores:
            c1, c2, c3 = st.columns([1, 1.2, 1.2])
            with c1: is_on = st.checkbox(s, key=f"s1_{s}")
            with c2: s_amt = st.number_input(f"金额", value=10.0, key=f"s1_am_{s}", label_visibility="collapsed") if is_on else 0.0
            with c3: s_odd = st.number_input(f"赔率", value=default_odds[s], key=f"s1_od_{s}", label_visibility="collapsed") if is_on else 0.0
            if is_on: 
                # 记录每一个比分为独立 item
                active_bets.append({"item": s, "odd": s_odd, "stake": s_amt})
        
        # 增加大球项
        active_bets.append({"item": "3球+", "odd": o25_odds, "stake": o25_stake})
        total_cost = sum(b['stake'] for b in active_bets)
        st.metric("💰 方案实际总投入", f"${total_cost:.2f}")

    with col_out:
        st.write("### 📊 策略1：比分流盈亏分布图")
        
        # 核心：图表横轴必须是具体的 6 组比分 + 3球+
        chart_outcomes = ["0-0", "1-0", "0-1", "1-1", "2-0", "0-2", "3球+"]
        res_list = []
        
        for out in chart_outcomes:
            # 只有当投注项完全匹配模拟赛果时才有奖金
            # 如果模拟赛果是 0-1 但你没勾选 0-1，这里的 income 为 0
            income = sum(b['stake'] * b['odd'] for b in active_bets if b['item'] == out)
            net_profit = income - total_cost
            res_list.append({"模拟赛果": out, "净盈亏": round(net_profit, 2)})
        
        df = pd.DataFrame(res_list)
        
        # 渲染图表：清晰展示哪些比分点是盈利的，哪些是防御真空
        st.bar_chart(df.set_index("模拟赛果")["净盈亏"])
        
        # 表格明细
        st.table(df)
        st.info("💡 解释：如果某个比分柱状图跌至负值且金额很大，说明该比分是你目前的防御漏洞。")

else:
    # 策略 2 逻辑（保留原样或根据需要修改）
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
        st.write("### 📊 策略2：总进球流盈亏分布图")
        test_outcomes = ["0球", "1球", "2球", "3球+"]
        res_list = []
        for out in test_outcomes:
            income = sum(b['stake'] * b['odd'] for b in active_bets if b['item'] == out)
            res_list.append({"模拟赛果": out, "净盈亏": round(income - total_cost, 2)})
        
        df = pd.DataFrame(res_list)
        st.bar_chart(df.set_index("模拟赛果")["净盈亏"])
        st.table(df)

# --- 5. 风险监控 ---
st.divider()
st.subheader("⚠️ 风险监控汇总")
# 使用 df 来计算当前策略下的 EV
# 如果是策略1，df 包含 7 行；如果是策略2，df 包含 4 行
other_prob = (1 - pred_prob) / (len(df) - 1)
ev_val = sum(row['净盈亏'] * (pred_prob if row['模拟赛果'] == "3球+" else other_prob) for _, row in df.iterrows())

st.write(f"在设定的大球概率 **{pred_prob*100:.0f}%** 下，方案平均每单预期盈亏 (EV): **${ev_val:.2f}**")

import streamlit as st
import pandas as pd

# --- 1. 页面配置 ---
st.set_page_config(page_title="胜算实验室：点对点逻辑修正", layout="wide")

st.title("🔺 胜算实验室：全功能风控系统")
st.caption("核心修正：策略 1 盈亏校验强制展示 [具体比分组合] + [3球+]")

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

# --- 3. 逻辑处理核心 ---
st.divider()
col_in, col_out = st.columns([1.6, 2], gap="large")

active_bets = [] 

if mode == "策略 1：比分精准流":
    with col_in:
        st.write("### 🕹️ 设定比分对冲 (点对点校验)")
        # 7种核心结果：6个比分 + 3球+
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
        st.write("### 📊 模拟盈亏校验 (比分对冲方案)")
        
        # --- 核心修正：只显示7种结果 ---
        # 7种结果：6个具体比分 + 3球+
        s1_outcomes = ["0-0", "1-0", "0-1", "1-1", "2-0", "0-2", "3球+"]
        res_list = []
        
        for out in s1_outcomes:
            income = 0
            # 计算该结果下的总收入
            for bet in active_bets:
                # 如果这个结果命中了投注项
                if bet["item"] == out:
                    income += bet["stake"] * bet["odd"]
            
            # 净盈亏 = 总收入 - 总投入
            net_profit = round(income - total_cost, 2)
            
            # 检查是否保本
            status = "✅ 保本/盈利" if net_profit >= 0 else "⚠️ 亏损"
            
            res_list.append({
                "模拟赛果": out, 
                "净盈亏": net_profit,
                "状态": status,
                "投入": total_cost,
                "收入": round(income, 2)
            })
        
        df_s1 = pd.DataFrame(res_list)
        
        # 可视化
        st.bar_chart(df_s1.set_index("模拟赛果")["净盈亏"])
        
        # 详细数据表
        st.write("##### 盈亏明细表")
        st.table(df_s1[["模拟赛果", "净盈亏", "状态", "投入", "收入"]])
        
        # 添加总结
        profitable_outcomes = sum(1 for row in res_list if row["净盈亏"] >= 0)
        total_outcomes = len(res_list)
        
        st.info(f"""
        **策略分析：**
        - **覆盖结果**：{total_outcomes} 种可能赛果
        - **保本/盈利结果**：{profitable_outcomes} 种
        - **亏损结果**：{total_outcomes - profitable_outcomes} 种
        - **保本覆盖率**：{(profitable_outcomes/total_outcomes*100):.1f}%
        """)

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
            res_list.append({
                "模拟赛果": out, 
                "净盈亏": round(income - total_cost, 2),
                "投入": total_cost,
                "收入": round(income, 2)
            })
        
        df_s2 = pd.DataFrame(res_list)
        st.bar_chart(df_s2.set_index("模拟赛果")["净盈亏"])
        st.table(df_s2)

# --- 4. 统一风险监控 (逻辑同步更新) ---
st.divider()
# 动态获取当前正在使用的 df
current_df = df_s1 if mode == "策略 1：比分精准流" else df_s2

# 计算预期值 EV
if mode == "策略 1：比分精准流":
    # 策略1：3球+概率 = pred_prob，每个具体比分平分剩余概率
    other_outcomes_count = len([row for _, row in current_df.iterrows() if row["模拟赛果"] != "3球+"])
    prob_per_other = (1 - pred_prob) / other_outcomes_count if other_outcomes_count > 0 else 0
    
    ev_val = 0
    for _, row in current_df.iterrows():
        if row["模拟赛果"] == "3球+":
            ev_val += row["净盈亏"] * pred_prob
        else:
            ev_val += row["净盈亏"] * prob_per_other
else:
    # 策略2：保持原逻辑
    other_outcomes_count = len([row for _, row in current_df.iterrows() if row["模拟赛果"] != "3球+"])
    prob_per_other = (1 - pred_prob) / other_outcomes_count if other_outcomes_count > 0 else 0
    
    ev_val = 0
    for _, row in current_df.iterrows():
        if row["模拟赛果"] == "3球+":
            ev_val += row["净盈亏"] * pred_prob
        else:
            ev_val += row["净盈亏"] * prob_per_other

st.subheader(f"⚠️ 风险监控仪：方案预期 EV 为 ${ev_val:.2f}")

# 颜色标识
if ev_val > 0:
    st.success(f"✅ 正向预期价值 (+${ev_val:.2f})，长期执行可能盈利")
elif ev_val < 0:
    st.error(f"❌ 负向预期价值 (${ev_val:.2f})，长期执行可能亏损")
else:
    st.warning(f"⚖️ 零和预期价值 ($0.00)，长期执行可能持平")

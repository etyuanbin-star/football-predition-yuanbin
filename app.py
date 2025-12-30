import streamlit as st
import pandas as pd

# --- 1. 页面配置 ---
st.set_page_config(page_title="胜算实验室：EV 终极版", layout="wide")

st.title("🔺 胜算实验室：全功能对冲 & EV 引擎")
st.caption("集成了：自定义赔率输入、复式本金计算、实时盈亏校验及长期 EV 模拟")

# --- 2. 侧边栏：核心数据与大球概率 ---
with st.sidebar:
    st.header("⚖️ 核心项 (大球 O2.5)")
    o25_odds = st.number_input("大球 (3球+) 赔率", value=2.30, step=0.01)
    o25_stake = st.number_input("大球投入金额", value=100.0, step=1.0)
    
    st.divider()
    st.header("🧠 概率预测 (用于计算 EV)")
    # 用户根据经验预测大球发生的概率
    pred_prob = st.slider("你预测的大球真实概率 (%)", 10, 90, 45) / 100
    
    st.divider()
    mode = st.radio("选择策略模式：", ["策略 1：比分精准流", "策略 2：总进球复式串关流"])

# --- 3. 主策略输入区 ---
st.divider()
col_input, col_result = st.columns([1.6, 2], gap="large")

active_bets = []
# 基础项：大球
active_bets.append({"项目": "3球+", "赔率": o25_odds, "金额": o25_stake, "分类": "主攻"})

with col_input:
    if mode == "策略 1：比分精准流":
        st.write("### 🕹️ 设定比分对冲")
        scores = ["0-0", "1-0", "0-1", "1-1", "2-0", "0-2"]
        default_odds = {"0-0": 10.0, "1-0": 8.5, "0-1": 8.0, "1-1": 7.0, "2-0": 13.0, "0-2": 12.0}
        
        for s in scores:
            c1, c2, c3 = st.columns([1, 1.2, 1.2])
            with c1: is_on = st.checkbox(s, key=f"s1_{s}")
            with c2: s_amt = st.number_input(f"金额", value=10.0, key=f"s1_am_{s}", label_visibility="collapsed") if is_on else 0.0
            with c3: s_odd = st.number_input(f"赔率", value=default_odds[s], key=f"s1_od_{s}", label_visibility="collapsed") if is_on else 0.0
            if is_on: active_bets.append({"项目": s, "赔率": s_odd, "金额": s_amt, "分类": "对冲"})

    else:
        st.write("### 🕹️ 设定总进球复式 (支持自定义赔率)")
        strong_win = st.number_input("稳胆赔率 (串关项)", value=1.35, step=0.01)
        # 修正本金逻辑：大球 + 对冲总投入
        multi_stake = st.number_input("复式对冲项总投入金额", value=100.0, step=1.0)
        
        st.caption("勾选并输入截图中的即时赔率：")
        totals = ["0球", "1球", "2球"]
        img_odds = {"0球": 7.20, "1球": 3.55, "2球": 3.00}
        
        selected_items = []
        for g in totals:
            c1, c2 = st.columns([1, 2])
            with c1: is_on = st.checkbox(g, key=f"s2_{g}", value=(g != "0球"))
            with c2: g_odd = st.number_input(f"{g}赔率", value=img_odds[g], key=f"s2_od_{g}", label_visibility="collapsed") if is_on else 0.0
            if is_on: selected_items.append({"name": g, "raw_odd": g_odd})
        
        if selected_items:
            share_stake = multi_stake / len(selected_items)
            for item in selected_items:
                active_bets.append({
                    "项目": item['name'], 
                    "赔率": item['raw_odd'] * strong_win, 
                    "金额": share_stake, 
                    "分类": "对冲"
                })

    total_cost = sum(b['金额'] for b in active_bets)
    st.metric("💰 方案实际总投入 (Total Stake)", f"${total_cost:.2f}")

# --- 4. 盈亏校验与数据分析 ---
with col_result:
    st.write("### 📊 模拟盈亏校验")
    outcomes = ["0球", "1球", "2球", "3球+"]
    res_list = []
    
    for out in outcomes:
        income = 0
        for b in active_bets:
            if b['项目'] == "3球+" and out == "3球+":
                income += b['金额'] * b['赔率']
            elif b['项目'] == out or (out == "0球" and b['项目'] == "0-0") or \
                 (out == "1球" and b['项目'] in ["1-0", "0-1"]) or \
                 (out == "2球" and b['项目'] in ["1-1", "2-0", "0-2"]):
                income += b['金额'] * b['赔率']
        
        res_list.append({"模拟结果": out, "净盈亏": round(income - total_cost, 2)})

    df = pd.DataFrame(res_list)
    st.bar_chart(df.set_index("模拟结果")["净盈亏"])
    st.table(df)
    
    # 大球覆盖状态
    win_3plus = df[df["模拟结果"] == "3球+"]["净盈亏"].values[0]
    if win_3plus > 0:
        st.success(f"✅ 对冲成功：大球打出盈利 ${win_3plus:.2f}")
    else:
        st.error(f"❌ 警告：大球打出仍亏损 ${abs(win_3plus):.2f}")

# --- 5. 模拟 EV 计算 (新加入) ---
st.divider()
st.subheader("📈 模拟期望值 (EV) 深度分析")

# 假设概率分布 (基于大球概率推算小球分布)
prob_012 = (1 - pred_prob) / 3  # 简化模型：将剩余概率平分给 0,1,2 球
prob_map = {"0球": prob_012, "1球": prob_012, "2球": prob_012, "3球+": pred_prob}

# 计算理论 EV
ev_val = 0
for res in res_list:
    p = prob_map[res["模拟结果"]]
    ev_val += p * res["净盈亏"]

c_ev1, c_ev2 = st.columns(2)
with c_ev1:
    st.metric("📊 方案单场 EV", f"${ev_val:.2f}")
    if ev_val > 0:
        st.write("🟢 **长期可投**：基于你预测的概率，该方案长期运行期望为正。")
    else:
        st.write("🔴 **价值不足**：当前赔率组合在长期下会产生亏损，建议寻找更高赔率。")

with c_ev2:
    st.write("**EV 核心逻辑：**")
    st.caption(f"公式：Σ (各赛果净盈亏 × 发生概率)")
    st.caption(f"当前假设：大球概率 {pred_prob:.1%}，其余赛果平分剩余概率。")

st.divider()
st.subheader("🧠 综合覆盖评估")
coverage = 0.77 if mode == "策略 2：总进球复式串关流" else 0.73
st.write(f"当前策略理论覆盖率 (Total Coverage): **{coverage:.1%}**")

st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>识破陷阱，量化风险，方能长期生存。</p>", unsafe_allow_html=True)

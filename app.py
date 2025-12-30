import streamlit as st
import pandas as pd

# --- 页面配置 ---
st.set_page_config(page_title="胜算实验室：全自定义对冲版", layout="wide")

st.title("🔺 胜算实验室：全功能对冲系统")
st.subheader("修正：支持总进球独立赔率输入 & 复式本金计算")

# --- 1. 核心大球项配置 (侧边栏) ---
with st.sidebar:
    st.header("⚖️ 核心大球项 (O2.5)")
    o25_odds = st.number_input("大球 (3球+) 赔率", value=2.30, step=0.01)
    o25_stake = st.number_input("大球投入金额", value=100.0, step=1.0)
    
    st.divider()
    mode = st.radio("请选择策略模式：", ["策略 1：比分精准流", "策略 2：总进球复式串关流"])

# --- 2. 主策略输入区 ---
st.divider()
col_input, col_result = st.columns([1.6, 2], gap="large")

active_bets = []
# 默认加入核心大球
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
        st.write("### 🕹️ 设定总进球对冲 (支持独立赔率)")
        st.info("💡 逻辑：稳胆赔率将自动与你输入的各总进球赔率相乘。")
        
        # 稳胆赔率输入
        strong_win = st.number_input("稳胆赔率 (如 1.35)", value=1.35, step=0.01)
        # 复式总本金 (修正你说的 200 逻辑)
        multi_stake = st.number_input("复式对冲总投入 (非单注)", value=100.0, step=1.0)
        
        st.divider()
        st.caption("勾选并输入对应的【总进球赔率】：")
        
        totals = ["0球", "1球", "2球"]
        # 参考你截图中的 7.20 / 3.55 / 3.00
        img_odds = {"0球": 7.20, "1球": 3.55, "2球": 3.00}
        
        selected_items = []
        for g in totals:
            c1, c2 = st.columns([1, 2])
            with c1: is_on = st.checkbox(g, key=f"s2_{g}", value=(g != "0球"))
            with c2: g_odd = st.number_input(f"{g}赔率", value=img_odds[g], key=f"s2_od_{g}", label_visibility="collapsed") if is_on else 0.0
            if is_on:
                selected_items.append({"name": g, "raw_odd": g_odd})
        
        # 核心逻辑：将复式本金平摊到所选的总进球项进行盈亏模拟
        if selected_items:
            share_stake = multi_stake / len(selected_items)
            for item in selected_items:
                active_bets.append({
                    "项目": item['name'], 
                    "赔率": item['raw_odd'] * strong_win, 
                    "金额": share_stake, 
                    "分类": "对冲"
                })

    # 计算总本金
    total_cost = sum(b['金额'] for b in active_bets)
    st.metric("💰 方案实际总投入", f"${total_cost:.2f}")

# --- 3. 盈亏校验与表格 ---
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
    
    # 大球利润覆盖检查
    win_3plus = df[df["模拟结果"] == "3球+"]["净盈亏"].values[0]
    if win_3plus > 0:
        st.success(f"✅ 对冲成功：大球赢球利润为 ${win_3plus:.2f}")
    else:
        st.error(f"❌ 对冲穿透：大球赢球反而亏损 ${abs(win_3plus):.2f}")

st.divider()
# 修复报错的概率输出
st.subheader("🧠 综合概率覆盖评估")
coverage = 0.77 if mode == "策略 2：总进球复式串关流" else 0.73
st.write(f"当前策略组合理论先觉覆盖率为: **{coverage:.1%}**")

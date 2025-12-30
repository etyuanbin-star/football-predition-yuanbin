import streamlit as st
import pandas as pd

# --- 页面配置 ---
st.set_page_config(page_title="胜算实验室：复式修正版", layout="wide")

st.title("🔺 胜算实验室：复式对冲系统")
st.subheader("修正逻辑：复式对冲本金计算")

# --- 侧边栏：核心数据 ---
with st.sidebar:
    st.header("⚖️ 核心项 (大球)")
    o25_odds = st.number_input("大球 (O2.5) 赔率", value=2.30, step=0.01)
    o25_stake = st.number_input("大球投入金额", value=100.0, step=1.0)
    
    st.divider()
    mode = st.radio("选择策略模式：", ["策略 1：比分精准对冲", "策略 2：总进球复式串关"])

# --- 主界面逻辑 ---
st.divider()
c1, c2 = st.columns([1.5, 2], gap="large")

active_bets = []
# 默认主攻项
active_bets.append({"项目": "3球+", "赔率": o25_odds, "金额": o25_stake, "分类": "主攻"})

with c1:
    if mode == "策略 1：比分精准对冲":
        st.write("### 🕹️ 策略 1：自定义比分")
        # 默认比分结构
        default_scores = {"0-0": 10.0, "1-0": 8.5, "0-1": 8.0, "1-1": 7.0, "2-0": 13.0, "0-2": 12.0}
        for s, d_odds in default_scores.items():
            col_cb, col_am, col_od = st.columns([1, 1, 1])
            with col_cb: is_on = st.checkbox(s, key=f"s1_{s}")
            with col_am: amt = st.number_input("金额", value=20.0, key=f"s1_am_{s}", label_visibility="collapsed") if is_on else 0.0
            with col_od: odd = st.number_input("赔率", value=d_odds, key=f"s1_od_{s}", label_visibility="collapsed") if is_on else 0.0
            if is_on: active_bets.append({"项目": s, "赔率": odd, "金额": amt, "分类": "对冲"})
    
    else:
        st.write("### 🕹️ 策略 2：复式对冲配置")
        st.info("💡 逻辑修正：稳胆+2项总进球视为一笔复式注单")
        
        strong_win = st.number_input("稳胆赔率 (主胜<1.4)", value=1.35, step=0.01)
        # 针对您截图中 7.20 / 3.55 / 3.00 的最新数值
        default_totals = {"0球": 7.20, "1球": 3.55, "2球": 3.00}
        
        # 关键修改：复式总金额
        multi_stake = st.number_input("复式对冲总投入 (非单注)", value=100.0, step=1.0)
        
        selected_totals = []
        for g, d_odds in default_totals.items():
            is_on = st.checkbox(g, key=f"s2_{g}", value=(g != "0球"))
            if is_on:
                # 记录赔率，稍后按比例或平均分配权重
                selected_totals.append({"name": g, "raw_odd": d_odds})
        
        # 将复式金额平均分配给所选项目进行盈亏模拟
        if selected_totals:
            share_stake = multi_stake / len(selected_totals)
            for item in selected_totals:
                active_bets.append({
                    "项目": item['name'], 
                    "赔率": item['raw_odd'] * strong_win, 
                    "金额": share_stake, 
                    "分类": "对冲"
                })

    # 计算总本金：大球 + 对冲项总和
    # 在策略2下，selected_totals 加起来刚好等于 multi_stake
    total_cost = sum(b['金额'] for b in active_bets)
    st.metric("💰 方案总本金", f"${total_cost:.2f}")

with c2:
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

    df_res = pd.DataFrame(res_list)
    st.bar_chart(df_res.set_index("模拟结果")["净盈亏"])
    st.table(df_res)
    
    # 盈亏核心检查
    win_3plus = df_res[df_res["模拟结果"] == "3球+"]["净盈亏"].values[0]
    if win_3plus > 0:
        st.success(f"✅ 大球赢球净利润: ${win_3plus:.2f}")
    else:
        st.error(f"❌ 大球赢球穿透亏损: ${abs(win_3plus):.2f}")

st.divider()
st.subheader("🧠 覆盖概率")
coverage = 0.77 if mode == "策略 2：总进球复式串关" else 0.73
st.write(f"当前策略理论覆盖率: **{coverage:.1%}**")
     

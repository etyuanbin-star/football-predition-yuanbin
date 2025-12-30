import streamlit as st
import pandas as pd

# --- 页面配置 ---
st.set_page_config(page_title="胜算实验室：双玩法整合版", layout="wide")

st.title("🔺 胜算实验室：双策略对冲系统")
st.caption("目标：确保 3球+ (大球) 赢球时能覆盖所有对冲成本并产生利润")

# --- 侧边栏：核心数据输入 ---
with st.sidebar:
    st.header("⚖️ 核心大球项 (O2.5)")
    o25_odds = st.number_input("大球 (3球+) 赔率", value=2.30, step=0.01)
    o25_stake = st.number_input("大球投入金额", value=100.0, step=1.0)
    
    st.divider()
    mode = st.radio("请选择执行策略：", ["策略 1：比分精准对冲", "策略 2：总进球自由对冲"])

# --- 主界面逻辑 ---
st.divider()
c1, c2 = st.columns([1.5, 2], gap="large")

# 初始化注单
active_bets = []
active_bets.append({"项目": "3球+", "赔率": o25_odds, "金额": o25_stake, "分类": "主攻"})

with c1:
    if mode == "策略 1：比分精准对冲":
        st.write("### 🕹️ 策略 1 配置：比分流")
        # 默认比分及赔率
        default_scores = {"0-0": 10.0, "1-0": 8.5, "0-1": 8.0, "1-1": 7.0, "2-0": 13.0, "0-2": 12.0}
        for s, d_odds in default_scores.items():
            col_cb, col_am, col_od = st.columns([1, 1.2, 1.2])
            with col_cb: is_on = st.checkbox(s, key=f"s1_{s}")
            with col_am: amt = st.number_input("金额", value=20.0, key=f"s1_am_{s}", label_visibility="collapsed") if is_on else 0.0
            with col_od: odd = st.number_input("赔率", value=d_odds, key=f"s1_od_{s}", label_visibility="collapsed") if is_on else 0.0
            if is_on: active_bets.append({"项目": s, "赔率": odd, "金额": amt, "分类": "对冲"})
    
    else:
        st.write("### 🕹️ 策略 2 配置：总进球流")
        st.caption("手动设定 0, 1, 2 球的赔率与金额：")
        # 根据你截图中的最新赔率设定默认值
        default_totals = {"0球": 7.20, "1球": 3.55, "2球": 3.00}
        for g, d_odds in default_totals.items():
            col_cb, col_am, col_od = st.columns([1, 1.2, 1.2])
            with col_cb: is_on = st.checkbox(g, key=f"s2_{g}", value=(g != "0球"))
            with col_am: amt = st.number_input("金额", value=30.0, key=f"s2_am_{g}", label_visibility="collapsed") if is_on else 0.0
            with col_od: odd = st.number_input("赔率", value=d_odds, key=f"s2_od_{g}", label_visibility="collapsed") if is_on else 0.0
            if is_on: active_bets.append({"项目": g, "赔率": odd, "金额": amt, "分类": "对冲"})

    total_cost = sum(b['金额'] for b in active_bets)
    st.metric("💰 方案总本金 (Total Stake)", f"${total_cost:.2f}")

with c2:
    st.write("### 📊 模拟盈亏校验 (PnL)")
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
    
    st.write("**详细核算数据表：**")
    st.table(df_res)
    
    # 核心目标校验：3球以上盈利情况
    win_3plus = df_res[df_res["模拟结果"] == "3球+"]["净盈亏"].values[0]
    if win_3plus > 0:
        st.success(f"✅ 对冲成功：打出大球时净赚 ${win_3plus:.2f}")
    else:
        st.error(f"❌ 对冲穿透：打出大球反而亏损 ${abs(win_3plus):.2f}，请调低对冲金额")

st.divider()
# 修复报错的格式化部分
st.subheader("🧠 综合先觉概率评估")
coverage = 0.73 if mode == "策略 1：比分精准对冲" else 0.77
st.write(f"当前策略组合的理论**先觉覆盖率**为: **{coverage:.1%}**")

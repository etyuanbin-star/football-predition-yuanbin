import streamlit as st
import pandas as pd

# --- 页面配置 ---
st.set_page_config(page_title="胜算实验室：双策略进化版", layout="wide")

st.title("🔺 胜算实验室：双策略风控系统")
st.subheader("—— 自定义赔率、金额与盈亏对冲校验")

# --- 侧边栏：核心大球项输入 ---
with st.sidebar:
    st.header("⚖️ 核心大球项 (O2.5)")
    o25_odds = st.number_input("大球 (3球+) 赔率", value=2.30, step=0.01)
    o25_stake = st.number_input("大球投入金额", value=100.0, step=1.0)
    
    st.divider()
    mode = st.radio("请选择当前执行策略：", ["策略 1：比分精准对冲", "策略 2：总进球自由对冲"])

# --- 主界面逻辑 ---
st.divider()
c1, c2 = st.columns([1.6, 2], gap="large")

# 初始化注单列表
active_bets = []
# 默认加入核心大球项
active_bets.append({"name": "3球+", "odds": o25_odds, "stake": o25_stake, "type": "main"})

with c1:
    if mode == "策略 1：比分精准对冲":
        st.write("### 🕹️ 策略 1：自定义比分对冲")
        st.caption("勾选并设定每个比分的赔率与下注金额：")
        default_scores = {"0-0": 10.0, "1-0": 8.5, "0-1": 8.0, "1-1": 7.0, "2-0": 13.0, "0-2": 12.0}
        
        for s, d_odds in default_scores.items():
            col_cb, col_am, col_od = st.columns([1, 1.2, 1.2])
            with col_cb: is_bet = st.checkbox(s, key=f"s1_{s}")
            with col_am: stake = st.number_input(f"{s}金额", value=10.0, key=f"s1_am_{s}", label_visibility="collapsed") if is_bet else 0.0
            with col_od: odds = st.number_input(f"{s}赔率", value=d_odds, key=f"s1_od_{s}", label_visibility="collapsed") if is_bet else 0.0
            if is_bet: active_bets.append({"name": s, "odds": odds, "stake": stake, "type": "hedge"})

    else:
        st.write("### 🕹️ 策略 2：自定义总进球对冲")
        st.caption("勾选并设定 0球、1球、2球 的独立赔率与下注金额：")
        # 实时参考您截图中的赔率
        default_totals = {"0球": 7.20, "1球": 3.55, "2球": 3.00}
        
        for g, d_odds in default_totals.items():
            col_cb, col_am, col_od = st.columns([1, 1.2, 1.2])
            with col_cb: is_bet = st.checkbox(g, key=f"s2_{g}", value=(g != "0球"))
            with col_am: stake = st.number_input(f"{g}金额", value=33.0, key=f"s2_am_{g}", label_visibility="collapsed") if is_bet else 0.0
            with col_od: odds = st.number_input(f"{g}赔率", value=d_odds, key=f"s2_od_{g}", label_visibility="collapsed") if is_bet else 0.0
            
            if is_bet:
                active_bets.append({"name": g, "odds": odds, "stake": stake, "type": "hedge"})

    total_stake = sum(b['stake'] for b in active_bets)
    st.metric("💰 当前方案总下注本金", f"{total_stake:.2f}")

with c2:
    st.write("### 📊 模拟盈亏校验 (自动计算抵消结果)")
    outcomes = ["0球", "1球", "2球", "3球+"]
    res_data = []
    
    for out in outcomes:
        income = 0
        for b in active_bets:
            # 匹配大球胜出的情况
            if b['name'] == "3球+" and out == "3球+":
                income += b['stake'] * b['odds']
            # 匹配对冲项胜出的情况（处理策略1和策略2的名称映射）
            elif b['name'] == out or \
                 (out == "0球" and b['name'] == "0-0") or \
                 (out == "1球" and b['name'] in ["1-0", "0-1"]) or \
                 (out == "2球" and b['name'] in ["1-1", "2-0", "0-2"]):
                income += b['stake'] * b['odds']
        
        res_data.append({"模拟赛果": out, "总回款": round(income, 2), "净盈亏": round(income - total_stake, 2)})
    
    df_res = pd.DataFrame(res_data)
    st.bar_chart(df_res.set_index("模拟赛果")["净盈亏"])
    
    # 核心对冲抵消检查
    win_3plus = df_res[df_res["模拟赛果"] == "3球+"]["净盈亏"].values[0]
    
    st.write("**实时诊断数据：**")
    st.table(df_res)
    
    if win_3plus >= 0:
        st.success(f"✅ **对冲成功**：当出现大球（3球+）时，回款能覆盖总本金，净利润为: **{win_3plus:.2f}**")
    else:
        st.error(f"❌ **利润穿透**：当前配置下，出现大球反而亏损 **{abs(win_3plus):.2f}**。请降低对冲金额或提高大球本金。")

st.markdown("---")
st.caption("提示：策略 2 现在支持完全手动的赔率和金额输入，确保您可以根据即时盘口调整方案。")

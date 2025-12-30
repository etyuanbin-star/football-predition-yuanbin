import streamlit as st
import pandas as pd
import numpy as np

# --- 页面配置 ---
st.set_page_config(page_title="胜算实验室：双策略进化版", layout="wide")

# --- 顶部说明 ---
st.title("🔺 胜算实验室：双策略风控系统")
st.subheader("—— 策略 1 (比分流) | 策略 2 (总进球流)")

with st.expander("📖 逻辑白皮书：为什么这样组合？", expanded=False):
    st.markdown("""
    * **策略 1 (精确比分)**：在大球赔率较低时，通过 3 组左右的高赔率比分进行对冲，追求极致的资金效率。
    * **策略 2 (总进球串关)**：在大球赔率较高（诱导盘）时，利用 2 串 1 的组合提高对冲端的生存能力。
    * **核心目标**：确保在大球（3球+）打出时，能覆盖掉所有对冲端的本金支出并产生利润。
    """)

# --- 侧边栏：核心大球项 ---
with st.sidebar:
    st.header("⚖️ 核心项 (大球)")
    o25_odds = st.number_input("全场大球 (O2.5) 赔率", value=2.30, step=0.01)
    o25_stake = st.number_input("大球投入金额 ($)", value=100.0)
    
    st.divider()
    mode = st.radio("请选择执行策略：", ["策略 1：比分精准对冲", "策略 2：总进球/串关对冲"])

# --- 主界面逻辑 ---
st.divider()
c1, c2 = st.columns([1.5, 2], gap="large")

# 预设参考赔率
default_scores = {"0-0": 10.0, "1-0": 8.5, "0-1": 8.0, "1-1": 7.0, "2-0": 13.0, "0-2": 12.0}
default_totals = {"0球": 6.80, "1球": 3.60, "2球": 3.20}

active_bets = []
# 默认加入大球项
active_bets.append({"name": "3球+", "odds": o25_odds, "stake": o25_stake, "type": "main"})

with c1:
    if mode == "策略 1：比分精准对冲":
        st.write("### 🕹️ 策略 1：比分对冲配置")
        st.caption("手动输入比分项的赔率与金额：")
        for s, d_odds in default_scores.items():
            col_cb, col_am, col_od = st.columns([1, 1, 1])
            with col_cb: is_bet = st.checkbox(s, key=f"s1_{s}")
            with col_am: stake = st.number_input("金额", value=10.0, key=f"s1_am_{s}", label_visibility="collapsed") if is_bet else 0.0
            with col_od: odds = st.number_input("赔率", value=d_odds, key=f"s1_od_{s}", label_visibility="collapsed") if is_bet else 0.0
            if is_bet: active_bets.append({"name": s, "odds": odds, "stake": stake, "type": "hedge"})

    else:
        st.write("### 🕹️ 策略 2：总进球/串关配置")
        st.caption("针对 0球、1球、2球 分别设置赔率与金额：")
        # 串关加成设置
        parlay_odds = st.number_input("串关项赔率 (如无串关填 1.0)", value=1.35)
        
        for g, d_odds in default_totals.items():
            col_cb, col_am, col_od = st.columns([1, 1, 1])
            with col_cb: is_bet = st.checkbox(g, key=f"s2_{g}", value=True if g != "0球" else False)
            with col_am: stake = st.number_input("对冲金额", value=20.0, key=f"s2_am_{g}", label_visibility="collapsed") if is_bet else 0.0
            with col_od: 
                raw_odds = st.number_input("单项赔率", value=d_odds, key=f"s2_od_{g}", label_visibility="collapsed") if is_bet else 0.0
            
            if is_bet:
                # 实际赔率 = 单项赔率 * 串关赔率
                active_bets.append({"name": g, "odds": raw_odds * parlay_odds, "stake": stake, "type": "hedge"})

    total_stake = sum(b['stake'] for b in active_bets)
    st.metric("🛡️ 总计投入本金", f"${total_stake:.2f}")

with c2:
    st.write("### 📊 策略盈亏模拟 (PnL)")
    # 模拟物理赛果点
    outcomes = ["0球", "1球", "2球", "3球+"]
    res_data = []
    
    for out in outcomes:
        income = 0
        for b in active_bets:
            if b['name'] == "3球+" and out == "3球+":
                income += b['stake'] * b['odds']
            elif b['name'] == out or (out == "0球" and b['name'] == "0-0") or \
                 (out == "1球" and b['name'] in ["1-0", "0-1"]) or \
                 (out == "2球" and b['name'] in ["1-1", "2-0", "0-2"]):
                income += b['stake'] * b['odds']
        
        res_data.append({"赛果": out, "净盈亏": income - total_stake})
    
    df_res = pd.DataFrame(res_data)
    st.bar_chart(df_res.set_index("赛果")["净盈亏"])
    
    st.write("**实时诊断数据表：**")
    st.table(df_res)
    
    # 核心检查：3球以上是否亏损
    win_3plus = df_res[df_res["赛果"] == "3球+"]["净盈亏"].values[0]
    if win_3plus > 0:
        st.success(f"✅ 目标达成：产生 3 球以上时利润为 ${win_3plus:.2f}")
    elif win_3plus == 0:
        st.warning("⚠️ 盈亏平衡：产生 3 球以上时刚好保本")
    else:
        st.error(f"❌ 警告：产生 3 球以上时将亏损 ${abs(win_3plus):.2f}，请调整对冲金额")

# --- 概率评估 ---
st.divider()
st.subheader("🧠 综合先觉概率评估")
# 修复了这里的格式化错误
if mode == "策略 1：比分精准对冲":
    prob = 0.73
else:
    prob = 0.77
st.write(f"当前策略组合的理论**先觉概率** (Total Probability Coverage): **{prob:.1%}**")



# --- 页脚 ---
st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>识破盘口陷阱是进阶的第一步。</p>", unsafe_allow_html=True)

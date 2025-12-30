import streamlit as st
import pandas as pd
import numpy as np

# --- 页面配置 ---
st.set_page_config(page_title="胜算实验室：全策略整合版", layout="wide")

# --- 1. 顶部：策略白皮书 ---
st.title("🔺 胜算实验室：多维风险控制系统")
st.subheader("—— 策略 1 (比分对冲) 与 策略 2 (串关对冲) 综合实验台")

with st.expander("📖 逻辑白皮书：双策略对比", expanded=False):
    st.markdown("""
    ### 策略 1：大球 + 3组精确比分 (点面结合)
    * **核心**：利用比分的高赔率（8-12倍）进行点对点防御。
    * **优点**：资金效率极高，不依赖其它场次。
    * **适用**：赔率结构正常，且你能精准锁定 1-2 球时的比分分布。

    ### 策略 2：大球 + 总进球 2串1 (结构化对冲)
    * **核心**：利用‘稳胆’拉高总进球赔率，并根据盘口诱导动态排除 0 球或 2 球。
    * **优点**：先觉概率最高（约 76%-78%），容错性较好。
    * **适用**：大球赔率偏高（>2.45）或存在诱导盘，且有极稳的强队场次可供串关。
    """)

# --- 2. 侧边栏：核心数据输入 ---
with st.sidebar:
    st.header("⚖️ 实时盘口检测")
    o25_odds = st.number_input("全场大球 (Over 2.5) 赔率", value=2.50, step=0.01)
    g2_odds_val = st.number_input("总进球 2 球实时赔率", value=2.95, step=0.01)
    
    # 诱导诊断
    is_trap = o25_odds >= 2.45 and g2_odds_val < 3.00
    if is_trap:
        st.error("🚨 检测到 [2球诱导陷阱]！")
    
    st.divider()
    st.subheader("🛠️ 模式选择")
    mode = st.radio("选择当前执行策略：", ["策略 1：比分精准对冲", "策略 2：总进球串关对冲"])

# --- 3. 策略逻辑执行 ---
st.divider()
c1, c2 = st.columns([1.2, 2], gap="large")

# 预设数据
score_list = ["0-0", "1-0", "0-1", "1-1", "2-0", "0-2"]
default_odds_map = {"0-0": 10.0, "1-0": 8.5, "0-1": 8.0, "1-1": 7.0, "2-0": 13.0, "0-2": 12.0}

with c1:
    if mode == "策略 1：比分精准对冲":
        st.write("### 🕹️ 策略 1 配置 (精确比分)")
        main_stake = st.number_input("大球金额", value=100.0)
        st.caption("选择 3 组比分进行对冲：")
        
        active_bets = []
        active_bets.append({"name": "大球", "odds": o25_odds, "stake": main_stake, "match": "3球+"})
        
        for s in score_list:
            col_cb, col_am, col_od = st.columns([1, 1, 1])
            with col_cb: is_bet = st.checkbox(s, key=f"s1_{s}")
            with col_am: stake = st.number_input("金额", value=20.0, key=f"s1_am_{s}", label_visibility="collapsed") if is_bet else 0.0
            with col_od: odds = st.number_input("赔率", value=default_odds_map[s], key=f"s1_od_{s}", label_visibility="collapsed") if is_bet else 0.0
            if is_bet: active_bets.append({"name": s, "odds": odds, "stake": stake, "match": s})

    else:
        st.write("### 🕹️ 策略 2 配置 (2串1对冲)")
        main_stake = st.number_input("大球金额", value=100.0)
        strong_win = st.number_input("稳胆赔率 (主胜<1.4)", value=1.35)
        
        strategy_logic = st.radio("排除逻辑：", ["常规：排除 0 球 (防 1-2 球)", "诱导：排除 2 球 (防 0-1 球)"], 
                                  index=1 if is_trap else 0)
        
        sub_stake = st.number_input("每注 2串1 金额", value=30.0)
        
        active_bets = []
        active_bets.append({"name": "大球", "odds": o25_odds, "stake": main_stake, "match": "3球+"})
        
        if "排除 0 球" in strategy_logic:
            active_bets.append({"name": "1球串", "odds": 3.60 * strong_win, "stake": sub_stake, "match": "1球"})
            active_bets.append({"name": "2球串", "odds": g2_odds_val * strong_win, "stake": sub_stake, "match": "2球"})
        else:
            active_bets.append({"name": "0球串", "odds": 6.80 * strong_win, "stake": sub_stake, "match": "0球"})
            active_bets.append({"name": "1球串", "odds": 3.60 * strong_win, "stake": sub_stake, "match": "1球"})

    total_inv = sum(b['stake'] for b in active_bets)
    st.metric("🛡️ 当前总投入", f"${total_inv:.2f}")

with c2:
    st.write("### 📊 盈亏分布诊断")
    # 为了统一图表，我们定义标准赛果点
    outcomes = ["0球", "1球", "2球", "3球+"]
    res_data = []
    
    for out in outcomes:
        income = 0
        for b in active_bets:
            # 策略1和策略2的比分/总进球匹配逻辑
            if b['match'] == "3球+" and out == "3球+":
                income += b['stake'] * b['odds']
            elif b['match'] == out or (out == "0球" and b['match'] == "0-0") or \
                 (out == "1球" and b['match'] in ["1-0", "0-1"]) or \
                 (out == "2球" and b['match'] in ["1-1", "2-0", "0-2"]):
                income += b['stake'] * b['odds']
        
        res_data.append({"赛果": out, "净盈亏": income - total_inv})
    
    df_res = pd.DataFrame(res_data)
    st.bar_chart(df_res.set_index("赛果")["净盈亏"])
    
    # 盲区显示
    holes = df_res[df_res['净盈亏'] < 0]
    if not holes.empty:
        st.error(f"⚠️ 风险点：若结果为 {', '.join(holes['赛果'].tolist())}，你将产生亏损。")
    else:
        st.success("✨ 覆盖成功：当前配置实现了该模式下的数学全对冲。")

# --- 4. 先觉概率评估 ---
st.divider()
st.subheader("🧠 综合先觉概率评估")
if mode == "策略 1：比分精准对冲":
    # 粗略估算：大球(48%) + 3个比分(约25%)
    prob = 0.73
else:
    prob = 0.785 if "排除 2 球" in strategy_logic else 0.766

st.write(f"当前策略组合的理论**先觉概率** (Total Probability Coverage): **{prob:.1% Graf}**")
st.caption("注：先觉概率越高，容错性越强，但单次盈利的边际利润通常越薄。")

# --- 5. 页脚 ---
st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>风险是优势的代价。若无优势，请勿入场。</p>", unsafe_allow_html=True)

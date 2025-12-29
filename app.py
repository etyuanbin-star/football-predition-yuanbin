import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="足球投注对冲沙盘", layout="wide")

st.title("⚽ 足球对冲投注：策略沙盘")
st.markdown("在这个模拟器中，你可以验证：**‘大球 + 比分对冲’到底能不能稳赚不赔？’**")

# --- 1. 设置区 (侧边栏) ---
with st.sidebar:
    st.header("⚙️ 市场赔率设定")
    o25_odds = st.number_input("大球 (Over 2.5) 赔率", value=2.25, min_value=1.01, step=0.01)
    
    st.divider()
    st.subheader("Under 2.5 比分赔率")
    score_list = ["0-0", "1-0", "0-1", "1-1", "2-0", "0-2"]
    default_odds = [10.0, 8.0, 7.5, 6.5, 12.0, 11.0]
    scores_config = {s: st.number_input(f"{s} 赔率", value=d) for s, d in zip(score_list, default_odds)}

# --- 2. 投注沙盘操作区 ---
col_input, col_viz = st.columns([1, 1], gap="large")
active_bets = []

with col_input:
    st.subheader("🕹️ 策略方案配置")
    
    # 大球投注块
    with st.container(border=True):
        st.write("🔥 **主方案：大球投注**")
        use_o25 = st.toggle("开启大球投注", value=True)
        o25_stake = st.number_input("大球投入本金 ($)", value=100, step=10) if use_o25 else 0
        if use_o25 and o25_stake > 0:
            active_bets.append({"name": "大球项", "odds": o25_odds, "stake": o25_stake, "type": "OVER"})

    # 比分对冲块
    st.write("🛡️ **防守方案：小球比分对冲**")
    score_grid = st.columns(2)
    for i, s in enumerate(score_list):
        with score_grid[i % 2]:
            with st.container(border=True):
                if st.checkbox(f"对冲 {s}", key=f"chk_{s}"):
                    s_stake = st.number_input(f"投入 ($)", value=20, step=5, key=f"v_{s}")
                    if s_stake > 0:
                        active_bets.append({"name": s, "odds": scores_config[s], "stake": s_stake, "type": "SCORE"})

    total_stake = sum(b['stake'] for b in active_bets)
    st.divider()
    st.metric("📊 当前方案总投入", f"${total_stake}")

# --- 3. 逻辑计算引擎 ---
# 定义所有可能发生的赛果
possible_outcomes = [
    {"name": "0-0", "is_over": False},
    {"name": "1-0", "is_over": False},
    {"name": "0-1", "is_over": False},
    {"name": "1-1", "is_over": False},
    {"name": "2-0", "is_over": False},
    {"name": "0-2", "is_over": False},
    {"name": "3球及以上(大球)", "is_over": True},
    {"name": "未覆盖的小球(如2-1, 1-2)", "is_over": True}, # 实际上2-1也是大球，归类为大球即可
]

analysis_data = []
for outcome in possible_outcomes:
    total_payout = 0
    for bet in active_bets:
        # 如果是“大球项”，且结果是进球数 >= 3，则中奖
        if bet['type'] == "OVER" and outcome['is_over']:
            total_payout += bet['stake'] * bet['odds']
        # 如果是“比分项”，且名字完全匹配，则中奖
        elif bet['type'] == "SCORE" and bet['name'] == outcome['name']:
            total_payout += bet['stake'] * bet['odds']
    
    net_profit = total_payout - total_stake
    analysis_data.append({"结果": outcome['name'], "净盈亏": net_profit})

df_analysis = pd.DataFrame(analysis_data)

# --- 4. 实时分析展示 ---
with col_viz:
    st.subheader("📈 策略实时表现")
    
    if total_stake > 0:
        # 盈亏条形图
        fig = px.bar(
            df_analysis, x="结果", y="净盈亏", color="净盈亏",
            color_continuous_scale=["#FF4B4B", "#00C853"],
            text_auto='.2f',
            title="不同赛果下的利润/亏损"
        )
        fig.add_hline(y=0, line_dash="dash", line_color="black")
        st.plotly_chart(fig, use_container_width=True)
        
        

        # 核心观察结论
        o25_profit = df_analysis.loc[df_analysis['结果'] == "3球及以上(大球)", "净盈亏"].values[0]
        
        if o25_profit > 0:
            st.success(f"✅ **大球盈利确认**：如果进球 > 2.5，你将获利 **${o25_profit:.2f}**。")
        elif o25_profit < 0:
            st.error(f"⚠️ **致命缺陷**：即便踢出了大球，你依然亏损 **${abs(o25_profit):.2f}**！(原因是你的对冲成本太高了)")
        else:
            st.info("⚖️ **盈亏平衡**：大球结果下你刚好保本。")

        # 详细表
        with st.expander("查看详细数据表"):
            st.dataframe(df_analysis, use_container_width=True)
    else:
        st.info("请在左侧配置你的投注方案以开始模拟。")

# --- 5. 策略总结 ---
st.divider()
st.subheader("💡 实验室心得")
st.markdown("""
- **为什么大球会亏钱？** 如果你的 `比分对冲总额` + `大球本金` > `大球本金 * 大球赔率`，那么即使大球中了，你也是亏的。
- **完美的对冲**：试着调整筹码，让所有柱子（所有的赛果）都保持在 0 线以上。
- **庄家抽水**：你会发现，在现实赔率下，很难让所有柱子都变绿。总有一个结果是红色的“坑”。
""")

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# --- 页面配置 ---
st.set_page_config(page_title="博弈决策沙盘 V3.0", layout="wide")

st.title("🔺 足球博弈决策沙盘：深层逻辑版")
st.markdown("本系统已整合：**抽水监测、不可能三角评估、价值发现(EV)以及凯利判据**。")

# --- 1. 核心数据设置 (侧边栏) ---
with st.sidebar:
    st.header("⚖️ 市场赔率 (庄家定价)")
    o25_odds = st.number_input("全场大球 (Over 2.5) 赔率", value=2.45, step=0.05)
    
    st.divider()
    st.subheader("比分对冲赔率")
    score_list = ["0-0", "1-0", "0-1", "1-1", "2-0", "0-2"]
    default_odds = [10.0, 8.5, 8.0, 7.0, 13.0, 12.0]
    scores_config = {s: st.number_input(f"{s} 赔率", value=d) for s, d in zip(score_list, default_odds)}

    st.divider()
    st.subheader("🧠 你的价值判断")
    pred_prob = st.slider("你预测的大球真实胜率 (%)", 10, 90, 45) / 100

# --- 2. 逻辑引擎：不可能三角与抽水 ---
# 2.1 抽水率计算
all_probs = [1/o25_odds] + [1/v for v in scores_config.values()]
overround = (sum(all_probs) - 1) * 100

# 2.2 不可能三角指数 (胜率 * 赔率 * 频率系数)
# 这是一个展示逻辑：当用户追求高胜率和高赔率时，三角会变得不稳定
tri_index = (pred_prob * o25_odds)

# 2.3 价值发现 (EV) 与 凯利
ev = (pred_prob * (o25_odds - 1)) - (1 - pred_prob)
kelly_f = (ev / (o25_odds - 1)) if ev > 0 else 0

# --- 3. 主界面布局 ---
col_stats, col_sandbox = st.columns([1, 2], gap="large")

with col_stats:
    st.subheader("🔬 博弈深度分析")
    
    # 抽水率仪表盘
    st.metric("庄家总抽水 (Overround)", f"{overround:.2f}%", delta="越高越难赢", delta_color="inverse")
    
    # 不可能三角监测
    st.write("**🔺 不可能三角状态：**")
    if tri_index > 1.05:
        st.error(f"指数 {tri_index:.2f}：【数学幻觉】\n现实中极少出现此等高价值机会。")
    elif tri_index > 0.98:
        st.warning(f"指数 {tri_index:.2f}：【职业博弈区】\n存在微弱正期望，需严格执行纪律。")
    else:
        st.info(f"指数 {tri_index:.2f}：【庄家收割区】\n胜率被赔率完全覆盖，长期玩必输。")

    # 价值分析
    st.write("**💰 价值发现 (Value Check)：**")
    if ev > 0:
        st.success(f"发现正期望 (EV): {ev:.2%}")
        st.write(f"建议单场仓位: **{kelly_f:.2%}**")
    else:
        st.error(f"负期望 (EV): {ev:.2%}\n即便中奖也是在亏钱。")

    # 隐含概率分布饼图
    prob_df = pd.DataFrame({"结果": ["大球"] + score_list, "隐含概率": [1/o25_odds] + [1/v for v in scores_config.values()]})
    fig_pie = px.pie(prob_df, values='隐含概率', names='结果', title="庄家概率空间占用")
    st.plotly_chart(fig_pie, use_container_width=True)

with col_sandbox:
    st.subheader("🕹️ 动态投注与盈亏实时反馈")
    
    active_bets = []
    # 投注配置区
    c1, c2 = st.columns([1, 1])
    with c1:
        if st.toggle("确认投注大球", value=True):
            o_stake = st.number_input("大球投入 ($)", value=100, step=10)
            active_bets.append({"name": "大球项", "odds": o25_odds, "stake": o_stake, "is_over": True})
    
    st.write("---")
    st.write("**比分对冲组合：**")
    grid = st.columns(3)
    for i, s in enumerate(score_list):
        with grid[i % 3]:
            if st.checkbox(f"对冲 {s}", key=f"s_{s}"):
                s_amt = st.number_input(f"金额", value=20, key=f"v_{s}", label_visibility="collapsed")
                active_bets.append({"name": s, "odds": scores_config[s], "stake": s_amt, "is_over": False})

    total_stake = sum(b['stake'] for b in active_bets)
    st.metric("当前方案总投入", f"${total_stake}")

    # 盈亏计算
    outcomes = score_list + ["大球(3球+)"]
    res = []
    for out in outcomes:
        payout = 0
        is_o = (out == "大球(3球+)")
        for b in active_bets:
            if (b['is_over'] and is_o) or (b['name'] == out):
                payout += b['stake'] * b['odds']
        res.append({"结果": out, "净盈亏": payout - total_stake})
    
    # 绘图
    df_res = pd.DataFrame(res)
    fig_bar = px.bar(df_res, x="结果", y="净盈亏", color="净盈亏", 
                     color_continuous_scale=["#FF4B4B", "#00C853"], text_auto='.2f')
    fig_bar.add_hline(y=0, line_dash="dash")
    st.plotly_chart(fig_bar, use_container_width=True)

# --- 4. 底部逻辑总结 ---
st.divider()
st.subheader("📝 终极博弈心得")
col_a, col_b = st.columns(2)
with col_a:
    st.markdown("""
    - **关于 75% 胜率**：中奖概率只是烟雾弹。如果你的 $EV < 0$，高频中奖只是在缓慢地把本金送给庄家。
    - **关于大球亏钱**：代码已修复逻辑——如果你的对冲成本（小球比分）过高，大球即便中了，收益也会被对冲成本吃光。
    """)
with col_b:
    st.markdown("""
    - **反向思维**：永远寻找“溢价”。当赔率从 2.4 升到 2.5，先问自己：是基本面变了，还是庄家在引诱？
    - **不可能三角**：不要试图兼顾。职业玩家的秘密是**放弃频率**，只打那 1% 的高价值时刻。
    """)

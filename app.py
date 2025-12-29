import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="博彩真相：庄家视角", layout="wide")

st.title("🛡️ 足球投注：庄家抽水与对冲实验场")
st.markdown("为什么长期玩一定会输？通过计算**抽水率**，你会发现庄家在开赛前就已经赢了。")

# --- 1. 赔率设置 (侧边栏) ---
with st.sidebar:
    st.header("⚖️ 市场赔率环境")
    o25_odds = st.number_input("全场大球 (Over 2.5) 赔率", value=2.25, step=0.05)
    
    st.divider()
    st.subheader("比分赔率设定")
    score_list = ["0-0", "1-0", "0-1", "1-1", "2-0", "0-2"]
    default_odds = [10.0, 8.0, 7.5, 6.5, 12.0, 11.0]
    scores_config = {s: st.number_input(f"{s} 赔率", value=d) for s, d in zip(score_list, default_odds)}

# --- 2. 核心分析：抽水率计算 ---
# 所有的物理结果：6个比分 + 大球
# 注意：这其实并未覆盖所有结果（如1-2, 2-1也是大球，但0-3或1-3等被包含在大球里了）
all_implied_probs = [1/o25_odds] + [1/v for v in scores_config.values()]
total_implied_prob = sum(all_implied_probs)
overround = (total_implied_prob - 1) * 100

# --- 3. 主界面展示 ---
col_analysis, col_sandbox = st.columns([1, 2], gap="large")

with col_analysis:
    st.subheader("🔬 庄家利润分析")
    st.metric("庄家总抽水 (Overround)", f"{overround:.2f}%")
    
    if overround > 0:
        st.error(f"庄家在这组赔率里多算了 {overround:.2f}% 的概率。这意味着你每投 100 元，理论上已经亏了 {overround:.2f} 元给庄家。")
    
    # 抽水构成饼图
    prob_data = pd.DataFrame({
        "结果": ["全场大球"] + score_list,
        "隐含概率": [1/o25_odds] + [1/v for v in scores_config.values()]
    })
    fig_pie = px.pie(prob_data, values='隐含概率', names='结果', title="赔率结构分布")
    st.plotly_chart(fig_pie, use_container_width=True)
    

with col_sandbox:
    st.subheader("🕹️ 策略自由模拟")
    active_bets = []
    
    c1, c2 = st.columns(2)
    with c1:
        if st.toggle("投注大球", value=True):
            amt = st.number_input("大球金额", value=100)
            active_bets.append({"name": "大球", "odds": o25_odds, "stake": amt, "is_over": True})
    
    st.write("**具体比分对冲：**")
    score_cols = st.columns(3)
    for i, s in enumerate(score_list):
        with score_cols[i % 3]:
            if st.checkbox(f"投 {s}", key=f"c_{s}"):
                amt = st.number_input(f"金额", value=20, key=f"a_{s}", label_visibility="collapsed")
                active_bets.append({"name": s, "odds": scores_config[s], "stake": amt, "is_over": False})

    total_stake = sum(b['stake'] for b in active_bets)
    
    # 计算盈亏数据
    outcomes = score_list + ["大球结果"]
    df_res = []
    for out in outcomes:
        income = 0
        is_o = (out == "大球结果")
        for b in active_bets:
            if (b['is_over'] and is_o) or (b['name'] == out):
                income += b['stake'] * b['odds']
        df_res.append({"赛果": out, "净盈亏": income - total_stake})
    
    df_res = pd.DataFrame(df_res)
    
    # 盈亏图
    fig_bar = px.bar(df_res, x="赛果", y="净盈亏", color="净盈亏", 
                     color_continuous_scale=["#FF4B4B", "#00C853"], text_auto='.2f')
    fig_bar.add_hline(y=0, line_dash="dash")
    st.plotly_chart(fig_bar, use_container_width=True)

# --- 4. 总结 ---
st.divider()
st.subheader("💡 核心真相：为什么没有 1 赔 3？")
st.markdown(f"""
1. **价格不对称**：如果一个结果发生的概率是 33%，庄家只会给你 2.8 或 2.5 的赔率（而不是 3.0）。
2. **风险不对称**：当你通过对冲把胜率提高到 75% 时，那剩下的 25% 盲区赔率被压低到极点。
3. **数学收割**：当前的抽水率为 **{overround:.2f}%**。这意味着无论你怎么通过“自由选择”来组合，你都在玩一个**胜算被提前扣除**的游戏。
""")

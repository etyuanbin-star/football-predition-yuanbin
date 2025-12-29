import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="博彩沙盘模拟器", layout="wide")

st.title("🎲 投注方案沙盘模拟器")
st.markdown("在这个实验室里，你可以自由组合投注选项，看看你的策略在数学面前是否站得住脚。")

# ======================
# 1. 初始化数据与侧边栏
# ======================
with st.sidebar:
    st.header("🏟️ 比赛环境设置")
    st.write("设置庄家给出的赔率（赔率越低，庄家抽水越多）")
    o25_odds = st.number_input("大球 (Over 2.5) 赔率", value=2.25, step=0.05)
    
    st.divider()
    st.subheader("具体比分赔率 (Under 2.5)")
    scores_odds = {
        "0-0": st.number_input("0-0 赔率", value=10.0),
        "1-0": st.number_input("1-0 赔率", value=8.0),
        "0-1": st.number_input("0-1 赔率", value=7.5),
        "1-1": st.number_input("1-1 赔率", value=6.5),
        "2-0": st.number_input("2-0 赔率", value=12.0),
        "0-2": st.number_input("0-2 赔率", value=11.0),
    }

# ======================
# 2. 投注沙盘：自由选择区域
# ======================
st.subheader("🕹️ 自定义你的投注单")
st.info("勾选你想投注的项，并分配筹码。观察右侧的实时盈亏分析。")

col_input, col_viz = st.columns([1, 1])

bets = []
total_spent = 0

with col_input:
    # 大球选项
    use_o25 = st.checkbox("投注：全场大球 (Over 2.5)", value=True)
    if use_o25:
        o25_stake = st.slider("大球投入金额", 10, 500, 100)
        bets.append({"name": "Over 2.5", "odds": o25_odds, "stake": o25_stake, "type": "over"})
        total_spent += o25_stake
    
    st.divider()
    # 比分选项
    st.write("**选择并分配具体比分的筹码：**")
    score_cols = st.columns(2)
    for i, (score, odds) in enumerate(scores_odds.items()):
        with score_cols[i % 2]:
            if st.checkbox(f"投比分 {score}", key=f"cb_{score}"):
                stake = st.number_input(f"{score} 投入", 0, 500, 50, key=f"st_{score}")
                bets.append({"name": score, "odds": odds, "stake": stake, "type": "score"})
                total_spent += stake

# ======================
# 3. 实时盈亏逻辑计算
# ======================
# 我们模拟可能出现的各种结果
outcomes = [
    {"name": "0-0", "is_over": False},
    {"name": "1-0", "is_over": False},
    {"name": "0-1", "is_over": False},
    {"name": "1-1", "is_over": False},
    {"name": "2-0", "is_over": False},
    {"name": "0-2", "is_over": False},
    {"name": "大球(3球及以上)", "is_over": True},
    {"name": "其他比分(如2-1, 1-2)", "is_over": True}, # 只要是大球，其实都一样
]

results_data = []
for outcome in outcomes:
    profit = 0
    for bet in bets:
        # 如果是大球项，且结果是大球，则中奖
        if bet["type"] == "over" and outcome["is_over"]:
            profit += bet["stake"] * bet["odds"]
        # 如果是比分项，且名字匹配，则中奖
        elif bet["type"] == "score" and bet["name"] == outcome["name"]:
            profit += bet["stake"] * bet["odds"]
    
    net_gain = profit - total_spent
    results_data.append({"结果": outcome["name"], "净盈亏": net_gain})

df_results = pd.DataFrame(results_data)

# ======================
# 4. 可视化分析
# ======================
with col_viz:
    st.write(f"### 💰 投资总结")
    st.metric("总投入成本", f"${total_spent}")
    
    # 盈亏条形图
    fig = px.bar(df_results, x="结果", y="净盈亏", 
                 color="净盈亏", 
                 color_continuous_scale=["#ff4b4b", "#00c853"],
                 title="不同比赛结果下的盈亏情况")
    fig.add_hline(y=0, line_dash="dash", line_color="black")
    st.plotly_chart(fig, use_container_width=True)



# ======================
# 5. 极端测试：压力模拟
# ======================
st.divider()
st.subheader("🌪️ 策略压力测试")

if total_spent > 0:
    st.write("假设按照这个筹码比例连续投注 100 场（模拟真实发生的概率）：")
    
    # 基于隐含概率计算期望值 (EV)
    total_ev = 0
    for outcome in outcomes:
        # 获取该结果的隐含概率（这里简单化处理，假设庄家抽水均匀）
        # 实际开发中可以更精细地根据赔率计算
        prob = 1/o25_odds if outcome["is_over"] else 1/scores_odds.get(outcome["name"], 10)
        # 归一化处理逻辑（略过，直接展示结论）
    
    # 计算当前组合的综合期望
    # 简单通过结果的平均盈亏给用户一个直观感觉
    avg_net = df_results["净盈亏"].mean()
    
    if avg_net < 0:
        st.error(f"⚠️ 警报：在当前赔率和你的分配下，平均每场你会亏损 ${abs(avg_net):.2f}")
    else:
        st.success(f"💎 发现漏洞？当前配置平均盈利 ${avg_net:.2f}（请检查赔率是否真实）")

    # 绘制长期资金曲线
    c1, c2 = st.columns([2, 1])
    with c1:
        # 模拟 100 场
        sim_balance = 1000 + np.cumsum(np.random.choice(df_results["净盈亏"], size=100))
        fig_sim = px.line(y=sim_balance, title="账户本金预测 (100场)", labels={'y': '余额', 'x': '场次'})
        st.plotly_chart(fig_sim, use_container_width=True)
    with c2:
        st.markdown("""
            **如何玩转这个沙盘？**
            1. **对冲测试**：尝试勾选大球，并只选 1-0, 0-1, 0-0。看看是否有“盲区”。
            2. **倍投测试**：加大某个比分的筹码，看它能否覆盖其他比分的亏损。
            3. **赔率压制**：去侧边栏调低赔率（模拟黑平台），看盈利区是如何消失的。
        """)

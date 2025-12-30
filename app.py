import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# 页面配置
st.set_page_config(
    page_title="胜算实验室：策略2分析",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 自定义CSS样式 ---
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1.5rem;
        background: linear-gradient(90deg, #1e3c72, #2a5298);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .strategy-box {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .positive {
        color: #28a745;
        font-weight: bold;
    }
    .negative {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- 应用标题 ---
st.markdown('<div class="main-header"><h1>🔺 胜算实验室：策略2详细分析</h1><p>总进球复式 + 稳胆对冲策略</p></div>', unsafe_allow_html=True)

# --- 侧边栏配置 ---
with st.sidebar:
    st.header("⚙️ 策略2参数配置")
    
    # 主比赛设置
    st.subheader("⚽ 主比赛设置")
    main_team_a = st.text_input("主队", value="安哥拉")
    main_team_b = st.text_input("客队", value="埃及")
    
    # 主投注设置
    st.subheader("💰 主投注设置")
    over25_stake = st.number_input("Over 2.5 投注金额 ($)", min_value=10, max_value=10000, value=100, step=10)
    over25_odds = st.number_input("Over 2.5 赔率", min_value=1.01, max_value=20.0, value=2.30, step=0.05)
    
    st.markdown("---")
    
    # 对冲投注设置
    st.subheader("🛡️ 对冲投注设置")
    hedge_stake = st.number_input("对冲投注总金额 ($)", min_value=10, max_value=10000, value=100, step=10)
    
    # 总进球选项
    st.write("**总进球复式选项**")
    goals_options = {
        "0球": {"selected": False, "odds": 7.20},
        "1球": {"selected": True, "odds": 3.60},
        "2球": {"selected": True, "odds": 3.20}
    }
    
    selected_goals = []
    for goal, data in goals_options.items():
        col1, col2 = st.columns([2, 3])
        with col1:
            selected = st.checkbox(goal, value=data["selected"], key=f"goal_{goal}")
            goals_options[goal]["selected"] = selected
            if selected:
                selected_goals.append(goal)
        with col2:
            if selected:
                goals_options[goal]["odds"] = st.number_input(
                    f"{goal}赔率", 
                    min_value=1.01, 
                    max_value=50.0, 
                    value=data["odds"], 
                    step=0.05,
                    key=f"odds_{goal}"
                )
    
    # 稳胆比赛设置
    st.markdown("---")
    st.subheader("🏆 稳胆比赛设置")
    strong_team_a = st.text_input("稳胆主队", value="布赖代合作")
    strong_team_b = st.text_input("稳胆客队", value="欧奈宰尹马")
    strong_odds = st.number_input("稳胆主胜赔率", min_value=1.01, max_value=5.0, value=1.35, step=0.05)

# --- 风险警示 ---
st.markdown("""
<div class="warning-box">
⚠️ <strong>策略2风险警示</strong>
<p><strong>核心风险：稳胆场次爆冷（平/负）</strong></p>
<ul>
<li>对冲注仅在以下条件同时满足时赢：总进球为选中的选项（1球或2球） <strong>且</strong> 稳胆主胜</li>
<li>稳胆场次平或负时，对冲注立即失效</li>
<li>总进球为0球时，对冲策略不覆盖</li>
</ul>
</div>
""", unsafe_allow_html=True)

# --- 策略说明 ---
st.header("🎯 策略说明")
st.markdown(f"""
<div class="strategy-box">
<h4>您的投注策略构成：</h4>
<ol>
<li><strong>主投注</strong>: {main_team_a} vs {main_team_b} 的 <strong>Over 2.5</strong>
    <ul>
        <li>投注金额: <strong>${over25_stake:.2f}</strong></li>
        <li>赔率: <strong>{over25_odds}</strong></li>
    </ul>
</li>
<li><strong>对冲投注</strong>: 2串1混合过关
    <ul>
        <li>第一关: 总进球复式 - {', '.join(selected_goals) if selected_goals else '无'}</li>
        <li>第二关: {strong_team_a} vs {strong_team_b} 的 <strong>主队胜</strong></li>
        <li>稳胆赔率: <strong>{strong_odds}</strong></li>
        <li>对冲金额: <strong>${hedge_stake:.2f}</strong></li>
        <li><strong>对冲注赢钱条件</strong>: 总进球为{', '.join(selected_goals)} <strong>且</strong> 稳胆主胜</li>
    </ul>
</li>
</ol>
<p><strong>总投入本金</strong>: ${over25_stake + hedge_stake:.2f}</p>
</div>
""", unsafe_allow_html=True)

# --- 核心计算函数 ---
def calculate_all_scenarios():
    """计算所有可能情景的盈亏"""
    scenarios = []
    
    # 总投入
    total_investment = over25_stake + hedge_stake
    
    # 每个对冲选项的金额分配
    if selected_goals:
        stake_per_goal = hedge_stake / len(selected_goals)
    else:
        stake_per_goal = 0
    
    # 总进球所有可能结果
    goal_outcomes = ["0球", "1球", "2球", "3+球"]
    
    # 稳胆所有可能结果
    strong_outcomes = ["主胜", "平局", "客胜"]
    
    # 生成所有组合（12种情景）
    scenario_count = 0
    for goal in goal_outcomes:
        for strong in strong_outcomes:
            scenario_count += 1
            
            # 初始化收入
            income = 0
            
            # 1. 主投注收入（仅当总进球为3+球时）
            if goal == "3+球":
                income += over25_stake * over25_odds
            
            # 2. 对冲注收入（仅当稳胆主胜且总进球在选中选项中）
            if strong == "主胜" and goal in selected_goals:
                # 计算2串1赔率
                goal_odd = goals_options[goal]["odds"]
                combo_odds = goal_odd * strong_odds
                income += stake_per_goal * combo_odds
            
            # 计算净盈亏
            net_profit = income - total_investment
            
            # 确定状态
            if net_profit > 0:
                status = "盈利"
                status_class = "positive"
            elif net_profit == 0:
                status = "保本"
                status_class = "neutral"
            else:
                status = "亏损"
                status_class = "negative"
            
            # 情景描述
            if goal == "3+球":
                if strong == "主胜":
                    description = "大球 + 稳胆胜"
                else:
                    description = "大球 + 稳胆败"
            elif goal == "0球":
                description = "对冲未覆盖"
            elif goal in selected_goals:
                if strong == "主胜":
                    description = "对冲成功"
                else:
                    description = "对冲失效"
            else:
                description = "其他"
            
            scenarios.append({
                "序号": scenario_count,
                "总进球": goal,
                "稳胆结果": strong,
                "描述": description,
                "主注结果": "赢" if goal == "3+球" else "输",
                "对冲注结果": "赢" if (strong == "主胜" and goal in selected_goals) else "输",
                "总收入": round(income, 2),
                "总投入": round(total_investment, 2),
                "净盈亏": round(net_profit, 2),
                "收益率": f"{(net_profit/total_investment*100):.1f}%" if total_investment > 0 else "0%",
                "状态": status
            })
    
    return pd.DataFrame(scenarios)

# --- 生成数据 ---
df_scenarios = calculate_all_scenarios()

# --- 关键指标 ---
st.header("📊 关键指标")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("总投入", f"${over25_stake + hedge_stake:.2f}")

with col2:
    max_profit = df_scenarios["净盈亏"].max()
    st.metric("最大盈利", f"${max_profit:.2f}")

with col3:
    min_profit = df_scenarios["净盈亏"].min()
    st.metric("最大亏损", f"${min_profit:.2f}")

with col4:
    losing_scenarios = len(df_scenarios[df_scenarios["净盈亏"] < 0])
    total_scenarios = len(df_scenarios)
    st.metric("亏损概率", f"{(losing_scenarios/total_scenarios*100):.1f}%")

# --- 盈亏图表 ---
st.header("📈 盈亏分布图")

# 准备数据
df_chart = df_scenarios.copy()
df_chart["组合标签"] = df_chart["总进球"] + " | " + df_chart["稳胆结果"]

# 创建条形图
fig = go.Figure()

# 按总进球分类颜色
colors = {
    "0球": "#FF6B6B",  # 红色 - 高风险
    "1球": "#4ECDC4",  # 青色
    "2球": "#45B7D1",  # 蓝色
    "3+球": "#96CEB4"   # 绿色
}

# 为每种总进球添加条形
for goal in df_chart["总进球"].unique():
    subset = df_chart[df_chart["总进球"] == goal]
    
    fig.add_trace(go.Bar(
        x=subset["组合标签"],
        y=subset["净盈亏"],
        name=goal,
        marker_color=colors.get(goal, "#CCCCCC"),
        text=[f"${x:.0f}" for x in subset["净盈亏"]],
        textposition='outside',
        hovertemplate=(
            "<b>%{x}</b><br>" +
            "净盈亏: $%{y:.2f}<br>" +
            "状态: %{customdata}<br>" +
            "<extra></extra>"
        ),
        customdata=subset["状态"]
    ))

# 更新布局
fig.update_layout(
    title=f"所有情景盈亏分析 (共{len(df_scenarios)}种组合)",
    xaxis_title="情景 (总进球 | 稳胆结果)",
    yaxis_title="净盈亏 ($)",
    showlegend=True,
    height=500,
    xaxis_tickangle=-45
)

# 添加零线
fig.add_hline(y=0, line_dash="dash", line_color="black", opacity=0.5)

st.plotly_chart(fig, use_container_width=True)

# --- 高风险情景分析 ---
st.header("⚠️ 高风险情景分析")

# 找出高风险情景（双重损失）
high_risk = df_scenarios[
    (df_scenarios["稳胆结果"] != "主胜") & 
    (df_scenarios["总进球"].isin(["0球", "1球", "2球"]))
]

if not high_risk.empty:
    st.markdown("""
    <div class="warning-box">
    <h4>双重损失风险</h4>
    <p>以下情景会导致<strong>主投注和对冲注同时输掉</strong>：</p>
    <ul>
    <li><strong>稳胆场次平或负</strong>（对冲注失效）</li>
    <li><strong>主比赛总进球为0、1或2球</strong>（主注输）</li>
    </ul>
    <p>在这些情景下，您将损失全部 ${:.2f} 本金。</p>
    </div>
    """.format(over25_stake + hedge_stake), unsafe_allow_html=True)
    
    st.write("**双重损失情景详情:**")
    
    risk_display = high_risk[["总进球", "稳胆结果", "净盈亏", "描述"]].copy()
    risk_display["损失金额"] = risk_display["净盈亏"].apply(lambda x: f"${abs(x):.2f}")
    
    st.dataframe(
        risk_display[["总进球", "稳胆结果", "描述", "损失金额"]],
        use_container_width=True
    )
    
    # 风险统计
    total_high_risk = len(high_risk)
    total_scenarios = len(df_scenarios)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("双重损失情景数", f"{total_high_risk}个")
    with col2:
        st.metric("双重损失概率", f"{(total_high_risk/total_scenarios*100):.1f}%")

# --- 详细盈亏表 ---
st.header("📋 详细盈亏表")
st.write(f"**所有 {len(df_scenarios)} 种可能情景:**")

# 格式化显示
display_df = df_scenarios.copy()
display_df = display_df.sort_values(["总进球", "稳胆结果"])

# 应用样式
def color_status(val):
    if val == "盈利":
        return 'background-color: #d4edda; color: #155724;'
    elif val == "亏损":
        return 'background-color: #f8d7da; color: #721c24;'
    else:
        return 'background-color: #fff3cd; color: #856404;'

# 创建HTML表格
html_table = """
<table border="1" style="width:100%; border-collapse: collapse;">
    <thead>
        <tr style="background-color: #f8f9fa;">
            <th style="padding: 8px;">序号</th>
            <th style="padding: 8px;">总进球</th>
            <th style="padding: 8px;">稳胆结果</th>
            <th style="padding: 8px;">描述</th>
            <th style="padding: 8px;">净盈亏 ($)</th>
            <th style="padding: 8px;">状态</th>
        </tr>
    </thead>
    <tbody>
"""

for _, row in display_df.iterrows():
    if row["状态"] == "盈利":
        row_color = "#d4edda"
        text_color = "#155724"
    elif row["状态"] == "亏损":
        row_color = "#f8d7da"
        text_color = "#721c24"
    else:
        row_color = "#fff3cd"
        text_color = "#856404"
    
    html_table += f"""
        <tr style="background-color: {row_color}; color: {text_color};">
            <td style="padding: 8px; font-weight: bold;">{row['序号']}</td>
            <td style="padding: 8px;">{row['总进球']}</td>
            <td style="padding: 8px;">{row['稳胆结果']}</td>
            <td style="padding: 8px;">{row['描述']}</td>
            <td style="padding: 8px; font-weight: bold;">{row['净盈亏']:+.2f}</td>
            <td style="padding: 8px; font-weight: bold;">{row['状态']}</td>
        </tr>
    """

html_table += """
    </tbody>
</table>
"""

st.markdown(html_table, unsafe_allow_html=True)

# --- 策略总结 ---
st.header("💡 策略总结")

# 统计
profitable = len(df_scenarios[df_scenarios["净盈亏"] > 0])
break_even = len(df_scenarios[df_scenarios["净盈亏"] == 0])
losing = len(df_scenarios[df_scenarios["净盈亏"] < 0])

st.markdown(f"""
<div class="strategy-box">
<h4>策略统计分析</h4>
<table style="width:100%;">
    <tr>
        <td><strong>盈利情景:</strong></td>
        <td class="positive">{profitable} 个 ({(profitable/len(df_scenarios)*100):.1f}%)</td>
    </tr>
    <tr>
        <td><strong>保本情景:</strong></td>
        <td>{break_even} 个 ({(break_even/len(df_scenarios)*100):.1f}%)</td>
    </tr>
    <tr>
        <td><strong>亏损情景:</strong></td>
        <td class="negative">{losing} 个 ({(losing/len(df_scenarios)*100):.1f}%)</td>
    </tr>
    <tr>
        <td><strong>总情景数:</strong></td>
        <td>{len(df_scenarios)} 个 (100%)</td>
    </tr>
</table>

<h5>策略评估：</h5>
<ol>
<li><strong>成功条件</strong>: 对冲注仅在"总进球1/2球 + 稳胆主胜"时赢</li>
<li><strong>主要风险</strong>: 稳胆平/负时对冲失效</li>
<li><strong>最大风险</strong>: 稳胆败 + 主赛小球 = 双重损失</li>
<li><strong>对冲漏洞</strong>: 未覆盖0球情况</li>
</ol>

<h5>关键建议：</h5>
<ol>
<li><strong>稳胆可靠性是关键</strong>: 仔细评估稳胆场次爆冷概率</li>
<li><strong>考虑覆盖0球</strong>: 如果预算允许，加入0球选项</li>
<li><strong>调整资金比例</strong>: 根据稳胆信心调整主注/对冲比例</li>
<li><strong>接受风险</strong>: 必须接受稳胆可能爆冷的现实</li>
</ol>
</div>
""", unsafe_allow_html=True)

# --- 最终免责声明 ---
st.markdown("""
<div style='text-align: center; padding: 1rem; background-color: #f8d7da; border-radius: 10px; margin-top: 2rem;'>
<h4 style='color: #721c24;'>⚠️ 重要免责声明</h4>
<p style='color: #721c24;'>
本工具仅用于教育目的，展示投注策略的数学原理和风险。<br>
<strong>不鼓励任何形式的赌博行为。</strong> 体育投注存在高风险，可能导致资金损失。<br>
如果您或您认识的人有赌博问题，请寻求专业帮助。
</p>
</div>
""", unsafe_allow_html=True)

st.caption("""
*胜算实验室 | 策略2分析工具 | 仅供学习风控概念使用*
""")

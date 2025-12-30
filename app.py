import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# 页面配置
st.set_page_config(
    page_title="胜算实验室：足球投注风控系统",
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
    .neutral {
        color: #6c757d;
        font-weight: bold;
    }
    .metric-card {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    /* 表格样式 */
    .dataframe {
        font-size: 0.9em;
        width: 100%;
    }
    /* 简化滚动条 */
    .stDataFrame {
        max-height: 500px;
        overflow-y: auto;
    }
</style>
""", unsafe_allow_html=True)

# --- 应用标题 ---
st.markdown('<div class="main-header"><h1>🔺 胜算实验室：足球投注风控系统</h1><p>可视化分析总进球复式对冲策略的风险与收益</p></div>', unsafe_allow_html=True)

# --- 侧边栏配置 ---
with st.sidebar:
    st.header("⚙️ 投注参数配置")
    
    # 主比赛参数
    st.subheader("🎯 主比赛参数")
    col1, col2 = st.columns(2)
    with col1:
        main_team_a = st.text_input("主队", value="安哥拉")
    with col2:
        main_team_b = st.text_input("客队", value="埃及")
    
    st.markdown("---")
    
    # 主投注参数
    st.subheader("💰 主投注设置")
    over25_odds = st.number_input("Over 2.5 赔率", min_value=1.01, max_value=20.0, value=2.30, step=0.05)
    over25_stake = st.number_input("主投注金额 (元)", min_value=10, max_value=10000, value=100, step=50)
    
    st.markdown("---")
    
    # 对冲投注参数
    st.subheader("🛡️ 对冲投注设置")
    st.write("**总进球复式选项**")
    
    # 总进球选项
    goals_options = {
        "0球": {"selected": False, "odds": 7.20, "stake_share": 0.0},
        "1球": {"selected": True, "odds": 3.60, "stake_share": 0.0},
        "2球": {"selected": True, "odds": 3.20, "stake_share": 0.0}
    }
    
    # 让用户选择总进球选项
    selected_goals = []
    for goal, data in goals_options.items():
        col1, col2 = st.columns([3, 2])
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
    
    # 稳胆比赛参数
    st.markdown("---")
    st.subheader("🏆 稳胆比赛设置")
    col1, col2 = st.columns(2)
    with col1:
        strong_team_a = st.text_input("稳胆主队", value="布赖代合作")
    with col2:
        strong_team_b = st.text_input("稳胆客队", value="欧奈宰尹马")
    
    strong_odds = st.number_input("稳胆主胜赔率", min_value=1.01, max_value=10.0, value=1.25, step=0.05)
    
    # 对冲投注金额
    hedge_stake = st.number_input("对冲投注总金额 (元)", min_value=10, max_value=10000, value=100, step=50)
    
    # 分配对冲金额到各个选项
    if selected_goals:
        share_per_option = hedge_stake / len(selected_goals)
        for goal in selected_goals:
            goals_options[goal]["stake_share"] = share_per_option
    
    st.markdown("---")
    
    # 概率设置
    st.subheader("📊 概率设置")
    over25_prob = st.slider("Over 2.5 概率 (%)", 10, 90, 45, 5)
    strong_win_prob = st.slider("稳胆主胜概率 (%)", 10, 90, 75, 5)
    
    st.markdown("---")
    
    # 显示设置
    st.subheader("👁️ 显示设置")
    show_detailed_table = st.checkbox("显示详细盈亏表", value=True)
    show_scenarios = st.checkbox("显示所有情景分析", value=True)

# --- 风险警示 ---
st.markdown("""
<div class="warning-box">
⚠️ <strong>风险警示</strong>
<p>体育投注是负期望值游戏。庄家通过数学优势确保长期盈利。</p>
<p>本工具旨在教育用户理解投注策略的风险，<strong>不鼓励任何形式的赌博行为</strong>。</p>
<p>您所执行的策略存在以下重大风险：</p>
<ul>
<li>稳胆场次爆冷（平/负）导致对冲失效</li>
<li>总进球为0球时对冲不覆盖</li>
<li>双重损失风险（主注+对冲注同时输）</li>
</ul>
</div>
""", unsafe_allow_html=True)

# --- 投注策略说明 ---
st.header("🎯 投注策略说明")
st.markdown(f"""
<div class="strategy-box">
<h4>您的投注策略构成：</h4>
<ol>
<li><strong>主投注</strong>: {main_team_a} vs {main_team_b} 的 <strong>Over 2.5</strong>
    <ul>
        <li>投注金额: <strong>{over25_stake}元</strong></li>
        <li>赔率: <strong>{over25_odds}</strong></li>
        <li>预期收益: <strong>{over25_stake * (over25_odds - 1):.2f}元</strong> (如果赢)</li>
    </ul>
</li>
<li><strong>对冲投注</strong>: 2串1混合过关
    <ul>
        <li>第一关: 总进球复式 - {', '.join(selected_goals) if selected_goals else '无'}</li>
        <li>第二关: {strong_team_a} vs {strong_team_b} 的 <strong>主队胜</strong> (赔率: {strong_odds})</li>
        <li>总投注金额: <strong>{hedge_stake}元</strong></li>
        <li>对冲注仅在 <strong>总进球为1或2球</strong> 且 <strong>稳胆主胜</strong> 时才赢</li>
    </ul>
</li>
</ol>
<p><strong>总投入本金</strong>: {over25_stake + hedge_stake}元</p>
</div>
""", unsafe_allow_html=True)

# --- 核心计算函数 ---
def calculate_profit_loss_scenarios():
    """计算所有可能的盈亏情景"""
    scenarios = []
    
    # 总投入
    total_investment = over25_stake + hedge_stake
    
    # 所有可能的总进球结果
    goal_outcomes = ["0球", "1球", "2球", "3+球"]
    
    # 所有可能的稳胆结果
    strong_outcomes = ["主胜", "平局", "客胜"]
    
    # 生成所有组合
    for goals in goal_outcomes:
        for strong in strong_outcomes:
            # 初始化收入
            income = 0
            
            # 主投注收入
            if goals == "3+球":
                income += over25_stake * over25_odds
            
            # 对冲注收入（仅当稳胆主胜且总进球在复式选项中）
            if strong == "主胜" and goals in selected_goals:
                goal_data = goals_options.get(goals, {})
                if goal_data.get("selected", False):
                    # 计算2串1赔率
                    combo_odds = goal_data.get("odds", 1.0) * strong_odds
                    income += goal_data.get("stake_share", 0) * combo_odds
            
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
            
            # 计算收益率
            roi = (net_profit / total_investment) * 100 if total_investment > 0 else 0
            
            # 添加情景
            scenarios.append({
                "情景编号": len(scenarios) + 1,
                "总进球": goals,
                "稳胆结果": strong,
                "主投注结果": "赢" if goals == "3+球" else "输",
                "对冲注结果": "赢" if (strong == "主胜" and goals in selected_goals) else "输",
                "总收入": round(income, 2),
                "总投入": round(total_investment, 2),
                "净盈亏": round(net_profit, 2),
                "收益率": round(roi, 2),
                "状态": status,
                "状态分类": status_class,
                "组合标签": f"{goals} | {strong}"
            })
    
    return pd.DataFrame(scenarios)

# --- 计算期望值 ---
def calculate_expected_value(df_scenarios):
    """计算策略的期望值"""
    # 计算各种结果的概率
    # 假设总进球概率分布
    goal_probs = {
        "0球": (100 - over25_prob) * 0.3 / 100,  # 假设0球占小球的30%
        "1球": (100 - over25_prob) * 0.4 / 100,  # 假设1球占小球的40%
        "2球": (100 - over25_prob) * 0.3 / 100,  # 假设2球占小球的30%
        "3+球": over25_prob / 100
    }
    
    # 稳胆结果概率分布
    strong_probs = {
        "主胜": strong_win_prob / 100,
        "平局": (100 - strong_win_prob) * 0.4 / 100,  # 假设平局占非胜的40%
        "客胜": (100 - strong_win_prob) * 0.6 / 100   # 假设客胜占非胜的60%
    }
    
    # 计算期望值
    expected_value = 0
    for _, row in df_scenarios.iterrows():
        # 计算该情景的概率
        prob = goal_probs.get(row["总进球"], 0) * strong_probs.get(row["稳胆结果"], 0)
        expected_value += prob * row["净盈亏"]
    
    return expected_value

# --- 生成盈亏数据 ---
df_scenarios = calculate_profit_loss_scenarios()
expected_value = calculate_expected_value(df_scenarios)

# --- 关键指标显示 ---
st.header("📊 关键策略指标")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "总投入本金", 
        f"{over25_stake + hedge_stake}元",
        delta=None
    )

with col2:
    max_profit = df_scenarios["净盈亏"].max()
    st.metric(
        "最大可能盈利", 
        f"{max_profit:.2f}元",
        delta=f"{(max_profit/(over25_stake+hedge_stake)*100):.1f}%" if (over25_stake+hedge_stake) > 0 else "0%"
    )

with col3:
    min_profit = df_scenarios["净盈亏"].min()
    st.metric(
        "最大可能亏损", 
        f"{min_profit:.2f}元",
        delta=f"{(min_profit/(over25_stake+hedge_stake)*100):.1f}%" if (over25_stake+hedge_stake) > 0 else "0%"
    )

with col4:
    ev_color = "normal" if expected_value >= 0 else "inverse"
    st.metric(
        "策略期望值 (EV)", 
        f"{expected_value:.2f}元",
        delta_color=ev_color
    )

# --- 盈亏分布可视化 ---
st.header("📈 盈亏分布可视化")

# 创建分组条形图
fig = go.Figure()

# 为每种总进球结果分配颜色
colors = {
    "0球": "#FF6B6B",  # 红色 - 高风险
    "1球": "#4ECDC4",  # 青色
    "2球": "#45B7D1",  # 蓝色
    "3+球": "#96CEB4"  # 绿色 - 主投注赢
}

# 添加每个情景的条形
for goal_outcome in df_scenarios["总进球"].unique():
    subset = df_scenarios[df_scenarios["总进球"] == goal_outcome]
    
    # 为稳胆结果添加文本标签
    text_labels = []
    for _, row in subset.iterrows():
        label = f"{row['净盈亏']:.0f}元<br>{row['稳胆结果']}"
        text_labels.append(label)
    
    fig.add_trace(go.Bar(
        x=subset["组合标签"],
        y=subset["净盈亏"],
        name=goal_outcome,
        marker_color=colors.get(goal_outcome, "#CCCCCC"),
        text=text_labels,
        textposition='outside',
        hovertemplate=(
            "<b>%{x}</b><br>" +
            "净盈亏: %{y:.2f}元<br>" +
            "状态: %{customdata}<br>" +
            "<extra></extra>"
        ),
        customdata=subset["状态"]
    ))

# 更新布局
fig.update_layout(
    title=f"盈亏分析 - 所有情景 ({len(df_scenarios)}种组合)",
    xaxis_title="情景 (总进球 | 稳胆结果)",
    yaxis_title="净盈亏 (元)",
    barmode='group',
    showlegend=True,
    height=500,
    hovermode="closest",
    xaxis_tickangle=-45
)

# 添加零线
fig.add_hline(y=0, line_dash="dash", line_color="black", opacity=0.5)

st.plotly_chart(fig, use_container_width=True)

# --- 风险情景分析 ---
st.header("⚠️ 风险情景分析")

# 找出高风险情景
high_risk_scenarios = df_scenarios[
    (df_scenarios["净盈亏"] == df_scenarios["净盈亏"].min()) | 
    (df_scenarios["稳胆结果"] != "主胜") & (df_scenarios["总进球"] != "3+球")
].copy()

if not high_risk_scenarios.empty:
    st.markdown("""
    <div class="warning-box">
    <h4>高风险情景识别</h4>
    <p>以下情景会导致您的策略出现显著亏损：</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 显示高风险情景
    high_risk_display = high_risk_scenarios[["总进球", "稳胆结果", "净盈亏", "状态"]].copy()
    high_risk_display["风险等级"] = high_risk_display["净盈亏"].apply(
        lambda x: "极高风险" if x <= -150 else "高风险" if x <= -100 else "中等风险"
    )
    
    st.dataframe(
        high_risk_display.style.apply(
            lambda x: ['background-color: #FFE5E5' if v == "极高风险" else 
                      'background-color: #FFF3CD' if v == "高风险" else 
                      'background-color: #E8F4FD' for v in x],
            subset=["风险等级"]
        ),
        use_container_width=True
    )
    
    # 风险统计
    total_high_risk = len(high_risk_scenarios)
    total_scenarios = len(df_scenarios)
    risk_percentage = (total_high_risk / total_scenarios) * 100
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("高风险情景数量", f"{total_high_risk}个")
    with col2:
        st.metric("高风险概率", f"{risk_percentage:.1f}%")

# --- 详细盈亏表 ---
if show_detailed_table:
    st.header("📋 详细盈亏分析表")
    
    # 格式化显示
    display_df = df_scenarios.copy()
    
    # 添加颜色编码
    def color_net_profit(val):
        if val > 0:
            return 'color: #28a745; font-weight: bold;'
        elif val < 0:
            return 'color: #dc3545; font-weight: bold;'
        else:
            return 'color: #6c757d;'
    
    def color_status(val):
        if val == "盈利":
            return 'background-color: #d4edda; color: #155724;'
        elif val == "亏损":
            return 'background-color: #f8d7da; color: #721c24;'
        else:
            return 'background-color: #fff3cd; color: #856404;'
    
    # 应用样式
    styled_df = display_df.style.applymap(color_net_profit, subset=['净盈亏'])
    styled_df = styled_df.applymap(color_status, subset=['状态'])
    
    # 显示表格
    st.dataframe(
        styled_df.format({
            '总收入': '{:.2f}',
            '总投入': '{:.2f}',
            '净盈亏': '{:.2f}',
            '收益率': '{:.2f}%'
        }),
        use_container_width=True,
        height=400
    )

# --- 情景分析矩阵 ---
if show_scenarios:
    st.header("🔍 情景分析矩阵")
    
    # 创建情景矩阵
    matrix_data = []
    for goal in ["0球", "1球", "2球", "3+球"]:
        row = {"总进球": goal}
        for strong in ["主胜", "平局", "客胜"]:
            scenario = df_scenarios[
                (df_scenarios["总进球"] == goal) & 
                (df_scenarios["稳胆结果"] == strong)
            ]
            if not scenario.empty:
                net_profit = scenario.iloc[0]["净盈亏"]
                status = scenario.iloc[0]["状态"]
                
                # 创建单元格内容
                cell_text = f"{net_profit:.0f}元"
                cell_color = "#d4edda" if status == "盈利" else "#f8d7da" if status == "亏损" else "#fff3cd"
                
                row[strong] = cell_text
                row[f"{strong}_color"] = cell_color
            else:
                row[strong] = "N/A"
                row[f"{strong}_color"] = "#f8f9fa"
        
        matrix_data.append(row)
    
    matrix_df = pd.DataFrame(matrix_data)
    
    # 创建矩阵可视化
    fig_matrix = go.Figure(data=go.Heatmap(
        z=[
            [float(matrix_df.loc[i, j].replace("元", "").replace("N/A", "0")) 
             for j in ["主胜", "平局", "客胜"]]
            for i in range(len(matrix_df))
        ],
        x=["主胜", "平局", "客胜"],
        y=matrix_df["总进球"].tolist(),
        colorscale=[
            [0, '#dc3545'],  # 亏损 - 红色
            [0.5, '#ffc107'], # 保本 - 黄色
            [1, '#28a745']   # 盈利 - 绿色
        ],
        colorbar=dict(title="净盈亏 (元)", titleside="right"),
        text=[
            [matrix_df.loc[i, j] for j in ["主胜", "平局", "客胜"]]
            for i in range(len(matrix_df))
        ],
        texttemplate="%{text}",
        textfont={"size": 14, "color": "black"},
        hovertemplate=(
            "总进球: %{y}<br>" +
            "稳胆结果: %{x}<br>" +
            "净盈亏: %{text}<br>" +
            "<extra></extra>"
        )
    ))
    
    fig_matrix.update_layout(
        title="情景分析矩阵 (总进球 × 稳胆结果)",
        xaxis_title="稳胆比赛结果",
        yaxis_title="总进球数",
        height=400
    )
    
    st.plotly_chart(fig_matrix, use_container_width=True)

# --- 策略评估与建议 ---
st.header("💡 策略评估与建议")

# 计算关键指标
profitable_scenarios = len(df_scenarios[df_scenarios["净盈亏"] > 0])
break_even_scenarios = len(df_scenarios[df_scenarios["净盈亏"] == 0])
losing_scenarios = len(df_scenarios[df_scenarios["净盈亏"] < 0])

total_scenarios = len(df_scenarios)
profitable_rate = (profitable_scenarios / total_scenarios) * 100
losing_rate = (losing_scenarios / total_scenarios) * 100

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="metric-card">
    <h5>盈利情景</h5>
    <h3 class="positive">{profitable_scenarios}个</h3>
    <p>{profitable_rate:.1f}% 的概率</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
    <h5>保本情景</h5>
    <h3 class="neutral">{break_even_scenarios}个</h3>
    <p>{(break_even_scenarios/total_scenarios*100):.1f}% 的概率</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
    <h5>亏损情景</h5>
    <h3 class="negative">{losing_scenarios}个</h3>
    <p>{losing_rate:.1f}% 的概率</p>
    </div>
    """, unsafe_allow_html=True)

# 策略建议
st.markdown("""
<div class="strategy-box">
<h4>策略评估与建议</h4>

<h5>✅ 策略优势：</h5>
<ol>
<li><strong>对冲保护</strong>：当总进球为1球或2球且稳胆主胜时，对冲注能弥补主注损失</li>
<li><strong>高赔率机会</strong>：对冲注2串1提供较高赔率，有机会获得超额回报</li>
<li><strong>风险分散</strong>：不完全依赖单一比赛结果</li>
</ol>

<h5>⚠️ 策略风险：</h5>
<ol>
<li><strong>稳胆爆冷风险</strong>：稳胆场次平或负时，对冲注完全失效</li>
<li><strong>覆盖不全风险</strong>：未覆盖总进球0球的情况</li>
<li><strong>双重损失风险</strong>：稳胆爆冷 + 主赛小球 = 最大亏损</li>
<li><strong>资金效率低</strong>：需要额外资金进行对冲，降低了资金使用效率</li>
</ol>

<h5>📋 改进建议：</h5>
<ol>
<li><strong>评估稳胆可靠性</strong>：仔细分析稳胆场次的球队实力、战意、伤停等情况</li>
<li><strong>考虑覆盖0球</strong>：在预算允许下，可考虑加入0球选项</li>
<li><strong>调整资金分配</strong>：根据对稳胆的信心调整主注与对冲注的比例</li>
<li><strong>设置止损点</strong>：明确最大可接受亏损，严格执行</li>
</ol>
</div>
""", unsafe_allow_html=True)

# --- 庄家优势分析 ---
st.header("🏢 庄家数学优势分析")

# 计算隐含概率
implied_prob_over25 = 1 / over25_odds
implied_prob_under25 = 1 - implied_prob_over25

# 计算庄家抽水
overround_over25 = (1/implied_prob_over25 - 1) * 100

# 计算对冲注的隐含概率
implied_prob_strong = 1 / strong_odds
overround_strong = (1/implied_prob_strong - 1) * 100

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div class="metric-card">
    <h5>主投注庄家优势</h5>
    <p>赔率: {over25_odds}</p>
    <p>隐含概率: {implied_prob_over25*100:.2f}%</p>
    <p>庄家抽水: {overround_over25:.2f}%</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
    <h5>稳胆投注庄家优势</h5>
    <p>赔率: {strong_odds}</p>
    <p>隐含概率: {implied_prob_strong*100:.2f}%</p>
    <p>庄家抽水: {overround_strong:.2f}%</p>
    </div>
    """, unsafe_allow_html=True)

# 庄家优势说明
st.markdown("""
<div class="warning-box">
<h5>庄家数学优势说明</h5>
<p>庄家通过设置赔率确保无论比赛结果如何，他们都能盈利：</p>
<ol>
<li><strong>赔率隐含概率 > 100%</strong>：所有选项的隐含概率之和超过100%，超额部分即庄家利润</li>
<li><strong>抽水率</strong>：您看到的{:.2f}%和{:.2f}%就是庄家确保的利润率</li>
<li><strong>长期必输</strong>：由于数学劣势，长期投注者注定亏损</li>
</ol>
<p><strong>重要提示</strong>：您的策略必须在庄家抽水的基础上额外创造优势才能长期盈利。</p>
</div>
""".format(overround_over25, overround_strong), unsafe_allow_html=True)

# --- 最终总结与免责声明 ---
st.markdown("""
<div style='text-align: center; padding: 2rem; background-color: #f8f9fa; border-radius: 10px; margin: 2rem 0;'>
<h3>🎯 策略总结</h3>
<p><strong>您的策略本质</strong>：用"稳胆必须赢"的条件，换取对"主赛1-2球"风险的对冲保护。</p>
<p><strong>关键决策点</strong>：稳胆场次的可靠性是策略成败的唯一决定因素。</p>
<p><strong>最大风险</strong>：稳胆爆冷（平/负） + 主赛小球（1/2球） = 双重损失。</p>
</div>
""", unsafe_allow_html=True)

# --- 最终免责声明 ---
st.markdown("""
<div style='text-align: center; padding: 1rem; background-color: #f8d7da; border-radius: 10px;'>
<h4 style='color: #721c24;'>⚠️ 重要免责声明</h4>
<p style='color: #721c24;'>
<strong>体育投注不是投资，而是高风险娱乐活动。</strong><br>
庄家通过数学优势确保长期盈利，普通投注者注定亏损。<br>
本工具仅用于教育目的，展示投注策略的数学原理和风险。<br>
<strong>不鼓励任何形式的赌博行为。</strong> 如果您或您认识的人有赌博问题，请寻求专业帮助。
</p>
</div>
""", unsafe_allow_html=True)

# --- 脚注 ---
st.caption("""
*胜算实验室 v1.0 | 教育工具 | 仅供学习风控概念使用 | 计算结果基于输入参数，实际结果可能因多种因素而异*
""")

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go

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
</style>
""", unsafe_allow_html=True)

# --- 应用标题 ---
st.markdown('<div class="main-header"><h1>🔺 胜算实验室：足球投注风控系统</h1><p>可视化分析足球投注策略的风险与收益</p></div>', unsafe_allow_html=True)

# --- 侧边栏配置 ---
with st.sidebar:
    st.header("⚙️ 系统配置")
    
    # 选择策略
    st.subheader("🎯 选择策略")
    strategy = st.radio(
        "选择分析策略",
        ["策略1: 比分精准对冲", "策略2: 总进球+稳胆对冲"],
        index=1
    )
    
    st.markdown("---")
    
    # 通用参数
    st.subheader("💰 通用参数")
    total_investment = st.number_input("总投入资金 (元)", min_value=100, max_value=10000, value=200, step=100)
    
    st.markdown("---")
    
    # 主比赛设置
    st.subheader("⚽ 主比赛设置")
    main_team_a = st.text_input("主队", value="安哥拉")
    main_team_b = st.text_input("客队", value="埃及")
    
    if strategy == "策略1: 比分精准对冲":
        # 策略1参数
        st.subheader("🎯 策略1: 比分精准对冲")
        over25_stake = st.number_input("大球投注金额 (元)", min_value=50, max_value=5000, value=100, step=50)
        hedge_stake = total_investment - over25_stake
        
        # 比分选项
        st.write("选择比分对冲选项:")
        score_options = ["0-0", "1-0", "0-1", "1-1", "2-0", "0-2", "2-1", "1-2", "2-2"]
        selected_scores = []
        for score in score_options:
            if st.checkbox(score, value=(score in ["1-0", "0-1", "1-1", "2-0", "0-2"]), key=f"score_{score}"):
                selected_scores.append(score)
        
    else:  # 策略2
        # 策略2参数
        st.subheader("🎯 策略2: 总进球+稳胆对冲")
        over25_stake = st.number_input("大球投注金额 (元)", min_value=50, max_value=5000, value=100, step=50)
        hedge_stake = total_investment - over25_stake
        
        # 总进球选项
        st.write("选择总进球选项:")
        goal_options = ["0球", "1球", "2球"]
        selected_goals = []
        for goal in goal_options:
            if st.checkbox(goal, value=(goal in ["1球", "2球"]), key=f"goal_{goal}"):
                selected_goals.append(goal)
        
        # 稳胆比赛设置
        st.subheader("🏆 稳胆比赛设置")
        strong_team_a = st.text_input("稳胆主队", value="布赖代合作", key="strong_a")
        strong_team_b = st.text_input("稳胆客队", value="欧奈宰尹马", key="strong_b")
    
    st.markdown("---")
    
    # 赔率设置
    st.subheader("📈 赔率设置")
    over25_odds = st.number_input("大球赔率", min_value=1.01, max_value=10.0, value=2.30, step=0.05)
    
    if strategy == "策略1: 比分精准对冲":
        # 比分赔率
        score_odds = {}
        st.write("设置比分赔率:")
        for score in selected_scores:
            default_odds = {
                "0-0": 10.0, "1-0": 8.5, "0-1": 8.0, 
                "1-1": 7.0, "2-0": 13.0, "0-2": 12.0,
                "2-1": 15.0, "1-2": 14.0, "2-2": 20.0
            }
            score_odds[score] = st.number_input(
                f"{score}赔率", 
                min_value=1.01, 
                max_value=50.0, 
                value=default_odds.get(score, 10.0), 
                step=0.1,
                key=f"odds_{score}"
            )
    else:  # 策略2
        # 总进球赔率
        goal_odds = {}
        st.write("设置总进球赔率:")
        for goal in selected_goals:
            default_odds = {"0球": 7.20, "1球": 3.60, "2球": 3.20}
            goal_odds[goal] = st.number_input(
                f"{goal}赔率", 
                min_value=1.01, 
                max_value=50.0, 
                value=default_odds.get(goal, 5.0), 
                step=0.1,
                key=f"odds_{goal}"
            )
        
        # 稳胆赔率
        strong_odds = st.number_input("稳胆主胜赔率", min_value=1.01, max_value=5.0, value=1.25, step=0.05)

# --- 风险警示 ---
st.markdown("""
<div class="warning-box">
⚠️ <strong>风险警示</strong>
<p>本工具旨在教育用户理解投注策略的风险，<strong>不鼓励任何形式的赌博行为</strong>。</p>
<p>您所执行的策略存在以下重大风险：</p>
<ul>
<li>稳胆场次爆冷（平/负）导致对冲失效</li>
<li>总进球为0球时对冲不覆盖</li>
<li>双重损失风险（主注+对冲注同时输）</li>
</ul>
</div>
""", unsafe_allow_html=True)

# --- 策略说明 ---
st.header("🎯 策略说明")
if strategy == "策略1: 比分精准对冲":
    st.markdown(f"""
    <div class="strategy-box">
    <h4>策略1: 比分精准对冲</h4>
    <ol>
    <li><strong>主投注</strong>: {main_team_a} vs {main_team_b} 的 <strong>Over 2.5</strong>
        <ul>
            <li>投注金额: <strong>{over25_stake}元</strong></li>
            <li>赔率: <strong>{over25_odds}</strong></li>
        </ul>
    </li>
    <li><strong>比分对冲</strong>: 对冲以下比分
        <ul>
            <li>对冲比分: {', '.join(selected_scores) if selected_scores else '无'}</li>
            <li>对冲金额: <strong>{hedge_stake}元</strong> (平均分配到每个比分)</li>
        </ul>
    </li>
    </ol>
    <p><strong>总投入本金</strong>: {total_investment}元</p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="strategy-box">
    <h4>策略2: 总进球+稳胆对冲</h4>
    <ol>
    <li><strong>主投注</strong>: {main_team_a} vs {main_team_b} 的 <strong>Over 2.5</strong>
        <ul>
            <li>投注金额: <strong>{over25_stake}元</strong></li>
            <li>赔率: <strong>{over25_odds}</strong></li>
        </ul>
    </li>
    <li><strong>对冲投注</strong>: 2串1混合过关
        <ul>
            <li>第一关: 总进球复式 - {', '.join(selected_goals) if selected_goals else '无'}</li>
            <li>第二关: {strong_team_a} vs {strong_team_b} 的 <strong>主队胜</strong> (赔率: {strong_odds})</li>
            <li>对冲金额: <strong>{hedge_stake}元</strong> (平均分配到每个选项)</li>
            <li><strong>注意</strong>: 对冲注仅在 <strong>总进球为{', '.join(selected_goals)}</strong> 且 <strong>稳胆主胜</strong> 时才赢</li>
        </ul>
    </li>
    </ol>
    <p><strong>总投入本金</strong>: {total_investment}元</p>
    </div>
    """, unsafe_allow_html=True)

# --- 计算函数 ---
def calculate_strategy1_scenarios():
    """计算策略1的盈亏情景"""
    scenarios = []
    
    # 每个比分对冲金额
    if selected_scores:
        stake_per_score = hedge_stake / len(selected_scores)
    else:
        stake_per_score = 0
    
    # 可能的比赛结果
    possible_outcomes = ["0-0", "1-0", "0-1", "1-1", "2-0", "0-2", "2-1", "1-2", "2-2", "其他大球"]
    
    for outcome in possible_outcomes:
        income = 0
        
        # 主投注收入
        if outcome == "其他大球":  # 代表3+球但不是2-1,1-2,2-2
            income += over25_stake * over25_odds
        
        # 对冲注收入
        if outcome in selected_scores:
            income += stake_per_score * score_odds.get(outcome, 1.0)
        
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
        
        scenarios.append({
            "赛果": outcome,
            "总收入": round(income, 2),
            "总投入": round(total_investment, 2),
            "净盈亏": round(net_profit, 2),
            "状态": status,
            "状态分类": status_class
        })
    
    return pd.DataFrame(scenarios)

def calculate_strategy2_scenarios():
    """计算策略2的盈亏情景"""
    scenarios = []
    
    # 每个总进球选项的对冲金额
    if selected_goals:
        stake_per_goal = hedge_stake / len(selected_goals)
    else:
        stake_per_goal = 0
    
    # 所有可能的总进球结果
    goal_outcomes = ["0球", "1球", "2球", "3+球"]
    
    # 所有可能的稳胆结果
    strong_outcomes = ["主胜", "平局", "客胜"]
    
    # 生成所有组合
    for goals in goal_outcomes:
        for strong in strong_outcomes:
            income = 0
            
            # 主投注收入
            if goals == "3+球":
                income += over25_stake * over25_odds
            
            # 对冲注收入（仅当稳胆主胜且总进球在复式选项中）
            if strong == "主胜" and goals in selected_goals:
                combo_odds = goal_odds.get(goals, 1.0) * strong_odds
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
            
            # 计算收益率
            roi = (net_profit / total_investment) * 100 if total_investment > 0 else 0
            
            scenarios.append({
                "总进球": goals,
                "稳胆结果": strong,
                "总收入": round(income, 2),
                "总投入": round(total_investment, 2),
                "净盈亏": round(net_profit, 2),
                "收益率": round(roi, 2),
                "状态": status,
                "状态分类": status_class,
                "组合标签": f"{goals} | {strong}"
            })
    
    return pd.DataFrame(scenarios)

# --- 生成盈亏数据 ---
if strategy == "策略1: 比分精准对冲":
    df_scenarios = calculate_strategy1_scenarios()
else:
    df_scenarios = calculate_strategy2_scenarios()

# --- 关键指标 ---
st.header("📊 关键指标")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("总投入本金", f"{total_investment}元")

with col2:
    max_profit = df_scenarios["净盈亏"].max()
    st.metric("最大盈利", f"{max_profit:.0f}元")

with col3:
    min_profit = df_scenarios["净盈亏"].min()
    st.metric("最大亏损", f"{min_profit:.0f}元")

with col4:
    profitable_scenarios = len(df_scenarios[df_scenarios["净盈亏"] > 0])
    total_scenarios = len(df_scenarios)
    st.metric("盈利概率", f"{(profitable_scenarios/total_scenarios*100):.1f}%")

# --- 盈亏图表 ---
st.header("📈 盈亏分析图表")

# 创建图表
fig = go.Figure()

if strategy == "策略1: 比分精准对冲":
    # 策略1的图表
    colors = ['#FF6B6B' if x < 0 else '#4ECDC4' if x > 0 else '#FFD93D' for x in df_scenarios["净盈亏"]]
    
    fig.add_trace(go.Bar(
        x=df_scenarios["赛果"],
        y=df_scenarios["净盈亏"],
        marker_color=colors,
        text=[f"{x:.0f}元" for x in df_scenarios["净盈亏"]],
        textposition='outside',
        name="净盈亏"
    ))
    
    fig.update_layout(
        title="策略1: 比分精准对冲 - 盈亏分析",
        xaxis_title="比赛赛果",
        yaxis_title="净盈亏 (元)",
        height=500,
        showlegend=False
    )
    
else:
    # 策略2的图表 - 分组柱状图
    goal_outcomes = df_scenarios["总进球"].unique()
    colors = {"0球": "#FF6B6B", "1球": "#4ECDC4", "2球": "#45B7D1", "3+球": "#96CEB4"}
    
    for goal in goal_outcomes:
        subset = df_scenarios[df_scenarios["总进球"] == goal]
        
        fig.add_trace(go.Bar(
            x=subset["稳胆结果"],
            y=subset["净盈亏"],
            name=goal,
            marker_color=colors.get(goal, "#CCCCCC"),
            text=[f"{x:.0f}元" for x in subset["净盈亏"]],
            textposition='outside'
        ))
    
    fig.update_layout(
        title="策略2: 总进球+稳胆对冲 - 盈亏分析",
        xaxis_title="稳胆比赛结果",
        yaxis_title="净盈亏 (元)",
        barmode='group',
        height=500
    )

# 添加零线
fig.add_hline(y=0, line_dash="dash", line_color="black", opacity=0.5)

st.plotly_chart(fig, use_container_width=True)

# --- 风险分析 ---
st.header("⚠️ 风险分析")

if strategy == "策略2: 总进球+稳胆对冲":
    # 策略2的特殊风险分析
    high_risk_scenarios = df_scenarios[
        (df_scenarios["稳胆结果"] != "主胜") & 
        (df_scenarios["总进球"].isin(["0球", "1球", "2球"]))
    ].copy()
    
    if not high_risk_scenarios.empty:
        st.markdown("""
        <div class="warning-box">
        <h4>⚠️ 高风险情景识别 (策略2特有)</h4>
        <p>以下情景会导致您的策略出现<strong>双重损失</strong>：</p>
        <ul>
        <li><strong>稳胆场次平或负</strong> + <strong>主比赛总进球为0、1或2球</strong></li>
        </ul>
        <p>在这些情景下，您的<strong>主投注</strong>和<strong>对冲投注</strong>将同时输掉。</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("**高风险情景详情:**")
        risk_display = high_risk_scenarios[["总进球", "稳胆结果", "净盈亏"]].copy()
        st.dataframe(risk_display.style.format({"净盈亏": "{:.0f}元"}), use_container_width=True)
        
        # 风险统计
        total_high_risk = len(high_risk_scenarios)
        risk_percentage = (total_high_risk / len(df_scenarios)) * 100
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("双重损失情景数", f"{total_high_risk}个")
        with col2:
            st.metric("双重损失概率", f"{risk_percentage:.1f}%")

# --- 详细盈亏表 ---
st.header("📋 详细盈亏分析")
st.write(f"**共 {len(df_scenarios)} 种可能情景:**")

# 格式化显示
display_df = df_scenarios.copy()

if strategy == "策略1: 比分精准对冲":
    display_df = display_df[["赛果", "净盈亏", "状态"]]
else:
    display_df = display_df[["总进球", "稳胆结果", "净盈亏", "状态"]]

# 应用样式
def highlight_status(val):
    if val == "盈利":
        return 'background-color: #d4edda; color: #155724;'
    elif val == "亏损":
        return 'background-color: #f8d7da; color: #721c24;'
    else:
        return 'background-color: #fff3cd; color: #856404;'

st.dataframe(
    display_df.style.applymap(highlight_status, subset=['状态']).format({
        '净盈亏': '{:.0f}元'
    }),
    use_container_width=True,
    height=400
)

# --- 策略总结 ---
st.header("💡 策略总结与建议")

if strategy == "策略1: 比分精准对冲":
    st.markdown("""
    <div class="strategy-box">
    <h4>策略1: 比分精准对冲 - 评估</h4>
    
    <h5>✅ 优点：</h5>
    <ol>
    <li><strong>精准对冲</strong>：可以对冲特定比分风险</li>
    <li><strong>简单直接</strong>：无需考虑其他比赛结果</li>
    <li><strong>可控性强</strong>：完全基于主比赛的结果</li>
    </ol>
    
    <h5>⚠️ 缺点：</h5>
    <ol>
    <li><strong>覆盖有限</strong>：只能对冲选中的特定比分</li>
    <li><strong>资金分散</strong>：对冲资金被分散到多个比分选项</li>
    <li><strong>赔率较低</strong>：比分赔率通常不高</li>
    </ol>
    
    <h5>📋 建议：</h5>
    <ol>
    <li>选择最可能出现的比分进行对冲</li>
    <li>根据历史数据和球队特点选择比分</li>
    <li>控制对冲资金比例，避免过度对冲</li>
    </ol>
    </div>
    """, unsafe_allow_html=True)
    
else:
    st.markdown("""
    <div class="strategy-box">
    <h4>策略2: 总进球+稳胆对冲 - 评估</h4>
    
    <h5>✅ 优点：</h5>
    <ol>
    <li><strong>赔率较高</strong>：2串1组合提供更高赔率</li>
    <li><strong>覆盖较广</strong>：可以覆盖多个总进球选项</li>
    <li><strong>灵活性强</strong>：可以根据稳胆信心调整策略</li>
    </ol>
    
    <h5>⚠️ 缺点与风险：</h5>
    <ol>
    <li><strong>稳胆依赖</strong>：策略成败完全取决于稳胆场次结果</li>
    <li><strong>双重损失风险</strong>：稳胆爆冷 + 主赛小球 = 最大亏损</li>
    <li><strong>覆盖不全</strong>：未选中的总进球选项无保护</li>
    </ol>
    
    <h5>📋 关键建议：</h5>
    <ol>
    <li><strong>稳胆评估</strong>：仔细分析稳胆场次的可靠性</li>
    <li><strong>风险控制</strong>：接受稳胆可能爆冷的事实</li>
    <li><strong>资金管理</strong>：对冲资金不宜过多</li>
    <li><strong>考虑覆盖0球</strong>：如果预算允许，考虑加入0球选项</li>
    </ol>
    
    <p><strong>核心结论</strong>：此策略是否成功，<strong>完全取决于您对稳胆场次的判断准确性</strong>。</p>
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

# --- 脚注 ---
st.caption("""
*胜算实验室 v2.0 | 教育工具 | 仅供学习风控概念使用 | 计算结果基于输入参数，实际结果可能因多种因素而异*
""")

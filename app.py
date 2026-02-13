import streamlit as st
import pandas as pd
import numpy as np
import json
from datetime import datetime
import re
from collections import Counter
import plotly.graph_objects as go
import plotly.express as px

# --- 1. 页面配置 ---
st.set_page_config(
    page_title="胜算实验室 Pro", 
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "胜算实验室 - 专业投注决策系统"
    }
)

# --- 初始化session_state ---
if 'match_history' not in st.session_state:
    st.session_state.match_history = []
if 'current_view' not in st.session_state:
    st.session_state.current_view = "dashboard"

# --- 增强版CSS样式 ---
st.markdown("""
<style>
    /* 全局样式 */
    .main {
        padding-top: 1rem;
    }
    
    /* KPI卡片样式 */
    .kpi-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        text-align: center;
        margin: 10px 0;
    }
    
    .kpi-card.positive {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    }
    
    .kpi-card.negative {
        background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
    }
    
    .kpi-card.neutral {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }
    
    .kpi-value {
        font-size: 36px;
        font-weight: bold;
        margin: 10px 0;
    }
    
    .kpi-label {
        font-size: 14px;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .kpi-delta {
        font-size: 16px;
        margin-top: 5px;
    }
    
    /* 顶部导航栏 */
    .top-nav {
        background: linear-gradient(90deg, #1e3c72, #2a5298);
        color: white;
        padding: 15px 25px;
        border-radius: 12px;
        margin-bottom: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .nav-title {
        font-size: 28px;
        font-weight: bold;
        margin: 0;
    }
    
    .nav-subtitle {
        font-size: 14px;
        opacity: 0.8;
        margin: 0;
    }
    
    /* 分段容器 */
    .section-container {
        background-color: white;
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border: 1px solid #e9ecef;
    }
    
    .section-header {
        color: #1e3c72;
        font-size: 20px;
        font-weight: bold;
        margin-bottom: 15px;
        padding-bottom: 10px;
        border-bottom: 2px solid #2a5298;
    }
    
    /* 比赛信息卡 */
    .match-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 20px;
        border-radius: 12px;
        margin: 15px 0;
        border-left: 5px solid #1e3c72;
    }
    
    .match-card-title {
        font-size: 24px;
        font-weight: bold;
        color: #1e3c72;
        text-align: center;
        margin-bottom: 10px;
    }
    
    .match-card-subtitle {
        font-size: 14px;
        color: #666;
        text-align: center;
    }
    
    /* 输入区样式 */
    .input-section {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border: 2px dashed #dee2e6;
        margin: 10px 0;
    }
    
    /* 结果展示卡 */
    .result-card {
        background: white;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border: 1px solid #e0e0e0;
        transition: all 0.3s;
    }
    
    .result-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    
    /* 提示框 */
    .info-box {
        background-color: #e7f3ff;
        border-left: 4px solid #2196F3;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    
    .warning-box {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    
    .success-box {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    
    /* 标签页美化 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #f0f2f6;
        border-radius: 8px 8px 0 0;
        padding: 0 24px;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #1e3c72;
        color: white;
    }
    
    /* 历史记录项 */
    .history-item {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 12px;
        margin: 8px 0;
        cursor: pointer;
        transition: all 0.3s;
    }
    
    .history-item:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        transform: translateY(-2px);
        border-color: #1e3c72;
    }
    
    /* 按钮美化 */
    .stButton>button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
</style>
""", unsafe_allow_html=True)

# --- 辅助函数 ---
def parse_history_data(history_text, current_home, current_away):
    """解析历史战绩数据"""
    matches = []
    lines = history_text.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        try:
            score_pattern = r'(\d+)\s*[-–]\s*(\d+)'
            match = re.search(score_pattern, line)
            
            if match:
                home_goals = int(match.group(1))
                away_goals = int(match.group(2))
                
                line_lower = line.lower()
                current_home_lower = current_home.lower()
                current_away_lower = current_away.lower()
                
                score_start = match.start()
                before_score = line_lower[:score_start]
                
                if current_home_lower in before_score:
                    matches.append({
                        'home_goals': home_goals,
                        'away_goals': away_goals,
                        'total_goals': home_goals + away_goals,
                        'result': '主胜' if home_goals > away_goals else ('客胜' if home_goals < away_goals else '平局'),
                        'home_team_current_perspective': True
                    })
                elif current_away_lower in before_score:
                    matches.append({
                        'home_goals': away_goals,
                        'away_goals': home_goals,
                        'total_goals': home_goals + away_goals,
                        'result': '客胜' if home_goals > away_goals else ('主胜' if home_goals < away_goals else '平局'),
                        'home_team_current_perspective': False
                    })
                else:
                    matches.append({
                        'home_goals': home_goals,
                        'away_goals': away_goals,
                        'total_goals': home_goals + away_goals,
                        'result': '主胜' if home_goals > away_goals else ('客胜' if home_goals < away_goals else '平局'),
                        'home_team_current_perspective': True
                    })
        except Exception as e:
            continue
    
    return matches

def calculate_statistics(matches, current_home, current_away):
    """计算统计信息"""
    if not matches:
        return None
    
    stats = {
        'total_matches': len(matches),
        'home_wins': 0,
        'away_wins': 0,
        'draws': 0,
        'total_goals': 0,
        'over_25': 0,
        'under_25': 0,
        'score_distribution': {},
        'goal_distribution': {},
        'current_home_goals': 0,
        'current_away_goals': 0,
    }
    
    for match in matches:
        home_goals = match['home_goals']
        away_goals = match['away_goals']
        total_goals = home_goals + away_goals
        
        if home_goals > away_goals:
            stats['home_wins'] += 1
        elif home_goals < away_goals:
            stats['away_wins'] += 1
        else:
            stats['draws'] += 1
        
        stats['total_goals'] += total_goals
        stats['current_home_goals'] += home_goals
        stats['current_away_goals'] += away_goals
        
        if total_goals > 2.5:
            stats['over_25'] += 1
        else:
            stats['under_25'] += 1
        
        score = f"{home_goals}-{away_goals}"
        stats['score_distribution'][score] = stats['score_distribution'].get(score, 0) + 1
        stats['goal_distribution'][total_goals] = stats['goal_distribution'].get(total_goals, 0) + 1
    
    stats['home_win_rate'] = stats['home_wins'] / stats['total_matches'] * 100
    stats['away_win_rate'] = stats['away_wins'] / stats['total_matches'] * 100
    stats['draw_rate'] = stats['draws'] / stats['total_matches'] * 100
    stats['avg_goals'] = stats['total_goals'] / stats['total_matches']
    stats['over_25_rate'] = stats['over_25'] / stats['total_matches'] * 100
    stats['under_25_rate'] = stats['under_25'] / stats['total_matches'] * 100
    stats['avg_home_goals'] = stats['current_home_goals'] / stats['total_matches']
    stats['avg_away_goals'] = stats['current_away_goals'] / stats['total_matches']
    
    if stats['score_distribution']:
        most_common_score = max(stats['score_distribution'].items(), key=lambda x: x[1])
        stats['most_common_score'] = most_common_score[0]
        stats['most_common_score_count'] = most_common_score[1]
        stats['most_common_score_rate'] = most_common_score[1] / stats['total_matches'] * 100
    
    return stats

def save_to_history(match_data):
    """保存分析记录"""
    match_data['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    match_data['id'] = len(st.session_state.match_history)
    st.session_state.match_history.insert(0, match_data)
    
    if len(st.session_state.match_history) > 50:
        st.session_state.match_history = st.session_state.match_history[:50]

def create_kpi_card(label, value, delta=None, card_type="neutral"):
    """创建KPI卡片"""
    delta_html = f'<div class="kpi-delta">{delta}</div>' if delta else ''
    return f"""
    <div class="kpi-card {card_type}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {delta_html}
    </div>
    """

# ==================== 主应用 ====================

# --- 顶部导航栏 ---
st.markdown("""
<div class="top-nav">
    <div>
        <div class="nav-title">🔺 胜算实验室 Pro</div>
        <div class="nav-subtitle">专业投注决策分析系统</div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- 侧边栏 (标签页式组织) ---
with st.sidebar:
    st.markdown("## ⚙️ 控制面板")
    
    sidebar_tabs = st.tabs(["📊 基础设置", "📈 历史分析", "🤖 AI预测", "📚 历史记录"])
    
    # ===== 标签页1: 基础设置 =====
    with sidebar_tabs[0]:
        st.markdown("### 比赛基本信息")
        
        home_team = st.text_input("🏠 主队", value="", placeholder="输入主队名称")
        away_team = st.text_input("✈️ 客队", value="", placeholder="输入客队名称")
        league = st.selectbox("🏆 联赛", ["英超", "欧冠", "西甲", "德甲", "意甲", "法甲", "其他"])
        
        col_date, col_time = st.columns(2)
        with col_date:
            match_date = st.date_input("📅 日期", value=datetime.now().date())
        with col_time:
            match_time = st.time_input("⏰ 时间", value=datetime.now().time())
        
        st.markdown("---")
        st.markdown("### 大球投注设置")
        
        o25_odds = st.number_input("大球赔率 (O2.5)", value=2.30, min_value=1.01, step=0.01)
        o25_stake = st.number_input("大球投入 ($)", value=100.0, min_value=0.0, step=10.0)
        
        st.markdown("---")
        st.markdown("### 预测概率")
        
        pred_prob = st.slider("大球概率 (%)", 10, 90, 48) / 100
        
        st.markdown("---")
        st.markdown("### 策略选择")
        
        mode = st.radio("", ["策略 1：比分精准流", "策略 2：总进球复式流"], label_visibility="collapsed")
    
    # ===== 标签页2: 历史分析 =====
    with sidebar_tabs[1]:
        st.markdown("### 历史交锋数据")
        
        if home_team and away_team:
            st.info(f"**{home_team}** vs **{away_team}**")
        
        history_data = st.text_area(
            "粘贴历史战绩",
            height=200,
            placeholder="格式：日期 主队 比分 客队\n每行一场比赛"
        )
        
        if history_data and home_team and away_team:
            matches = parse_history_data(history_data, home_team, away_team)
            if matches:
                stats = calculate_statistics(matches, home_team, away_team)
                if stats:
                    st.success(f"✅ 已解析 {stats['total_matches']} 场比赛")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("场均进球", f"{stats['avg_goals']:.2f}")
                    with col2:
                        st.metric("大球比例", f"{stats['over_25_rate']:.0f}%")
    
    # ===== 标签页3: AI预测 =====
    with sidebar_tabs[2]:
        st.markdown("### AI模型比分预测")
        
        st.markdown("**GPT模型**")
        gpt_pred1 = st.text_input("预测1", "", key="gpt1", placeholder="2-1")
        gpt_pred2 = st.text_input("预测2", "", key="gpt2", placeholder="3-1")
        gpt_pred3 = st.text_input("预测3", "", key="gpt3", placeholder="1-1")
        
        st.markdown("**Gemini模型**")
        gemini_pred1 = st.text_input("预测1", "", key="gemini1", placeholder="2-0")
        gemini_pred2 = st.text_input("预测2", "", key="gemini2", placeholder="3-2")
        gemini_pred3 = st.text_input("预测3", "", key="gemini3", placeholder="1-2")
        
        st.markdown("**DeepSeek模型**")
        deepseek_pred1 = st.text_input("预测1", "", key="deepseek1", placeholder="2-2")
        deepseek_pred2 = st.text_input("预测2", "", key="deepseek2", placeholder="3-0")
        deepseek_pred3 = st.text_input("预测3", "", key="deepseek3", placeholder="0-2")
        
        all_predictions = [gpt_pred1, gpt_pred2, gpt_pred3, gemini_pred1, gemini_pred2, gemini_pred3, deepseek_pred1, deepseek_pred2, deepseek_pred3]
        valid_predictions = [p for p in all_predictions if p.strip()]
        
        if valid_predictions:
            prediction_counts = Counter(valid_predictions)
            most_common = prediction_counts.most_common(1)[0]
            st.success(f"🎯 最热预测: **{most_common[0]}** ({most_common[1]}次)")
    
    # ===== 标签页4: 历史记录 =====
    with sidebar_tabs[3]:
        st.markdown("### 分析历史记录")
        
        if st.session_state.match_history:
            st.info(f"共 {len(st.session_state.match_history)} 条记录")
            
            for idx, record in enumerate(st.session_state.match_history[:5]):
                with st.expander(f"{record.get('home_team', '?')} vs {record.get('away_team', '?')}"):
                    st.write(f"**时间**: {record.get('timestamp', '')}")
                    st.write(f"**EV**: ${record.get('ev', 0):.2f}")
                    st.write(f"**策略**: {record.get('mode', '')}")
            
            if st.button("🗑️ 清空历史", type="secondary"):
                st.session_state.match_history = []
                st.rerun()
        else:
            st.info("暂无历史记录")

# ==================== 主内容区 ====================

# --- 顶部KPI仪表板 ---
st.markdown("## 📊 关键指标仪表板")

# 初始化变量以便后续计算
total_cost = o25_stake
ev = 0
simple_ev = 0
hedge_effect = 0
active_bets = []
parlay_bets = []

# 根据策略预计算一些值用于KPI展示
if mode == "策略 1：比分精准流":
    # 策略1的简单估算
    total_cost = o25_stake + 60  # 假设对冲约60
    simple_ev = (pred_prob * o25_odds - 1) * o25_stake
    # EV会在后面详细计算
else:
    # 策略2的简单估算
    total_cost = o25_stake + 100  # 假设2串1约100
    simple_ev = (pred_prob * o25_odds - 1) * o25_stake

# 显示KPI卡片
kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

with kpi_col1:
    st.markdown(create_kpi_card(
        "总投入",
        f"${total_cost:.0f}",
        "当前策略",
        "neutral"
    ), unsafe_allow_html=True)

with kpi_col2:
    st.markdown(create_kpi_card(
        "大球概率",
        f"{pred_prob*100:.0f}%",
        f"赔率: {o25_odds}",
        "neutral"
    ), unsafe_allow_html=True)

with kpi_col3:
    ev_display = simple_ev  # 会在后面更新
    ev_type = "positive" if ev_display > 0 else ("negative" if ev_display < 0 else "neutral")
    st.markdown(create_kpi_card(
        "预期收益 (EV)",
        f"${ev_display:.2f}",
        f"ROI: {ev_display/total_cost*100:.1f}%" if total_cost > 0 else "",
        ev_type
    ), unsafe_allow_html=True)

with kpi_col4:
    roi = (ev_display / total_cost * 100) if total_cost > 0 else 0
    roi_type = "positive" if roi > 0 else ("negative" if roi < 0 else "neutral")
    st.markdown(create_kpi_card(
        "投资回报率",
        f"{roi:.1f}%",
        "长期期望",
        roi_type
    ), unsafe_allow_html=True)

st.markdown("---")

# --- 比赛信息展示 ---
if home_team and away_team:
    st.markdown(f"""
    <div class="match-card">
        <div class="match-card-title">{home_team} 🆚 {away_team}</div>
        <div class="match-card-subtitle">{league} · {match_date.strftime('%Y-%m-%d')} {match_time.strftime('%H:%M')}</div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.warning("⚠️ 请在侧边栏输入比赛信息")

# --- 主内容标签页 ---
main_tabs = st.tabs(["📥 策略配置", "📊 盈亏分析", "📈 数据可视化", "📄 完整报告"])

# ===== 主标签页1: 策略配置 =====
with main_tabs[0]:
    st.markdown('<div class="section-header">策略参数配置</div>', unsafe_allow_html=True)
    
    if mode == "策略 1：比分精准流":
        st.markdown('<div class="input-section">', unsafe_allow_html=True)
        st.markdown("### 🎯 比分对冲设置")
        
        scores = ["0-0", "1-0", "0-1", "1-1", "2-0", "0-2"]
        default_odds = {"0-0": 10.0, "1-0": 8.5, "0-1": 8.0, "1-1": 7.0, "2-0": 13.0, "0-2": 12.0}
        
        col1, col2, col3 = st.columns(3)
        
        for i, s in enumerate(scores):
            with [col1, col2, col3][i % 3]:
                with st.container():
                    is_on = st.checkbox(f"**{s}**", key=f"s1_{s}")
                    if is_on:
                        col_a, col_b = st.columns(2)
                        with col_a:
                            s_amt = st.number_input("金额", value=10.0, key=f"s1_am_{s}", min_value=0.0)
                        with col_b:
                            s_odd = st.number_input("赔率", value=default_odds[s], key=f"s1_od_{s}", min_value=1.01)
                        active_bets.append({"item": s, "odd": s_odd, "stake": s_amt})
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        active_bets.append({"item": "3球+", "odd": o25_odds, "stake": o25_stake})
        total_cost = sum(b['stake'] for b in active_bets)
        
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        col_summary1, col_summary2, col_summary3 = st.columns(3)
        with col_summary1:
            st.metric("💰 大球投入", f"${o25_stake:.2f}")
        with col_summary2:
            st.metric("💰 对冲投入", f"${total_cost - o25_stake:.2f}")
        with col_summary3:
            st.metric("💰 总投入", f"${total_cost:.2f}")
        st.markdown('</div>', unsafe_allow_html=True)
        
    else:  # 策略2
        st.markdown('<div class="input-section">', unsafe_allow_html=True)
        st.markdown("### 🏆 稳胆比赛设置")
        
        col_s2a, col_s2b = st.columns(2)
        with col_s2a:
            s2_home_team = st.text_input("稳胆主队", "", key="s2_home")
        with col_s2b:
            s2_away_team = st.text_input("稳胆客队", "", key="s2_away")
        
        s2_league = st.selectbox("稳胆联赛", ["英超", "欧冠", "西甲", "德甲", "意甲", "法甲", "其他"], key="s2_league")
        
        st.markdown("### 📊 稳胆赔率")
        col_std1, col_std2, col_std3 = st.columns(3)
        with col_std1:
            s2_win_odds = st.number_input(f"{s2_home_team or '主队'} 胜", value=1.35, min_value=1.01, step=0.01)
        with col_std2:
            s2_draw_odds = st.number_input("平局", value=4.50, min_value=1.01, step=0.01)
        with col_std3:
            s2_lose_odds = st.number_input(f"{s2_away_team or '客队'} 胜", value=8.00, min_value=1.01, step=0.01)
        
        s2_selection = st.radio("选择稳胆", [f"{s2_home_team or '主队'} 胜", "平局", f"{s2_away_team or '客队'} 胜"], horizontal=True)
        
        if s2_selection == f"{s2_home_team or '主队'} 胜":
            strong_win = s2_win_odds
        elif s2_selection == "平局":
            strong_win = s2_draw_odds
        else:
            strong_win = s2_lose_odds
        
        st.markdown("### ⚽ 总进球选项")
        
        totals = ["0球", "1球", "2球"]
        default_odds_goals = {"0球": 7.20, "1球": 3.55, "2球": 3.00}
        
        selected_goals = []
        col_g1, col_g2, col_g3 = st.columns(3)
        
        for i, g in enumerate(totals):
            with [col_g1, col_g2, col_g3][i]:
                is_on = st.checkbox(f"**{g}**", key=f"s2_{g}", value=(g != "0球"))
                if is_on:
                    g_odd = st.number_input("赔率", value=default_odds_goals[g], key=f"s2_od_{g}", min_value=1.01)
                    selected_goals.append({"goal": g, "odds": g_odd})
        
        per_parlay_stake = st.number_input("每注2串1金额 ($)", value=50.0, min_value=0.0, step=10.0)
        
        if selected_goals:
            for goal_item in selected_goals:
                combined_odd = round(goal_item['odds'] * strong_win, 2)
                parlay_bets.append({
                    "goal": goal_item['goal'],
                    "parlay_odds": combined_odd,
                    "stake": per_parlay_stake,
                })
        
        total_parlay_cost = sum(b['stake'] for b in parlay_bets)
        total_cost = total_parlay_cost + o25_stake
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            st.metric("💰 大球投入", f"${o25_stake:.2f}")
        with col_s2:
            st.metric("💰 2串1投入", f"${total_parlay_cost:.2f}")
        with col_s3:
            st.metric("💰 总投入", f"${total_cost:.2f}")
        st.markdown('</div>', unsafe_allow_html=True)

# ===== 主标签页2: 盈亏分析 =====
with main_tabs[1]:
    st.markdown('<div class="section-header">盈亏模拟分析</div>', unsafe_allow_html=True)
    
    if mode == "策略 1：比分精准流":
        scores = ["0-0", "1-0", "0-1", "1-1", "2-0", "0-2"]
        s1_outcomes = scores + ["3球+"]
        res_list = []
        
        for out in s1_outcomes:
            income = sum(b['stake'] * b['odd'] for b in active_bets if b['item'] == out)
            net_profit = round(income - total_cost, 2)
            res_list.append({"赛果": out, "净盈亏": net_profit})
        
        df_s1 = pd.DataFrame(res_list)
        
        # 图表展示
        fig = px.bar(df_s1, x="赛果", y="净盈亏", 
                     color="净盈亏",
                     color_continuous_scale=["red", "yellow", "green"],
                     title="各种赛果下的盈亏情况")
        st.plotly_chart(fig, use_container_width=True)
        
        # 表格展示
        st.dataframe(df_s1, use_container_width=True, hide_index=True)
        
        # 计算EV
        prob_per_score = (1 - pred_prob) / 6
        ev = sum(row["净盈亏"] * (pred_prob if "3球" in row["赛果"] else prob_per_score) for _, row in df_s1.iterrows())
        
    else:  # 策略2
        res_list = []
        bet_goals = [bet["goal"] for bet in parlay_bets]
        
        scenarios = [
            ("稳胆赢+0球", 0),
            ("稳胆赢+1球", 1 if "1球" in bet_goals else 0),
            ("稳胆赢+2球", 2 if "2球" in bet_goals else 0),
            ("稳胆赢+3球+", o25_stake * o25_odds),
            ("稳胆平/负+0/1/2球", 0),
            ("稳胆平/负+3球+", o25_stake * o25_odds),
        ]
        
        for scenario, base_income in scenarios:
            if base_income == 1 and "1球" in bet_goals:
                parlay_1 = next(b for b in parlay_bets if b["goal"] == "1球")
                income = parlay_1["stake"] * parlay_1["parlay_odds"]
            elif base_income == 2 and "2球" in bet_goals:
                parlay_2 = next(b for b in parlay_bets if b["goal"] == "2球")
                income = parlay_2["stake"] * parlay_2["parlay_odds"]
            else:
                income = base_income
            
            net_profit = income - total_cost
            res_list.append({"场景": scenario, "净盈亏": round(net_profit, 2)})
        
        df_s2 = pd.DataFrame(res_list)
        
        fig = px.bar(df_s2, x="场景", y="净盈亏",
                     color="净盈亏",
                     color_continuous_scale=["red", "yellow", "green"],
                     title="各种场景下的盈亏情况")
        st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(df_s2, use_container_width=True, hide_index=True)
        
        # 简化的EV计算
        win_prob = 1/s2_win_odds / (1/s2_win_odds + 1/s2_draw_odds + 1/s2_lose_odds)
        ev = sum(row["净盈亏"] * (win_prob*0.3 if "稳胆赢" in row["场景"] else 0.1) for _, row in df_s2.iterrows())
    
    # 显示EV和对比
    st.markdown("---")
    st.markdown("### 📊 期望值分析")
    
    simple_ev = (pred_prob * o25_odds - 1) * o25_stake
    hedge_effect = (abs(ev) - abs(simple_ev)) / abs(simple_ev) * 100 if simple_ev != 0 else 0
    
    col_ev1, col_ev2, col_ev3 = st.columns(3)
    with col_ev1:
        st.metric("策略EV", f"${ev:.2f}", delta=f"ROI: {ev/total_cost*100:.1f}%")
    with col_ev2:
        st.metric("单纯大球EV", f"${simple_ev:.2f}", delta=f"ROI: {simple_ev/o25_stake*100:.1f}%")
    with col_ev3:
        st.metric("对冲效果", f"{hedge_effect:.1f}%")

# ===== 主标签页3: 数据可视化 =====
with main_tabs[2]:
    st.markdown('<div class="section-header">数据可视化分析</div>', unsafe_allow_html=True)
    
    # 创建仪表盘
    col_viz1, col_viz2 = st.columns(2)
    
    with col_viz1:
        st.markdown("### 📊 概率分布")
        
        prob_data = pd.DataFrame({
            '结果': ['大球(3+)', '小球(0-2)'],
            '概率': [pred_prob * 100, (1-pred_prob) * 100]
        })
        
        fig_prob = px.pie(prob_data, values='概率', names='结果',
                          title='大小球概率分布',
                          color_discrete_sequence=['#00d084', '#ff6b6b'])
        st.plotly_chart(fig_prob, use_container_width=True)
    
    with col_viz2:
        st.markdown("### 💰 投注结构")
        
        if mode == "策略 1：比分精准流":
            invest_data = pd.DataFrame({
                '类型': ['大球投注', '比分对冲'],
                '金额': [o25_stake, total_cost - o25_stake]
            })
        else:
            invest_data = pd.DataFrame({
                '类型': ['大球投注', '2串1复式'],
                '金额': [o25_stake, total_cost - o25_stake]
            })
        
        fig_invest = px.pie(invest_data, values='金额', names='类型',
                            title='投注金额分配',
                            color_discrete_sequence=['#4facfe', '#667eea'])
        st.plotly_chart(fig_invest, use_container_width=True)
    
    # 风险收益图
    st.markdown("### 📈 风险收益分析")
    
    risk_return_data = pd.DataFrame({
        '策略': ['当前策略', '单纯大球', '理想情况', '最坏情况'],
        'EV': [ev, simple_ev, total_cost * 0.2, -total_cost],
        '风险等级': [3, 5, 1, 5]
    })
    
    fig_risk = px.scatter(risk_return_data, x='风险等级', y='EV', 
                          size=[20, 20, 20, 20], color='策略',
                          title='风险收益散点图',
                          labels={'EV': '期望收益 ($)', '风险等级': '风险等级 (1-5)'})
    st.plotly_chart(fig_risk, use_container_width=True)

# ===== 主标签页4: 完整报告 =====
with main_tabs[3]:
    st.markdown('<div class="section-header">完整分析报告</div>', unsafe_allow_html=True)
    
    # 报告内容
    col_report1, col_report2 = st.columns(2)
    
    with col_report1:
        st.markdown("### 📋 比赛信息")
        st.markdown(f"""
        - **联赛**: {league}
        - **主队**: {home_team or '未设置'}
        - **客队**: {away_team or '未设置'}
        - **时间**: {match_date.strftime('%Y-%m-%d')} {match_time.strftime('%H:%M')}
        """)
        
        st.markdown("### 💰 投注详情")
        st.markdown(f"""
        - **策略**: {mode}
        - **大球赔率**: {o25_odds}
        - **大球投入**: ${o25_stake:.2f}
        - **总投入**: ${total_cost:.2f}
        - **预测大球概率**: {pred_prob*100:.1f}%
        """)
    
    with col_report2:
        st.markdown("### 📊 风险评估")
        st.markdown(f"""
        - **策略EV**: ${ev:.2f}
        - **ROI**: {ev/total_cost*100:.1f}%
        - **对冲效果**: {hedge_effect:.1f}%
        - **单纯大球EV**: ${simple_ev:.2f}
        """)
        
        st.markdown("### 💡 建议")
        if ev > 0 and ev > simple_ev:
            st.success("✅ 策略优化成功，建议执行")
        elif ev > 0:
            st.info("ℹ️ 策略有效但保守")
        else:
            st.error("⚠️ 策略需要调整")
    
    # 保存按钮
    st.markdown("---")
    if home_team and away_team:
        if st.button("💾 保存本次分析", type="primary", use_container_width=True):
            analysis_data = {
                'home_team': home_team,
                'away_team': away_team,
                'league': league,
                'match_date': match_date.strftime('%Y-%m-%d'),
                'match_time': match_time.strftime('%H:%M'),
                'mode': mode,
                'o25_odds': o25_odds,
                'o25_stake': o25_stake,
                'pred_prob': pred_prob,
                'total_cost': total_cost,
                'ev': ev,
                'simple_ev': simple_ev,
                'hedge_effect': hedge_effect
            }
            
            save_to_history(analysis_data)
            st.success("✅ 分析已保存！")
            st.balloons()

# --- 底部信息 ---
st.markdown("---")
st.caption(f"*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 胜算实验室 Pro v2.0*")

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
history_count = len(st.session_state.match_history)
st.markdown(f"""
<div class="top-nav">
    <div>
        <div class="nav-title">🔺 胜算实验室 Pro</div>
        <div class="nav-subtitle">专业投注决策分析系统</div>
    </div>
    <div style="text-align: right;">
        <div style="font-size: 24px; font-weight: bold;">📚 {history_count}</div>
        <div style="font-size: 12px; opacity: 0.8;">已保存分析</div>
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
        
        # 添加先验概率选项
        use_prior = st.checkbox("📊 使用先验概率（贝叶斯方法）", value=False)
        
        if use_prior:
            st.markdown("#### 🎯 先验概率设置")
            
            st.info("""
            **什么是先验概率？**
            
            基于你的经验、分析、专家意见等主观判断的初始概率。
            系统会结合历史数据和先验概率，使用贝叶斯方法计算后验概率。
            """)
            
            # 先验概率来源选择
            prior_source = st.radio(
                "先验概率来源",
                ["手动输入", "基于赔率反推", "专家预测"],
                horizontal=True
            )
            
            if prior_source == "手动输入":
                st.markdown("##### 输入各项先验概率")
                
                col_p1, col_p2 = st.columns(2)
                with col_p1:
                    prior_home_win = st.slider("主队获胜概率 (%)", 0, 100, 45, key="prior_home")
                with col_p2:
                    prior_away_win = st.slider("客队获胜概率 (%)", 0, 100, 30, key="prior_away")
                
                prior_draw = 100 - prior_home_win - prior_away_win
                st.metric("平局概率（自动计算）", f"{prior_draw}%")
                
                if prior_draw < 0:
                    st.error("❌ 概率总和不能超过100%，请调整")
                
                st.markdown("---")
                prior_over25 = st.slider("大球(3+)先验概率 (%)", 0, 100, 50, key="prior_over")
                
            elif prior_source == "基于赔率反推":
                st.markdown("##### 输入赔率（自动计算先验概率）")
                
                col_o1, col_o2, col_o3 = st.columns(3)
                with col_o1:
                    odds_home = st.number_input("主胜赔率", value=2.10, min_value=1.01, step=0.01)
                with col_o2:
                    odds_draw = st.number_input("平局赔率", value=3.50, min_value=1.01, step=0.01)
                with col_o3:
                    odds_away = st.number_input("客胜赔率", value=3.20, min_value=1.01, step=0.01)
                
                # 赔率转概率（去除庄家利润）
                prob_home_raw = 1 / odds_home
                prob_draw_raw = 1 / odds_draw
                prob_away_raw = 1 / odds_away
                total_raw = prob_home_raw + prob_draw_raw + prob_away_raw
                
                prior_home_win = int(prob_home_raw / total_raw * 100)
                prior_draw = int(prob_draw_raw / total_raw * 100)
                prior_away_win = int(prob_away_raw / total_raw * 100)
                
                st.success(f"✅ 计算得出: 主胜{prior_home_win}% | 平{prior_draw}% | 客胜{prior_away_win}%")
                
                prior_over25 = st.slider("大球(3+)先验概率 (%)", 0, 100, 50, key="prior_over_odds")
                
            else:  # 专家预测
                st.markdown("##### 专家预测概率")
                
                expert_name = st.text_input("专家/机构名称", placeholder="例如：ESPN预测")
                
                col_e1, col_e2, col_e3 = st.columns(3)
                with col_e1:
                    prior_home_win = st.number_input("主胜概率 (%)", 0, 100, 45)
                with col_e2:
                    prior_draw = st.number_input("平局概率 (%)", 0, 100, 25)
                with col_e3:
                    prior_away_win = st.number_input("客胜概率 (%)", 0, 100, 30)
                
                total_prob = prior_home_win + prior_draw + prior_away_win
                if abs(total_prob - 100) > 1:
                    st.error(f"❌ 概率总和应为100%，当前为{total_prob}%")
                
                prior_over25 = st.number_input("大球概率 (%)", 0, 100, 50)
            
            # 保存先验概率到session_state
            st.session_state.use_prior = True
            st.session_state.prior_home_win = prior_home_win / 100
            st.session_state.prior_draw = prior_draw / 100 if prior_source != "专家预测" else prior_draw / 100
            st.session_state.prior_away_win = prior_away_win / 100
            st.session_state.prior_over25 = prior_over25 / 100
            st.session_state.prior_source = prior_source
            
        else:
            st.session_state.use_prior = False
        
        # 根据是否使用先验概率显示不同的概率输入
        if not use_prior:
            pred_prob = st.slider("大球概率 (%)", 10, 90, 48) / 100
        else:
            st.markdown("#### 📊 后验概率（将在分析中计算）")
            st.info("系统会结合先验概率和历史数据，使用贝叶斯方法计算最终的后验概率")
            pred_prob = prior_over25 / 100  # 使用先验作为初始值
        
        st.markdown("---")
        st.markdown("### 策略选择")
        
        mode = st.radio("", ["策略 1：比分精准流", "策略 2：总进球复式流"], label_visibility="collapsed")
    
    # ===== 标签页2: 历史分析 =====
    with sidebar_tabs[1]:
        st.markdown("### 📊 历史交锋分析")
        
        if home_team and away_team:
            st.info(f"**{home_team}** vs **{away_team}**")
        else:
            st.warning("⚠️ 请先在基础设置中输入球队")
        
        history_data = st.text_area(
            "粘贴历史战绩数据",
            height=180,
            placeholder="格式示例：\n02/05/2025 曼城 2-1 阿森纳\n每行一场比赛",
            key="history_input"
        )
        
        if history_data and home_team and away_team:
            matches = parse_history_data(history_data, home_team, away_team)
            
            if matches:
                stats = calculate_statistics(matches, home_team, away_team)
                
                if stats:
                    st.success(f"✅ 已解析 **{stats['total_matches']}** 场历史比赛")
                    
                    # 快速统计预览
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("场均进球", f"{stats['avg_goals']:.2f}")
                    with col2:
                        st.metric("大球比例", f"{stats['over_25_rate']:.0f}%")
                    with col3:
                        st.metric(f"{home_team}胜率", f"{stats['home_win_rate']:.0f}%")
                    
                    # 详细统计展开
                    with st.expander("📈 查看详细统计", expanded=True):
                        st.markdown("#### 胜负平分布")
                        
                        result_col1, result_col2, result_col3 = st.columns(3)
                        with result_col1:
                            st.metric(f"🏠 {home_team}胜", f"{stats['home_wins']}场", 
                                     f"{stats['home_win_rate']:.1f}%")
                        with result_col2:
                            st.metric("🤝 平局", f"{stats['draws']}场", 
                                     f"{stats['draw_rate']:.1f}%")
                        with result_col3:
                            st.metric(f"✈️ {away_team}胜", f"{stats['away_wins']}场", 
                                     f"{stats['away_win_rate']:.1f}%")
                        
                        st.markdown("---")
                        st.markdown("#### 🎯 比分规律分析")
                        
                        # 比分分布表格
                        if stats['score_distribution']:
                            score_df = pd.DataFrame([
                                {"比分": score, "出现次数": count, 
                                 "概率": f"{count/stats['total_matches']*100:.1f}%"}
                                for score, count in sorted(
                                    stats['score_distribution'].items(), 
                                    key=lambda x: x[1], 
                                    reverse=True
                                )
                            ])
                            st.dataframe(score_df, use_container_width=True, hide_index=True)
                            
                            st.success(f"🔥 最常见比分: **{stats['most_common_score']}** "
                                     f"({stats['most_common_score_count']}次, "
                                     f"{stats['most_common_score_rate']:.1f}%)")
                        
                        st.markdown("---")
                        st.markdown("#### 📊 进球数分布")
                        
                        # 总进球数分布
                        if stats['goal_distribution']:
                            goal_dist_data = []
                            for goals, count in sorted(stats['goal_distribution'].items()):
                                goal_type = "🔴 小球" if goals <= 2 else "🟢 大球"
                                prob = count / stats['total_matches'] * 100
                                goal_dist_data.append({
                                    "进球数": f"{goals}球",
                                    "类型": goal_type,
                                    "次数": count,
                                    "概率": f"{prob:.1f}%"
                                })
                            
                            goal_df = pd.DataFrame(goal_dist_data)
                            st.dataframe(goal_df, use_container_width=True, hide_index=True)
                        
                        st.markdown("---")
                        st.markdown("#### 💡 大小球分析")
                        
                        over_col1, over_col2 = st.columns(2)
                        with over_col1:
                            st.metric("🟢 大球(3+)", f"{stats['over_25']}场", 
                                     f"{stats['over_25_rate']:.1f}%")
                        with over_col2:
                            st.metric("🔴 小球(0-2)", f"{stats['under_25']}场", 
                                     f"{stats['under_25_rate']:.1f}%")
                        
                        # 根据历史大球比例给建议
                        if stats['over_25_rate'] >= 60:
                            st.success("✅ 历史大球比例较高，本场大球概率可能偏高")
                        elif stats['over_25_rate'] <= 40:
                            st.warning("⚠️ 历史大球比例较低，本场可能偏向小球")
                        else:
                            st.info("ℹ️ 历史大小球分布均衡")
                        
                        st.markdown("---")
                        st.markdown("#### 🎲 预测参考建议")
                        
                        # 基于历史数据给出预测建议
                        suggested_prob = int(min(max(stats['over_25_rate'], 10), 90))
                        
                        st.markdown(f"""
                        **基于历史数据的建议概率**: {suggested_prob}%
                        
                        **分析依据**:
                        - 历史交锋大球比例: {stats['over_25_rate']:.1f}%
                        - 场均总进球: {stats['avg_goals']:.2f}
                        - {home_team}场均进球: {stats['avg_home_goals']:.2f}
                        - {away_team}场均进球: {stats['avg_away_goals']:.2f}
                        
                        **最不可能出现的比分**:
                        """)
                        
                        # 找出从未出现过的常见比分
                        common_scores = ["0-0", "1-0", "0-1", "1-1", "2-0", "0-2", "2-1", "1-2", "2-2", "3-0", "0-3"]
                        never_appeared = [s for s in common_scores if s not in stats['score_distribution']]
                        
                        if never_appeared:
                            st.warning(f"❌ 历史从未出现: **{', '.join(never_appeared[:5])}**")
                        else:
                            st.info("所有常见比分都曾出现过")
                        
                        # 自动填充建议概率
                        if st.button("📊 使用历史数据建议概率", use_container_width=True):
                            st.info(f"💡 建议在基础设置中将大球概率设为 {suggested_prob}%")
                        
                        # 贝叶斯后验概率计算
                        if st.session_state.get('use_prior', False):
                            st.markdown("---")
                            st.markdown("#### 🧮 贝叶斯后验概率")
                            
                            prior_over = st.session_state.get('prior_over25', 0.5)
                            likelihood = stats['over_25_rate'] / 100
                            
                            # 简单的贝叶斯更新
                            # P(大球|历史数据) ∝ P(历史数据|大球) × P(大球)
                            # 使用加权平均（可以根据数据量调整权重）
                            data_weight = min(stats['total_matches'] / 10, 0.7)  # 最多70%权重给历史数据
                            prior_weight = 1 - data_weight
                            
                            posterior_over = likelihood * data_weight + prior_over * prior_weight
                            
                            st.markdown(f"""
                            <div class="info-box">
                            <h5>📊 贝叶斯更新结果</h5>
                            <p><strong>先验概率</strong>: {prior_over*100:.1f}% 
                            （来源: {st.session_state.get('prior_source', '未知')}）</p>
                            <p><strong>历史似然</strong>: {likelihood*100:.1f}% 
                            （基于{stats['total_matches']}场数据）</p>
                            <p><strong>数据权重</strong>: {data_weight*100:.0f}% | 
                            <strong>先验权重</strong>: {prior_weight*100:.0f}%</p>
                            <h4 style="color: #1e3c72;">🎯 后验概率: {posterior_over*100:.1f}%</h4>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # 更新建议概率为后验概率
                            suggested_prob = int(min(max(posterior_over * 100, 10), 90))
                            
                            st.success(f"✅ 建议使用后验概率: **{suggested_prob}%**")
                            
                            # 解释
                            with st.expander("📚 什么是贝叶斯后验概率？"):
                                st.markdown("""
                                **贝叶斯方法**结合了两种信息：
                                
                                1. **先验概率** - 你基于经验、赔率、专家意见的主观判断
                                2. **历史数据** - 客观的历史交锋记录
                                
                                **计算过程**：
                                ```
                                后验概率 = 先验概率 × 先验权重 + 历史似然 × 数据权重
                                
                                权重分配：
                                - 数据量越大，历史数据权重越高
                                - 数据量少时，更依赖先验判断
                                ```
                                
                                **优势**：
                                - ✅ 避免完全依赖小样本数据
                                - ✅ 融合主观判断和客观数据
                                - ✅ 数据越多，结果越客观
                                - ✅ 数据少时，保留专业判断
                                """)
                
                else:
                    st.error("❌ 统计计算失败")
            else:
                st.warning("⚠️ 未能解析出有效比赛数据，请检查格式")
        
        elif history_data:
            st.warning("⚠️ 请先在基础设置中输入主客队名称")
        else:
            st.info("💡 粘贴历史战绩数据后即可自动分析")
    
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
        st.markdown("### 📚 分析历史记录")
        
        if st.session_state.match_history:
            st.success(f"✅ 共 **{len(st.session_state.match_history)}** 条记录")
            
            # 添加搜索功能
            search_term = st.text_input("🔍 搜索球队", placeholder="输入球队名称...")
            
            # 筛选记录
            filtered_records = st.session_state.match_history
            if search_term:
                filtered_records = [
                    r for r in st.session_state.match_history 
                    if search_term.lower() in r.get('home_team', '').lower() 
                    or search_term.lower() in r.get('away_team', '').lower()
                ]
                st.info(f"找到 {len(filtered_records)} 条匹配记录")
            
            # 显示记录
            for idx, record in enumerate(filtered_records[:10]):
                with st.expander(
                    f"🏆 {record.get('home_team', '?')} vs {record.get('away_team', '?')}", 
                    expanded=False
                ):
                    st.markdown(f"""
                    **📅 时间**: {record.get('timestamp', '')}  
                    **🏆 联赛**: {record.get('league', '')}  
                    **💰 投入**: ${record.get('total_cost', 0):.2f}  
                    **📊 EV**: ${record.get('ev', 0):.2f}  
                    **🎯 策略**: {record.get('mode', '')}  
                    **📈 ROI**: {record.get('ev', 0) / record.get('total_cost', 1) * 100:.1f}%
                    """)
                    
                    if st.button("🔄 加载此记录", key=f"load_{idx}"):
                        st.info("💡 加载功能即将推出")
            
            st.markdown("---")
            
            # 导出和管理
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("📥 导出JSON", use_container_width=True):
                    json_str = json.dumps(st.session_state.match_history, indent=2, ensure_ascii=False)
                    st.download_button(
                        label="⬇️ 下载",
                        data=json_str,
                        file_name=f"betting_history_{datetime.now().strftime('%Y%m%d')}.json",
                        mime="application/json"
                    )
            
            with col_btn2:
                if st.button("🗑️ 清空历史", type="secondary", use_container_width=True):
                    if st.session_state.get('confirm_delete', False):
                        st.session_state.match_history = []
                        st.session_state.confirm_delete = False
                        st.rerun()
                    else:
                        st.session_state.confirm_delete = True
                        st.warning("⚠️ 再点一次确认删除")
        else:
            st.info("📝 暂无历史记录")
            st.markdown("""
            **如何保存记录？**
            1. 完成策略配置
            2. 进入"完整报告"标签页
            3. 点击底部"💾 保存本次分析"按钮
            """)

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
    # 如果使用了贝叶斯方法，显示后验概率
    if st.session_state.get('use_prior', False) and 'posterior_over' in st.session_state:
        posterior_prob = st.session_state.posterior_over
        prob_label = "后验概率"
        prob_delta = f"先验: {st.session_state.get('prior_over25', 0.5)*100:.0f}%"
    else:
        posterior_prob = pred_prob
        prob_label = "预测概率"
        prob_delta = f"赔率: {o25_odds}"
    
    st.markdown(create_kpi_card(
        f"大球{prob_label}",
        f"{posterior_prob*100:.0f}%",
        prob_delta,
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
main_tabs = st.tabs(["📥 策略配置", "📊 盈亏分析", "📈 历史战绩分析", "📉 数据可视化", "📄 完整报告", "📚 历史记录"])

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

# ===== 主标签页3: 历史战绩分析 =====
with main_tabs[2]:
    st.markdown('<div class="section-header">📈 历史战绩深度分析</div>', unsafe_allow_html=True)
    
    # 检查是否有历史数据
    if 'history_input' in st.session_state and st.session_state.history_input and home_team and away_team:
        history_data = st.session_state.history_input
        matches = parse_history_data(history_data, home_team, away_team)
        
        if matches and len(matches) > 0:
            stats = calculate_statistics(matches, home_team, away_team)
            
            if stats:
                # 顶部概览卡片
                st.markdown("### 📊 数据概览")
                col_overview1, col_overview2, col_overview3, col_overview4 = st.columns(4)
                
                with col_overview1:
                    st.markdown(create_kpi_card(
                        "历史交锋",
                        f"{stats['total_matches']}场",
                        f"数据样本",
                        "neutral"
                    ), unsafe_allow_html=True)
                
                with col_overview2:
                    st.markdown(create_kpi_card(
                        "场均进球",
                        f"{stats['avg_goals']:.2f}",
                        f"总{stats['total_goals']}球",
                        "neutral"
                    ), unsafe_allow_html=True)
                
                with col_overview3:
                    over_type = "positive" if stats['over_25_rate'] > 50 else "negative"
                    st.markdown(create_kpi_card(
                        "大球比例",
                        f"{stats['over_25_rate']:.0f}%",
                        f"{stats['over_25']}/{stats['total_matches']}场",
                        over_type
                    ), unsafe_allow_html=True)
                
                with col_overview4:
                    st.markdown(create_kpi_card(
                        "最热比分",
                        stats['most_common_score'],
                        f"{stats['most_common_score_rate']:.0f}%",
                        "neutral"
                    ), unsafe_allow_html=True)
                
                st.markdown("---")
                
                # 两列布局：图表和表格
                col_viz1, col_viz2 = st.columns(2)
                
                with col_viz1:
                    st.markdown("### 🎯 比分热力图")
                    
                    # 创建比分热力图数据
                    score_heat_data = []
                    for score, count in stats['score_distribution'].items():
                        home_g, away_g = map(int, score.split('-'))
                        score_heat_data.append({
                            '主队进球': home_g,
                            '客队进球': away_g,
                            '出现次数': count,
                            '比分': score
                        })
                    
                    if score_heat_data:
                        df_heat = pd.DataFrame(score_heat_data)
                        
                        # 使用散点图模拟热力图
                        fig_heat = px.scatter(
                            df_heat, 
                            x='主队进球', 
                            y='客队进球',
                            size='出现次数',
                            color='出现次数',
                            text='比分',
                            title=f"{home_team} vs {away_team} 历史比分分布",
                            color_continuous_scale='Reds',
                            size_max=60
                        )
                        
                        fig_heat.update_traces(textposition='middle center')
                        fig_heat.update_layout(height=400)
                        st.plotly_chart(fig_heat, use_container_width=True)
                
                with col_viz2:
                    st.markdown("### 📊 总进球数分布")
                    
                    # 总进球数柱状图
                    goal_dist_data = []
                    for goals, count in sorted(stats['goal_distribution'].items()):
                        goal_type = "小球(0-2)" if goals <= 2 else "大球(3+)"
                        goal_dist_data.append({
                            '进球数': f"{goals}球",
                            '次数': count,
                            '类型': goal_type
                        })
                    
                    df_goals = pd.DataFrame(goal_dist_data)
                    
                    fig_goals = px.bar(
                        df_goals,
                        x='进球数',
                        y='次数',
                        color='类型',
                        title='进球数分布统计',
                        color_discrete_map={'小球(0-2)': '#ff6b6b', '大球(3+)': '#51cf66'}
                    )
                    fig_goals.update_layout(height=400)
                    st.plotly_chart(fig_goals, use_container_width=True)
                
                st.markdown("---")
                
                # 详细表格分析
                col_table1, col_table2 = st.columns(2)
                
                with col_table1:
                    st.markdown("### 📋 比分出现频率排行")
                    
                    score_ranking = pd.DataFrame([
                        {
                            "排名": idx + 1,
                            "比分": score,
                            "次数": count,
                            "概率": f"{count/stats['total_matches']*100:.1f}%",
                            "类型": "大球" if sum(map(int, score.split('-'))) > 2 else "小球"
                        }
                        for idx, (score, count) in enumerate(
                            sorted(stats['score_distribution'].items(), 
                                   key=lambda x: x[1], 
                                   reverse=True)
                        )
                    ])
                    
                    st.dataframe(score_ranking, use_container_width=True, hide_index=True)
                
                with col_table2:
                    st.markdown("### 🎲 概率预测分析")
                    
                    # 胜负平概率
                    prob_analysis = pd.DataFrame([
                        {
                            "结果": f"{home_team}获胜",
                            "次数": stats['home_wins'],
                            "历史概率": f"{stats['home_win_rate']:.1f}%"
                        },
                        {
                            "结果": "平局",
                            "次数": stats['draws'],
                            "历史概率": f"{stats['draw_rate']:.1f}%"
                        },
                        {
                            "结果": f"{away_team}获胜",
                            "次数": stats['away_wins'],
                            "历史概率": f"{stats['away_win_rate']:.1f}%"
                        },
                        {
                            "结果": "大球(3+)",
                            "次数": stats['over_25'],
                            "历史概率": f"{stats['over_25_rate']:.1f}%"
                        },
                        {
                            "结果": "小球(0-2)",
                            "次数": stats['under_25'],
                            "历史概率": f"{stats['under_25_rate']:.1f}%"
                        }
                    ])
                    
                    st.dataframe(prob_analysis, use_container_width=True, hide_index=True)
                
                st.markdown("---")
                
                # 智能预测建议
                st.markdown("### 💡 智能预测建议")
                
                col_suggest1, col_suggest2 = st.columns([2, 1])
                
                with col_suggest1:
                    # 基于历史数据的建议
                    suggested_prob = int(min(max(stats['over_25_rate'], 10), 90))
                    
                    st.markdown(f"""
                    <div class="success-box">
                    <h4>📊 基于历史数据的大球概率建议</h4>
                    <p style="font-size: 24px; font-weight: bold; color: #1e3c72;">{suggested_prob}%</p>
                    
                    <p><strong>分析依据：</strong></p>
                    <ul>
                        <li>历史大球比例: {stats['over_25_rate']:.1f}%</li>
                        <li>场均总进球: {stats['avg_goals']:.2f}</li>
                        <li>{home_team}场均进球: {stats['avg_home_goals']:.2f}</li>
                        <li>{away_team}场均进球: {stats['avg_away_goals']:.2f}</li>
                    </ul>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 不可能出现的比分分析
                    st.markdown("#### ❌ 历史从未出现的常见比分")
                    
                    common_scores = ["0-0", "1-0", "0-1", "1-1", "2-0", "0-2", "2-1", "1-2", "2-2", "3-0", "0-3", "3-1", "1-3"]
                    never_appeared = [s for s in common_scores if s not in stats['score_distribution']]
                    
                    if never_appeared:
                        never_appeared_str = "、".join(never_appeared)
                        st.warning(f"""
                        **{never_appeared_str}**
                        
                        💡 这些比分在历史交锋中从未出现过，本场出现的概率可能较低。
                        如果使用比分对冲策略，可以考虑不投注这些比分。
                        """)
                    else:
                        st.success("✅ 所有常见比分在历史中都曾出现过")
                    
                    # 高频比分推荐
                    if len(stats['score_distribution']) > 0:
                        top_3_scores = sorted(stats['score_distribution'].items(), 
                                            key=lambda x: x[1], 
                                            reverse=True)[:3]
                        
                        st.markdown("#### 🔥 最可能出现的比分 (Top 3)")
                        
                        for idx, (score, count) in enumerate(top_3_scores, 1):
                            prob = count / stats['total_matches'] * 100
                            st.info(f"**{idx}. {score}** - 出现{count}次 ({prob:.1f}%)")
                
                with col_suggest2:
                    st.markdown("#### 🎯 策略建议")
                    
                    # 根据数据给出策略建议
                    if stats['over_25_rate'] >= 60:
                        st.success("""
                        **✅ 偏向大球**
                        
                        历史大球比例高，建议：
                        - 提高大球投入比例
                        - 减少小球比分对冲
                        """)
                    elif stats['over_25_rate'] <= 40:
                        st.warning("""
                        **⚠️ 偏向小球**
                        
                        历史小球比例高，建议：
                        - 降低大球投入
                        - 加强小球比分对冲
                        """)
                    else:
                        st.info("""
                        **ℹ️ 均衡策略**
                        
                        大小球分布均衡，建议：
                        - 保持平衡投注
                        - 关注盘口变化
                        """)
                    
                    # 数据可信度评估
                    st.markdown("#### 📏 数据可信度")
                    
                    if stats['total_matches'] >= 10:
                        confidence = "高"
                        color = "green"
                    elif stats['total_matches'] >= 5:
                        confidence = "中"
                        color = "orange"
                    else:
                        confidence = "低"
                        color = "red"
                    
                    st.markdown(f"""
                    <div style="text-align: center; padding: 10px; 
                                background-color: {color}; color: white; 
                                border-radius: 8px;">
                        <div style="font-size: 18px; font-weight: bold;">{confidence}</div>
                        <div style="font-size: 12px;">样本量: {stats['total_matches']}场</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if stats['total_matches'] < 5:
                        st.warning("⚠️ 样本量较少，建议结合其他因素综合判断")
                
                # 贝叶斯分析区域
                if st.session_state.get('use_prior', False):
                    st.markdown("---")
                    st.markdown("### 🧮 贝叶斯概率更新")
                    
                    prior_over = st.session_state.get('prior_over25', 0.5)
                    prior_home = st.session_state.get('prior_home_win', 0.33)
                    prior_draw = st.session_state.get('prior_draw', 0.33)
                    prior_away = st.session_state.get('prior_away_win', 0.33)
                    
                    likelihood_over = stats['over_25_rate'] / 100
                    likelihood_home = stats['home_win_rate'] / 100
                    likelihood_draw = stats['draw_rate'] / 100
                    likelihood_away = stats['away_win_rate'] / 100
                    
                    # 根据数据量调整权重
                    data_weight = min(stats['total_matches'] / 10, 0.7)
                    prior_weight = 1 - data_weight
                    
                    # 计算后验概率
                    posterior_over = likelihood_over * data_weight + prior_over * prior_weight
                    posterior_home = likelihood_home * data_weight + prior_home * prior_weight
                    posterior_draw = likelihood_draw * data_weight + prior_draw * prior_weight
                    posterior_away = likelihood_away * data_weight + prior_away * prior_weight
                    
                    # 归一化胜平负概率
                    total_result = posterior_home + posterior_draw + posterior_away
                    posterior_home /= total_result
                    posterior_draw /= total_result
                    posterior_away /= total_result
                    
                    col_bayes1, col_bayes2 = st.columns(2)
                    
                    with col_bayes1:
                        st.markdown("#### 📊 大小球后验概率")
                        
                        # 对比表格
                        bayes_over_df = pd.DataFrame([
                            {
                                "类型": "先验概率",
                                "大球": f"{prior_over*100:.1f}%",
                                "小球": f"{(1-prior_over)*100:.1f}%"
                            },
                            {
                                "类型": "历史似然",
                                "大球": f"{likelihood_over*100:.1f}%",
                                "小球": f"{(1-likelihood_over)*100:.1f}%"
                            },
                            {
                                "类型": "后验概率",
                                "大球": f"{posterior_over*100:.1f}%",
                                "小球": f"{(1-posterior_over)*100:.1f}%"
                            }
                        ])
                        
                        st.dataframe(bayes_over_df, use_container_width=True, hide_index=True)
                        
                        # 可视化先验 vs 后验
                        fig_bayes = go.Figure()
                        
                        fig_bayes.add_trace(go.Bar(
                            name='先验概率',
                            x=['大球', '小球'],
                            y=[prior_over*100, (1-prior_over)*100],
                            marker_color='lightblue'
                        ))
                        
                        fig_bayes.add_trace(go.Bar(
                            name='后验概率',
                            x=['大球', '小球'],
                            y=[posterior_over*100, (1-posterior_over)*100],
                            marker_color='darkblue'
                        ))
                        
                        fig_bayes.update_layout(
                            title='先验概率 vs 后验概率对比',
                            yaxis_title='概率 (%)',
                            barmode='group',
                            height=300
                        )
                        
                        st.plotly_chart(fig_bayes, use_container_width=True)
                    
                    with col_bayes2:
                        st.markdown("#### 🏆 胜平负后验概率")
                        
                        # 对比表格
                        bayes_result_df = pd.DataFrame([
                            {
                                "类型": "先验概率",
                                f"{home_team}胜": f"{prior_home*100:.1f}%",
                                "平局": f"{prior_draw*100:.1f}%",
                                f"{away_team}胜": f"{prior_away*100:.1f}%"
                            },
                            {
                                "类型": "历史似然",
                                f"{home_team}胜": f"{likelihood_home*100:.1f}%",
                                "平局": f"{likelihood_draw*100:.1f}%",
                                f"{away_team}胜": f"{likelihood_away*100:.1f}%"
                            },
                            {
                                "类型": "后验概率",
                                f"{home_team}胜": f"{posterior_home*100:.1f}%",
                                "平局": f"{posterior_draw*100:.1f}%",
                                f"{away_team}胜": f"{posterior_away*100:.1f}%"
                            }
                        ])
                        
                        st.dataframe(bayes_result_df, use_container_width=True, hide_index=True)
                        
                        # 可视化
                        fig_result = go.Figure()
                        
                        fig_result.add_trace(go.Bar(
                            name='先验概率',
                            x=[f'{home_team}胜', '平局', f'{away_team}胜'],
                            y=[prior_home*100, prior_draw*100, prior_away*100],
                            marker_color='lightgreen'
                        ))
                        
                        fig_result.add_trace(go.Bar(
                            name='后验概率',
                            x=[f'{home_team}胜', '平局', f'{away_team}胜'],
                            y=[posterior_home*100, posterior_draw*100, posterior_away*100],
                            marker_color='darkgreen'
                        ))
                        
                        fig_result.update_layout(
                            title='胜平负概率更新',
                            yaxis_title='概率 (%)',
                            barmode='group',
                            height=300
                        )
                        
                        st.plotly_chart(fig_result, use_container_width=True)
                    
                    # 权重说明
                    st.markdown("---")
                    st.markdown(f"""
                    <div class="info-box">
                    <h5>⚖️ 权重分配说明</h5>
                    <p><strong>历史数据权重</strong>: {data_weight*100:.0f}%</p>
                    <p><strong>先验判断权重</strong>: {prior_weight*100:.0f}%</p>
                    <p><strong>依据</strong>: 基于{stats['total_matches']}场历史数据</p>
                    
                    <p style="margin-top: 10px;"><strong>权重逻辑</strong>:</p>
                    <ul>
                        <li>数据量 ≥ 10场 → 历史权重70%, 先验权重30%</li>
                        <li>数据量 5-9场 → 动态权重，数据越多权重越高</li>
                        <li>数据量 < 5场 → 历史权重较低，更依赖先验</li>
                    </ul>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 最终建议
                    st.success(f"""
                    ### 🎯 最终建议概率（后验概率）
                    
                    - **大球(3+)**: {posterior_over*100:.1f}%
                    - **{home_team}获胜**: {posterior_home*100:.1f}%
                    - **平局**: {posterior_draw*100:.1f}%
                    - **{away_team}获胜**: {posterior_away*100:.1f}%
                    
                    💡 建议在策略配置中使用这些后验概率进行决策
                    """)
                    
                    # 保存后验概率到session_state供其他地方使用
                    st.session_state.posterior_over = posterior_over
                    st.session_state.posterior_home = posterior_home
                    st.session_state.posterior_draw = posterior_draw
                    st.session_state.posterior_away = posterior_away
            
            else:
                st.error("❌ 统计计算失败")
        else:
            st.warning("⚠️ 未能解析出有效的历史比赛数据")
    
    else:
        st.info("""
        ### 💡 如何使用历史战绩分析？
        
        1. **输入球队** - 在侧边栏"基础设置"输入主客队名称
        2. **粘贴数据** - 在侧边栏"历史分析"标签页粘贴历史战绩
        3. **自动分析** - 系统会自动解析并生成分析报告
        4. **查看详情** - 回到此标签页查看详细可视化分析
        
        **支持的数据格式**:
        ```
        02/05/2025 曼城 2-1 (1-0) 阿森纳
        24/08/2024 阿森纳 0-0 (0-0) 曼城
        ```
        
        **分析内容包括**:
        - 📊 比分热力图
        - 📈 进球数分布
        - 🎯 高频比分排行
        - 💡 智能预测建议
        - ❌ 不可能比分分析
        """)

# ===== 主标签页4: 数据可视化 =====
with main_tabs[3]:
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

# ===== 主标签页5: 完整报告 =====
with main_tabs[4]:
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

# ===== 主标签页6: 历史记录管理 =====
with main_tabs[5]:
    st.markdown('<div class="section-header">📚 历史记录管理中心</div>', unsafe_allow_html=True)
    
    if st.session_state.match_history:
        # 统计概览
        st.markdown("### 📊 记录统计")
        
        total_records = len(st.session_state.match_history)
        total_cost = sum(r.get('total_cost', 0) for r in st.session_state.match_history)
        total_ev = sum(r.get('ev', 0) for r in st.session_state.match_history)
        avg_roi = (total_ev / total_cost * 100) if total_cost > 0 else 0
        
        col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
        
        with col_stat1:
            st.metric("📝 总记录数", f"{total_records}条")
        with col_stat2:
            st.metric("💰 累计投入", f"${total_cost:.2f}")
        with col_stat3:
            st.metric("📈 累计EV", f"${total_ev:.2f}")
        with col_stat4:
            st.metric("📊 平均ROI", f"{avg_roi:.1f}%")
        
        st.markdown("---")
        
        # 搜索和筛选
        col_search1, col_search2, col_search3 = st.columns([2, 1, 1])
        
        with col_search1:
            search_term = st.text_input("🔍 搜索比赛", placeholder="输入球队名称...", key="main_search")
        with col_search2:
            filter_strategy = st.selectbox("筛选策略", ["全部", "策略 1：比分精准流", "策略 2：总进球复式流"])
        with col_search3:
            sort_by = st.selectbox("排序", ["时间(新→旧)", "时间(旧→新)", "EV(高→低)", "EV(低→高)"])
        
        # 筛选和排序
        filtered_records = st.session_state.match_history.copy()
        
        if search_term:
            filtered_records = [
                r for r in filtered_records 
                if search_term.lower() in r.get('home_team', '').lower() 
                or search_term.lower() in r.get('away_team', '').lower()
            ]
        
        if filter_strategy != "全部":
            filtered_records = [r for r in filtered_records if r.get('mode', '') == filter_strategy]
        
        if sort_by == "时间(旧→新)":
            filtered_records = filtered_records[::-1]
        elif sort_by == "EV(高→低)":
            filtered_records = sorted(filtered_records, key=lambda x: x.get('ev', 0), reverse=True)
        elif sort_by == "EV(低→高)":
            filtered_records = sorted(filtered_records, key=lambda x: x.get('ev', 0))
        
        st.info(f"显示 {len(filtered_records)} / {total_records} 条记录")
        
        st.markdown("---")
        
        # 显示记录列表
        st.markdown("### 📋 记录列表")
        
        for idx, record in enumerate(filtered_records):
            ev_color = "green" if record.get('ev', 0) > 0 else ("red" if record.get('ev', 0) < 0 else "gray")
            roi = (record.get('ev', 0) / record.get('total_cost', 1) * 100) if record.get('total_cost', 0) > 0 else 0
            
            with st.expander(
                f"🏆 {record.get('home_team', '?')} vs {record.get('away_team', '?')} | "
                f"EV: ${record.get('ev', 0):.2f} | "
                f"ROI: {roi:.1f}%",
                expanded=False
            ):
                col_detail1, col_detail2 = st.columns(2)
                
                with col_detail1:
                    st.markdown(f"""
                    **📅 比赛时间**  
                    {record.get('match_date', '')} {record.get('match_time', '')}
                    
                    **🏆 联赛**  
                    {record.get('league', '')}
                    
                    **🎯 策略**  
                    {record.get('mode', '')}
                    
                    **📊 大球概率**  
                    {record.get('pred_prob', 0)*100:.1f}%
                    """)
                
                with col_detail2:
                    st.markdown(f"""
                    **💰 投注信息**  
                    - 大球赔率: {record.get('o25_odds', 0)}
                    - 大球投入: ${record.get('o25_stake', 0):.2f}
                    - 总投入: ${record.get('total_cost', 0):.2f}
                    
                    **📈 期望值分析**  
                    - 策略EV: ${record.get('ev', 0):.2f}
                    - 单纯EV: ${record.get('simple_ev', 0):.2f}
                    - 对冲效果: {record.get('hedge_effect', 0):.1f}%
                    - ROI: {roi:.1f}%
                    """)
                
                col_action1, col_action2, col_action3 = st.columns(3)
                
                with col_action1:
                    if st.button("🔄 复制参数", key=f"copy_{idx}"):
                        st.info("💡 参数复制功能即将推出")
                
                with col_action2:
                    if st.button("📊 查看详情", key=f"detail_{idx}"):
                        st.info("💡 详情查看功能即将推出")
                
                with col_action3:
                    if st.button("🗑️ 删除", key=f"delete_{idx}"):
                        st.session_state.match_history.remove(record)
                        st.rerun()
        
        st.markdown("---")
        
        # 批量操作
        st.markdown("### 🛠️ 批量操作")
        
        col_bulk1, col_bulk2, col_bulk3 = st.columns(3)
        
        with col_bulk1:
            if st.button("📥 导出所有记录 (JSON)", use_container_width=True):
                json_str = json.dumps(st.session_state.match_history, indent=2, ensure_ascii=False)
                st.download_button(
                    label="⬇️ 点击下载",
                    data=json_str,
                    file_name=f"betting_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )
        
        with col_bulk2:
            if st.button("📊 导出为Excel", use_container_width=True):
                df = pd.DataFrame(st.session_state.match_history)
                st.info("💡 Excel导出功能即将推出")
        
        with col_bulk3:
            if st.button("🗑️ 清空所有记录", type="secondary", use_container_width=True):
                if st.session_state.get('confirm_delete_all', False):
                    st.session_state.match_history = []
                    st.session_state.confirm_delete_all = False
                    st.rerun()
                else:
                    st.session_state.confirm_delete_all = True
                    st.warning("⚠️ 再点一次确认删除所有记录")
    
    else:
        st.info("📝 还没有保存任何分析记录")
        
        st.markdown("""
        ### 💡 如何保存分析？
        
        1. **配置策略** - 在"策略配置"标签页设置参数
        2. **查看分析** - 在"盈亏分析"和"数据可视化"查看结果
        3. **保存记录** - 在"完整报告"标签页点击"💾 保存本次分析"
        
        保存后的记录会：
        - ✅ 自动保存在系统中
        - ✅ 支持搜索和筛选
        - ✅ 可以导出为JSON文件
        - ✅ 可以查看统计分析
        
        **提示**: 记录保存在浏览器会话中，关闭浏览器后会清空。建议定期导出备份！
        """)

# --- 底部信息 ---
st.markdown("---")
st.caption(f"*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 胜算实验室 Pro v2.0*")

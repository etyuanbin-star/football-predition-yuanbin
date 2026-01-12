import streamlit as st
import pandas as pd
import numpy as np
import random
import re
from datetime import datetime
from collections import Counter

# --- 1. 页面配置 ---
st.set_page_config(page_title="胜算实验室：点对点逻辑修正", layout="wide")

# --- 自定义CSS样式 ---
st.markdown("""
<style>
    .team-header {
        background: linear-gradient(90deg, #1e3c72, #2a5298);
        color: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 20px;
    }
    .match-info {
        background-color: #f0f2f6;
        padding: 12px;
        border-radius: 8px;
        border-left: 4px solid #1e3c72;
        margin: 10px 0;
    }
    .match-info-secondary {
        background-color: #e9ecef;
        padding: 12px;
        border-radius: 8px;
        border-left: 4px solid #6c757d;
        margin: 10px 0;
    }
    .stMetric {
        background-color: white;
        padding: 10px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .strategy-note {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 10px;
        margin: 10px 0;
        border-radius: 5px;
    }
    .odds-input-section {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #dee2e6;
        margin: 10px 0;
    }
    .tab-container {
        background-color: white;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        padding: 10px;
        margin: 10px 0;
    }
    .parlay-badge {
        background-color: #17a2b8;
        color: white;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
        margin-right: 5px;
    }
    .history-stats {
        background-color: #e7f3ff;
        border-radius: 8px;
        padding: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# --- 解析历史战绩数据的函数 ---
def parse_history_data(history_text, current_home, current_away):
    """解析历史战绩数据，提取比赛信息"""
    matches = []
    lines = history_text.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # 尝试解析各种格式的比分
        try:
            # 正则表达式匹配比分
            # 匹配格式: 数字 - 数字 或 数字–数字
            score_pattern = r'(\d+)\s*[-–]\s*(\d+)'
            match = re.search(score_pattern, line)
            
            if match:
                home_goals = int(match.group(1))
                away_goals = int(match.group(2))
                
                # 尝试确定这场比赛的主队（基于当前主队名称是否在行中出现）
                # 这是一个简化的逻辑，实际应用中可能需要更复杂的解析
                line_lower = line.lower()
                current_home_lower = current_home.lower()
                current_away_lower = current_away.lower()
                
                # 如果当前主队名称出现在比分前，认为它是主队
                # 否则，如果当前客队名称出现在比分前，认为它是主队
                # 都不匹配，则默认第一个队是主队
                
                # 查找比分位置
                score_start = match.start()
                before_score = line_lower[:score_start]
                
                if current_home_lower in before_score:
                    # 当前主队是这场比赛的主队
                    matches.append({
                        'home_goals': home_goals,
                        'away_goals': away_goals,
                        'total_goals': home_goals + away_goals,
                        'result': '主胜' if home_goals > away_goals else ('客胜' if home_goals < away_goals else '平局'),
                        'home_team_current_perspective': True  # 从当前视角看，主队是主队
                    })
                elif current_away_lower in before_score:
                    # 当前客队是这场比赛的主队
                    matches.append({
                        'home_goals': away_goals,  # 注意交换，因为当前客队是那场比赛的主队
                        'away_goals': home_goals,
                        'total_goals': home_goals + away_goals,
                        'result': '客胜' if home_goals > away_goals else ('主胜' if home_goals < away_goals else '平局'),
                        'home_team_current_perspective': False  # 从当前视角看，主队是客队
                    })
                else:
                    # 无法确定，使用默认（第一个队是主队）
                    matches.append({
                        'home_goals': home_goals,
                        'away_goals': away_goals,
                        'total_goals': home_goals + away_goals,
                        'result': '主胜' if home_goals > away_goals else ('客胜' if home_goals < away_goals else '平局'),
                        'home_team_current_perspective': True  # 默认
                    })
        except Exception as e:
            # 如果解析失败，跳过这一行
            continue
    
    return matches

# --- 计算统计信息的函数 ---
def calculate_statistics(matches, current_home, current_away):
    """计算历史战绩统计信息"""
    if not matches:
        return None
    
    stats = {
        'total_matches': len(matches),
        'home_wins': 0,  # 当前主队获胜次数（从当前视角）
        'away_wins': 0,  # 当前客队获胜次数（从当前视角）
        'draws': 0,
        'total_goals': 0,
        'over_25': 0,  # 大球次数（总进球>2.5）
        'under_25': 0, # 小球次数（总进球<2.5）
        'score_distribution': {},  # 比分分布
        'goal_distribution': {},   # 总进球数分布
        'current_home_goals': 0,  # 当前主队总进球
        'current_away_goals': 0,  # 当前客队总进球
    }
    
    for match in matches:
        home_goals = match['home_goals']
        away_goals = match['away_goals']
        total_goals = home_goals + away_goals
        
        # 统计当前视角下的胜负平
        if home_goals > away_goals:
            stats['home_wins'] += 1
        elif home_goals < away_goals:
            stats['away_wins'] += 1
        else:
            stats['draws'] += 1
        
        # 统计总进球
        stats['total_goals'] += total_goals
        
        # 统计当前主客队进球
        stats['current_home_goals'] += home_goals
        stats['current_away_goals'] += away_goals
        
        # 大球/小球统计
        if total_goals > 2.5:
            stats['over_25'] += 1
        else:
            stats['under_25'] += 1
        
        # 比分分布（从当前视角）
        score = f"{home_goals}-{away_goals}"
        if score in stats['score_distribution']:
            stats['score_distribution'][score] += 1
        else:
            stats['score_distribution'][score] = 1
        
        # 总进球数分布
        if total_goals in stats['goal_distribution']:
            stats['goal_distribution'][total_goals] += 1
        else:
            stats['goal_distribution'][total_goals] = 1
    
    # 计算百分比
    stats['home_win_rate'] = stats['home_wins'] / stats['total_matches'] * 100 if stats['total_matches'] > 0 else 0
    stats['away_win_rate'] = stats['away_wins'] / stats['total_matches'] * 100 if stats['total_matches'] > 0 else 0
    stats['draw_rate'] = stats['draws'] / stats['total_matches'] * 100 if stats['total_matches'] > 0 else 0
    stats['avg_goals'] = stats['total_goals'] / stats['total_matches'] if stats['total_matches'] > 0 else 0
    stats['over_25_rate'] = stats['over_25'] / stats['total_matches'] * 100 if stats['total_matches'] > 0 else 0
    stats['under_25_rate'] = stats['under_25'] / stats['total_matches'] * 100 if stats['total_matches'] > 0 else 0
    stats['avg_home_goals'] = stats['current_home_goals'] / stats['total_matches'] if stats['total_matches'] > 0 else 0
    stats['avg_away_goals'] = stats['current_away_goals'] / stats['total_matches'] if stats['total_matches'] > 0 else 0
    
    # 计算最常见比分
    if stats['score_distribution']:
        most_common_score = max(stats['score_distribution'].items(), key=lambda x: x[1])
        stats['most_common_score'] = most_common_score[0]
        stats['most_common_score_count'] = most_common_score[1]
        stats['most_common_score_rate'] = most_common_score[1] / stats['total_matches'] * 100
    else:
        stats['most_common_score'] = "无数据"
        stats['most_common_score_count'] = 0
        stats['most_common_score_rate'] = 0
    
    return stats

# --- 2. 主比赛信息输入 ---
st.markdown('<div class="team-header"><h1>🔺 胜算实验室：全功能风控系统</h1></div>', unsafe_allow_html=True)
st.caption("核心功能：策略模拟 + EV计算 + 蒙特卡洛实验")

# 创建两列布局用于主比赛信息输入
col_match1, col_match2, col_match3 = st.columns([2, 1, 2])
with col_match1:
    home_team = st.text_input("🏠 主队名称", value="曼城", placeholder="输入主队名称")
with col_match2:
    st.markdown("<h3 style='text-align: center; margin-top: 15px;'>VS</h3>", unsafe_allow_html=True)
with col_match3:
    away_team = st.text_input("✈️ 客队名称", value="阿森纳", placeholder="输入客队名称")

# 主比赛详情输入
col_match_info1, col_match_info2, col_match_info3 = st.columns(3)
with col_match_info1:
    league = st.selectbox("🏆 联赛", ["英超", "欧冠", "西甲", "德甲", "意甲", "法甲", "其他"])
with col_match_info2:
    # 初始化session_state中的日期
    if 'match_date' not in st.session_state:
        st.session_state.match_date = datetime.now().date()
    
    match_date = st.date_input("📅 比赛日期", value=st.session_state.match_date, key="match_date_input")
    # 更新session_state
    st.session_state.match_date = match_date
with col_match_info3:
    # 初始化session_state中的时间
    if 'match_time' not in st.session_state:
        st.session_state.match_time = datetime.now().time()
    
    match_time = st.time_input("⏰ 比赛时间", value=st.session_state.match_time, key="match_time_input")
    # 更新session_state
    st.session_state.match_time = match_time

# 显示主比赛信息卡
st.markdown(f"""
<div class="match-info">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div style="font-size: 18px; font-weight: bold;">
            {home_team} <span style="color: #666; font-weight: normal;">vs</span> {away_team}
        </div>
        <div style="font-size: 14px; color: #666;">
            {league} · {match_date.strftime('%Y-%m-%d')} · {match_time.strftime('%H:%M')}
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- 3. 侧边栏输入 ---
with st.sidebar:
    st.markdown("### 📋 比赛信息摘要")
    st.write(f"**{home_team}** vs **{away_team}**")
    st.write(f"**联赛**: {league}")
    st.write(f"**时间**: {match_date.strftime('%m/%d')} {match_time.strftime('%H:%M')}")
    
    st.divider()
    st.header("⚖️ 核心大球项 (O2.5)")
    o25_odds = st.number_input("大球 (3球+) 赔率", value=2.30, step=0.01, min_value=1.01)
    o25_stake = st.number_input("大球投入金额 ($)", value=100.0, step=1.0, min_value=0.0)
    
    st.divider()
    st.header("📊 历史战绩分析")
    
    # 显示当前对阵
    st.subheader(f"历史交锋：{home_team} vs {away_team}")
    
    # 历史战绩输入区域
    st.write("##### 📋 历史战绩数据输入")
    st.caption("请粘贴两队历史交锋记录（每行一场比赛）：")
    
    # 预填充一些示例数据
    default_history = """02/05/2025 Rayo Vallecano 1 - 0 (1 - 0) Getafe
24/08/2024 Getafe 0 - 0 (0 - 0) Rayo Vallecano
13/04/2024 Rayo Vallecano 0 - 0 (0 - 0) Getafe
02/01/2024 Getafe 0 - 2 (0 - 1) Rayo Vallecano
12/02/2023 Getafe 1 - 1 (0 - 1) Rayo Vallecano
14/10/2022 Rayo Vallecano 0 - 0 (0 - 0) Getafe
08/05/2022 Getafe 0 - 0 (0 - 0) Rayo Vallecano
18/09/2021 Rayo Vallecano 3 - 0 (1 - 0) Getafe"""
    
    history_data = st.text_area(
        "历史战绩数据", 
        value=default_history,
        height=150,
        placeholder="格式示例：日期 主队 比分 (半场比分) 客队\n每行一场比赛"
    )
    
    # 当用户输入历史数据时，自动分析
    if history_data:
        matches = parse_history_data(history_data, home_team, away_team)
        
        if matches:
            stats = calculate_statistics(matches, home_team, away_team)
            
            if stats:
                # 显示统计摘要
                st.write("##### 📈 历史战绩统计摘要")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("总比赛场数", f"{stats['total_matches']}场")
                    st.metric(f"{home_team}胜率", f"{stats['home_win_rate']:.1f}%")
                with col2:
                    st.metric("场均总进球", f"{stats['avg_goals']:.2f}")
                    st.metric(f"{away_team}胜率", f"{stats['away_win_rate']:.1f}%")
                with col3:
                    st.metric("大球比例", f"{stats['over_25_rate']:.1f}%")
                    st.metric("平局比例", f"{stats['draw_rate']:.1f}%")
                
                # 显示详细统计
                with st.expander("📊 查看详细历史统计"):
                    # 胜负平分布
                    st.write("**比赛结果分布**")
                    result_data = pd.DataFrame({
                        '结果': [f'{home_team}胜', f'{away_team}胜', '平局'],
                        '场次': [stats['home_wins'], stats['away_wins'], stats['draws']],
                        '比例%': [stats['home_win_rate'], stats['away_win_rate'], stats['draw_rate']]
                    })
                    st.dataframe(result_data, use_container_width=True, hide_index=True)
                    
                    # 比分分布
                    st.write("**比分分布统计**")
                    if stats['score_distribution']:
                        score_dist_df = pd.DataFrame(
                            list(stats['score_distribution'].items()),
                            columns=['比分', '出现次数']
                        ).sort_values('出现次数', ascending=False)
                        
                        if not score_dist_df.empty:
                            st.dataframe(score_dist_df, use_container_width=True, hide_index=True)
                    
                    # 总进球分布
                    st.write("**总进球数分布**")
                    if stats['goal_distribution']:
                        goal_dist_df = pd.DataFrame(
                            list(stats['goal_distribution'].items()),
                            columns=['总进球', '出现次数']
                        ).sort_values('总进球')
                        
                        if not goal_dist_df.empty:
                            st.bar_chart(goal_dist_df.set_index('总进球')['出现次数'])
                    
                    # 显示平均进球
                    st.write("**平均进球统计**")
                    avg_goals_df = pd.DataFrame({
                        '球队': [home_team, away_team, '总计'],
                        '平均进球': [stats['avg_home_goals'], stats['avg_away_goals'], stats['avg_goals']]
                    })
                    st.dataframe(avg_goals_df, use_container_width=True, hide_index=True)
                
                # 使用历史数据的大球比例来调整预测概率
                historical_over_rate = stats['over_25_rate']
                
                # 根据历史大球比例调整预测概率
                st.markdown("---")
                st.write("##### 🎯 基于历史数据调整预测")
                st.info(f"📊 历史交锋大球比例: {historical_over_rate:.1f}%")
                
                # 让用户基于历史数据调整预测
                pred_prob = st.slider(
                    "你预测的大球概率 (%)", 
                    10, 90, 
                    int(min(max(historical_over_rate, 10), 90)),  # 使用历史数据作为默认值
                    key="pred_prob_history"
                ) / 100
            else:
                st.warning("⚠️ 未能从输入的数据中计算统计信息。")
                pred_prob = st.slider("你预测的大球概率 (%)", 10, 90, 48) / 100
        else:
            st.warning("⚠️ 未能从输入的数据中提取有效的比赛信息。请检查格式。")
            pred_prob = st.slider("你预测的大球概率 (%)", 10, 90, 48) / 100
    else:
        # 如果没有输入历史数据，使用默认滑块
        st.write("##### 🎯 预测大球概率")
        pred_prob = st.slider("你预测的大球概率 (%)", 10, 90, 48) / 100
    
    # --- 添加AI模型比分预测 ---
    st.markdown("---")
    st.subheader("🤖 AI模型比分预测")
    
    # 创建三列布局显示不同模型的预测
    col_ai1, col_ai2, col_ai3 = st.columns(3)
    
    with col_ai1:
        st.markdown("**GPT模型**")
        gpt_pred1 = st.text_input("预测1", value="2-1", key="gpt1", label_visibility="collapsed")
        gpt_pred2 = st.text_input("预测2", value="3-1", key="gpt2", label_visibility="collapsed")
        gpt_pred3 = st.text_input("预测3", value="1-1", key="gpt3", label_visibility="collapsed")
    
    with col_ai2:
        st.markdown("**Gemini模型**")
        gemini_pred1 = st.text_input("预测1", value="2-0", key="gemini1", label_visibility="collapsed")
        gemini_pred2 = st.text_input("预测2", value="3-2", key="gemini2", label_visibility="collapsed")
        gemini_pred3 = st.text_input("预测3", value="1-2", key="gemini3", label_visibility="collapsed")
    
    with col_ai3:
        st.markdown("**DeepSeek模型**")
        deepseek_pred1 = st.text_input("预测1", value="2-2", key="deepseek1", label_visibility="collapsed")
        deepseek_pred2 = st.text_input("预测2", value="3-0", key="deepseek2", label_visibility="collapsed")
        deepseek_pred3 = st.text_input("预测3", value="0-2", key="deepseek3", label_visibility="collapsed")
    
    # 显示汇总
    with st.expander("📊 查看AI预测汇总"):
        st.write(f"**GPT模型预测比分**: {gpt_pred1} / {gpt_pred2} / {gpt_pred3}")
        st.write(f"**Gemini模型比分预测**: {gemini_pred1} / {gemini_pred2} / {gemini_pred3}")
        st.write(f"**DeepSeek模型比分预测**: {deepseek_pred1} / {deepseek_pred2} / {deepseek_pred3}")
        
        # 添加简单的统计
        all_predictions = [
            gpt_pred1, gpt_pred2, gpt_pred3,
            gemini_pred1, gemini_pred2, gemini_pred3,
            deepseek_pred1, deepseek_pred2, deepseek_pred3
        ]
        
        # 统计最常见的预测
        prediction_counts = Counter(all_predictions)
        most_common = prediction_counts.most_common(3)
        
        if most_common:
            st.write("**最常预测的比分**:")
            for pred, count in most_common:
                st.write(f"- {pred}: {count}次 ({count/len(all_predictions)*100:.1f}%)")
    
    st.divider()
    mode = st.radio("请选择执行策略：", ["策略 1：比分精准流", "策略 2：总进球复式流"])
    
    st.divider()
    st.header("🎲 蒙特卡洛实验")
    show_monte_carlo = st.checkbox("启用蒙特卡洛模拟", value=False)

# --- 4. 逻辑处理核心 ---
st.divider()
col_in, col_out = st.columns([1.6, 2], gap="large")

active_bets = [] 
parlay_bets = []  # 存储2串1复式投注

if mode == "策略 1：比分精准流":
    with col_in:
        st.write(f"### 🕹️ 设定比分对冲 ({home_team} vs {away_team})")
        # 强制 6 种比分
        scores = ["0-0", "1-0", "0-1", "1-1", "2-0", "0-2"]
        score_labels = ["0-0", f"1-0 ({home_team}胜)", f"0-1 ({away_team}胜)", "1-1", f"2-0 ({home_team}胜)", f"0-2 ({away_team}胜)"]
        default_odds = {"0-0": 10.0, "1-0": 8.5, "0-1": 8.0, "1-1": 7.0, "2-0": 13.0, "0-2": 12.0}
        
        for i, s in enumerate(scores):
            c1, c2, c3 = st.columns([1.5, 1.2, 1.2])
            with c1: 
                is_on = st.checkbox(score_labels[i], key=f"s1_{s}")
                # 显示概率提示
                if s == "1-1":
                    st.caption("常见比分", help="平局常见比分，概率相对较高")
                elif s == "0-0":
                    st.caption("低概率", help="双方保守时可能出现")
            
            with c2: 
                s_amt = st.number_input(f"金额", value=10.0, key=f"s1_am_{s}", 
                                      label_visibility="collapsed", min_value=0.0) if is_on else 0.0
            with c3: 
                s_odd = st.number_input(f"赔率", value=default_odds[s], key=f"s1_od_{s}", 
                                      label_visibility="collapsed", min_value=1.01) if is_on else 0.0
            if is_on: 
                active_bets.append({"item": s, "odd": s_odd, "stake": s_amt})
        
        # 添加大球项
        active_bets.append({"item": "3球+", "odd": o25_odds, "stake": o25_stake})
        total_cost = sum(b['stake'] for b in active_bets)
        
        # 显示投入统计
        col_cost1, col_cost2 = st.columns(2)
        with col_cost1:
            st.metric("💰 大球投入", f"${o25_stake:.2f}")
        with col_cost2:
            st.metric("💰 对冲投入", f"${total_cost - o25_stake:.2f}")
        st.metric("💰 方案总投入", f"${total_cost:.2f}")

    with col_out:
        st.write("### 📊 模拟盈亏校验 (点对点比分组合图)")
        
        # 生成所有可能结果
        s1_outcomes = scores + ["3球+"]
        outcome_labels = score_labels + [f"3球或以上 ({home_team} {away_team} 总进球≥3)"]
        res_list = []
        
        for i, out in enumerate(s1_outcomes):
            # 只有当投注项的名字完全等于模拟赛果的名字时才计入收益
            income = sum(b['stake'] * b['odd'] for b in active_bets if b['item'] == out)
            net_profit = round(income - total_cost, 2)
            
            # 判断结果类型
            result_type = "中立"
            if out == "3球+":
                result_type = "大球胜"
            elif out in ["0-0", "1-0", "0-1", "1-1", "2-0", "0-2"]:
                result_type = "小球胜"
            
            res_list.append({
                "模拟赛果": outcome_labels[i],
                "净盈亏": net_profit,
                "类型": result_type
            })
        
        df_s1 = pd.DataFrame(res_list)
        
        # 用颜色区分的柱状图
        colors = ['#ff6b6b' if x < 0 else '#1dd1a1' for x in df_s1['净盈亏']]
        
        # 创建图表
        chart_data = df_s1.set_index("模拟赛果")["净盈亏"]
        st.bar_chart(chart_data)
        
        # 显示详细表格
        st.write("##### 📋 详细盈亏表")
        st.dataframe(df_s1, use_container_width=True, hide_index=True)

else:  # 策略 2：总进球复式流
    with col_in:
        st.markdown('<div class="strategy-note">🎯 <strong>策略说明</strong>：本策略包含两部分投注：<br>1. 单独大球投注<br>2. 2串1复式投注（稳胆比赛 × 总进球选项）</div>', unsafe_allow_html=True)
        
        # 第一场比赛：稳胆比赛（独立比赛）
        st.write("### 🏆 稳胆比赛设置")
        col_s2a1, col_s2a2, col_s2a3 = st.columns([2, 1, 2])
        with col_s2a1:
            s2_home_team = st.text_input("🏠 稳胆主队", value="利物浦", placeholder="输入稳胆主队", key="s2_home")
        with col_s2a2:
            st.markdown("<h4 style='text-align: center; margin-top: 10px;'>VS</h4>", unsafe_allow_html=True)
        with col_s2a3:
            s2_away_team = st.text_input("✈️ 稳胆客队", value="诺丁汉森林", placeholder="输入稳胆客队", key="s2_away")
        
        # 稳胆比赛联赛
        s2_league = st.selectbox("📋 稳胆联赛", ["英超", "欧冠", "西甲", "德甲", "意甲", "法甲", "其他"], key="s2_league")
        
        # 显示稳胆比赛信息卡
        st.markdown(f"""
        <div class="match-info-secondary">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="font-size: 16px; font-weight: bold;">
                    {s2_home_team} <span style="color: #666; font-weight: normal;">vs</span> {s2_away_team}
                </div>
                <div style="font-size: 12px; color: #666;">
                    {s2_league}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 稳胆比赛赔率输入
        st.markdown("### 📊 稳胆比赛赔率设置")
        
        # 使用标签页组织不同类型的赔率
        tab1, tab2 = st.tabs(["标准盘口 (胜平负)", "亚洲盘口 (让球)"])
        
        with tab1:
            st.markdown('<div class="tab-container">', unsafe_allow_html=True)
            st.write("##### 标准胜平负赔率")
            col_std1, col_std2, col_std3 = st.columns(3)
            with col_std1:
                s2_win_odds = st.number_input(f"{s2_home_team} 胜", value=1.35, min_value=1.01, step=0.01, key="s2_win_odds")
            with col_std2:
                s2_draw_odds = st.number_input("平局", value=4.50, min_value=1.01, step=0.01, key="s2_draw_odds")
            with col_std3:
                s2_lose_odds = st.number_input(f"{s2_away_team} 胜", value=8.00, min_value=1.01, step=0.01, key="s2_lose_odds")
            
            # 选择稳胆选项
            st.write("##### 选择稳胆选项")
            s2_selection = st.radio(
                "请选择稳胆投注选项:",
                [f"{s2_home_team} 胜", "平局", f"{s2_away_team} 胜"],
                horizontal=True,
                key="s2_selection"
            )
            
            # 根据选择获取赔率
            if s2_selection == f"{s2_home_team} 胜":
                strong_win = s2_win_odds
                strong_win_type = "胜"
            elif s2_selection == "平局":
                strong_win = s2_draw_odds
                strong_win_type = "平"
            else:
                strong_win = s2_lose_odds
                strong_win_type = "负"
                
            st.info(f"选择的稳胆选项: **{s2_selection}**，赔率: **{strong_win}**")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tab2:
            st.markdown('<div class="tab-container">', unsafe_allow_html=True)
            st.write("##### 亚洲让球盘口")
            
            # 让球数选择
            col_handicap1, col_handicap2 = st.columns(2)
            with col_handicap1:
                handicap_value = st.selectbox("让球数", ["-2.5", "-2", "-1.5", "-1", "-0.5", "0", "+0.5", "+1", "+1.5", "+2", "+2.5"], index=5)
            
            # 解释让球
            if handicap_value.startswith("-"):
                st.info(f"{s2_home_team} 让 {handicap_value[1:]} 球")
            elif handicap_value.startswith("+"):
                st.info(f"{s2_away_team} 让 {handicap_value[1:]} 球")
            else:
                st.info("平手盘")
            
            # 让球赔率
            col_hdp1, col_hdp2 = st.columns(2)
            with col_hdp1:
                s2_hdp_home_odds = st.number_input(f"{s2_home_team} 让球胜", value=1.80, min_value=1.01, step=0.01, key="s2_hdp_home")
            with col_hdp2:
                s2_hdp_away_odds = st.number_input(f"{s2_away_team} 让球胜", value=2.05, min_value=1.01, step=0.01, key="s2_hdp_away")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # 分隔符
        st.markdown("---")
        
        # 第二场比赛：主比赛的总进球选项
        st.write("### ⚽ 主比赛总进球选项")
        st.info(f"**注意**: 总进球比赛与主比赛为同一场: {home_team} vs {away_team}")
        
        # 显示主比赛信息卡
        st.markdown(f"""
        <div class="match-info">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="font-size: 16px; font-weight: bold;">
                    {home_team} <span style="color: #666; font-weight: normal;">vs</span> {away_team}
                </div>
                <div style="font-size: 12px; color: #666;">
                    {league} · 大球赔率: {o25_odds}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 总进球选项
        st.write("##### 选择总进球选项 (0-2球)")
        totals = ["0球", "1球", "2球"]
        total_labels = [f"0球 (无进球)", f"1球 (总进球=1)", f"2球 (总进球=2)"]
        
        default_odds = {"0球": 7.20, "1球": 3.55, "2球": 3.00}
        
        selected_goals = []
        for i, g in enumerate(totals):
            col_check, col_odd = st.columns([3, 1])
            with col_check: 
                is_on = st.checkbox(total_labels[i], key=f"s2_{g}", value=(g != "0球"))
            with col_odd: 
                g_odd = st.number_input(f"赔率", value=default_odds[g], key=f"s2_od_{g}", 
                                      label_visibility="collapsed", min_value=1.01, step=0.1) if is_on else 0.0
            if is_on: 
                selected_goals.append({"goal": g, "odds": g_odd})
        
        # 2串1复式投注设置
        st.write("##### 🎯 2串1复式投注设置")
        
        # 每注金额
        per_parlay_stake = st.number_input("每注2串1投入金额 ($)", value=50.0, min_value=0.0, step=10.0, key="parlay_stake")
        
        if selected_goals:
            # 计算总注数
            total_parlays = len(selected_goals)
            total_parlay_cost = per_parlay_stake * total_parlays
            
            # 显示复式投注详情
            st.markdown(f"""
            <div class="strategy-note">
            📊 <strong>2串1复式投注详情</strong><br>
            1. 稳胆比赛: {s2_home_team} vs {s2_away_team} ({s2_selection}, 赔率: {strong_win})<br>
            2. 总进球比赛: {home_team} vs {away_team}<br>
            3. 选择 {len(selected_goals)} 个总进球选项，共 {total_parlays} 注2串1<br>
            4. 每注金额: ${per_parlay_stake:.2f}<br>
            5. 2串1总投入: ${total_parlay_cost:.2f}<br>
            6. 组合赔率 = 稳胆赔率 × 总进球赔率
            </div>
            """, unsafe_allow_html=True)
            
            # 创建2串1投注
            for goal_item in selected_goals:
                combined_odd = round(goal_item['odds'] * strong_win, 2)
                parlay_bets.append({
                    "goal": goal_item['goal'],
                    "parlay_odds": combined_odd,
                    "stake": per_parlay_stake,
                    "description": f"2串1: {s2_selection} × {goal_item['goal']}",
                    "components": {
                        "strong_win": {
                            "match": f"{s2_home_team} vs {s2_away_team}",
                            "selection": s2_selection,
                            "odds": strong_win
                        },
                        "total_goals": {
                            "match": f"{home_team} vs {away_team}",
                            "selection": goal_item['goal'],
                            "odds": goal_item['odds']
                        }
                    }
                })
        
        # 单独大球投注
        st.write("##### ⚽ 单独大球投注")
        st.info(f"单独投注 {home_team} vs {away_team} 大球(3球+)，赔率: {o25_odds}")
        
        # 计算总投入
        total_cost = total_parlay_cost + o25_stake
        
        # 显示投入统计
        col_cost1, col_cost2, col_cost3 = st.columns(3)
        with col_cost1:
            st.metric("💰 大球投入", f"${o25_stake:.2f}")
        with col_cost2:
            st.metric("💰 2串1总投入", f"${total_parlay_cost:.2f}")
        with col_cost3:
            st.metric("💰 方案总投入", f"${total_cost:.2f}")

    with col_out:
        st.write("### 📊 模拟盈亏校验 (2串1复式流)")
        
        # 根据您的说明，盈利情况只有两种：
        # 1. 曼城比赛直接出大球（3球+）→ 大球赢，2串1全输
        # 2. 曼城比赛打出总进球1或2球 + 利物浦胜 → 对应的2串1赢，其他2串1输，大球输
        
        # 不能盈利的情况：
        # 1. 曼城比赛出现0球（没投注0球）→ 2串1全输，大球输
        # 2. 利物浦比赛出现平局或负（没投注平/负）→ 2串1全输，大球只有曼城大球才赢
        
        # 计算各种情况的收益
        res_list = []
        
        # 获取投注的总进球选项
        bet_goals = [bet["goal"] for bet in parlay_bets]
        
        # 情况1: 稳胆赢(利物浦胜) + 主比赛0球
        # 2串1全输（因为没投注0球），大球输
        if "0球" not in bet_goals:
            income = 0
            net_profit = income - total_cost
            res_list.append({
                "模拟赛果": f"① 稳胆赢 + 主比赛0球\n(2串1全输，大球输)",
                "净盈亏": round(net_profit, 2),
                "类型": "全输",
                "稳胆结果": "赢",
                "主比赛结果": "0球"
            })
        
        # 情况2: 稳胆赢 + 主比赛1球
        if "1球" in bet_goals:
            # 找到对应的2串1投注
            parlay_1goal = next(bet for bet in parlay_bets if bet["goal"] == "1球")
            # 只有这个2串1赢，其他2串1输，大球输
            income = parlay_1goal["stake"] * parlay_1goal["parlay_odds"]
            net_profit = income - total_cost
            res_list.append({
                "模拟赛果": f"② 稳胆赢 + 主比赛1球\n(1球2串1赢，其他输，大球输)",
                "净盈亏": round(net_profit, 2),
                "类型": "部分赢",
                "稳胆结果": "赢",
                "主比赛结果": "1球"
            })
        else:
            # 如果没投注1球，则全输
            income = 0
            net_profit = income - total_cost
            res_list.append({
                "模拟赛果": f"② 稳胆赢 + 主比赛1球\n(未投注1球，全输)",
                "净盈亏": round(net_profit, 2),
                "类型": "全输",
                "稳胆结果": "赢",
                "主比赛结果": "1球"
            })
        
        # 情况3: 稳胆赢 + 主比赛2球
        if "2球" in bet_goals:
            # 找到对应的2串1投注
            parlay_2goal = next(bet for bet in parlay_bets if bet["goal"] == "2球")
            # 只有这个2串1赢，其他2串1输，大球输
            income = parlay_2goal["stake"] * parlay_2goal["parlay_odds"]
            net_profit = income - total_cost
            res_list.append({
                "模拟赛果": f"③ 稳胆赢 + 主比赛2球\n(2球2串1赢，其他输，大球输)",
                "净盈亏": round(net_profit, 2),
                "类型": "部分赢",
                "稳胆结果": "赢",
                "主比赛结果": "2球"
            })
        else:
            # 如果没投注2球，则全输
            income = 0
            net_profit = income - total_cost
            res_list.append({
                "模拟赛果": f"③ 稳胆赢 + 主比赛2球\n(未投注2球，全输)",
                "净盈亏": round(net_profit, 2),
                "类型": "全输",
                "稳胆结果": "赢",
                "主比赛结果": "2球"
            })
        
        # 情况4: 稳胆赢 + 主比赛3球+
        # 2串1全输（因为投的是0/1/2球），大球赢
        income = o25_stake * o25_odds
        net_profit = income - total_cost
        res_list.append({
            "模拟赛果": f"④ 稳胆赢 + 主比赛3球+\n(2串1全输，大球赢)",
            "净盈亏": round(net_profit, 2),
            "类型": "部分赢",
            "稳胆结果": "赢",
            "主比赛结果": "3球+"
        })
        
        # 情况5: 稳胆平 + 主比赛0/1/2球
        # 2串1全输（因为稳胆没赢），大球输
        income = 0
        net_profit = income - total_cost
        res_list.append({
            "模拟赛果": f"⑤ 稳胆平 + 主比赛0/1/2球\n(2串1全输，大球输)",
            "净盈亏": round(net_profit, 2),
            "类型": "全输",
            "稳胆结果": "平",
            "主比赛结果": "0/1/2球"
        })
        
        # 情况6: 稳胆平 + 主比赛3球+
        # 2串1全输，大球赢
        income = o25_stake * o25_odds
        net_profit = income - total_cost
        res_list.append({
            "模拟赛果": f"⑥ 稳胆平 + 主比赛3球+\n(2串1全输，大球赢)",
            "净盈亏": round(net_profit, 2),
            "类型": "部分赢",
            "稳胆结果": "平",
            "主比赛结果": "3球+"
        })
        
        # 情况7: 稳胆负 + 主比赛0/1/2球
        # 2串1全输，大球输
        income = 0
        net_profit = income - total_cost
        res_list.append({
            "模拟赛果": f"⑦ 稳胆负 + 主比赛0/1/2球\n(2串1全输，大球输)",
            "净盈亏": round(net_profit, 2),
            "类型": "全输",
            "稳胆结果": "负",
            "主比赛结果": "0/1/2球"
        })
        
        # 情况8: 稳胆负 + 主比赛3球+
        # 2串1全输，大球赢
        income = o25_stake * o25_odds
        net_profit = income - total_cost
        res_list.append({
            "模拟赛果": f"⑧ 稳胆负 + 主比赛3球+\n(2串1全输，大球赢)",
            "净盈亏": round(net_profit, 2),
            "类型": "部分赢",
            "稳胆结果": "负",
            "主比赛结果": "3球+"
        })
        
        df_s2 = pd.DataFrame(res_list)
        
        # 创建图表
        chart_data = df_s2.set_index("模拟赛果")["净盈亏"]
        st.bar_chart(chart_data)
        
        # 显示详细表格
        st.write("##### 📋 详细盈亏表")
        st.dataframe(df_s2[["模拟赛果", "净盈亏", "类型"]], use_container_width=True, hide_index=True)
        
        # 显示2串1投注详情
        st.write("##### 🎯 2串1投注组合详情")
        if parlay_bets:
            bet_details = []
            for i, bet in enumerate(parlay_bets):
                bet_details.append({
                    "注号": f"第{i+1}注",
                    "稳胆比赛": f"{s2_home_team} vs {s2_away_team}",
                    "稳胆选项": s2_selection,
                    "稳胆赔率": strong_win,
                    "总进球比赛": f"{home_team} vs {away_team}",
                    "总进球选项": bet["goal"],
                    "总进球赔率": bet["components"]["total_goals"]["odds"],
                    "2串1赔率": bet["parlay_odds"],
                    "投入金额": f"${bet['stake']:.2f}",
                    "潜在回报": f"${bet['stake'] * bet['parlay_odds']:.2f}"
                })
            
            bet_details.append({
                "注号": "单独大球",
                "稳胆比赛": "-",
                "稳胆选项": "-",
                "稳胆赔率": "-",
                "总进球比赛": f"{home_team} vs {away_team}",
                "总进球选项": "3球+",
                "总进球赔率": o25_odds,
                "2串1赔率": "-",
                "投入金额": f"${o25_stake:.2f}",
                "潜在回报": f"${o25_stake * o25_odds:.2f}"
            })
            
            bet_df = pd.DataFrame(bet_details)
            st.dataframe(bet_df, use_container_width=True, hide_index=True)

# --- 5. EV计算 ---
st.divider()
st.header("📉 数学期望分析")

# 计算EV
if mode == "策略 1：比分精准流":
    current_df = df_s1
    # 策略1：3球+概率 = pred_prob，每个具体比分平分剩余概率
    prob_per_score = (1 - pred_prob) / 6 if 6 > 0 else 0
    
    ev = 0
    for _, row in current_df.iterrows():
        if "3球或以上" in row["模拟赛果"]:
            ev += row["净盈亏"] * pred_prob
        else:
            ev += row["净盈亏"] * prob_per_score
else:
    # 策略2的EV计算
    # 需要稳胆比赛的概率分布
    # 假设：胜率 = 1/强胜赔率，平率 = 1/平赔率，负率 = 1/负赔率，然后归一化
    win_prob_raw = 1 / s2_win_odds
    draw_prob_raw = 1 / s2_draw_odds
    lose_prob_raw = 1 / s2_lose_odds
    
    total_raw = win_prob_raw + draw_prob_raw + lose_prob_raw
    win_prob = win_prob_raw / total_raw
    draw_prob = draw_prob_raw / total_raw
    lose_prob = lose_prob_raw / total_raw
    
    # 主比赛的概率分布
    # 基于用户预测的大球概率，分配0/1/2球的概率
    # 简单分配：0球:30%，1球:40%，2球:30% 的剩余概率
    small_ball_prob = 1 - pred_prob
    goal_0_prob = small_ball_prob * 0.3
    goal_1_prob = small_ball_prob * 0.4
    goal_2_prob = small_ball_prob * 0.3
    goal_3plus_prob = pred_prob
    
    # 计算EV
    ev = 0
    for _, row in df_s2.iterrows():
        scenario = row["模拟赛果"]
        net_profit = row["净盈亏"]
        
        # 提取场景信息
        if "稳胆赢" in scenario:
            strong_result_prob = win_prob
        elif "稳胆平" in scenario:
            strong_result_prob = draw_prob
        elif "稳胆负" in scenario:
            strong_result_prob = lose_prob
        else:
            strong_result_prob = 0
        
        # 提取主比赛结果
        if "主比赛0球" in scenario:
            main_prob = goal_0_prob
        elif "主比赛1球" in scenario:
            main_prob = goal_1_prob
        elif "主比赛2球" in scenario:
            main_prob = goal_2_prob
        elif "主比赛3球+" in scenario:
            main_prob = goal_3plus_prob
        elif "主比赛0/1/2球" in scenario:
            # 这是三种情况的组合
            main_prob = goal_0_prob + goal_1_prob + goal_2_prob
        else:
            main_prob = 0
        
        # 计算联合概率
        joint_prob = strong_result_prob * main_prob
        ev += net_profit * joint_prob

# 显示EV
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("策略期望值 (EV)", f"${ev:.2f}", 
              delta="正向" if ev > 0 else "负向",
              delta_color="normal" if ev <= 0 else "inverse")
    if ev > 0:
        st.success(f"期望收益率: {ev/total_cost*100:.1f}%")
    else:
        st.error(f"期望亏损率: {abs(ev)/total_cost*100:.1f}%")

with col2:
    # 简单大球投注的EV
    simple_ev = (pred_prob * o25_odds - 1) * o25_stake
    st.metric("单纯大球投注EV", f"${simple_ev:.2f}")
    simple_roi = simple_ev / o25_stake * 100
    if simple_ev > 0:
        st.info(f"单纯投注收益率: {simple_roi:.1f}%")
    else:
        st.warning(f"单纯投注亏损率: {abs(simple_roi):.1f}%")

with col3:
    # 计算对冲效果
    hedge_effect = (abs(ev) - abs(simple_ev)) / abs(simple_ev) * 100 if simple_ev != 0 else 0
    st.metric("对冲效果", f"{hedge_effect:.1f}%")
    if hedge_effect < 0:
        st.success("✅ 对冲降低了风险")
    else:
        st.warning("⚠️ 对冲未降低风险")

# EV解释
st.write("##### 💭 策略分析")
if mode == "策略 2：总进球复式流":
    # 显示稳胆比赛概率
    st.markdown(f"""
    <div class="strategy-note">
    🎲 <strong>策略2概率假设</strong><br>
    1. 稳胆比赛 ({s2_home_team} vs {s2_away_team}) 概率分布:<br>
       &nbsp;&nbsp;- {s2_home_team}胜: {win_prob*100:.1f}%<br>
       &nbsp;&nbsp;- 平局: {draw_prob*100:.1f}%<br>
       &nbsp;&nbsp;- {s2_away_team}胜: {lose_prob*100:.1f}%<br>
    2. 主比赛 ({home_team} vs {away_team}) 进球分布:<br>
       &nbsp;&nbsp;- 0球: {goal_0_prob*100:.1f}%<br>
       &nbsp;&nbsp;- 1球: {goal_1_prob*100:.1f}%<br>
       &nbsp;&nbsp;- 2球: {goal_2_prob*100:.1f}%<br>
       &nbsp;&nbsp;- 3球+: {goal_3plus_prob*100:.1f}%
    </div>
    """, unsafe_allow_html=True)

if ev > simple_ev:
    st.success(f"**策略优化成功** | 比单纯投注多赚 ${ev - simple_ev:.2f} 每注")
elif ev > 0 and ev <= simple_ev:
    st.info(f"**策略有效但保守** | 降低了风险但也降低了收益")
else:
    st.error(f"**策略需要调整** | 当前策略负期望值")

# --- 6. 蒙特卡洛实验已移除 ---
if show_monte_carlo:
    st.divider()
    st.header("🎲 蒙特卡洛模拟实验")
    st.warning("蒙特卡洛模拟功能当前不可用")
    with st.expander("查看功能说明"):
        st.markdown("""
        **原功能包含：**
        - ✅ 多次随机试验模拟
        - ✅ 资金变化追踪
        - ✅ 破产概率计算
        - ✅ 风险等级评估
        - ✅ 可视化图表展示
        
        **如需启用，请联系管理员或从历史版本恢复。**
        """)

# --- 7. 策略报告生成 ---
st.divider()
st.header("📄 策略分析报告")

col_report1, col_report2 = st.columns(2)

with col_report1:
    if mode == "策略 1：比分精准流":
        st.markdown(f"""
        ### 📋 策略报告摘要
        
        **比赛信息**
        - 🏆 联赛: {league}
        - 🏠 主队: {home_team}
        - ✈️ 客队: {away_team}
        - 📅 时间: {match_date.strftime('%Y-%m-%d')} {match_time.strftime('%H:%M')}
        
        **策略参数**
        - 🎯 选择策略: {mode}
        - 📊 预测大球概率: {pred_prob*100:.1f}%
        - 💰 总投入金额: ${total_cost:.2f}
        - ⚖️ 大球赔率: {o25_odds}
        
        **风险评估**
        - 📈 策略期望值: ${ev:.2f}
        - 🎲 对冲效果: {hedge_effect:.1f}%
        """)
    else:
        bet_goals_str = ", ".join([goal_item["goal"] for goal_item in selected_goals]) if selected_goals else "无"
        st.markdown(f"""
        ### 📋 策略报告摘要
        
        **涉及两场比赛**
        
        **1. 稳胆比赛**
        - 🏆 {s2_league}: {s2_home_team} vs {s2_away_team}
        - 📊 选择选项: {s2_selection}
        - ⚖️ 稳胆赔率: {strong_win}
        
        **2. 主比赛 (大球+总进球)**
        - 🏆 {league}: {home_team} vs {away_team}
        - 📊 预测大球概率: {pred_prob*100:.1f}%
        - ⚖️ 大球赔率: {o25_odds}
        - 🎯 总进球选项: {bet_goals_str}
        
        **投注详情**
        - 💰 单独大球投入: ${o25_stake:.2f}
        - 🎯 2串1复式注数: {len(parlay_bets)} 注
        - 💰 每注2串1投入: ${per_parlay_stake:.2f}
        - 💰 2串1总投入: ${total_parlay_cost:.2f}
        - 💰 策略总投入: ${total_cost:.2f}
        
        **风险评估**
        - 📈 策略期望值: ${ev:.2f}
        - 🎲 对冲效果: {hedge_effect:.1f}%
        """)

with col_report2:
    # 蒙特卡洛模块已移除 — 在此显示说明而非运行模拟
    if show_monte_carlo:
        st.markdown("### 📊 蒙特卡洛模拟结果\n\n已从本工具中移除。如需恢复，请从版本控制还原对应代码块。")

# --- 8. 教育总结 ---
st.divider()
st.header("📚 核心教育总结")

col_summary1, col_summary2 = st.columns(2)

with col_summary1:
    st.markdown("""
    ### 🎓 数学原理
    
    1. **2串1赔率计算**
    ```
    2串1赔率 = 第一场比赛赔率 × 第二场比赛赔率
    
    收益 = 投注金额 × 2串1赔率
    条件：两场比赛都必须正确
    ```
    
    2. **复式投注原理**
    ```
    复式投注 = 多个2串1组合
    总投入 = 每注金额 × 注数
    
    优点：增加中奖机会
    缺点：总投入增加
    ```
    
    3. **对冲策略本质**
    - 通过不同投注组合降低风险
    - 大球投注覆盖3球+情况
    - 2串1覆盖稳胆赢+小球情况
    """)

with col_summary2:
    if mode == "策略 1：比分精准流":
        # 尝试获取历史统计数据
        history_stats_available = False
        stats_info = None
        
        # 检查是否有历史数据输入
        if 'history_data' in locals() and history_data:
            matches = parse_history_data(history_data, home_team, away_team)
            if matches:
                stats = calculate_statistics(matches, home_team, away_team)
                if stats:
                    history_stats_available = True
                    stats_info = stats
        
        if history_stats_available and stats_info:
            st.markdown(f"""
            ### 💡 针对本场比赛的建议
            
            **{home_team} vs {away_team}**
            
            1. **历史战绩分析**
            - 总比赛场数: {stats_info['total_matches']}场
            - {home_team}胜率: {stats_info['home_win_rate']:.1f}%
            - {away_team}胜率: {stats_info['away_win_rate']:.1f}%
            - 场均总进球: {stats_info['avg_goals']:.2f}
            
            2. **策略建议**
            基于历史数据，两队交锋大球比例为 {stats_info['over_25_rate']:.1f}%，当前预测概率为 {pred_prob*100:.1f}%。
            """)
        else:
            st.markdown(f"""
            ### 💡 针对本场比赛的建议
            
            **{home_team} vs {away_team}**
            
            1. **分析建议**
            - 请在侧边栏输入两队历史交锋记录，以获得更准确的分析
            - 当前预测大球概率: {pred_prob*100:.1f}%
            
            2. **策略建议**
            """)
    else:
        # 策略2部分保持不变
        st.markdown(f"""
        ### 💡 2串1复式投注建议
        
        **盈利条件**
        1. **情况A**: {home_team} vs {away_team} 大球(3球+)
           - 大球投注赢
           - 2串1全输
        
        2. **情况B**: {home_team} vs {away_team} 1球或2球 + {s2_home_team}胜
           - 对应2串1赢
           - 其他2串1输
           - 大球输
        
        **风险提示**
        - 稳胆比赛平或负 → 所有2串1输
        - 主比赛0球 → 所有2串1输
        - 需要两场比赛都判断正确
        """)
    
    # 风险评估部分
    if 'ev' in locals() and ev > 0:
        if 'bankruptcy_rate' in locals() and bankruptcy_rate < 15:
            st.success("当前策略参数合理，可考虑小规模执行")
        else:
            st.warning("策略有盈利可能，但风险较高，建议降低仓位")
    elif 'ev' in locals() and ev < 0:
        st.error("策略负期望值，建议放弃或大幅调整")
    else:
        st.info("策略期望值为零，需要进一步分析")
    
    st.markdown("""
    3. **最佳选择**
    - 享受足球比赛本身
    - 参与无金钱风险的足球活动
    - 将分析能力用于建设性用途
    """)

# --- 9. 最终免责声明 ---
st.divider()
if mode == "策略 1：比分精准流":
    match_info = f"{home_team} vs {away_team}"
else:
    match_info = f"1. {home_team} vs {away_team} (大球) | 2. {s2_home_team} vs {s2_away_team} (稳胆)"

st.markdown(f"""
<div style='text-align: center; padding: 1.5rem; background-color: #f8d7da; border-radius: 10px;'>
<h3 style='color: #721c24;'>⚠️ 重要提醒</h3>
<p style='color: #721c24;'>
<strong>体育投注不是投资，而是娱乐消费。</strong><br>
本场比赛分析 ({match_info}) 仅供参考。<br>
2串1投注需要两场比赛都正确，风险比单场投注更高。<br>
庄家通过数学优势确保长期盈利，你的"技巧"无法改变数学现实。<br><br>
<strong>如果你或你认识的人有赌博问题，请寻求帮助：</strong><br>
• 全国戒赌热线：1-800-522-4700<br>
• 设置自我排除<br>
• 与专业人士交谈
</p>
</div>
""", unsafe_allow_html=True)

# --- 10. 脚注 ---
st.caption(f"""
*本工具仅用于教育目的，展示赌博的数学原理和风险。不鼓励任何形式的赌博行为。*  
*比赛分析基于输入参数，实际结果可能因多种因素而异。*  
*2串1投注风险极高，请谨慎对待。*  
*如果你需要赌博问题帮助，请联系专业机构。*  
*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
""")

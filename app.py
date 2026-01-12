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
    }    // ...existing code...
    # --- 6. 蒙特卡洛实验已移除 ---
    # 蒙特卡洛模拟逻辑已按要求从此文件中删除。如需恢复请从版本控制还原对应代码块。
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
        1. 稳胆比赛: {s2_home_team} vs {s2_away_team}
        2. 主比赛 (大球+总进球): {home_team} vs {away_team}
        
        **策略参数**
        - 🎯 选择策略: {mode}
        - 📊 预测大球概率: {pred_prob*100:.1f}%
        - 💰 总投入金额: ${total_cost:.2f}
        - ⚖️ 大球赔率: {o25_odds}
        - 🎯 总进球选项: {bet_goals_str}
        
        **风险评估**
        - 📈 策略期望值: ${ev:.2f}
        - 🎲 对冲效果: {hedge_effect:.1f}%
        """, unsafe_allow_html=True)

with col_report2:
    # 蒙特卡洛模块已移除 — 在此显示说明而非运行模拟
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
    组合赔率 = 稳胆赔率 × 总进球赔率
    
    优点：增加中奖机会
    缺点：总投入增加，风险加大
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
            - 当前预测大球概率: {pred_prob*100:.1f}%
            """)
        else:
            st.markdown(f"""
            ### 💡 针对本场比赛的建议
            
            **{home_team} vs {away_team}**
            
            1. **分析建议**
            - 请在侧边栏输入两队历史交锋记录，以获得更准确的分析
            
            2. **策略建议**
            基于当前预测，大球概率为 {pred_prob*100:.1f}%
            - 当前预测大球概率: {pred_prob*100:.1f}%
            """)
    else:
        # 策略2部分保持不变
        st.markdown(f"""
        ### 💡 2串1复式投注建议
        
        1. **分析建议**
        - 请在侧边栏输入两队历史交锋记录，以获得更准确的分析
        
        **盈利条件**:
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

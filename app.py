import streamlit as st
import pandas as pd
import numpy as np
import random
from datetime import datetime

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
</style>
""", unsafe_allow_html=True)

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
    match_date = st.date_input("📅 比赛日期", value=datetime.now().date())
with col_match_info3:
    match_time = st.time_input("⏰ 比赛时间", value=datetime.now().time())

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
    st.header("🧠 风险参数")
    
    # 添加基本面分析
    st.subheader("🏟️ 基本面分析")
    home_attack = st.slider(f"{home_team} 进攻力", 1, 10, 8)
    away_defense = st.slider(f"{away_team} 防守力", 1, 10, 7)
    historical_goals = st.slider("历史交锋场均进球", 1.0, 5.0, 2.8, step=0.1)
    
    # 根据分析调整预测概率
    base_prob = 45  # 基础概率45%
    adj_factor = (home_attack + (10 - away_defense)) / 20  # 调整因子
    adj_prob = base_prob + (historical_goals - 2.5) * 10
    
    st.info(f"系统建议概率: {min(max(adj_prob, 10), 90):.1f}%")
    
    pred_prob = st.slider("你预测的大球概率 (%)", 10, 90, int(min(max(adj_prob, 10), 90))) / 100
    
    st.divider()
    mode = st.radio("请选择执行策略：", ["策略 1：比分精准流", "策略 2：总进球复式流"])
    
    st.divider()
    st.header("🎲 蒙特卡洛实验")
    show_monte_carlo = st.checkbox("启用蒙特卡洛模拟", value=True)
    
    if show_monte_carlo:
        sim_trials = st.slider("模拟试验次数", 100, 10000, 1000)
        sim_bets = st.slider("每次试验投注次数", 10, 500, 100)
        initial_capital = st.number_input("初始资金 ($)", value=1000.0)

# --- 4. 逻辑处理核心 ---
st.divider()
col_in, col_out = st.columns([1.6, 2], gap="large")

active_bets = [] 

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
        st.markdown('<div class="strategy-note">🎯 <strong>策略说明</strong>：本策略由两场比赛组成<br>1. 稳胆比赛（独立比赛）<br>2. 主比赛（大球+总进球复式）</div>', unsafe_allow_html=True)
        
        # 第一场比赛：稳胆比赛（独立比赛）
        st.write("### 🏆 稳胆比赛设置（独立比赛）")
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
            elif s2_selection == "平局":
                strong_win = s2_draw_odds
            else:
                strong_win = s2_lose_odds
                
            st.info(f"选择的稳胆赔率: **{strong_win}**")
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
        
        # 第二场比赛：主比赛的总进球复式（与主比赛同一场）
        st.write("### ⚽ 主比赛总进球复式设置")
        st.info(f"**注意**: 总进球复式比赛与主比赛为同一场: {home_team} vs {away_team}")
        
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
        st.write("##### 总进球选项 (0-2球)")
        totals = ["0球", "1球", "2球"]
        total_labels = [f"0球 (无进球)", f"1球 (总进球=1)", f"2球 (总进球=2)"]
        
        img_odds = {"0球": 7.20, "1球": 3.55, "2球": 3.00}
        
        selected = []
        for i, g in enumerate(totals):
            col_check, col_odd = st.columns([3, 1])
            with col_check: 
                is_on = st.checkbox(total_labels[i], key=f"s2_{g}", value=(g != "0球"))
            with col_odd: 
                g_odd = st.number_input(f"赔率", value=img_odds[g], key=f"s2_od_{g}", 
                                      label_visibility="collapsed", min_value=1.01, step=0.1) if is_on else 0.0
            if is_on: 
                selected.append({"name": g, "odd": g_odd})
        
        # 复式投注金额
        st.write("##### 💰 复式投注金额")
        multi_stake = st.number_input("复式对冲总投入 ($)", value=100.0, min_value=0.0, step=10.0, key="s2_multi_stake")
        
        if selected:
            share = multi_stake / len(selected)
            
            # 显示复式投注详情
            st.markdown(f"""
            <div class="strategy-note">
            📊 <strong>复式投注详情</strong><br>
            1. 稳胆比赛: {s2_home_team} vs {s2_away_team} ({s2_selection}, 赔率: {strong_win})<br>
            2. 总进球比赛: {home_team} vs {away_team}<br>
            3. 选择 {len(selected)} 个总进球选项 × ${share:.2f} 每项<br>
            4. 组合赔率 = 稳胆赔率 × 总进球赔率
            </div>
            """, unsafe_allow_html=True)
            
            for item in selected:
                combined_odd = item['odd'] * strong_win
                active_bets.append({
                    "item": item['name'], 
                    "odd": round(combined_odd, 2), 
                    "stake": share,
                    "description": f"{s2_selection} × {item['name']}",
                    "type": "复式串关"
                })
        
        # 添加大球项（主比赛的大球投注）
        active_bets.append({
            "item": "3球+", 
            "odd": o25_odds, 
            "stake": o25_stake,
            "description": f"{home_team} vs {away_team} 大球(3球+)",
            "type": "单独投注"
        })
        
        total_cost = sum(b['stake'] for b in active_bets)
        
        # 显示投入统计
        col_cost1, col_cost2, col_cost3 = st.columns(3)
        with col_cost1:
            st.metric("💰 大球投入", f"${o25_stake:.2f}")
        with col_cost2:
            st.metric("💰 复式投入", f"${total_cost - o25_stake:.2f}")
        with col_cost3:
            st.metric("💰 方案总投入", f"${total_cost:.2f}")

    with col_out:
        st.write("### 📊 模拟盈亏校验 (总进球复式流)")
        
        # 策略2的可能结果（基于两场比赛）
        # 稳胆比赛结果：稳胆赢 vs 稳胆输
        # 主比赛结果：0球、1球、2球、3球+
        
        # 但主比赛的0/1/2球和3球+是互斥的
        # 所以总共有以下情况：
        # 1. 稳胆输 + 主比赛0/1/2球
        # 2. 稳胆输 + 主比赛3球+
        # 3. 稳胆赢 + 主比赛0球（如果投注了0球）
        # 4. 稳胆赢 + 主比赛1球（如果投注了1球）
        # 5. 稳胆赢 + 主比赛2球（如果投注了2球）
        # 6. 稳胆赢 + 主比赛3球+
        
        res_list = []
        
        # 情况1: 稳胆输 + 主比赛0/1/2球 (但未投注该进球数，或投注了但不是稳胆赢)
        # 这种情况只能赢大球，但大球是3球+，所以大球也输，全部输
        income = 0
        net_profit = round(income - total_cost, 2)
        res_list.append({
            "模拟赛果": f"① 稳胆输 + 主比赛0/1/2球\n(未投注该进球数)",
            "净盈亏": net_profit,
            "类型": "全输",
            "稳胆结果": "输",
            "主比赛结果": "0/1/2球"
        })
        
        # 情况2: 稳胆输 + 主比赛3球+
        # 大球赢，但复式输
        income = o25_stake * o25_odds
        net_profit = round(income - total_cost, 2)
        res_list.append({
            "模拟赛果": f"② 稳胆输 + 主比赛3球+\n(大球赢，复式输)",
            "净盈亏": net_profit,
            "类型": "部分赢",
            "稳胆结果": "输",
            "主比赛结果": "3球+"
        })
        
        # 情况3-5: 稳胆赢 + 主比赛特定进球数（如果投注了）
        for i, goal_option in enumerate(["0球", "1球", "2球"]):
            # 检查是否投注了这个进球数
            is_bet_on_goal = any(b["item"] == goal_option for b in active_bets if b["type"] == "复式串关")
            
            if is_bet_on_goal:
                # 找到对应的投注项
                bet_item = next(b for b in active_bets if b["item"] == goal_option and b["type"] == "复式串关")
                
                # 稳胆赢 + 该特定进球数：复式赢，但大球输（因为不是3球+）
                income = bet_item['stake'] * bet_item['odd']
                net_profit = round(income - total_cost, 2)
                
                res_list.append({
                    "模拟赛果": f"③ 稳胆赢 + 主比赛{goal_option}\n(复式赢，大球输)",
                    "净盈亏": net_profit,
                    "类型": "部分赢",
                    "稳胆结果": "赢",
                    "主比赛结果": goal_option
                })
        
        # 情况6: 稳胆赢 + 主比赛3球+
        # 大球赢，但复式输（因为复式投的是0/1/2球）
        income = o25_stake * o25_odds
        net_profit = round(income - total_cost, 2)
        res_list.append({
            "模拟赛果": f"④ 稳胆赢 + 主比赛3球+\n(大球赢，复式输)",
            "净盈亏": net_profit,
            "类型": "部分赢",
            "稳胆结果": "赢",
            "主比赛结果": "3球+"
        })
        
        df_s2 = pd.DataFrame(res_list)
        
        # 创建图表
        chart_data = df_s2.set_index("模拟赛果")["净盈亏"]
        st.bar_chart(chart_data)
        
        # 显示详细表格
        st.write("##### 📋 详细盈亏表")
        st.dataframe(df_s2[["模拟赛果", "净盈亏", "类型"]], use_container_width=True, hide_index=True)
        
        # 显示投注组合详情
        st.write("##### 🎯 投注组合详情")
        if selected:
            bet_details = []
            for i, bet in enumerate(active_bets):
                if bet["type"] == "复式串关":
                    base_odd = round(bet['odd'] / strong_win, 2)
                    bet_details.append({
                        "组合": f"串关 {i+1}",
                        "稳胆比赛": f"{s2_home_team} vs {s2_away_team}",
                        "稳胆选项": s2_selection,
                        "稳胆赔率": strong_win,
                        "总进球比赛": f"{home_team} vs {away_team}",
                        "总进球选项": bet["item"],
                        "总进球赔率": base_odd,
                        "组合赔率": bet['odd'],
                        "投入金额": f"${bet['stake']:.2f}"
                    })
            
            bet_details.append({
                "组合": "单独大球",
                "稳胆比赛": "无",
                "稳胆选项": "-",
                "稳胆赔率": "-",
                "总进球比赛": f"{home_team} vs {away_team}",
                "总进球选项": "3球+",
                "总进球赔率": o25_odds,
                "组合赔率": o25_odds,
                "投入金额": f"${o25_stake:.2f}"
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
    current_df = df_s2
    # 策略2的EV计算
    # 假设稳胆比赛胜率为70%
    strong_win_prob = 0.70
    
    # 主比赛的概率分布（基于用户预测的大球概率）
    # 剩余概率(1-pred_prob)分配给0/1/2球
    # 这里简单分配：0球:20%, 1球:30%, 2球:50% 的剩余概率
    goal_probs = {
        "0球": (1 - pred_prob) * 0.20,
        "1球": (1 - pred_prob) * 0.30,
        "2球": (1 - pred_prob) * 0.50,
        "3球+": pred_prob
    }
    
    ev = 0
    for _, row in current_df.iterrows():
        scenario = row["模拟赛果"]
        
        if "稳胆输 + 主比赛0/1/2球" in scenario:
            # 稳胆输的概率 × 主比赛0/1/2球的概率
            prob = (1 - strong_win_prob) * (1 - pred_prob)
            ev += row["净盈亏"] * prob
            
        elif "稳胆输 + 主比赛3球+" in scenario:
            # 稳胆输的概率 × 主比赛3球+的概率
            prob = (1 - strong_win_prob) * pred_prob
            ev += row["净盈亏"] * prob
            
        elif "稳胆赢 + 主比赛0球" in scenario:
            # 检查是否投注了0球
            is_bet_on_0 = any(b["item"] == "0球" for b in active_bets if b["type"] == "复式串关")
            if is_bet_on_0:
                prob = strong_win_prob * goal_probs["0球"]
                ev += row["净盈亏"] * prob
                
        elif "稳胆赢 + 主比赛1球" in scenario:
            # 检查是否投注了1球
            is_bet_on_1 = any(b["item"] == "1球" for b in active_bets if b["type"] == "复式串关")
            if is_bet_on_1:
                prob = strong_win_prob * goal_probs["1球"]
                ev += row["净盈亏"] * prob
                
        elif "稳胆赢 + 主比赛2球" in scenario:
            # 检查是否投注了2球
            is_bet_on_2 = any(b["item"] == "2球" for b in active_bets if b["type"] == "复式串关")
            if is_bet_on_2:
                prob = strong_win_prob * goal_probs["2球"]
                ev += row["净盈亏"] * prob
                
        elif "稳胆赢 + 主比赛3球+" in scenario:
            prob = strong_win_prob * goal_probs["3球+"]
            ev += row["净盈亏"] * prob

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
    # 计算主比赛概率分布
    goal_probs_display = {
        "0球": round((1 - pred_prob) * 0.20 * 100, 1),
        "1球": round((1 - pred_prob) * 0.30 * 100, 1),
        "2球": round((1 - pred_prob) * 0.50 * 100, 1),
        "3球+": round(pred_prob * 100, 1)
    }
    
    st.markdown(f"""
    <div class="strategy-note">
    🎲 <strong>策略2概率假设</strong><br>
    1. 稳胆比赛 ({s2_home_team} vs {s2_away_team}) 胜率: 70%<br>
    2. 主比赛 ({home_team} vs {away_team}) 进球分布:<br>
       &nbsp;&nbsp;- 0球: {goal_probs_display['0球']}%<br>
       &nbsp;&nbsp;- 1球: {goal_probs_display['1球']}%<br>
       &nbsp;&nbsp;- 2球: {goal_probs_display['2球']}%<br>
       &nbsp;&nbsp;- 3球+: {goal_probs_display['3球+']}%
    </div>
    """, unsafe_allow_html=True)

if ev > simple_ev:
    st.success(f"**策略优化成功** | 比单纯投注多赚 ${ev - simple_ev:.2f} 每注")
elif ev > 0 and ev <= simple_ev:
    st.info(f"**策略有效但保守** | 降低了风险但也降低了收益")
else:
    st.error(f"**策略需要调整** | 当前策略负期望值")

# --- 6. 蒙特卡洛实验 ---
if show_monte_carlo and 'sim_trials' in locals():
    st.divider()
    st.header("🎲 蒙特卡洛模拟实验")
    
    if mode == "策略 1：比分精准流":
        st.write(f"模拟设置：{sim_trials}次试验 × {sim_bets}次投注 | 比赛: {home_team} vs {away_team}")
    else:
        st.write(f"模拟设置：{sim_trials}次试验 × {sim_bets}次投注")
        st.write(f"涉及比赛: 1. {home_team} vs {away_team} (大球+总进球) | 2. {s2_home_team} vs {s2_away_team} (稳胆)")
    
    # 存储结果
    all_final_balances = []
    all_profitable_trials = []
    all_max_drawdowns = []
    
    # 进度条
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for trial in range(sim_trials):
        # 更新进度
        if trial % 100 == 0:
            progress_bar.progress(min((trial + 1) / sim_trials, 1.0))
            status_text.text(f"正在模拟: {trial+1}/{sim_trials} 次试验...")
        
        # 初始资金
        capital = initial_capital
        peak_capital = initial_capital
        max_drawdown = 0
        
        # 执行多次投注
        for bet in range(sim_bets):
            if mode == "策略 1：比分精准流":
                # 策略1模拟
                is_over25 = random.random() < pred_prob
                
                if is_over25:
                    # 大球赢
                    capital += o25_stake * (o25_odds - 1)
                else:
                    # 大球输
                    capital -= o25_stake
            else:
                # 策略2模拟 - 涉及两场比赛
                # 1. 稳胆比赛结果 (70%胜率)
                strong_win_result = random.random() < 0.70
                
                # 2. 主比赛结果
                # 基于预测的大球概率
                main_over25 = random.random() < pred_prob
                
                if not main_over25:
                    # 主比赛0/1/2球
                    # 随机分配0/1/2球的概率
                    goal_random = random.random()
                    if goal_random < 0.20:  # 0球
                        main_goals = "0球"
                    elif goal_random < 0.50:  # 1球 (0.20+0.30)
                        main_goals = "1球"
                    else:  # 2球
                        main_goals = "2球"
                else:
                    main_goals = "3球+"
                
                # 计算收益
                if main_over25:
                    # 主大球赢
                    capital += o25_stake * (o25_odds - 1)
                else:
                    # 主大球输
                    capital -= o25_stake
                
                # 复式投注结果
                if strong_win_result and main_goals in ["0球", "1球", "2球"]:
                    # 检查是否投注了这个进球数
                    bet_found = False
                    for bet_item in active_bets:
                        if bet_item["type"] == "复式串关" and bet_item["item"] == main_goals:
                            capital += bet_item['stake'] * (bet_item['odd'] - 1)
                            bet_found = True
                            break
                    
                    if not bet_found:
                        # 投注了这个进球数，但没中
                        for bet_item in active_bets:
                            if bet_item["type"] == "复式串关":
                                capital -= bet_item['stake']
                else:
                    # 稳胆输或主比赛3球+，复式输
                    for bet_item in active_bets:
                        if bet_item["type"] == "复式串关":
                            capital -= bet_item['stake']
            
            # 更新峰值和最大回撤
            if capital > peak_capital:
                peak_capital = capital
            drawdown = (peak_capital - capital) / peak_capital * 100
            if drawdown > max_drawdown:
                max_drawdown = drawdown
            
            # 如果资金为负，则破产
            if capital <= 0:
                capital = 0
                break
        
        all_final_balances.append(capital)
        all_profitable_trials.append(capital > initial_capital)
        all_max_drawdowns.append(max_drawdown)
    
    # 完成进度
    progress_bar.progress(1.0)
    status_text.text("✅ 模拟完成！")
    
    # 计算统计
    avg_final = np.mean(all_final_balances)
    median_final = np.median(all_final_balances)
    bankruptcy_count = sum(1 for b in all_final_balances if b <= 0)
    bankruptcy_rate = bankruptcy_count / sim_trials * 100
    profitable_count = sum(all_profitable_trials)
    profitable_rate = profitable_count / sim_trials * 100
    avg_max_drawdown = np.mean(all_max_drawdowns)
    
    # 显示结果
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("平均最终资金", f"${avg_final:,.0f}", 
                  delta=f"{avg_final-initial_capital:+,.0f}")
    
    with col2:
        st.metric("破产概率", f"{bankruptcy_rate:.1f}%")
    
    with col3:
        st.metric("盈利试验比例", f"{profitable_rate:.1f}%")
    
    with col4:
        st.metric("平均最大回撤", f"{avg_max_drawdown:.1f}%")
    
    # 资金分布直方图
    st.write("##### 📊 最终资金分布")
    
    # 创建分布数据
    bins = 15
    hist_data = np.histogram(all_final_balances, bins=bins)
    
    # 创建DataFrame
    bin_edges = hist_data[1]
    bin_counts = hist_data[0]
    
    bin_labels = []
    for i in range(len(bin_edges)-1):
        if bin_edges[i+1] <= 0:
            bin_labels.append(f"破产")
        else:
            bin_labels.append(f"${int(bin_edges[i]):,}-${int(bin_edges[i+1]):,}")
    
    dist_df = pd.DataFrame({
        "资金范围": bin_labels,
        "试验数量": bin_counts,
        "比例": bin_counts / sim_trials * 100
    })
    
    # 显示图表
    st.bar_chart(dist_df.set_index("资金范围")["试验数量"])
    
    # 显示详细分布表
    with st.expander("📋 查看详细分布数据"):
        st.dataframe(dist_df, use_container_width=True)
    
    # 风险分析
    st.write("##### ⚠️ 风险分析")
    
    risk_level = "低"
    risk_color = "green"
    if bankruptcy_rate > 30:
        risk_level = "极高"
        risk_color = "red"
        st.error(f"❌ **{risk_level}破产风险** ({bankruptcy_rate:.1f}%) - 强烈不建议执行")
    elif bankruptcy_rate > 20:
        risk_level = "高"
        risk_color = "orange"
        st.warning(f"⚠️ **{risk_level}破产风险** ({bankruptcy_rate:.1f}%) - 需要谨慎操作")
    elif bankruptcy_rate > 10:
        risk_level = "中等"
        risk_color = "blue"
        st.info(f"ℹ️ **{risk_level}破产风险** ({bankruptcy_rate:.1f}%) - 建议优化策略")
    else:
        st.success(f"✅ **{risk_level}破产风险** ({bankruptcy_rate:.1f}%) - 风险可控")
    
    # 实验结论
    st.write("##### 💡 实验结论")
    
    if ev > 0 and profitable_rate > 60 and bankruptcy_rate < 10:
        st.success(f"""
        **🎯 策略表现优秀**:
        1. 正向期望值 (EV = ${ev:.2f})
        2. {profitable_rate:.1f}% 的试验盈利
        3. 仅 {bankruptcy_rate:.1f}% 的破产风险
        
        💰 **结论**: 理论上，长期执行此策略可能盈利。
        """)
    elif ev <= 0:
        st.error(f"""
        **🚫 策略存在根本问题**:
        1. 负向期望值 (EV = ${ev:.2f})
        2. 长期执行必然亏损
        3. 建议重新设计策略或调整参数
        """)
    else:
        st.warning(f"""
        **⚠️ 策略表现不稳定**:
        1. 虽然有正向期望值 (EV = ${ev:.2f})
        2. 但盈利比例 ({profitable_rate:.1f}%) 或破产风险 ({bankruptcy_rate:.1f}%) 不理想
        3. 需要进一步优化或降低仓位
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
        - 🎯 总进球选项: {', '.join([item['name'] for item in selected]) if selected else '无'}
        
        **策略参数**
        - 🎯 选择策略: {mode}
        - 💰 总投入金额: ${total_cost:.2f}
        
        **风险评估**
        - 📈 策略期望值: ${ev:.2f}
        - 🎲 对冲效果: {hedge_effect:.1f}%
        """)

with col_report2:
    if show_monte_carlo and 'sim_trials' in locals():
        st.markdown(f"""
        ### 📊 蒙特卡洛模拟结果
        
        **模拟设置**
        - 🔄 试验次数: {sim_trials:,}
        - 🎰 每次试验投注次数: {sim_bets}
        - 💵 初始资金: ${initial_capital:,.0f}
        
        **模拟结果**
        - ✅ 平均最终资金: ${avg_final:,.0f}
        - 📉 破产概率: {bankruptcy_rate:.1f}%
        - 📈 盈利试验比例: {profitable_rate:.1f}%
        - 🔻 平均最大回撤: {avg_max_drawdown:.1f}%
        
        **风险等级**: <span style='color:{risk_color}; font-weight:bold;'>{risk_level}风险</span>
        """, unsafe_allow_html=True)

# --- 8. 教育总结 ---
st.divider()
st.header("📚 核心教育总结")

col_summary1, col_summary2 = st.columns(2)

with col_summary1:
    st.markdown("""
    ### 🎓 数学原理
    
    1. **期望值 (EV) 公式**
    ```
    EV = Σ(概率ᵢ × 收益ᵢ) - 总投入
    
    盈利条件：EV > 0
    亏损条件：EV < 0
    ```
    
    2. **串关赔率计算**
    ```
    串关赔率 = 选项1赔率 × 选项2赔率 × ...
    
    风险：所有选项都必须正确
    回报：赔率相乘可能很高
    ```
    
    3. **大数定律**
    - 短期可能赢钱（运气）
    - 长期必然输给庄家优势
    - 你无法战胜数学
    """)

with col_summary2:
    if mode == "策略 1：比分精准流":
        st.markdown(f"""
        ### 💡 针对本场比赛的建议
        
        **{home_team} vs {away_team}**
        
        1. **基本面分析**
        - {home_team} 进攻力: {home_attack}/10
        - {away_team} 防守力: {away_defense}/10
        - 历史交锋场均进球: {historical_goals}
        
        2. **策略建议**
        """)
    else:
        st.markdown(f"""
        ### 💡 针对两场比赛的建议
        
        **涉及两场比赛**
        
        1. **稳胆比赛要求**
        - 选择胜率高的比赛作为稳胆
        - 赔率不宜过低，确保组合赔率有吸引力
        
        2. **主比赛分析**
        - 大球概率: {pred_prob*100:.1f}%
        - 总进球分布需仔细分析
        - 对冲策略降低了单一投注的风险
        
        3. **串关风险**
        - 两场比赛都必须正确才能赢钱
        - 风险比单场投注更高
        """)
    
    if ev > 0 and bankruptcy_rate < 15:
        st.success("当前策略参数合理，可考虑小规模执行")
    elif ev > 0:
        st.warning("策略有盈利可能，但风险较高，建议降低仓位")
    else:
        st.error("策略负期望值，建议放弃或大幅调整")
    
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
    match_info = f"1. {home_team} vs {away_team} (大球+总进球) | 2. {s2_home_team} vs {s2_away_team} (稳胆)"

st.markdown(f"""
<div style='text-align: center; padding: 1.5rem; background-color: #f8d7da; border-radius: 10px;'>
<h3 style='color: #721c24;'>⚠️ 重要提醒</h3>
<p style='color: #721c24;'>
<strong>体育投注不是投资，而是娱乐消费。</strong><br>
本场比赛分析 ({match_info}) 仅供参考。<br>
串关投注风险更高，所有选项必须全部正确才能赢钱。<br>
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
*串关投注风险极高，请谨慎对待。*  
*如果你需要赌博问题帮助，请联系专业机构。*  
*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
""")

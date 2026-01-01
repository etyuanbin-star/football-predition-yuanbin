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
    o25_odds = st.number_input("大球 (3球+) 赔率", value=2.30, step=0.01)
    o25_stake = st.number_input("大球投入金额 ($)", value=100.0, step=1.0)
    
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
        st.markdown('<div class="strategy-note">🎯 <strong>策略说明</strong>：本策略需要两场比赛 - 稳胆比赛 + 总进球复式比赛，组成2串1复式投注。</div>', unsafe_allow_html=True)
        
        # 分隔符
        st.markdown("---")
        
        # 第一场比赛：稳胆比赛
        st.write("### 🏆 稳胆比赛")
        col_s2a1, col_s2a2, col_s2a3 = st.columns([2, 1, 2])
        with col_s2a1:
            s2_home_team = st.text_input("🏠 稳胆主队", value="利物浦", placeholder="输入稳胆主队", key="s2_home")
        with col_s2a2:
            st.markdown("<h4 style='text-align: center; margin-top: 10px;'>VS</h4>", unsafe_allow_html=True)
        with col_s2a3:
            s2_away_team = st.text_input("✈️ 稳胆客队", value="诺丁汉森林", placeholder="输入稳胆客队", key="s2_away")
        
        col_s2a4, col_s2a5 = st.columns(2)
        with col_s2a4:
            s2_league = st.selectbox("📋 稳胆联赛", ["英超", "欧冠", "西甲", "德甲", "意甲", "法甲", "其他"], key="s2_league")
        with col_s2a5:
            strong_win = st.number_input("📊 稳胆赔率", value=1.35, min_value=1.01, step=0.01, help="稳胆比赛的胜/平/负赔率")
        
        # 显示稳胆比赛信息卡
        st.markdown(f"""
        <div class="match-info-secondary">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="font-size: 16px; font-weight: bold;">
                    {s2_home_team} <span style="color: #666; font-weight: normal;">vs</span> {s2_away_team}
                </div>
                <div style="font-size: 12px; color: #666;">
                    {s2_league} · 稳胆赔率: {strong_win}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 分隔符
        st.markdown("---")
        
        # 第二场比赛：总进球复式比赛
        st.write("### 🎯 总进球复式比赛")
        col_s2b1, col_s2b2, col_s2b3 = st.columns([2, 1, 2])
        with col_s2b1:
            s2b_home_team = st.text_input("🏠 复式主队", value="切尔西", placeholder="输入复式主队", key="s2b_home")
        with col_s2b2:
            st.markdown("<h4 style='text-align: center; margin-top: 10px;'>VS</h4>", unsafe_allow_html=True)
        with col_s2b3:
            s2b_away_team = st.text_input("✈️ 复式客队", value="布莱顿", placeholder="输入复式客队", key="s2b_away")
        
        s2b_league = st.selectbox("📋 复式联赛", ["英超", "欧冠", "西甲", "德甲", "意甲", "法甲", "其他"], key="s2b_league")
        
        # 显示复式比赛信息卡
        st.markdown(f"""
        <div class="match-info-secondary">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="font-size: 16px; font-weight: bold;">
                    {s2b_home_team} <span style="color: #666; font-weight: normal;">vs</span> {s2b_away_team}
                </div>
                <div style="font-size: 12px; color: #666;">
                    {s2b_league}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 总进球选项
        st.write("##### ⚽ 总进球选项")
        totals = ["0球", "1球", "2球"]
        total_labels = [f"0球 ({s2b_home_team} vs {s2b_away_team} 无进球)", 
                       f"1球 ({s2b_home_team} vs {s2b_away_team} 总进球=1)", 
                       f"2球 ({s2b_home_team} vs {s2b_away_team} 总进球=2)"]
        
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
        multi_stake = st.number_input("复式对冲总投入 ($)", value=100.0, min_value=0.0, step=10.0)
        
        if selected:
            share = multi_stake / len(selected)
            
            # 显示复式投注详情
            st.markdown(f"""
            <div class="strategy-note">
            📊 <strong>复式投注详情</strong><br>
            1. 稳胆比赛: {s2_home_team} vs {s2_away_team} (赔率: {strong_win})<br>
            2. 总进球比赛: {s2b_home_team} vs {s2b_away_team}<br>
            3. 选择 {len(selected)} 个选项 × ${share:.2f} 每项<br>
            4. 组合赔率 = 稳胆赔率 × 总进球赔率
            </div>
            """, unsafe_allow_html=True)
            
            for item in selected:
                combined_odd = item['odd'] * strong_win
                active_bets.append({
                    "item": item['name'], 
                    "odd": round(combined_odd, 2), 
                    "stake": share,
                    "description": f"{s2_home_team}胜 × {s2b_home_team} vs {s2b_away_team} {item['name']}"
                })
        
        # 添加大球项（原始比赛）
        active_bets.append({
            "item": "3球+", 
            "odd": o25_odds, 
            "stake": o25_stake,
            "description": f"{home_team} vs {away_team} 大球(3球+)"
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
        
        # 策略2的可能结果
        s2_outcomes = ["稳胆输", "稳胆赢+0球", "稳胆赢+1球", "稳胆赢+2球", "大球(3球+)"]
        outcome_labels = [
            f"{s2_home_team} vs {s2_away_team} 稳胆未中",
            f"{s2_home_team}胜 × {s2b_home_team} vs {s2b_away_team} 0球",
            f"{s2_home_team}胜 × {s2b_home_team} vs {s2b_away_team} 1球",
            f"{s2_home_team}胜 × {s2b_home_team} vs {s2b_away_team} 2球",
            f"{home_team} vs {away_team} 大球(3球+)"
        ]
        
        res_list = []
        
        for i, out in enumerate(s2_outcomes):
            income = 0
            if out == "稳胆输":
                # 稳胆输，只有大球可能赢
                for bet in active_bets:
                    if bet["item"] == "3球+":
                        income += bet['stake'] * bet['odd']
            elif out == "大球(3球+)":
                # 大球赢，加上所有稳胆赢的复式投注
                for bet in active_bets:
                    if bet["item"] == "3球+":
                        income += bet['stake'] * bet['odd']
                    # 稳胆赢了，但总进球复式不匹配大球情况
            else:
                # 稳胆赢 + 特定总进球
                total_goals = out.split("+")[1]  # 如"0球"
                for bet in active_bets:
                    if bet["item"] == total_goals:
                        income += bet['stake'] * bet['odd']
            
            net_profit = round(income - total_cost, 2)
            
            # 判断结果类型
            result_type = "大球胜" if out == "大球(3球+)" else "复式胜" if "稳胆赢" in out else "全输"
            
            res_list.append({
                "模拟赛果": outcome_labels[i],
                "净盈亏": net_profit,
                "类型": result_type
            })
        
        df_s2 = pd.DataFrame(res_list)
        
        # 创建图表
        chart_data = df_s2.set_index("模拟赛果")["净盈亏"]
        st.bar_chart(chart_data)
        
        # 显示详细表格
        st.write("##### 📋 详细盈亏表")
        st.dataframe(df_s2, use_container_width=True, hide_index=True)
        
        # 显示投注组合详情
        st.write("##### 🎯 投注组合详情")
        if selected:
            bet_details = []
            for i, bet in enumerate(active_bets):
                if bet["item"] != "3球+":
                    bet_details.append({
                        "组合": f"组合 {i+1}",
                        "稳胆比赛": f"{s2_home_team} vs {s2_away_team}",
                        "稳胆赔率": strong_win,
                        "总进球比赛": f"{s2b_home_team} vs {s2b_away_team}",
                        "总进球选项": bet["item"],
                        "总进球赔率": round(bet['odd'] / strong_win, 2),
                        "组合赔率": bet['odd'],
                        "投入金额": f"${bet['stake']:.2f}"
                    })
            
            bet_details.append({
                "组合": "单独大球",
                "稳胆比赛": "无",
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
    # 假设稳胆比赛胜率为70%，总进球分布概率
    strong_win_prob = 0.70  # 稳胆胜率
    goal_probs = {"0球": 0.15, "1球": 0.25, "2球": 0.30}  # 总进球分布
    
    ev = 0
    for _, row in current_df.iterrows():
        if "大球" in row["模拟赛果"]:
            # 大球的概率
            ev += row["净盈亏"] * pred_prob
        elif "全输" in row["类型"]:
            # 稳胆输的概率
            ev += row["净盈亏"] * (1 - strong_win_prob)
        elif "复式胜" in row["类型"]:
            # 稳胆赢且特定总进球
            # 从结果中提取总进球数
            result_text = row["模拟赛果"]
            if "0球" in result_text:
                goal_prob = goal_probs["0球"]
            elif "1球" in result_text:
                goal_prob = goal_probs["1球"]
            elif "2球" in result_text:
                goal_prob = goal_probs["2球"]
            else:
                goal_prob = 0
            
            # 稳胆赢且特定总进球的概率
            combined_prob = strong_win_prob * goal_prob
            ev += row["净盈亏"] * combined_prob

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
    st.markdown(f"""
    <div class="strategy-note">
    🎲 <strong>策略2概率假设</strong><br>
    1. 稳胆比赛 ({s2_home_team} vs {s2_away_team}) 胜率: 70%<br>
    2. 总进球比赛 ({s2b_home_team} vs {s2b_away_team}) 进球分布: 0球(15%), 1球(25%), 2球(30%)<br>
    3. 主大球比赛 ({home_team} vs {away_team}) 大球概率: {pred_prob*100:.1f}%
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
        st.write(f"涉及比赛: 1. {home_team} vs {away_team} (大球) | 2. {s2_home_team} vs {s2_away_team} (稳胆) | 3. {s2b_home_team} vs {s2b_away_team} (总进球)")
    
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
                # 策略2模拟 - 涉及三场比赛
                # 1. 主大球比赛结果
                main_over25 = random.random() < pred_prob
                
                # 2. 稳胆比赛结果 (70%胜率)
                strong_win_result = random.random() < 0.70
                
                # 3. 总进球比赛结果
                goal_outcome = random.choices(["0球", "1球", "2球", "3球+"], weights=[0.15, 0.25, 0.30, 0.30])[0]
                
                # 计算收益
                if main_over25:
                    # 主大球赢
                    capital += o25_stake * (o25_odds - 1)
                else:
                    # 主大球输
                    capital -= o25_stake
                
                # 复式投注结果
                if strong_win_result and goal_outcome in ["0球", "1球", "2球"]:
                    # 找到对应的投注项
                    for bet_item in active_bets:
                        if bet_item["item"] == goal_outcome:
                            capital += bet_item['stake'] * (bet_item['odd'] - 1)
                            break
                else:
                    # 复式投注输
                    for bet_item in active_bets:
                        if bet_item["item"] in ["0球", "1球", "2球"]:
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
        
        **涉及三场比赛**
        
        **1. 主大球比赛**
        - 🏆 {league}: {home_team} vs {away_team}
        - 📊 预测大球概率: {pred_prob*100:.1f}%
        - ⚖️ 大球赔率: {o25_odds}
        
        **2. 稳胆比赛**
        - 🏆 {s2_league}: {s2_home_team} vs {s2_away_team}
        - 📊 稳胆赔率: {strong_win}
        
        **3. 总进球复式比赛**
        - 🏆 {s2b_league}: {s2b_home_team} vs {s2b_away_team}
        
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
        ### 💡 针对多场比赛的建议
        
        **涉及三场比赛**
        
        1. **稳胆比赛要求**
        - 选择胜率高的比赛作为稳胆
        - 赔率不宜过低，确保组合赔率有吸引力
        
        2. **总进球比赛选择**
        - 选择进球分布可预测的比赛
        - 避免进球数波动大的比赛
        
        3. **大球比赛独立分析**
        - 单独分析主比赛的大球概率
        - 不要因为串关而影响大球判断
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
    match_info = f"1. {home_team} vs {away_team} | 2. {s2_home_team} vs {s2_away_team} | 3. {s2b_home_team} vs {s2b_away_team}"

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

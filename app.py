import streamlit as st
import pandas as pd

# --- 页面配置 ---
st.set_page_config(page_title="胜算实验室：终极对冲版", layout="wide")

st.title("🔺 胜算实验室：盈亏平衡实验室")
st.subheader("—— 目标：确保 3球+ (大球) 赢球时能够覆盖所有对冲成本")

# --- 1. 核心大球项配置 (侧边栏) ---
with st.sidebar:
    st.header("⚖️ 核心大球项 (O2.5)")
    o25_odds = st.number_input("大球 (3球+) 赔率", value=2.30, min_value=1.01, step=0.01)
    o25_stake = st.number_input("大球投入金额", value=100.0, min_value=0.0, step=1.0)
    
    st.divider()
    # 模式切换
    mode = st.radio("选择策略模式：", ["策略 1：精确比分流", "策略 2：总进球自由流"])

# --- 2. 策略输入区 ---
st.divider()
col_input, col_result = st.columns([1.5, 2], gap="large")

active_bets = []
# 默认添加主攻大球项
active_bets.append({"项目": "大球 (3球+)", "赔率": o25_odds, "金额": o25_stake, "分类": "主攻"})

with col_input:
    if mode == "策略 1：精确比分流":
        st.write("### 🕹️ 设定比分对冲")
        # 您截图中的 0-0, 0-1, 0-2 勾选逻辑
        scores = ["0-0", "1-0", "0-1", "1-1", "2-0", "0-2"]
        default_odds = {"0-0": 10.0, "1-0": 8.5, "0-1": 8.0, "1-1": 7.0, "2-0": 13.0, "0-2": 12.0}
        
        for s in scores:
            c1, c2, c3 = st.columns([1, 1.2, 1.2])
            with c1: is_on = st.checkbox(s, key=f"check_{s}")
            with c2: s_stake = st.number_input(f"金额", value=33.0, key=f"amt_{s}", label_visibility="collapsed") if is_on else 0.0
            with c3: s_odds = st.number_input(f"赔率", value=default_odds[s], key=f"odd_{s}", label_visibility="collapsed") if is_on else 0.0
            if is_on: active_bets.append({"项目": s, "赔率": s_odds, "金额": s_stake, "分类": "对冲"})

    else:
        st.write("### 🕹️ 设定总进球对冲")
        st.caption("请根据您的截图手动输入赔率 (如 7.20, 3.55, 3.00)")
        
        # 对应您最新截图中的 0, 1, 2 总进球
        totals = ["0球", "1球", "2球"]
        # 参考截图填入默认值
        img_odds = {"0球": 7.20, "1球": 3.55, "2球": 3.00}
        
        for g in totals:
            c1, c2, c3 = st.columns([1, 1.2, 1.2])
            with c1: is_on = st.checkbox(g, key=f"total_{g}", value=True)
            with c2: g_stake = st.number_input(f"下注金额", value=30.0, key=f"tamt_{g}", label_visibility="collapsed") if is_on else 0.0
            with c3: g_odds = st.number_input(f"实时赔率", value=img_odds[g], key=f"todd_{g}", label_visibility="collapsed") if is_on else 0.0
            if is_on: active_bets.append({"项目": g, "赔率": g_odds, "金额": g_stake, "分类": "对冲"})

    # 计算总本金
    total_cost = sum(b['金额'] for b in active_bets)
    st.metric("💰 方案总成本 (Total Stake)", f"${total_cost:.2f}")

# --- 3. 盈亏抵消校验区 ---
with col_result:
    st.write("### 📊 盈亏平衡校验 (自动计算抵消结果)")
    
    # 物理结果点
    points = ["0球", "1球", "2球", "3球+"]
    data = []
    
    for p in points:
        income = 0
        for b in active_bets:
            # 大球项赢钱
            if b['项目'] == "大球 (3球+)" and p == "3球+":
                income += b['金额'] * b['赔率']
            # 对冲项赢钱（策略1比分映射或策略2总进球映射）
            elif b['项目'] == p or \
                 (p == "0球" and b['项目'] == "0-0") or \
                 (p == "1球" and b['项目'] in ["1-0", "0-1"]) or \
                 (p == "2球" and b['项目'] in ["1-1", "2-0", "0-2"]):
                income += b['金额'] * b['赔率']
        
        data.append({"模拟结果": p, "回款金额": round(income, 2), "净盈亏": round(income - total_cost, 2)})

    df = pd.DataFrame(data)
    st.bar_chart(df.set_index("模拟结果")["净盈亏"])
    
    # 核心检查：大球是否覆盖成本
    over_pnl = df[df["模拟结果"] == "3球+"]["净盈亏"].values[0]
    
    st.table(df)
    
    if over_pnl > 0:
        st.success(f"✅ **对冲通过**：大球赢球时，扣除所有对冲成本后仍盈利 **${over_pnl:.2f}**")
    elif over_pnl == 0:
        st.warning(f"⚠️ **保本状态**：大球赢球仅能覆盖成本。")
    else:
        st.error(f"❌ **对冲失败**：大球赢球不仅没赚，还亏损 **${abs(over_pnl):.2f}**！请减少对冲金额。")

st.divider()
st.caption("提示：您可以直接在表格中查看每个赛果下的净收入。如果 0/1/2 球项的净盈亏是正数，说明您的对冲不仅保本还在赚钱。")

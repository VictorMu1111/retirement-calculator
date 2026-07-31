import streamlit as st
import pandas as pd
import numpy as np

# 設定頁面
st.set_page_config(page_title="退休金雙向規劃工具", page_icon="⚖️", layout="wide")

st.title("⚖️ 退休金雙向規劃工具")

# --- 側邊欄：共用參數 ---
with st.sidebar:
    st.header("⚙️ 基礎參數")
    inflation_rate = st.slider("預計每年平均通膨率 (%)", 0.0, 10.0, 2.0, 0.1) / 100
    retirement_years = st.number_input("預計退休生活年數", value=40, min_value=1)
    spending_ratio = 0.7
    st.info(f"註：本計畫將在退休期間用掉總資產價值的 {spending_ratio*100:.0f}%，保留 30% 作為預備金。")

# --- 主介面：分頁 ---
tab1, tab2 = st.tabs(["💰 正向試算 (我有多少錢)", "🎯 反向試算 (我想領多少)"])

# --- Tab 1: 正向試算 ---
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        initial_cap_a = st.number_input("目前退休資產 (萬元)", value=3000, step=100, key="cap_a")
        return_rate_a = st.slider("預計每年投資獲利率 (%)", 0.0, 15.0, 7.0, 0.5, key="ret_a") / 100
    
    # 計算邏輯
    real_ret_a = (1 + return_rate_a) / (1 + inflation_rate) - 1
    annuity_factor_a = ((1 - (1 + real_ret_a) ** -retirement_years) / real_ret_a) if real_ret_a != 0 else retirement_years
    
    monthly_drawdown_a = (initial_cap_a * spending_ratio / annuity_factor_a) / 12
    
    st.metric("💡 您每個月可以花 (現值)", f"{monthly_drawdown_a:.2f} 萬元")
    st.write(f"這代表在考慮 {inflation_rate*100:.1f}% 通膨後，您第一個月領 {monthly_drawdown_a:.2f} 萬，之後每年隨通膨調升，直到第 {retirement_years} 年結束。")

# --- Tab 2: 反向試算 ---
with tab2:
    st.subheader("設定您的理想退休生活")
    target_monthly_spending = st.number_input("理想每月花費 (現在購買力/萬元)", value=10.0, step=0.5)
    target_annual_spending = target_monthly_spending * 12
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("### 選項 A: 需準備多少本金？")
        fixed_return_rate = st.slider("假設固定年報酬率 (%)", 0.0, 15.0, 7.0, 0.5) / 100
        
        # 計算所需本金
        real_ret_b = (1 + fixed_return_rate) / (1 + inflation_rate) - 1
        annuity_factor_b = ((1 - (1 + real_ret_b) ** -retirement_years) / real_ret_b) if real_ret_b != 0 else retirement_years
        
        required_capital = (target_annual_spending * annuity_factor_b) / spending_ratio
        
        st.success(f"如果您希望月領 {target_monthly_spending} 萬")
        st.metric("您需要準備的初始本金", f"{required_capital:.0f} 萬元")

    with col4:
        st.markdown("### 選項 B: 需達到多少報酬率？")
        fixed_capital = st.number_input("假設手頭現有本金 (萬元)", value=3000, step=100)
        
        # 使用二分法尋找實質報酬率
        def solve_for_real_rate(target_pv, pmt, n):
            low = -0.2
            high = 1.0  # 提高搜尋上限
            for _ in range(100):
                mid = (low + high) / 2
                if mid == 0:
                    current_pv = pmt * n
                else:
                    current_pv = pmt * (1 - (1 + mid)**-n) / mid
                if current_pv > target_pv:
                    low = mid
                else:
                    high = mid
            return mid

        target_pv_for_spending = fixed_capital * spending_ratio
        required_real_rate = solve_for_real_rate(target_pv_for_spending, target_annual_spending, retirement_years)
        required_nominal_rate = (1 + required_real_rate) * (1 + inflation_rate) - 1
        
        st.warning(f"如果您只有 {fixed_capital} 萬元")
        if required_nominal_rate > 0.2:
            st.error(f"所需的年報酬率過高: {required_nominal_rate*100:.2f}% (這在現實中很難達成)")
        else:
            st.metric("您需要的年投資報酬率", f"{required_nominal_rate*100:.2f} %")

st.markdown("---")
st.caption("本計算機僅供模擬規劃參考，實際投資報酬可能隨市場波動。")
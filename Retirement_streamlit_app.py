import streamlit as st
import pandas as pd
import numpy as np

# 設定頁面
st.set_page_config(page_title="退休金雙向規劃工具 v2", page_icon="⚖️", layout="wide")

st.title("⚖️ 退休金規劃工具 (含資產配置與臨時支出)")

# --- 側邊欄：參數設定 ---
with st.sidebar:
    st.header("⚙️ 基礎參數")
    inflation_rate = st.slider("預計每年平均通膨率 (%)", 0.0, 10.0, 2.0, 0.1) / 100
    retirement_years = st.number_input("預計退休生活年數", value=40, min_value=1)
    
    st.markdown("---")
    st.header("⚡ 臨時大額支出")
    one_time_expense = st.number_input("額外支出金額 (萬元)", value=0, step=50)
    expense_year = st.slider("發生在退休第幾年？", 1, int(retirement_years), 10)

    st.markdown("---")
    st.info("""
    **資產配置邏輯：**
    - **70% 投資**：每年產生設定的報酬率。
    - **30% 現金**：保留在手上彈性操作（不計利息）。
    - **提領順序**：提領與支出會從總資產中按比例扣除。
    """)

# --- 計算核心函數 ---
def run_simulation(initial_cap, annual_ret, infl_rate, years, exp_amt, exp_year, monthly_drawdown_target=None):
    """
    執行退休模擬。若 monthly_drawdown_target 有值，則使用該值；
    若無，則根據「70% 總額消耗」原則反推第一年領取額。
    """
    # 這裡使用「有效報酬率」來估算正向領取額
    # 有效報酬率 = (70% * 投資報酬率) + (30% * 0%)
    effective_ret = annual_ret * 0.7
    real_ret = (1 + effective_ret) / (1 + infl_rate) - 1
    
    if monthly_drawdown_target is None:
        spending_ratio = 0.7
        annuity_factor = ((1 - (1 + real_ret) ** -years) / real_ret) if real_ret != 0 else years
        annual_drawdown = (initial_cap * spending_ratio / annuity_factor)
    else:
        annual_drawdown = monthly_drawdown_target * 12

    data = []
    curr_total = initial_cap
    curr_draw = annual_drawdown
    
    for y in range(1, years + 1):
        start_bal = curr_total
        
        # 1. 扣除每年生活費
        curr_total -= curr_draw
        
        # 2. 處理臨時支出
        actual_exp = 0
        if y == exp_year:
            actual_exp = exp_amt
            curr_total -= actual_exp
        
        # 3. 計算投資收益 (只有 70% 的錢在投資)
        invested_part = curr_total * 0.7
        cash_part = curr_total * 0.3
        gain = invested_part * annual_ret
        curr_total += gain
        
        data.append({
            "年份": y,
            "年初總資產": start_bal,
            "生活費提領": curr_draw,
            "臨時支出": actual_exp,
            "年底總資產": curr_total,
            "年底投資部位": curr_total * 0.7,
            "年底現金部位": curr_total * 0.3
        })
        
        # 生活費隨通膨調整
        curr_draw *= (1 + infl_rate)
        if curr_total <= 0: # 破產檢查
            break
            
    return pd.DataFrame(data), annual_drawdown / 12

# --- 主介面 ---
tab1, tab2 = st.tabs(["💰 正向試算 (我有多少錢)", "🎯 反向試算 (我想領多少)"])

# --- Tab 1: 正向試算 ---
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        initial_cap_a = st.number_input("目前退休資產 (萬元)", value=3000, step=100, key="cap_a")
        return_rate_a = st.slider("預計每年投資報酬率 (%)", 0.0, 15.0, 7.0, 0.5, key="ret_a") / 100
    
    df_a, monthly_v_a = run_simulation(initial_cap_a, return_rate_a, inflation_rate, retirement_years, one_time_expense, expense_year)
    
    st.metric("💡 您第一個月可以花 (現值)", f"{monthly_v_a:.2f} 萬元")
    if df_a["年底總資產"].iloc[-1] < 0:
        st.error("⚠️ 注意：目前的提領方案會導致資產在中途耗盡！")

# --- Tab 2: 反向試算 ---
with tab2:
    target_monthly = st.number_input("理想每月花費 (現在購買力/萬元)", value=10.0, step=0.5)
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("### 需準備多少本金？")
        fixed_ret = st.slider("假設投資報酬率 (%)", 0.0, 15.0, 7.0, 0.5, key="f_ret") / 100
        # 簡單估算：考慮有效利率後的現值
        eff_r = fixed_ret * 0.7
        real_r = (1 + eff_r) / (1 + inflation_rate) - 1
        ann_f = ((1 - (1 + real_r) ** -retirement_years) / real_r) if real_r != 0 else retirement_years
        req_cap = (target_monthly * 12 * ann_f) / 0.7
        # 加上臨時支出的現值補償
        req_cap += (one_time_expense / (1 + eff_r)**expense_year)
        
        st.metric("建議初始本金", f"{req_cap:.0f} 萬元")

    with col4:
        st.markdown("### 需達到多少報酬率？")
        fixed_cap = st.number_input("假設現有本金 (萬元)", value=3000, step=100, key="f_cap")
        # 二分法尋找
        low, high = 0.0, 0.3
        for _ in range(50):
            mid = (low + high) / 2
            df_test, _ = run_simulation(fixed_cap, mid, inflation_rate, retirement_years, one_time_expense, expense_year, monthly_drawdown_target=target_monthly)
            if len(df_test) < retirement_years or df_test["年底總資產"].iloc[-1] < (fixed_cap * 0.3):
                low = mid
            else:
                high = mid
        st.metric("建議投資報酬率", f"{low*100:.2f} %")

# --- 共用圖表與明細 (放在最下面) ---
st.markdown("---")
st.subheader("📊 退休金資產變化明細")

# 選擇要顯示哪一個分頁的結果
display_df = df_a if st.session_state.get('tab_select') != tab2 else df_test # 簡化處理，預設顯示 Tab 1

st.line_chart(display_df.set_index("年份")[["年底總資產", "生活費提領"]])

st.dataframe(
    display_df.style.format({
        "年初總資產": "{:.1f}",
        "生活費提領": "{:.2f}",
        "臨時支出": "{:.0f}",
        "年底總資產": "{:.1f}",
        "年底投資部位": "{:.1f}",
        "年底現金部位": "{:.1f}"
    }),
    use_container_width=True
)

st.caption("註：明細表基於「正向試算」分頁之參數產生。資產配置比例：70% 投資、30% 現金。")
import streamlit as st
import pandas as pd
import numpy as np

# 設定頁面
st.set_page_config(page_title="退休金規劃工具 v3", page_icon="⚖️", layout="wide")

# ============================================
# 頁面頂部：退休計劃基本原則說明
# ============================================
st.title("⚖️ 退休金規劃工具 v3")

with st.expander("📋 點擊查看：本退休計劃的基本原則", expanded=True):
    st.markdown("""
    ### 💡 核心哲學
        
    這是一個 **「財務自由退休規劃」** 工具，設計邏輯如下：

    ---
        
    #### 🛡️ 1. 資產配置：70/30 原則
    - **70% 投資**：追求長期複利成長（股票、債券、ETF 等）。
    - **30% 現金**：保留流動性，應付市場震盪與生活突發狀況。
    - **目的**：平衡「成長性」與「安全感」，確保退休期間不會因為短期市場波動而被迫賣出資產。

    ---

    #### 💰 2. 提領策略：夢幻帳戶法 (Total Spending Account)
    - 每年從總資產中提領生活費。
    - 將 70% 的資產作為「目標消耗池」，退休結束時僅需留存 30% 作為預備金。
    - **購買力不變**：每年提領金額會**隨通膨自動調升**，確保生活品質不縮水。

    ---

    #### ⚡ 3. 彈性支出：突發狀況預留
    - 退休生活難免有意外（醫療、旅遊、子女援助、節日大禮）。
    - 本工具允許您**設定多筆臨時支出**，觀察它們如何影響資產壽命。
    - **提醒**：在退休前幾年發生大額支出，對複利累積的殺傷力遠大於後期支出。

    ---

    #### ⚖️ 4. 雙向規劃思維
    - **正向**：我有 X 元，能過什麼生活？
    - **反向**：我想過 Y 生活，需要準備多少錢/達到什麼報酬率？
    - **目的**：讓夢想與現實可以對話，越早發現差距，越有時間調整。
    """)

st.markdown("---")

# ============================================
# 側邊欄：參數設定
# ============================================
with st.sidebar:
    st.header("⚙️ 基礎參數")
    inflation_rate = st.slider("預計每年平均通膨率 (%)", 0.0, 10.0, 2.0, 0.1) / 100
    retirement_years = st.number_input("預計退休生活年數", value=40, min_value=1)
    
    st.markdown("---")
    st.header("📝 多筆臨時支出設定")
    st.caption("您可以設定多筆不同年份的臨時支出，模擬各種人生規劃。")
    
    # 使用 Session State 來管理支出列表
    if 'expenses' not in st.session_state:
        st.session_state.expenses = []
    
    # 新增支出的 UI
    with st.container():
        new_year = st.number_input("支出年份 (第幾年)", min_value=1, max_value=int(retirement_years), value=10, key="new_year")
        new_amount = st.number_input("支出金額 (萬元)", min_value=0, value=100, step=10, key="new_amt")
        if st.button("➕ 加入此筆支出"):
            st.session_state.expenses.append({
                "year": int(new_year),
                "amount": float(new_amount)
            })
            st.success(f"✅ 已加入：第 {int(new_year)} 年支出 {float(new_amount)} 萬元")
    
    # 顯示當前支出列表
    if len(st.session_state.expenses) > 0:
        st.markdown("### 📋 目前設定的臨時支出：")
        for i, exp in enumerate(st.session_state.expenses):
            col_del1, col_del2 = st.columns([3, 1])
            with col_del1:
                st.write(f"第 {exp['year']} 年: {exp['amount']} 萬元")
            with col_del2:
                if st.button(f"🗑️ 刪除", key=f"del_{i}"):
                    st.session_state.expenses.pop(i)
                    st.rerun()
    
    st.markdown("---")
    st.info("""
    **資產配置邏輯：**
    - **70% 投資**：每年產生設定的報酬率。
    - **30% 現金**：保留在手上彈性操作（不計利息）。
    - **提領順序**：提領與支出會從總資產中按比例分配。
    """)

# ============================================
# 核心計算函數 (支持多筆支出)
# ============================================
def run_simulation(initial_cap, annual_ret, infl_rate, years, expenses_list, monthly_drawdown_target=None):
    """
    執行退休模擬
    - expenses_list: 列表，每個元素為 {"year": int, "amount": float}
    """
    # 有效報酬率 (70% 投資)
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
        
        # 2. 處理該年份的所有臨時支出
        total_expense = 0
        for exp in expenses_list:
            if exp["year"] == y:
                total_expense += exp["amount"]
        curr_total -= total_expense
        
        # 3. 計算投資收益 (只有 70% 的錢在投資)
        invested_part = curr_total * 0.7
        gain = invested_part * annual_ret
        curr_total += gain
        
        data.append({
            "年份": y,
            "年初總資產": start_bal,
            "生活費提領": curr_draw,
            "臨時支出": total_expense,
            "年底總資產": curr_total,
            "年底投資部位": curr_total * 0.7,
            "年底現金部位": curr_total * 0.3
        })
        
        # 生活費隨通膨調整
        curr_draw *= (1 + infl_rate)
        if curr_total <= 0:  # 破產檢查
            break
            
    return pd.DataFrame(data), annual_drawdown / 12

# ============================================
# 主介面：分頁
# ============================================
tab1, tab2 = st.tabs(["💰 正向試算 (我有多少錢)", "🎯 反向試算 (我想領多少)"])

# --- Tab 1: 正向試算 ---
with tab1:
    st.subheader("💡 我現在有錢，看看能領多少？")
    col1, col2 = st.columns(2)
    with col1:
        initial_cap_a = st.number_input("目前退休資產 (萬元)", value=3000, step=100, key="cap_a")
        return_rate_a = st.slider("預計每年投資報酬率 (%)", 0.0, 15.0, 7.0, 0.5, key="ret_a") / 100
    
    df_a, monthly_v_a = run_simulation(
        initial_cap_a, return_rate_a, inflation_rate, retirement_years, 
        st.session_state.expenses
    )
    
    st.metric("💡 您第一個月可以花 (現值)", f"{monthly_v_a:.2f} 萬元")
    
    if len(df_a) < retirement_years or df_a["年底總資產"].iloc[-1] < 0:
        st.error("⚠️ 注意：目前的提領方案會導致資產在中途耗盡！請調降生活費或增加本金。")
    else:
        final_ratio = df_a["年底總資產"].iloc[-1] / initial_cap_a * 100
        st.success(f"✅ 退休 {retirement_years} 年後，資產還剩約 {df_a['年底總資產'].iloc[-1]:.0f} 萬元 (約原始本金的 {final_ratio:.1f}%)")

# --- Tab 2: 反向試算 ---
with tab2:
    st.subheader("🎯 我夢想的生活，需要準備多少？")
    target_monthly = st.number_input("理想每月花費 (現在購買力/萬元)", value=10.0, step=0.5)
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("### 需準備多少本金？")
        fixed_ret = st.slider("假設投資報酬率 (%)", 0.0, 15.0, 7.0, 0.5, key="f_ret") / 100
        eff_r = fixed_ret * 0.7
        real_r = (1 + eff_r) / (1 + inflation_rate) - 1
        ann_f = ((1 - (1 + real_r) ** -retirement_years) / real_r) if real_r != 0 else retirement_years
        req_cap = (target_monthly * 12 * ann_f) / 0.7
        
        # 加上所有臨時支出的現值補償
        for exp in st.session_state.expenses:
            pv_exp = exp["amount"] / (1 + eff_r) ** exp["year"]
            req_cap += pv_exp
        
        st.metric("建議初始本金", f"{req_cap:.0f} 萬元")
        st.caption("已包含所有設定的臨時支出")

    with col4:
        st.markdown("### 需達到多少報酬率？")
        fixed_cap = st.number_input("假設現有本金 (萬元)", value=3000, step=100, key="f_cap")
        # 二分法尋找最佳報酬率
        low, high = 0.0, 0.5
        found = False
        for _ in range(60):
            mid = (low + high) / 2
            df_test, _ = run_simulation(
                fixed_cap, mid, inflation_rate, retirement_years, 
                st.session_state.expenses, monthly_drawdown_target=target_monthly
            )
            if len(df_test) < retirement_years or df_test["年底總資產"].iloc[-1] < (fixed_cap * 0.3):
                low = mid
            else:
                high = mid
                found = True
        
        if found:
            st.metric("建議投資報酬率", f"{low*100:.2f} %")
        else:
            st.error("💔 在合理報酬率範圍內 (0-50%)，無法達成您的目標。請考慮調降理想生活費或增加本金。")

# ============================================
# 圖表與明細 (最下方)
# ============================================
st.markdown("---")
st.subheader("📊 退休金資產變化明細")

# 顯示正向試算的結果
display_df = df_a

st.line_chart(display_df.set_index("年份")[["年底總資產", "年底投資部位", "年底現金部位", "生活費提領"]])

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
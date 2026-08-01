import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 設定頁面
st.set_page_config(page_title="退休金規劃工具 v4", page_icon="⚖️", layout="wide")

# ============================================
# 頁面頂部：退休計劃基本原則說明
# ============================================
st.title("⚖️ 退休金規劃工具 v4")

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

    #### 💰 2. 提領策略：夢幻帳戶法
    - 每年從總資產中提領生活費。
    - 將 70% 的資產作為「目標消耗池」，退休結束時僅需留存 30% 作為預備金。
    - **購買力不變**：每年提領金額會**隨通膨自動調升**，確保生活品質不縮水。

    ---

    #### 🏦 3. 勞保/勞退年金收入
    - 退休後通常會有 **勞保老年年金** 和 **勞工退休金** 的固定月收入。
    - 這些「現金流入」可以大幅減輕資產消耗的壓力。
    - **本工具已將此納入計算**，讓結果更貼近真實情況！

    ---

    #### ⚡ 4. 彈性支出：突發狀況預留
    - 退休生活難免有意外（醫療、旅遊、子女援助、節日大禮）。
    - 本工具允許您**設定多筆臨時支出**，觀察它們如何影響資產壽命。

    ---

    #### ⚖️ 5. 雙向規劃思維
    - **正向**：我有 X 元，能過什麼生活？
    - **反向**：我想過 Y 生活，需要準備多少錢/達到什麼報酬率？
    """)

st.markdown("---")

# ============================================
# 側邊欄：參數設定
# ============================================
with st.sidebar:
    st.header("⚙️ 基礎參數")
    inflation_rate = st.slider("預計每年平均通膨率 (%)", 0.0, 10.0, 2.0, 0.1) / 100
    retirement_years = st.number_input("預計退休生活年數", value=40, min_value=1)
    
    # ----- 新增：勞保/勞退年金 -----
    st.markdown("---")
    st.header("🏦 勞保/勞退年金")
    st.caption("退休後每月固定的社會保險收入")
    labor_pension_monthly = st.number_input("勞保老年年金 (每月/萬元)", value=2.0, step=0.1)
    retirement_fund_monthly = st.number_input("勞工退休金 (每月/萬元)", value=1.5, step=0.1)
    annual_social_income = (labor_pension_monthly + retirement_fund_monthly) * 12
    st.info(f"合計每年固定收入：{annual_social_income} 萬元")
    
    # ----- 投資組合配置 -----
    st.markdown("---")
    st.header("📈 投資組合配置")
    st.caption("調整股票/債券比例，預估不同風險等級下的報酬")
    
    # 預設歷史報酬率（可自行調整）
    stock_return_default = 9.5  # 股票歷史年化報酬率
    bond_return_default = 4.5   # 債券歷史年化報酬率
    
    stock_pct = st.slider("股票比例 (%)", 0, 100, 70, 5)
    bond_pct = 100 - stock_pct
    
    # 加權後的預期報酬率
    portfolio_return = (stock_pct / 100) * stock_return_default + (bond_pct / 100) * bond_return_default
    st.caption(f"預期組合報酬率：**{portfolio_return:.2f}%**")
    
    # 允許手動調整報酬率
    use_manual_return = st.checkbox("手動調整報酬率", value=False)
    if use_manual_return:
        portfolio_return = st.number_input("自訂報酬率 (%)", 0.0, 20.0, portfolio_return, 0.1)
    
    # ----- 多筆臨時支出 -----
    st.markdown("---")
    st.header("📝 多筆臨時支出設定")
    st.caption("您可以設定多筆不同年份的臨時支出，模擬各種人生規劃。")
    
    if 'expenses' not in st.session_state:
        st.session_state.expenses = []
    
    with st.container():
        new_year = st.number_input("支出年份 (第幾年)", min_value=1, max_value=int(retirement_years), value=10, key="new_year")
        new_amount = st.number_input("支出金額 (萬元)", min_value=0, value=100, step=10, key="new_amt")
        if st.button("➕ 加入此筆支出"):
            st.session_state.expenses.append({
                "year": int(new_year),
                "amount": float(new_amount)
            })
            st.success(f"✅ 已加入：第 {int(new_year)} 年支出 {float(new_amount)} 萬元")
    
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
    - **勞保+勞退**：每年穩定的現金流入減少提領壓力。
    - **提領順序**：先花社會保險收入，不足再從總資產提領。
    """)

# ============================================
# 核心計算函數 (支援勞退年金+多筆支出)
# ============================================
def run_simulation(initial_cap, annual_ret, infl_rate, years, expenses_list, social_income, monthly_drawdown_target=None):
    """
    執行退休模擬
    - expenses_list: 列表，每個元素為 {"year": int, "amount": float}
    - social_income: 每年勞保+勞退的年金收入 (萬元)
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
        
        # 1. 先收到社會保險收入
        curr_total += social_income
        
        # 2. 扣除每年生活費
        curr_total -= curr_draw
        
        # 3. 處理該年份的所有臨時支出
        total_expense = 0
        for exp in expenses_list:
            if exp["year"] == y:
                total_expense += exp["amount"]
        curr_total -= total_expense
        
        # 4. 計算投資收益 (只有 70% 的錢在投資)
        invested_part = curr_total * 0.7
        gain = invested_part * annual_ret
        curr_total += gain
        
        data.append({
            "年份": y,
            "年初總資產": start_bal,
            "社會保險收入": social_income,
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
        return_rate_a = st.slider("預計每年投資報酬率 (%)", 0.0, 15.0, portfolio_return, 0.5, key="ret_a") / 100
    
    df_a, monthly_v_a = run_simulation(
        initial_cap_a, return_rate_a, inflation_rate, retirement_years, 
        st.session_state.expenses, annual_social_income
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
        fixed_ret = st.slider("假設投資報酬率 (%)", 0.0, 15.0, portfolio_return, 0.5, key="f_ret") / 100
        eff_r = fixed_ret * 0.7
        real_r = (1 + eff_r) / (1 + inflation_rate) - 1
        ann_f = ((1 - (1 + real_r) ** -retirement_years) / real_r) if real_r != 0 else retirement_years
        
        # 扣除社會保險提供的現值
        social_pv = annual_social_income * ann_f
        req_cap = (target_monthly * 12 * ann_f - social_pv) / 0.7
        
        # 加上所有臨時支出的現值
        for exp in st.session_state.expenses:
            pv_exp = exp["amount"] / (1 + eff_r) ** exp["year"]
            req_cap += pv_exp
        
        st.metric("建議初始本金", f"{req_cap:.0f} 萬元")
        st.caption("已包含勞保勞退收入及所有臨時支出")

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
                st.session_state.expenses, annual_social_income, 
                monthly_drawdown_target=target_monthly
            )
            if len(df_test) < retirement_years or df_test["年底總資產"].iloc[-1] < (fixed_cap * 0.3):
                low = mid
            else:
                high = mid
                found = True
        
        if found:
            st.metric("建議投資報酬率", f"{low*100:.2f} %")
        else:
            st.error("💔 在合理報酬率範圍內 (0-50%)，無法達成您的目標。")

# ============================================
# Plotly 互動圖表 (最下方)
# ============================================
st.markdown("---")
st.subheader("📊 退休金資產變化互動圖表")

display_df = df_a

# 創建互動式圖表
fig = make_subplots(
    rows=2, cols=1,
    subplot_titles=("資產變化趨勢 (總資產/投資部位/現金部位)", "年度現金流 (提領/收入/支出)"),
    vertical_spacing=0.15
)

# 圖一：資產變化
fig.add_trace(
    go.Scatter(x=display_df["年份"], y=display_df["年底總資產"], 
               mode='lines+markers', name="總資產",
               line=dict(color='#2E86AB', width=3)),
    row=1, col=1
)
fig.add_trace(
    go.Scatter(x=display_df["年份"], y=display_df["年底投資部位"], 
               mode='lines', name="投資部位",
               line=dict(color='#FF6B6B', width=2, dash='dash')),
    row=1, col=1
)
fig.add_trace(
    go.Scatter(x=display_df["年份"], y=display_df["年底現金部位"], 
               mode='lines', name="現金部位",
               line=dict(color='#43AA8B', width=2, dash='dot')),
    row=1, col=1
)

# 圖二：年度現金流
fig.add_trace(
    go.Bar(x=display_df["年份"], y=display_df["生活費提領"], name="生活費提領",
           marker_color='#F9C74F'),
    row=2, col=1
)
fig.add_trace(
    go.Bar(x=display_df["年份"], y=display_df["社會保險收入"], name="社會保險收入",
           marker_color='#90BE6D'),
    row=2, col=1
)
fig.add_trace(
    go.Bar(x=display_df["年份"], y=display_df["臨時支出"], name="臨時支出",
           marker_color='#F94144'),
    row=2, col=1
)

fig.update_layout(
    height=700,
    showlegend=True,
    hovermode='x unified',
    title_text="退休規劃模擬結果",
    template='plotly_white'
)

fig.update_xaxes(title_text="年份")
fig.update_yaxes(title_text="金額 (萬元)")

st.plotly_chart(fig, use_container_width=True)

# ============================================
# 詳細明細表
# ============================================
st.markdown("---")
st.subheader("📋 年度詳細明細表")

st.dataframe(
    display_df.style.format({
        "年初總資產": "{:.1f}",
        "社會保險收入": "{:.2f}",
        "生活費提領": "{:.2f}",
        "臨時支出": "{:.0f}",
        "年底總資產": "{:.1f}",
        "年底投資部位": "{:.1f}",
        "年底現金部位": "{:.1f}"
    }),
    use_container_width=True,
    height=400
)

st.caption("註：明細表基於「正向試算」分頁之參數產生。資產配置比例：70% 投資、30% 現金。")
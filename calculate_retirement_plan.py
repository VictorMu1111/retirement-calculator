def calculate_retirement_plan():
    print("=== 退休金計劃計算器 ===")
    
    # 輸入參數
    try:
        initial_capital = float(input("1. 目前手上的退休資產 (萬元): "))
        annual_return_rate = float(input("2. 預計每年投資獲利率 (%): ")) / 100
        inflation_rate = float(input("3. 預計每年平均通膨率 (%): ")) / 100
        retirement_years = int(input("4. 預計退休生活年數 (年): "))
        spending_ratio = 0.7  # 使用掉 70% 的總額
    except ValueError:
        print("輸入錯誤，請輸入數字。")
        return

    # 實質報酬率計算 (考慮通膨後的購買力)
    # 公式: (1 + 報酬率) / (1 + 通膨率) - 1
    real_return_rate = (1 + annual_return_rate) / (1 + inflation_rate) - 1
    
    # 我們要計算每年的領取金額 (PMT)
    # 假設我們在 retirement_years 結束後，資產還剩下原本「複利成長後」總額的 30%
    # 為了簡化邏輯，我們計算如果要領完 70% 的資產，每年定額(經通膨調整後)可領取多少
    
    # 計算年金現值係數
    if real_return_rate != 0:
        annuity_factor = (1 - (1 + real_return_rate) ** -retirement_years) / real_return_rate
    else:
        annuity_factor = retirement_years

    # 總共要花掉的「現值」目標是初始資金的 70%
    # (註：這代表我們在退休第一年開始領取的金額，之後每年隨通膨調升)
    target_spendable_present_value = initial_capital * spending_ratio
    annual_drawdown_today_value = target_spendable_present_value / annuity_factor
    
    monthly_drawdown_today_value = annual_drawdown_today_value / 12

    # 計算退休結束後預計剩下的名目金額 (Nominal value)
    total_balance = initial_capital
    for _ in range(retirement_years):
        total_balance = (total_balance - annual_drawdown_today_value) * (1 + annual_return_rate)
        # 這裡簡化處理：每年領取金額隨通膨增長
        annual_drawdown_today_value *= (1 + inflation_rate)

    print("\n--- 計算結果 ---")
    print(f"退休期間：{retirement_years} 年")
    print(f"在不透支購買力的情況下，您第一個月可動用：")
    print(f"👉 【 {monthly_drawdown_today_value:.2f} 萬元 】 (約合台幣 {monthly_drawdown_today_value*10000:.0f} 元)")
    print(f"*(此金額已考慮通膨，代表在退休第 20 年時，您的購買力仍等同於現在的這筆錢)*")
    
    print(f"\n退休結束後（第 {retirement_years} 年末）：")
    print(f"預計剩餘名目資產：約 {total_balance:.2f} 萬元 (約為原始資金的 {total_balance/initial_capital*100:.1f}%)")
    print("----------------")
    print("備註：本程式假設投資收益每年結算，且每年年初領取生活費。")

if __name__ == "__main__":
    calculate_retirement_plan()
# 💰 退休金雙向規劃工具 (Retirement Calculator)

這是一個基於 Python 與 Streamlit 開發的互動式退休金規劃工具。它可以幫助使用者根據目前的資產、預期投資報酬率與通膨率，科學地規劃退休生活。

### 🌐 線上試用
如果你已經部署成功，可以在這裡放上你的連結：
[點擊前往網頁版](你的Streamlit連結)

---

## ✨ 核心功能

1. **正向試算 (Forward Calculation)**：
   - 輸入：目前資產、預期報酬率、通膨率、退休年數。
   - 輸出：在保留 30% 資產作為預備金的前提下，**現在購買力**下每月可領取的金額。

2. **反向目標規劃 (Reverse Planning)**：
   - **選項 A (需準備多少本金)**：設定理想月領金額，計算出退休時需要存到多少錢。
   - **選項 B (需達成多少報酬率)**：設定現有本金與理想月領金額，反推投資組合需要達到的年化報酬率。

3. **視覺化分析**：
   - 提供資產隨時間變化的趨勢圖表。
   - 提供年度詳細明細表（包含年初資產、當年領取額、年底餘額）。

---

## 🛠 使用技術
- **Python 3.x**
- **Streamlit**: 網頁介面開發
- **Pandas & NumPy**: 財務數值計算與數據處理

---

## 🚀 如何在本地端執行

1. **複製專案**：
   ```bash
   git clone https://github.com/你的帳號名/retirement-calculator.git
   cd retirement-calculator
   ```

2. **安裝必要套件**：
   ```bash
   pip install -r requirements.txt
   ```

3. **啟動程式**：
   ```bash
   streamlit run retirement_streamlit_app.py
   ```

---

## 📝 備註
- 本工具採用的邏輯為：每年提領金額隨通膨自動調整，以確保退休期間生活品質不縮水。
- 計算結果僅供參考，實際投資請務必考慮市場波動風險。
```

### 如何上傳這個 README 到 GitHub？

1. 在資料夾中儲存 `README.md`。
2. 在 Terminal 執行以下指令：

```bash
git add README.md
git commit -m "Add README file"
git push origin main
\# 個人綜所稅試算與節稅建議系統



本專案是一個以 \*\*Python + Streamlit\*\* 建立的互動式系統，  

透過 \*\*法規規則引擎 + 視覺化分析 + 報表產生\*\*，  

協助使用者快速完成台灣綜合所得稅的試算，並提供個人化節稅建議。



---



\## 功能特色



\- \*\*基本資料輸入\*\*  

&nbsp; - 申報方式（單身 / 夫妻合併）  

&nbsp; - 扶養親屬、長照需求、幼兒學前、身障人數等  

&nbsp; - 各類收入、保險費、房貸利息、房租支出  

&nbsp; - 自動帶入稅務法規限制（免稅額、扣除額上限）



\- \*\*即時計算\*\*  

&nbsp; - 自動計算綜合所得總額、免稅額、各項扣除額  

&nbsp; - 淨所得、應納稅額、退稅 / 補稅數字即時更新



\- \*\*節稅建議引擎\*\*  

&nbsp; - 根據輸入資料，動態給予節稅建議  

&nbsp; - 範例：捐贈上限提醒、房租與房貸二擇一、退稅調整建議  

&nbsp; - 所有規則皆符合台灣現行所得稅法規



\- \*\*情境模擬\*\*  

&nbsp; - 提供拉桿模擬（捐贈、保險費、房貸、房租）  

&nbsp; - 即時比較「現況 vs 模擬」的差異  

&nbsp; - 視覺化圖表 + 數據表格並列顯示



\- \*\*PDF 報告產生\*\*  

&nbsp; - 自動輸出完整的「綜所稅試算與節稅建議報告」  

&nbsp; - 包含基本數據表格 + 個人化節稅建議  

&nbsp; - 採用 NotoSansTC 字型，確保中文字正確顯示



---



\## 技術架構



\- \*\*前端介面\*\*： \[Streamlit](https://streamlit.io/)  

\- \*\*資料處理\*\*： Pandas  

\- \*\*視覺化\*\*： Matplotlib  

\- \*\*報表產生\*\*： ReportLab  

\- \*\*規則管理\*\*： JSON 法規檔（如 `rules/2025.json`，可更新以支援不同年度）



---



\## 專案結構



tax-mvp/

│

├── app.py # 主程式（Streamlit 入口）

├── engine/

│ ├── calculator.py # 核心計算邏輯

│ └── pdf\_report.py # PDF 報告生成

│

├── rules/

│ └── 2025.json # 稅務規則（年度可更新）

│

├── samples/

│ ├── case\_single.json # 範例：單身案例

│ └── case\_family.json # 範例：家庭案例

│

└── assets/

│   ├── NotoSansTC-Regular.ttf

│   └── screenshots/ 

│   └── screenshots/       

│       ├── advice.png

│       ├── chart.png      

│       ├── data1.png

│       ├── data2.png

│       ├── data3.png

│       ├── report.png

│       └── simulation.png

└── NotoSansTC-Regular.ttf # 中文字型



---



\## ⚙️ 安裝與執行



1.安裝依賴套件

```bash

pip install -r requirements.txt

2.啟動系統

streamlit run app.py

3.開啟瀏覽器

&nbsp;   系統將自動開啟http://localhost:8501，即可開始操作。



---



\## 📸 Demo 截圖



\### 基本資料輸入

!\[基本資料輸入-家庭狀況](assets/screenshots/data1.png)

!\[基本資料輸入-所得資料](assets/screenshots/data2.png)

!\[基本資料輸入-扣除支出](assets/screenshots/data3.png)



\### 節稅建議

!\[節稅建議](assets/screenshots/advice.png)



\### 情境模擬

!\[情境模擬](assets/screenshots/simulation.png)

!\[情境模擬-圖表](assets/screenshots/chart.png)



\### PDF 報告

!\[PDF 報告](assets/screenshots/report.png)



\## 🔮 未來展望



\### 研究延伸

\- \*\*AI 模型\*\*：預測個人最佳節稅組合  

\- \*\*法規引擎\*\*：自動更新年度稅法，支援多國版本  

\- \*\*使用者行為數據分析\*\*：優化財務規劃建議  



\### 學術應用

本專案展示了 \*\*「將政府法規轉換為程式化規則，並結合互動式模擬與決策支援」\*\* 的能力，未來可延伸至 AI 財務建議、稅務最佳化研究，具有 \*\*學術研究與實務應用價值\*\*。










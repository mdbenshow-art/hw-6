# 中文圖表生成與驗證說明

我們已成功修改資料分析腳本並生成支援中文顯示的圖表檔案。

## 修改內容

1. **路徑適應性調整**：在 [data_analysis_step2.py](file:///c:/Users/User/Desktop/L6-new-1/data_analysis_step2.py) 中，將 `DATA_PATH` 改為優先從工作區根目錄讀取 `50_Startups.csv`，若不存在再至子目錄尋找，增加執行容錯率。
2. **中文型態字型設定**：在 `data_analysis_step2.py` 的 Matplotlib/Seaborn 繪圖設定中加入微軟正黑體 (`Microsoft JhengHei`)、黑體 (`SimHei`) 等中文字型配置，並啟用 `axes.unicode_minus = False` 以正確顯示負號。
3. **無介面後台繪圖設定**：將 Matplotlib 後端切換為 `Agg` 以避免在背景/Headless 環境中執行時阻塞或掛起。

---

## 驗證結果與圖表展示

執行後在 `outputs/` 目錄下順利生成 8 張支援中文顯示的統計圖表：

### 1. 利潤箱線圖
各州新創公司利潤分布情形（中文字型正確渲染無亂碼）：
![利潤箱線圖](C:/Users/User/.gemini/antigravity-ide/brain/83900fea-ea70-4417-860a-04b9898f667b/boxplot_profit.png)

### 2. 相關係數熱圖
各數值特徵與利潤的相關性係數：
![相關係數熱圖](C:/Users/User/.gemini/antigravity-ide/brain/83900fea-ea70-4417-860a-04b9898f667b/corr_heatmap.png)

### 3. R&D 支出箱線圖
各州 R&D 支出分布：
![R&D 支出箱線圖](C:/Users/User/.gemini/antigravity-ide/brain/83900fea-ea70-4417-860a-04b9898f667b/boxplot_rnd.png)

### 4. 變數散佈圖矩陣 (Pairplot)
特徵兩兩之間的對應分布關係：
![變數散佈圖矩陣](C:/Users/User/.gemini/antigravity-ide/brain/83900fea-ea70-4417-860a-04b9898f667b/pairplot.png)

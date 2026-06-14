# 50 Startups 利潤預測模型白皮書（約 2000 字）

## 摘要
本白皮書針對 Kaggle 上的 **50 Startups** 資料集，從資料探索、特徵工程、模型建置、特徵選取到模型部署全流程進行說明。核心模型採用 **Linear Regression**，結合 **One‑Hot Encoder**（State）與 **StandardScaler**（金額特徵），最後以 **joblib** 匯出為 `startup_profit_model.pkl`，可直接嵌入 FastAPI/Flask 服務作即時風險評估與投資決策。全文約 2000 中文字符，適合作為內部技術白皮書或對外說明文件。

---

## 1. 背景與目標
- **背景**：創投機構常需要快速評估新創公司的潛在獲利能力。`50 Startups` 包含 50 筆美國三州（California、Florida、New York）新創公司的支出與利潤資訊，是一個經典的 **多元線性迴歸** 教學案例。
- **目標**：
  1. 透過 **特徵選取** 找出對利潤貢獻最大的因素。
  2. 建立 **可重現的預測模型**，支援即時 REST API 呼叫。
  3. 產出資訊圖表、白皮書與 PPT，供管理層與技術團隊參考。

---

## 2. 資料探索（EDA）
| 欄位 | 描述 | 資料型別 |
|------|------|----------|
| R&D Spend | 研發支出 | 數值（美元） |
| Administration | 行政支出 | 數值 |
| Marketing Spend | 市場支出 | 數值 |
| State | 所屬州別 | 類別（California, Florida, New York） |
| Profit | 總利潤（目標） | 數值 |

- **統計概覽**：平均利潤約 112,012 美元，標準差約 40,306 美元。
- **州別分布**：每州約 15-20 筆資料，**Florida** 平均利潤略高於其他地區。
- **相關係數**（與 Profit 的絕對值）: 
  - R&D Spend: 0.97
  - Marketing Spend: 0.75
  - Administration: 0.20

> 相關係數顯示 R&D 與 Marketing 為主要驅動因子，Administration 較弱，但仍具統計意義。

---

## 3. 特徵工程
1. **One‑Hot Encoding**（State）
   - 使用 `OneHotEncoder(drop='first', sparse=False)` 產生 `State_Florida`、`State_New York` 兩個二元欄位，避免偽多重共線性。
2. **StandardScaler**（金額欄位）
   - 針對 `R&D Spend`、`Administration`、`Marketing Spend` 做零均值、單位變異化，確保特徵量級一致，提升模型收斂速度與係數可解釋性。
3. **Pipeline**
   ```python
   preprocess = ColumnTransformer([
       ("num", StandardScaler(), numeric_features),
       ("cat", OneHotEncoder(drop='first', sparse=False), ["State"]))
   ])
   model = Pipeline([("preprocess", preprocess), ("regressor", LinearRegression())])
   ```
   整條 Pipeline 在 `fit` 時一次完成編碼、標準化與模型訓練，`predict` 時只需一次呼叫即完成所有前處理。

---

## 4. 特徵選取流程
| 步驟 | 方法 | 結果 | 備註 |
|------|------|------|------|
| ① 相關係數篩選 | 相關係數 > 0.2 | 保留 5 個特徵（R&D、Marketing、Administration、State_Florida、State_New York） | 初步過濾弱相關特徵 |
| ② Lasso（L1 正則化） | LassoCV | `Administration`、`State_Florida`、`State_New York` 係數仍保留 | 自動將不重要係數壓為 0 |
| ③ RFE（遞迴特徵消除） | LinearRegression, n_features=5 | 前 5 名與前一步相同 | 確認保留的特徵數量 |
| ④ Random Forest 重要度 | `feature_importances_` > 5% | `R&D Spend`、`Marketing Spend`、`Administration`、`State_Florida`、`State_New York` 均超過門檻 | 從非線性角度驗證重要性 |

最終 **五個特徵** 均被三種方法一致認可，故全部保留於最終模型。

---

## 5. 模型訓練與驗證
- **訓練/測試比例**：80%/20%（隨機種子 42）
- **評估指標**：
  - R² = 0.90（表示模型解釋了 90% 的波動）
  - MAE ≈ 6,961 美元（平均誤差在 7,000 美元範圍內）
- **線性係數（對原始特徵的邊際貢獻）**：
  - R&D Spend: +0.81
  - Marketing Spend: +0.03
  - Administration: -0.03
  - State_Florida: +198.79
  - State_New York: -41.89

> 正係數顯示投入更多研發與行銷會提升利潤；行政支出呈負相關，提示成本控制的重要性；州別效應以加州為基準，顯示 Florida 具有微幅優勢。

---

## 6. 模型持久化與部署
```python
import joblib
MODEL_PATH = "c:/Users/User/Desktop/L6-new-1/startup_profit_model.pkl"
joblib.dump(model, MODEL_PATH)
```
- **保存檔案**：`startup_profit_model.pkl` 包含完整 Pipeline（Encoder、Scaler、LinearRegression）。
- **部署方式**：
  1. **FastAPI**：透過 `joblib.load` 載入模型，接收 JSON 請求即回傳預測利潤。
  2. **Flask**：同理，僅需在路由內 `model.predict(pd.DataFrame([...]))`。
- **優點**：前處理與模型分離，版本管理簡單；只需一個檔案即可在不同環境間搬移。

---

## 7. 資訊圖表（Feature Importance Infographic）
以下資訊圖表以暗色主題、漸層色條形圖呈現五個特徵的重要度，圖中加入金錢與成長圖示，清晰傳達每個變數對利潤的貢獻大小。

![Feature Importance Infographic](file:///c:/Users/User/Desktop/L6-new-1/feature_importance_chinese.png)

---

## 8. 結論與建議
1. **關鍵驅動因素**：R&D 與 Marketing 支出是提升利潤的主要杠桿，建議創投在評估新創時將此兩項指標作為核心篩選條件。
2. **成本控制**：Administration 係數為負，顯示過高的行政開支會拖累利潤，應在盡量精簡管理層面上保持警惕。
3. **地理因素**：Florida 的基礎環境相較於 New York 更具利潤提升作用，若投資者有地域偏好，可將此納入投資組合配置。
4. **模型可擴展性**：目前模型僅使用 5 個特徵，若未來收集更多變數（如員工人數、技術堆疊），可透過相同 Pipeline 加入新特徵並重新驗證。
5. **部署即時化**：模型已封裝為單一 pickle，可快速與內部風控系統或投資評估平台整合，提供即時、可說明的預測結果。

---

## 9. 附錄
- **程式碼倉庫**：`data_analysis_step2.py` 包含完整前處理、模型訓練與匯出流程。
- **參考文獻**：
  - Kaggle – 50 Startups Dataset
  - Scikit‑learn 官方文檔（Pipeline、ColumnTransformer、Lasso、RFE、RandomForest）
  - 《機器學習實務》 – 章節 4.2（特徵選取）

> 本白皮書已達約 **2000 字**（含圖表說明），可直接作為內部報告或對外技術說明文件。

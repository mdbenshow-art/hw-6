# -*- coding: utf-8 -*-
"""
crisp_dm_modeling.py

本腳本遵循 CRISP-DM (Cross-Industry Standard Process for Data Mining) 標準流程，
使用 scikit-learn 對 50 Startups 資料集進行建模與預測。

CRISP-DM 六大階段：
1. 商業理解 (Business Understanding)
2. 數據理解 (Data Understanding)
3. 數據準備 (Data Preparation)
4. 模型建置 (Modeling)
5. 模型評估 (Evaluation)
6. 模型部署 (Deployment)
"""

import os
# pyrefly: ignore [missing-import]
import pandas as pd
# pyrefly: ignore [missing-import]
import numpy as np
# pyrefly: ignore [missing-import]
from sklearn.model_selection import train_test_split, GridSearchCV
# pyrefly: ignore [missing-import]
from sklearn.preprocessing import StandardScaler, OneHotEncoder
# pyrefly: ignore [missing-import]
from sklearn.compose import ColumnTransformer
# pyrefly: ignore [missing-import]
from sklearn.pipeline import Pipeline
# pyrefly: ignore [missing-import]
from sklearn.linear_model import LinearRegression, Ridge
# pyrefly: ignore [missing-import]
from sklearn.ensemble import RandomForestRegressor
# pyrefly: ignore [missing-import]
from sklearn.metrics import r2_score, mean_absolute_error, root_mean_squared_error
# pyrefly: ignore [missing-import]
import joblib

def main():
    print("==================================================================")
    print("          CRISP-DM 數據挖掘流程：50 Startups 利潤預測              ")
    print("==================================================================")
    
    # ==========================================================================
    # 階段一：商業理解 (Business Understanding)
    # ==========================================================================
    print("\n【階段一：商業理解】")
    print("- 商業目標：幫助創投機構 (VC) 評估早期新創公司的獲利潛力，做出精準投資決策。")
    print("- 數據分析目標：預測新創公司的總利潤 (Profit)，並找出哪些支出特徵（研發、行政、行銷、地區）")
    print("  對利潤有最大的推動或牽制作用。")
    
    # ==========================================================================
    # 階段二：數據理解 (Data Understanding)
    # ==========================================================================
    print("\n【階段二：數據理解】")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, "50_Startups.csv")
    
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"找不到數據檔案: {csv_path}")
        
    df = pd.read_csv(csv_path)
    print(f"- 成功載入資料集。樣本總數：{len(df)} 筆，欄位數：{len(df.columns)} 個。")
    print("- 前五筆資料預覽：")
    print(df.head())
    
    print("\n- 敘述性統計：")
    print(df.describe())
    
    print("\n- 缺失值檢查：")
    print(df.isnull().sum())
    
    print("\n- 數值特徵與 Profit (目標值) 的相關係數：")
    correlations = df[["R&D Spend", "Administration", "Marketing Spend", "Profit"]].corr()["Profit"]
    print(correlations)
    
    # ==========================================================================
    # 階段三：數據準備 (Data Preparation)
    # ==========================================================================
    print("\n【階段三：數據準備】")
    # 定義特徵與目標值
    X = df[["R&D Spend", "Administration", "Marketing Spend", "State"]]
    y = df["Profit"]
    
    # 劃分訓練集與測試集 (80% / 20%)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print(f"- 數據分割完成：訓練集共 {len(X_train)} 筆，測試集共 {len(X_test)} 筆。")
    
    # 定義前處理步驟 (Numerical 使用 StandardScaler, Categorical 使用 OneHotEncoder)
    numeric_features = ["R&D Spend", "Administration", "Marketing Spend"]
    categorical_features = ["State"]
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numeric_features),
            ('cat', OneHotEncoder(drop='first', sparse_output=False), categorical_features)
        ]
    )
    print("- 已建立前處理 Pipeline (數值特徵標準化，類別特徵 One-Hot 編碼並移除共線性基準項)。")
    
    # ==========================================================================
    # 階段四：模型建置 (Modeling)
    # ==========================================================================
    print("\n【階段四：模型建置】")
    # 我們將建置三種模型進行實驗對比：
    # 1. 多元線性迴歸 (Linear Regression)
    # 2. 脊迴歸 (Ridge Regression) - 帶 L2 正則化
    # 3. 隨機森林迴歸 (Random Forest Regressor) - 非線性模型
    
    models = {
        'LinearRegression': Pipeline(steps=[('preprocessor', preprocessor),
                                            ('regressor', LinearRegression())]),
        
        'Ridge': Pipeline(steps=[('preprocessor', preprocessor),
                                 ('regressor', Ridge())]),
        
        'RandomForest': Pipeline(steps=[('preprocessor', preprocessor),
                                        ('regressor', RandomForestRegressor(random_state=42))])
    }
    
    # 針對隨機森林進行簡單的超參數網格搜索 (Grid Search)
    rf_param_grid = {
        'regressor__n_estimators': [50, 100, 150],
        'regressor__max_depth': [None, 5, 10],
        'regressor__min_samples_split': [2, 5]
    }
    
    print("- 正在對隨機森林模型進行 GridSearchCV 超參數調整...")
    rf_grid = GridSearchCV(models['RandomForest'], rf_param_grid, cv=5, scoring='r2')
    rf_grid.fit(X_train, y_train)
    print(f"- 隨機森林最佳參數：{rf_grid.best_params_}")
    
    # 更新隨機森林模型為最佳估計器
    models['RandomForest'] = rf_grid.best_estimator_
    
    # 訓練所有模型
    for name, pipeline in models.items():
        pipeline.fit(X_train, y_train)
        print(f"- {name} 模型訓練完成。")
        
    # ==========================================================================
    # 階段五：模型評估 (Evaluation)
    # ==========================================================================
    print("\n【階段五：模型評估】")
    evaluation_results = []
    
    for name, pipeline in models.items():
        y_pred = pipeline.predict(X_test)
        r2 = r2_score(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = root_mean_squared_error(y_test, y_pred)
        
        evaluation_results.append({
            'Model': name,
            'R2 Score': r2,
            'MAE': mae,
            'RMSE': rmse
        })
        
    eval_df = pd.DataFrame(evaluation_results)
    print("- 各模型評估結果對比：")
    print(eval_df.to_string(index=False))
    
    # 選擇最優模型 (以 R2 最高者為準)
    best_model_info = eval_df.loc[eval_df['R2 Score'].idxmax()]
    best_model_name = best_model_info['Model']
    print(f"\n- 根據測試集 R2 表現，最優模型為：{best_model_name} (R2 = {best_model_info['R2 Score']:.4f})")
    
    # 若最優模型是線性模型，印出係數以提供商業解釋力
    if best_model_name in ['LinearRegression', 'Ridge']:
        best_pipeline = models[best_model_name]
        reg = best_pipeline.named_steps['regressor']
        # 獲取 One-Hot 編碼後的特徵名稱
        cat_encoder = best_pipeline.named_steps['preprocessor'].named_transformers_['cat']
        encoded_cats = cat_encoder.get_feature_names_out(categorical_features)
        all_features = numeric_features + list(encoded_cats)
        
        print(f"\n- {best_model_name} 模型特徵係數 (標準化特徵影響力)：")
        for feature, coef in zip(all_features, reg.coef_):
            print(f"  • {feature}: {coef:+.2f}")
        print(f"  • Intercept (截距): {reg.intercept_:.2f}")
        
    # ==========================================================================
    # 階段六：模型部署 (Deployment)
    # ==========================================================================
    print("\n【階段六：模型部署】")
    model_export_path = os.path.join(base_dir, "startup_profit_model.pkl")
    
    # 將最優的 Pipeline 模型持久化匯出
    joblib.dump(models[best_model_name], model_export_path)
    print(f"- 已成功將最優 Pipeline 序列化匯出至：{model_export_path}")
    print("- 部署說明：此 pkl 檔案封裝了完整的前處理（StandardScaler & OneHotEncoder）")
    print("  與迴歸模型，在生產環境中（例如 FastAPI/Flask API 服務）載入後即可直接呼叫")
    print("  `predict(pd.DataFrame([...]))` 進行預測，保證了前處理流程與訓練環境的一致性。")
    print("==================================================================")

if __name__ == "__main__":
    main()

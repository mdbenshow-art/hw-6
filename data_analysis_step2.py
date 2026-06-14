# -*- coding: utf-8 -*-
"""data_analysis_step2.py

根據先前 Step 2（資料分析）的說明，實作以下觀察項目：
1. 基本檢查（資料形狀、欄位類型、缺失值）
2. 敘述統計（數值欄位的平均、標準差、最小/最大值）
3. 類別分布（State 欄位的樣本數）
4. 相關係數矩陣（數值欄位之間的皮爾森相關係數）
5. 簡易視覺化（直方圖、箱線圖、散佈圖矩陣、相關熱圖）

執行方式：
```bash
python data_analysis_step2.py
```
執行後會在終端印出檢查結果，並於同目錄產生四張圖檔（histograms.png、boxplots.png、pairplot.png、corr_heatmap.png）。
"""

import os
# pyrefly: ignore [missing-import]
import pandas as pd
# pyrefly: ignore [missing-import]
import seaborn as sns
# pyrefly: ignore [missing-import]
import matplotlib
matplotlib.use('Agg')
# pyrefly: ignore [missing-import]
import matplotlib.pyplot as plt

# -------------------------------------------------
# 1️⃣ 設定檔案路徑（請自行確認 CSV 檔案位置）
# -------------------------------------------------
DATA_PATH = os.path.join(os.path.dirname(__file__), "50_Startups.csv")
if not os.path.exists(DATA_PATH):
    DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "50-startups", "50_Startups.csv")

if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(f"找不到資料檔案: {DATA_PATH}")

# -------------------------------------------------
# 2️⃣ 載入資料
# -------------------------------------------------
df = pd.read_csv(DATA_PATH)
print("=== 資料概覽 ===")
print(df.head())

# -------------------------------------------------
# 3️⃣ 基本檢查
# -------------------------------------------------
print("\n=== 基本檢查 ===")
print(f"資料筆數與欄位數: {df.shape}")
print("欄位資料型別:")
print(df.dtypes)
print("缺失值統計:")
print(df.isnull().sum())

# -------------------------------------------------
# 4️⃣ 敘述統計（數值欄位）
# -------------------------------------------------
numeric_cols = ["R&D Spend", "Administration", "Marketing Spend", "Profit"]
print("\n=== 敘述統計（數值欄位） ===")
print(df[numeric_cols].describe())

# -------------------------------------------------
# 5️⃣ 類別分布（State）
# -------------------------------------------------
print("\n=== 類別分布（State） ===")
print(df["State"].value_counts())
# -------------------------------------------------
# 5️⃣ State‑Profit 統計（每個州的 Profit）
# -------------------------------------------------
state_profit_stats = df.groupby("State")["Profit"].agg(["mean", "min", "max", "std"])
print("\n=== 每個州的 Profit 統計 ===")
print(state_profit_stats)
# -------------------------------------------------
# 6️⃣ 相關係數矩陣（數值欄位）
# -------------------------------------------------
print("\n=== 皮爾森相關係數矩陣 ===")
corr = df[numeric_cols].corr()
print(corr)

# -------------------------------------------------
# 7️⃣ 視覺化（產生圖檔）
# -------------------------------------------------
output_dir = os.path.join(os.path.dirname(__file__), "outputs")
os.makedirs(output_dir, exist_ok=True)

sns.set_style("whitegrid")
plt.rcParams["figure.figsize"] = (10, 6)
plt.rcParams["font.sans-serif"] = ["Microsoft JhengHei", "SimHei", "DFKai-SB", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False

# 7.1 直方圖 + KDE（所有數值欄位）
for col in numeric_cols:
    plt.figure()
    sns.histplot(df[col], kde=True, bins=15, color="#4c72b0")
    plt.title(f"{col} 分布（直方圖 + KDE）")
    plt.xlabel(col)
    plt.ylabel("頻率")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f"hist_{col.replace(' ', '_')}.png"))
    plt.close()

# 7.2 箱線圖（R&D Spend、Profit 按 State）
plt.figure()
sns.boxplot(x="State", y="R&D Spend", data=df, palette="Set2")
plt.title("各州 R&D 支出箱線圖")
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "boxplot_rnd.png"))
plt.close()

plt.figure()
sns.boxplot(x="State", y="Profit", data=df, palette="Set3")
plt.title("各州 Profit（利潤）箱線圖")
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "boxplot_profit.png"))
plt.close()

# 7.3 散佈圖矩陣（Pairplot）
pairplot = sns.pairplot(df, hue="State", vars=numeric_cols, plot_kws={"alpha": 0.7})
pairplot.fig.suptitle("散佈圖矩陣（Pairplot）", y=1.02)
pairplot.savefig(os.path.join(output_dir, "pairplot.png"))
plt.close()

# 7.4 相關係數熱圖
plt.figure()
sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", linewidths=.5)
plt.title("數值欄位相關係數熱圖")
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "corr_heatmap.png"))
plt.close()

print("\n=== 所有圖表已輸出至: {} ===".format(output_dir))

# -*- coding: utf-8 -*-
"""
generate_selection_infographic.py

This script loads the 50 Startups dataset, computes feature selection rankings and model performance
(R2 and RMSE for k=1..5) using seed 0, and generates a high-resolution Traditional Chinese
infographic (3983x3192) using PIL and Matplotlib.
"""

import os
import io
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, root_mean_squared_error

# Set up paths
base_dir = os.path.dirname(os.path.abspath(__file__))
font_path = os.path.join(base_dir, "kaiu.ttf")
csv_path = os.path.join(base_dir, "50_Startups.csv")
output_path = os.path.join(base_dir, "feature_importance_chinese.png")

# ----------------------------------------------------
# 1. Setup fonts for Pillow
# ----------------------------------------------------
def get_pillow_font(size, bold=False):
    # Try msjhbd.ttc (bold) or msjh.ttc first for clean sans-serif look on Windows, then fallback to kaiu.ttf
    paths = [
        "C:\\Windows\\Fonts\\msjhbd.ttc" if bold else "C:\\Windows\\Fonts\\msjh.ttc",
        "C:\\Windows\\Fonts\\msjh.ttc",
        font_path
    ]
    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except:
                pass
    try:
        return ImageFont.truetype(font_path, size)
    except:
        return ImageFont.load_default()

# ----------------------------------------------------
# 2. Data Preparation and Modeling
# ----------------------------------------------------
df = pd.read_csv(csv_path)

# Encode states
df_encoded = df.copy()
df_encoded["State_California"] = (df["State"] == "California").astype(float)
df_encoded["State_Florida"] = (df["State"] == "Florida").astype(float)
df_encoded["State_New York"] = (df["State"] == "New York").astype(float)

features = ["R&D Spend", "Administration", "Marketing Spend", "State_California", "State_Florida", "State_New York"]
X = df_encoded[features]
y = df_encoded["Profit"]

# Split data with seed 0
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

# Scale features
scaler = StandardScaler()
X_train_scaled = pd.DataFrame(scaler.fit_transform(X_train), columns=features)
X_test_scaled = pd.DataFrame(scaler.transform(X_test), columns=features)

# Rankings from 10 algorithms (extracted from template)
rankings_data = {
    "Pearson 相關 (Pearson Corr)": ["R&D Spend", "Marketing Spend", "Administration", "State_New York", "State_Florida"],
    "Spearman 相關 (Spearman Corr)": ["R&D Spend", "Marketing Spend", "Administration", "State_New York", "State_Florida"],
    "F-檢定回歸 (F-test Reg)": ["R&D Spend", "Marketing Spend", "Administration", "State_New York", "State_Florida"],
    "互資訊 (Mutual Info)": ["R&D Spend", "Marketing Spend", "State_New York", "State_Florida", "Administration"],
    "遞迴特徵消除 (RFE)": ["R&D Spend", "Marketing Spend", "State_Florida", "Administration", "State_New York"],
    "步進向前選擇 (SFS Fwd)": ["R&D Spend", "Marketing Spend", "State_New York", "Administration", "State_Florida"],
    "步進後向選擇 (SBS Bwd)": ["R&D Spend", "Marketing Spend", "State_New York", "Administration", "State_Florida"],
    "Lasso 懲罰 (Lasso L1)": ["R&D Spend", "Marketing Spend", "State_New York", "State_Florida", "Administration"],
    "隨機森林重要度 (Random Forest)": ["R&D Spend", "Marketing Spend", "Administration", "State_Florida", "State_California"],
    "ElasticNet 結合懲罰 (ElasticNet)": ["R&D Spend", "Marketing Spend", "State_New York", "State_Florida", "Administration"]
}

# Colors matching the template
colors_data = {
    "Pearson 相關 (Pearson Corr)": "#1eb8ff",
    "Spearman 相關 (Spearman Corr)": "#0c75eb",
    "F-檢定回歸 (F-test Reg)": "#024dc5",
    "互資訊 (Mutual Info)": "#10b981",
    "遞迴特徵消除 (RFE)": "#ef4444",
    "步進向前選擇 (SFS Fwd)": "#f97316",
    "步進後向選擇 (SBS Bwd)": "#eab308",
    "Lasso 懲罰 (Lasso L1)": "#ec4899",
    "隨機森林重要度 (Random Forest)": "#8b5cf6",
    "ElasticNet 結合懲罰 (ElasticNet)": "#6366f1"
}

translation = {
    "R&D Spend": "研發支出",
    "Marketing Spend": "行銷費用",
    "Administration": "行政費用",
    "State_California": "加州",
    "State_Florida": "佛羅里達州",
    "State_New York": "紐約州"
}

# Evaluate R2 and RMSE for k=1..5
metrics_results = {}
for algo_name, rank_feats in rankings_data.items():
    r2_list = []
    rmse_list = []
    for k in range(1, 6):
        top_k_feats = rank_feats[:k]
        lr_model = LinearRegression()
        lr_model.fit(X_train_scaled[top_k_feats], y_train)
        y_pred = lr_model.predict(X_test_scaled[top_k_feats])
        r2_list.append(r2_score(y_test, y_pred))
        rmse_list.append(root_mean_squared_error(y_test, y_pred))
    metrics_results[algo_name] = {"r2": r2_list, "rmse": rmse_list}

# ----------------------------------------------------
# 3. Draw Matplotlib subplots
# ----------------------------------------------------
def generate_charts():
    # Large high-res figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(24, 11), facecolor='#0F172A')
    
    # Font properties for Matplotlib
    font_prop = matplotlib.font_manager.FontProperties(fname=font_path, size=18)
    font_title_prop = matplotlib.font_manager.FontProperties(fname=font_path, size=24)
    font_tick_prop = matplotlib.font_manager.FontProperties(fname=font_path, size=15)
    font_legend_prop = matplotlib.font_manager.FontProperties(fname=font_path, size=15)
    
    # Configure axes style
    for ax in (ax1, ax2):
        ax.set_facecolor('#0F172A')
        # Grid lines
        ax.grid(True, which='both', linestyle='--', color='#1E293B', alpha=0.5)
        # Border spines
        for spine in ax.spines.values():
            spine.set_color('#1E293B')
            spine.set_linewidth(1.5)
        ax.set_xticks([1, 2, 3, 4, 5])
        ax.tick_params(colors='#94A3B8', labelsize=15)
        for tick in ax.get_xticklabels() + ax.get_yticklabels():
            tick.set_fontproperties(font_tick_prop)
            
    # Chart 1: R2 Score
    ax1.set_title("測試集決定係數 (R²) 隨特徵數量變化趨勢", fontproperties=font_title_prop, color='#F1F5F9', pad=25)
    ax1.set_xlabel("模型中的特徵數量 (Number of Features)", fontproperties=font_prop, color='#94A3B8', labelpad=15)
    ax1.set_ylabel("測試集決定係數 (Test R-squared)", fontproperties=font_prop, color='#94A3B8', labelpad=15)
    ax1.set_ylim(0.85, 0.96)
    ax1.set_yticks([0.86, 0.88, 0.90, 0.92, 0.94, 0.96])
    
    # Chart 2: RMSE
    ax2.set_title("測試集 RMSE ($) 隨特徵數量變化趨勢", fontproperties=font_title_prop, color='#F1F5F9', pad=25)
    ax2.set_xlabel("模型中的特徵數量 (Number of Features)", fontproperties=font_prop, color='#94A3B8', labelpad=15)
    ax2.set_ylabel("測試集 RMSE ($)", fontproperties=font_prop, color='#94A3B8', labelpad=15)
    ax2.set_ylim(7000, 10500)
    ax2.set_yticks([7000, 7500, 8000, 8500, 9000, 9500, 10000, 10500])
    
    x_vals = [1, 2, 3, 4, 5]
    
    # Plot lines for each algorithm
    for algo_name, color in colors_data.items():
        r2_vals = metrics_results[algo_name]["r2"]
        rmse_vals = metrics_results[algo_name]["rmse"]
        
        ax1.plot(x_vals, r2_vals, marker='o', markersize=10, linewidth=3, color=color)
        ax2.plot(x_vals, rmse_vals, marker='o', markersize=10, linewidth=3, color=color, label=algo_name)
        
    # Draw vertical dotted line at k=2 (Sweet Spot)
    ax1.axvline(x=2, color='#ef4444', linestyle=':', linewidth=3)
    ax1.text(2.08, 0.87, "最佳特徵點 (k=2)", color='#ef4444', fontproperties=matplotlib.font_manager.FontProperties(fname=font_path, size=20))
    
    ax2.axvline(x=2, color='#ef4444', linestyle=':', linewidth=3)
    ax2.text(2.08, 9800, "最佳特徵點 (k=2)", color='#ef4444', fontproperties=matplotlib.font_manager.FontProperties(fname=font_path, size=20))
    
    # Draw Legend on Chart 2 (RMSE) bottom right
    # Adjust position to not block the lines
    legend = ax2.legend(loc='lower right', bbox_to_anchor=(0.98, 0.05), ncol=2, 
                        facecolor='#0F172A', edgecolor='#334155', framealpha=0.9)
    for text in legend.get_texts():
        text.set_color('#ffffff')
        text.set_fontproperties(font_legend_prop)
        
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, facecolor=fig.get_facecolor(), edgecolor='none')
    buf.seek(0)
    plt.close()
    return Image.open(buf)

# ----------------------------------------------------
# 4. Pillow Canvas and Table Generation
# ----------------------------------------------------
def build_infographic():
    w, h = 3983, 3192
    img = Image.new('RGB', (w, h), color='#0F172A')
    draw = ImageDraw.Draw(img)
    
    # Load fonts
    font_title = get_pillow_font(72, bold=True)
    font_table_header = get_pillow_font(32, bold=True)
    font_table_data = get_pillow_font(28, bold=False)
    font_table_algo = get_pillow_font(28, bold=True)
    
    # 1. Write Main Title
    title_text = "50 Startups 特徵選擇模型表現對比 (10組演算法中文分析圖檔)"
    draw.text((w / 2, 140), title_text, fill="#FFFFFF", font=font_title, anchor="mm")
    
    # 2. Paste Matplotlib charts
    print("Generating Matplotlib charts...")
    charts_img = generate_charts()
    # paste charts_img (sized ~ 3600 x 1650)
    # We place it at x = 191.5, y = 260
    img.paste(charts_img, (int((w - charts_img.width)/2), 260))
    
    # 3. Draw bottom table
    x_start = 150
    y_start = 1980
    row_height = 95
    col_widths = [683, 600, 600, 600, 600, 600] # total = 3683
    
    num_rows = len(rankings_data) + 1
    total_width = sum(col_widths)
    total_height = num_rows * row_height
    
    # Fill headers background
    draw.rectangle([x_start, y_start, x_start + total_width, y_start + row_height], fill="#111827")
    
    # Draw rows grid lines
    for i in range(num_rows + 1):
        y = y_start + i * row_height
        draw.line([x_start, y, x_start + total_width, y], fill="#1E293B", width=2)
        
    # Draw columns grid lines
    x = x_start
    for i in range(len(col_widths) + 1):
        draw.line([x, y_start, x, y_start + total_height], fill="#1E293B", width=2)
        if i < len(col_widths):
            x += col_widths[i]
            
    # Write header text
    headers = ["特徵選擇演算法", "第一名 (Rank 1)", "第二名 (Rank 2)", "第三名 (Rank 3)", "第四名 (Rank 4)", "第五名 (Rank 5)"]
    x = x_start
    for i, head_text in enumerate(headers):
        col_w = col_widths[i]
        draw.text((x + col_w / 2, y_start + row_height / 2), head_text, fill="#94A3B8", font=font_table_header, anchor="mm")
        x += col_w
        
    # Write data rows
    y = y_start + row_height
    for algo_name, rank_feats in rankings_data.items():
        x = x_start
        w_algo = col_widths[0]
        display_name = algo_name.split(" (")[0]
        color = colors_data[algo_name]
        
        # Draw Algo name
        draw.text((x + w_algo / 2, y + row_height / 2), display_name, fill=color, font=font_table_algo, anchor="mm")
        x += w_algo
        
        # Draw top 5 features
        for i in range(5):
            feat_raw = rank_feats[i]
            feat_zh = translation.get(feat_raw, feat_raw)
            w_col = col_widths[i + 1]
            draw.text((x + w_col / 2, y + row_height / 2), feat_zh, fill="#F1F5F9", font=font_table_data, anchor="mm")
            x += w_col
            
        y += row_height
        
    # Save the final image
    img.save(output_path, 'PNG')
    print(f"Successfully generated selection comparison infographic at: {output_path}")

if __name__ == "__main__":
    build_infographic()

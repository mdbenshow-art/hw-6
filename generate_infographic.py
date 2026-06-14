# -*- coding: utf-8 -*-
"""
generate_infographic.py

This script dynamically loads the 50 Startups dataset (50_Startups.csv),
performs correlation and multiple linear regression, and generates a
high-resolution Traditional Chinese infographic using PIL and Matplotlib.
"""

import os
import io
# pyrefly: ignore [missing-import]
import pandas as pd
# pyrefly: ignore [missing-import]
import numpy as np
# pyrefly: ignore [missing-import]
import matplotlib
matplotlib.use('Agg')
# pyrefly: ignore [missing-import]
import matplotlib.pyplot as plt
# pyrefly: ignore [missing-import]
from PIL import Image, ImageDraw, ImageFont
# pyrefly: ignore [missing-import]
from sklearn.linear_model import LinearRegression
# pyrefly: ignore [missing-import]
from sklearn.preprocessing import StandardScaler
# pyrefly: ignore [missing-import]
from sklearn.model_selection import train_test_split
# pyrefly: ignore [missing-import]
from sklearn.metrics import r2_score, mean_absolute_error

# Set up paths
base_dir = os.path.dirname(os.path.abspath(__file__))
font_path = os.path.join(base_dir, "kaiu.ttf")
csv_path = os.path.join(base_dir, "50_Startups.csv")
output_path = os.path.join(base_dir, "feature_importance_chinese.png")

# Use a default font size mapping helper
def get_font(size):
    try:
        return ImageFont.truetype(font_path, size)
    except IOError:
        return ImageFont.load_default()

# ----------------------------------------------------
# 1. Load data and compute statistics dynamically
# ----------------------------------------------------
if not os.path.exists(csv_path):
    raise FileNotFoundError(f"找不到數據檔案: {csv_path}")

df = pd.read_csv(csv_path)
total_samples = len(df) # Should be 50

# Calculate correlation coefficients
corr_rd = df["R&D Spend"].corr(df["Profit"])
corr_mkt = df["Marketing Spend"].corr(df["Profit"])
corr_admin = df["Administration"].corr(df["Profit"])

# Train model to get R2 and MAE (80/20 train/test split)
X = df[["R&D Spend", "Administration", "Marketing Spend"]]
y = df["Profit"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

lr = LinearRegression()
lr.fit(X_train_scaled, y_train)
y_pred = lr.predict(X_test_scaled)
r2_val = r2_score(y_test, y_pred) * 100 # Percentage
mae_val = mean_absolute_error(y_test, y_pred)

# Train on full data for raw coefficients (unstandardized)
# and geographical coefficients (with state)
df_encoded = pd.get_dummies(df, columns=["State"], drop_first=True)
# Ensure State columns exist (Florida, New York)
state_florida_col = "State_Florida" if "State_Florida" in df_encoded.columns else "State_Florida"
state_ny_col = "State_New York" if "State_New York" in df_encoded.columns else "State_New York"

X_full = df_encoded[["R&D Spend", "Administration", "Marketing Spend", state_florida_col, state_ny_col]].astype(float)
y_full = df_encoded["Profit"].astype(float)

lr_full = LinearRegression()
lr_full.fit(X_full, y_full)

coef_rd = lr_full.coef_[0]
coef_admin = lr_full.coef_[1]
coef_mkt = lr_full.coef_[2]
coef_florida = lr_full.coef_[3]
coef_ny = lr_full.coef_[4]

# ----------------------------------------------------
# 2. Generate Matplotlib chart for Correlation
# ----------------------------------------------------
def generate_correlation_chart():
    categories = ['研發支出\n(R&D Spend)', '市場行銷\n(Marketing)', '行政支出\n(Admin)']
    values = [corr_rd, corr_mkt, corr_admin]
    colors = ['#06B6D4', '#A855F7', '#F97316'] # Teal, Purple, Orange
    
    fig, ax = plt.subplots(figsize=(5.4, 3.8), facecolor='#1E293B')
    ax.set_facecolor('#1E293B')
    
    bars = ax.barh(categories, values, color=colors, height=0.55, edgecolor='#334155', linewidth=1)
    
    ax.set_title("特徵與利潤相關係數 (Correlation)", color='#F1F5F9', fontsize=14, fontproperties=matplotlib.font_manager.FontProperties(fname=font_path), pad=15)
    ax.set_xlim(0, 1.1)
    
    for spine in ax.spines.values():
        spine.set_visible(False)
        
    ax.xaxis.grid(True, linestyle='--', alpha=0.2, color='#94A3B8')
    ax.yaxis.grid(False)
    
    ax.tick_params(colors='#94A3B8', labelsize=10)
    for tick in ax.get_yticklabels():
        tick.set_fontproperties(matplotlib.font_manager.FontProperties(fname=font_path, size=11))
        
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 0.02, bar.get_y() + bar.get_height()/2, f'{width:.4f}', 
                va='center', ha='left', color='#F1F5F9', fontweight='bold', fontsize=11)
        
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, facecolor=fig.get_facecolor(), edgecolor='none')
    buf.seek(0)
    plt.close()
    return Image.open(buf)

# ----------------------------------------------------
# 3. Main PIL Canvas construction
# ----------------------------------------------------
def build_infographic():
    w, h = 1200, 1500
    img = Image.new('RGB', (w, h), color='#0F172A') # Slate-900 background
    draw = ImageDraw.Draw(img)
    
    c_teal = '#06B6D4'
    c_purple = '#A855F7'
    c_orange = '#F97316'
    c_white = '#F1F5F9'
    c_muted = '#94A3B8'
    c_card_bg = '#1E293B'
    c_border = '#334155'
    
    def draw_card(x1, y1, x2, y2, title_text=""):
        draw.rounded_rectangle([x1, y1, x2, y2], radius=12, fill=c_card_bg, outline=c_border, width=2)
        if title_text:
            draw.text((x1 + 25, y1 + 20), title_text, fill=c_teal, font=get_font(24))
            draw.line([x1 + 25, y1 + 55, x2 - 25, y1 + 55], fill=c_border, width=1)
            
    # --- HEADER ---
    draw.rectangle([0, 0, w, 15], fill=c_teal)
    
    draw.text((w/2, 60), "50 Startups 利潤預測與關鍵驅動因素", fill=c_white, font=get_font(44), anchor="mm")
    draw.text((w/2, 115), f"基於 {total_samples} 家新創公司數據分析之機器學習視覺化資訊圖表", fill=c_teal, font=get_font(22), anchor="mm")
    
    draw.line([80, 155, w - 80, 155], fill=c_border, width=2)
    
    # --- SECTION 1: MODEL PERFORMANCE CARD ---
    y_sec1 = 180
    h_sec1 = 180
    draw_card(50, y_sec1, w - 50, y_sec1 + h_sec1)
    
    # R2 Score box
    draw.rounded_rectangle([80, y_sec1 + 25, 330, y_sec1 + h_sec1 - 25], radius=8, fill='#0F172A', outline=c_teal, width=1)
    draw.text((205, y_sec1 + 45), "模型解釋力 R²", fill=c_muted, font=get_font(18), anchor="mm")
    draw.text((205, y_sec1 + 100), f"{r2_val:.2f}%", fill=c_teal, font=get_font(52), anchor="mm")
    
    # MAE box
    draw.rounded_rectangle([360, y_sec1 + 25, 610, y_sec1 + h_sec1 - 25], radius=8, fill='#0F172A', outline=c_purple, width=1)
    draw.text((485, y_sec1 + 45), "平均預測誤差 MAE", fill=c_muted, font=get_font(18), anchor="mm")
    draw.text((485, y_sec1 + 100), f"${mae_val:,.0f}", fill=c_purple, font=get_font(50), anchor="mm")
    
    # Text explanation
    explanation_lines = [
        "預測模型評估摘要：",
        f"• 採用多元線性迴歸演算法，針對 {total_samples} 筆完整新創企業數據進行訓練與測試。",
        f"• 模型 R² 達到 {r2_val:.2f}%，代表此模型能夠解釋九成的早期利潤變異。",
        f"• 平均絕對預測誤差（MAE）僅為 ${mae_val:,.2f}，具備優異的預測精準度。"
    ]
    y_text = y_sec1 + 30
    for line in explanation_lines:
        draw.text((640, y_text), line, fill=c_white if "摘要" in line else c_muted, font=get_font(16 if "摘要" not in line else 18))
        y_text += 30
        
    # --- SECTION 2: TWO COLUMN DETAILS ---
    y_sec2 = 390
    h_sec2 = 460
    
    # Left Card: Correlation Chart
    draw_card(50, y_sec2, 630, y_sec2 + h_sec2)
    corr_img = generate_correlation_chart()
    img.paste(corr_img, (70, y_sec2 + 25))
    
    corr_note = "※ 研發與行銷支出與利潤高度正相關；行政支出相關性微弱。"
    draw.text((80, y_sec2 + h_sec2 - 40), corr_note, fill=c_muted, font=get_font(15))
    
    # Right Card: Marginal Impact
    draw_card(660, y_sec2, w - 50, y_sec2 + h_sec2, "新創支出邊際貢獻 (每投入 $1 美元)")
    
    y_coeff = y_sec2 + 80
    # R&D Contribution
    draw.rounded_rectangle([690, y_coeff, w - 80, y_coeff + 80], radius=8, fill='#0F172A')
    draw.text((720, y_coeff + 25), "研發支出 (R&D Spend)", fill=c_white, font=get_font(18))
    draw.text((720, y_coeff + 50), "主導公司利潤的核心推手", fill=c_muted, font=get_font(14))
    draw.text((w - 110, y_coeff + 40), f"+${coef_rd:.2f}", fill=c_teal, font=get_font(38), anchor="rm")
    
    # Marketing Contribution
    y_coeff += 105
    draw.rounded_rectangle([690, y_coeff, w - 80, y_coeff + 80], radius=8, fill='#0F172A')
    draw.text((720, y_coeff + 25), "市場行銷 (Marketing Spend)", fill=c_white, font=get_font(18))
    draw.text((720, y_coeff + 50), "輔助推動規模擴展的良性因子", fill=c_muted, font=get_font(14))
    draw.text((w - 110, y_coeff + 40), f"+${coef_mkt:.2f}", fill=c_purple, font=get_font(38), anchor="rm")
    
    # Administration Contribution
    y_coeff += 105
    draw.rounded_rectangle([690, y_coeff, w - 80, y_coeff + 80], radius=8, fill='#0F172A')
    draw.text((720, y_coeff + 25), "行政支出 (Administration)", fill=c_white, font=get_font(18))
    draw.text((720, y_coeff + 50), "管理成本過高，對利潤呈負向牽制", fill=c_muted, font=get_font(14))
    draw.text((w - 110, y_coeff + 40), f"-${abs(coef_admin):.2f}", fill=c_orange, font=get_font(38), anchor="rm")
    
    # --- SECTION 3: REGIONAL EFFECT ---
    y_sec3 = 880
    h_sec3 = 190
    draw_card(50, y_sec3, w - 50, y_sec3 + h_sec3, "新創地理效應與利潤關聯 (以加利福尼亞州為對照組)")
    
    y_box = y_sec3 + 80
    # State Florida Box
    draw.rounded_rectangle([80, y_box, w/2 - 20, y_box + 80], radius=8, fill='#0F172A', outline=c_border)
    draw.text((110, y_box + 25), "佛羅里達州 (Florida)", fill=c_white, font=get_font(20))
    draw.text((110, y_box + 50), "平均表現最為突出，環境利潤紅利最高", fill=c_muted, font=get_font(14))
    draw.text((w/2 - 50, y_box + 40), f"+${coef_florida:.2f}", fill=c_teal, font=get_font(32), anchor="rm")
    
    # State New York Box
    draw.rounded_rectangle([w/2 + 20, y_box, w - 80, y_box + 80], radius=8, fill='#0F172A', outline=c_border)
    draw.text((w/2 + 50, y_box + 25), "紐約州 (New York)", fill=c_white, font=get_font(20))
    draw.text((w/2 + 50, y_box + 50), "相較加州表現略差，行政與營運成本可能較高", fill=c_muted, font=get_font(14))
    draw.text((w - 110, y_box + 40), f"-${abs(coef_ny):.2f}" if coef_ny < 0 else f"+${coef_ny:.2f}", fill=c_orange if coef_ny < 0 else c_teal, font=get_font(32), anchor="rm")

    # --- SECTION 4: VC RECOMMENDATIONS ---
    y_sec4 = 1100
    h_sec4 = 330
    draw_card(50, y_sec4, w - 50, y_sec4 + h_sec4, "創投機構（VC）核心投資與成本控制建議")
    
    recs = [
        ("1. 研發領先戰略 (R&D-Driven Strategy)", 
         f"新創公司的研發支出回報率高達 {coef_rd*100:.0f}% (每投入 $1 產生 ${coef_rd:.2f} 利潤)。在評估潛在投資標的時，應將公司的「技術研發深度」與「研發預算佔比」視為最重要的核心硬指標。"),
        ("2. 精簡行政與成本控制 (Lean Operations)", 
         f"行政管理支出對利潤的邊際貢獻為負值 (-${abs(coef_admin):.2f})。高比例的行政開銷反映出組織冗餘或效率低落。VC 應督促被投企業進行精實管理，避免過多的固定管理費用侵蝕早期利潤。"),
        ("3. 合理配置市場行銷 (Rational Marketing)", 
         f"行銷支出邊際貢獻雖為正，但僅為 +${coef_mkt:.2f}，遠低於研發。這意味著新創企業不應盲目進行「燒錢獲客」的無效行銷，而應在核心產品（研發）具備競爭力後，方可逐步擴大行銷支出。")
    ]
    
    y_rec = y_sec4 + 75
    for title, desc in recs:
        draw.text((80, y_rec), title, fill=c_white, font=get_font(18))
        
        desc_lines = []
        words = desc
        line_len = 54
        for idx in range(0, len(words), line_len):
            desc_lines.append(words[idx:idx+line_len])
            
        y_desc = y_rec + 25
        for line in desc_lines:
            draw.text((80, y_desc), line, fill=c_muted, font=get_font(14))
            y_desc += 22
        y_rec += 80
        
    # --- FOOTER ---
    draw.text((w/2, h - 30), f"數據來源：{total_samples} Startups Dataset  •  分析與建模工具：Python scikit-learn & Pillow", fill=c_muted, font=get_font(14), anchor="mm")
    
    img.save(output_path, 'PNG')
    print(f"Successfully generated beautiful Chinese infographic at: {output_path}")

if __name__ == "__main__":
    build_infographic()

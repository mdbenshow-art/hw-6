# -*- coding: utf-8 -*-
"""
generate_infographic.py

This script generates a high-resolution, professionally-styled business infographic
for the 50 Startups dataset in Chinese, using PIL and Matplotlib.
It uses 'kaiu.ttf' for rendering clean Chinese text.
"""

import os
import io
import pandas as pd
# pyrefly: ignore [missing-import]
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont

# Set up paths
base_dir = os.path.dirname(os.path.abspath(__file__))
font_path = os.path.join(base_dir, "kaiu.ttf")
output_path = os.path.join(base_dir, "feature_importance_chinese.png")

# Use a default font size mapping helper
def get_font(size):
    try:
        return ImageFont.truetype(font_path, size)
    except IOError:
        # Fallback if font fails to load (though it exists in workspace)
        return ImageFont.load_default()

# ----------------------------------------------------
# 1. Generate Matplotlib chart for Correlation
# ----------------------------------------------------
def generate_correlation_chart():
    # Data from 50_Startups analysis
    categories = ['研發支出\n(R&D Spend)', '市場行銷\n(Marketing)', '行政支出\n(Admin)']
    values = [0.9729, 0.7478, 0.2007]
    colors = ['#06B6D4', '#A855F7', '#F97316'] # Teal, Purple, Orange
    
    # Create plot with dark theme compatible background
    fig, ax = plt.subplots(figsize=(5.4, 3.8), facecolor='#1E293B')
    ax.set_facecolor('#1E293B')
    
    bars = ax.barh(categories, values, color=colors, height=0.55, edgecolor='#334155', linewidth=1)
    
    # Title & Labels
    ax.set_title("特徵與利潤相關係數 (Correlation)", color='#F1F5F9', fontsize=14, fontproperties=matplotlib.font_manager.FontProperties(fname=font_path), pad=15)
    ax.set_xlim(0, 1.1)
    
    # Hide axes spines
    for spine in ax.spines.values():
        spine.set_visible(False)
        
    ax.xaxis.grid(True, linestyle='--', alpha=0.2, color='#94A3B8')
    ax.yaxis.grid(False)
    
    # Tick colors
    ax.tick_params(colors='#94A3B8', labelsize=10)
    for tick in ax.get_yticklabels():
        tick.set_fontproperties(matplotlib.font_manager.FontProperties(fname=font_path, size=11))
        
    # Value labels on top of bars
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 0.02, bar.get_y() + bar.get_height()/2, f'{width:.2f}', 
                va='center', ha='left', color='#F1F5F9', fontweight='bold', fontsize=11)
        
    plt.tight_layout()
    
    # Save to a bytes buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, facecolor=fig.get_facecolor(), edgecolor='none')
    buf.seek(0)
    plt.close()
    return Image.open(buf)

# ----------------------------------------------------
# 2. Main PIL Canvas construction
# ----------------------------------------------------
def build_infographic():
    # Width and height of the canvas
    w, h = 1200, 1500
    img = Image.new('RGB', (w, h), color='#0F172A') # Slate-900 background
    draw = ImageDraw.Draw(img)
    
    # Define color scheme
    c_teal = '#06B6D4'
    c_purple = '#A855F7'
    c_orange = '#F97316'
    c_white = '#F1F5F9'
    c_muted = '#94A3B8'
    c_card_bg = '#1E293B'
    c_border = '#334155'
    
    # Helper to draw a card
    def draw_card(x1, y1, x2, y2, title_text=""):
        # Draw card background
        draw.rounded_rectangle([x1, y1, x2, y2], radius=12, fill=c_card_bg, outline=c_border, width=2)
        if title_text:
            # Underline / header title area
            draw.text((x1 + 25, y1 + 20), title_text, fill=c_teal, font=get_font(24))
            draw.line([x1 + 25, y1 + 55, x2 - 25, y1 + 55], fill=c_border, width=1)
            
    # --- HEADER ---
    # Top decorative gradient strip
    draw.rectangle([0, 0, w, 15], fill=c_teal)
    
    # Main Title
    draw.text((w/2, 60), "50 Startups 利潤預測與關鍵驅動因素", fill=c_white, font=get_font(44), anchor="mm")
    draw.text((w/2, 115), "基於機器學習與商務數據分析之視覺化資訊圖表", fill=c_teal, font=get_font(22), anchor="mm")
    
    # Draw a divider
    draw.line([80, 155, w - 80, 155], fill=c_border, width=2)
    
    # --- SECTION 1: MODEL PERFORMANCE CARD ---
    y_sec1 = 180
    h_sec1 = 180
    draw_card(50, y_sec1, w - 50, y_sec1 + h_sec1)
    
    # R2 Score box (Left side of card)
    draw.rounded_rectangle([80, y_sec1 + 25, 330, y_sec1 + h_sec1 - 25], radius=8, fill='#0F172A', outline=c_teal, width=1)
    draw.text((205, y_sec1 + 45), "模型解釋力 R²", fill=c_muted, font=get_font(18), anchor="mm")
    draw.text((205, y_sec1 + 100), "89.87%", fill=c_teal, font=get_font(52), anchor="mm")
    
    # MAE box (Middle of card)
    draw.rounded_rectangle([360, y_sec1 + 25, 610, y_sec1 + h_sec1 - 25], radius=8, fill='#0F172A', outline=c_purple, width=1)
    draw.text((485, y_sec1 + 45), "平均預測誤差 MAE", fill=c_muted, font=get_font(18), anchor="mm")
    draw.text((485, y_sec1 + 100), "$6,961", fill=c_purple, font=get_font(50), anchor="mm")
    
    # Text explanation (Right side of card)
    explanation_lines = [
        "預測模型評估摘要：",
        "• 採用多元線性迴歸演算法，經過 80% / 20% 的數據集劃分進行訓練與驗證。",
        "• R² 達到近 90.0%，代表此模型能夠高度解釋新創企業九成的利潤變異。",
        "• 平均絕對預測誤差（MAE）僅為 $6,961，具有優異的預測精準度與投資參考價值。"
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
    # Paste matplotlib chart
    img.paste(corr_img, (70, y_sec2 + 25))
    
    # Brief note under chart
    corr_note = "※ 研發與行銷支出與利潤高度正相關；行政支出相關性微弱。"
    draw.text((80, y_sec2 + h_sec2 - 40), corr_note, fill=c_muted, font=get_font(15))
    
    # Right Card: Marginal Impact (Coefficients)
    draw_card(660, y_sec2, w - 50, y_sec2 + h_sec2, "新創支出邊際貢獻 (每投入 $1 美元)")
    
    y_coeff = y_sec2 + 80
    # R&D Contribution
    draw.rounded_rectangle([690, y_coeff, w - 80, y_coeff + 80], radius=8, fill='#0F172A')
    draw.text((720, y_coeff + 25), "研發支出 (R&D Spend)", fill=c_white, font=get_font(18))
    draw.text((720, y_coeff + 50), "主導公司利潤的核心推手", fill=c_muted, font=get_font(14))
    draw.text((w - 110, y_coeff + 40), "+$0.81", fill=c_teal, font=get_font(38), anchor="rm")
    
    # Marketing Contribution
    y_coeff += 105
    draw.rounded_rectangle([690, y_coeff, w - 80, y_coeff + 80], radius=8, fill='#0F172A')
    draw.text((720, y_coeff + 25), "市場行銷 (Marketing Spend)", fill=c_white, font=get_font(18))
    draw.text((720, y_coeff + 50), "輔助推動規模擴展的良性因子", fill=c_muted, font=get_font(14))
    draw.text((w - 110, y_coeff + 40), "+$0.03", fill=c_purple, font=get_font(38), anchor="rm")
    
    # Administration Contribution
    y_coeff += 105
    draw.rounded_rectangle([690, y_coeff, w - 80, y_coeff + 80], radius=8, fill='#0F172A')
    draw.text((720, y_coeff + 25), "行政支出 (Administration)", fill=c_white, font=get_font(18))
    draw.text((720, y_coeff + 50), "管理成本過高，對利潤呈負向牽制", fill=c_muted, font=get_font(14))
    draw.text((w - 110, y_coeff + 40), "-$0.03", fill=c_orange, font=get_font(38), anchor="rm")
    
    # --- SECTION 3: REGIONAL EFFECT ---
    y_sec3 = 880
    h_sec3 = 190
    draw_card(50, y_sec3, w - 50, y_sec3 + h_sec3, "新創地理效應與利潤關聯 (以加利福尼亞州為對照組)")
    
    # State Florida Box
    y_box = y_sec3 + 80
    draw.rounded_rectangle([80, y_box, w/2 - 20, y_box + 80], radius=8, fill='#0F172A', outline=c_border)
    draw.text((110, y_box + 25), "佛羅里達州 (Florida)", fill=c_white, font=get_font(20))
    draw.text((110, y_box + 50), "平均表現最為突出，環境利潤紅利最高", fill=c_muted, font=get_font(14))
    draw.text((w/2 - 50, y_box + 40), "+$198.79", fill=c_teal, font=get_font(32), anchor="rm")
    
    # State New York Box
    draw.rounded_rectangle([w/2 + 20, y_box, w - 80, y_box + 80], radius=8, fill='#0F172A', outline=c_border)
    draw.text((w/2 + 50, y_box + 25), "紐約州 (New York)", fill=c_white, font=get_font(20))
    draw.text((w/2 + 50, y_box + 50), "相較加州表現略差，行政與營運成本可能較高", fill=c_muted, font=get_font(14))
    draw.text((w - 110, y_box + 40), "-$41.89", fill=c_orange, font=get_font(32), anchor="rm")

    # --- SECTION 4: VC RECOMMENDATIONS ---
    y_sec4 = 1100
    h_sec4 = 330
    draw_card(50, y_sec4, w - 50, y_sec4 + h_sec4, "創投機構（VC）核心投資與成本控制建議")
    
    recs = [
        ("1. 研發領先戰略 (R&D-Driven Strategy)", 
         "新創公司的研發支出回報率高達 81% (每投入 $1 產生 $0.81 利潤)。在評估潛在投資標的時，應將公司的「技術研發深度」與「研發預算佔比」視為最重要的核心硬指標。"),
        ("2. 精簡行政與成本控制 (Lean Operations)", 
         "行政管理支出對利潤的邊際貢獻為負值 (-$0.03)。高比例的行政開銷反映出組織冗餘或效率低落。VC 應督促被投企業進行精實管理，避免過多的固定管理費用侵蝕早期利潤。"),
        ("3. 合理配置市場行銷 (Rational Marketing)", 
         "行銷支出邊際貢獻雖為正，但僅為 +$0.03，遠低於研發。這意味著新創企業不應盲目進行「燒錢獲客」的無效行銷，而應在核心產品（研發）具備競爭力後，方可逐步擴大行銷支出。")
    ]
    
    y_rec = y_sec4 + 75
    for title, desc in recs:
        # Draw small tag
        draw.text((80, y_rec), title, fill=c_white, font=get_font(18))
        
        # Wrapping description lines manually
        desc_lines = []
        words = desc
        # Simple character-based wrapping for Chinese
        line_len = 54
        for idx in range(0, len(words), line_len):
            desc_lines.append(words[idx:idx+line_len])
            
        y_desc = y_rec + 25
        for line in desc_lines:
            draw.text((80, y_desc), line, fill=c_muted, font=get_font(14))
            y_desc += 22
        y_rec += 80
        
    # --- FOOTER ---
    draw.text((w/2, h - 30), "數據來源：50 Startups Dataset  •  分析與建模工具：Python scikit-learn & Pillow", fill=c_muted, font=get_font(14), anchor="mm")
    
    # Save the output image
    img.save(output_path, 'PNG')
    print(f"Successfully generated beautiful Chinese infographic at: {output_path}")

if __name__ == "__main__":
    build_infographic()

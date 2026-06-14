# -*- coding: utf-8 -*-
"""generate_pdf.py

讀取 whitepaper_50startups.md 並將其轉換為排版精美的 PDF 說明書檔案（支援繁體中文）。
使用本地標楷體字型 (kaiu.ttf) 進行排版以確保所有中文與符號能正確顯示。
"""

import os
# pyrefly: ignore [missing-import]
import markdown
# pyrefly: ignore [missing-import]
from xhtml2pdf import pisa
# pyrefly: ignore [missing-import]
from xhtml2pdf.files import pisaFileObject

# =========================================================================
# 猴子補丁 (Monkeypatch) xhtml2pdf 的 pisaFileObject.getNamedFile
# 強制其直接回傳解析後的 URI 本地檔案路徑，避開 Windows 下臨時檔案複製與鎖定產生的 PermissionError 錯誤
# =========================================================================
pisaFileObject.getNamedFile = lambda self: self.uri
# =========================================================================

def link_callback(uri, rel):
    """
    資源解析回呼函數。將 HTML/CSS 中的相對路徑轉換為系統中的絕對路徑。
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 移除 URL 參數與錨點
    uri_clean = uri.split('?')[0].split('#')[0]
    
    # 處理 file:/// 前綴
    if uri_clean.startswith("file:///"):
        path = uri_clean.replace("file:///", "")
    elif uri_clean.startswith("file://"):
        path = uri_clean.replace("file://", "")
    else:
        path = uri_clean
        
    # 如果是相對路徑，結合 base_dir
    if not os.path.isabs(path):
        path = os.path.join(base_dir, path)
        
    path = os.path.normpath(path)
    return path

def convert_md_to_pdf():
    # 檔案路徑設定
    base_dir = os.path.dirname(os.path.abspath(__file__))
    md_path = os.path.join(base_dir, "whitepaper_50startups.md")
    pdf_path = os.path.join(base_dir, "whitepaper_50startups.pdf")

    if not os.path.exists(md_path):
        raise FileNotFoundError(f"找不到白皮書 Markdown 檔案: {md_path}")

    # 1. 讀取 Markdown 內容
    with open(md_path, "r", encoding="utf-8") as f:
        md_content = f.read()

    # 2. 轉換為 HTML
    # 使用 tables 和 fenced_code 擴充功能以正確呈現表格與程式碼區塊
    html_content = markdown.markdown(
        md_content,
        extensions=["tables", "fenced_code", "nl2br"]
    )

    # 3. 建立排版樣式與完整 HTML 模板
    # 註冊本地複製的標楷體字型 (kaiu.ttf)
    full_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    @font-face {{
        font-family: 'kaiu';
        src: url('kaiu.ttf');
    }}
    @page {{
        size: a4;
        margin: 2.5cm 2cm 2.5cm 2cm;
    }}
    body {{
        font-family: 'kaiu';
        font-size: 11pt;
        line-height: 1.6;
        color: #2d3748;
    }}
    h1 {{
        font-size: 22pt;
        color: #1a365d;
        text-align: center;
        margin-top: 30px;
        margin-bottom: 20px;
        font-weight: bold;
    }}
    h2 {{
        font-size: 15pt;
        color: #2b6cb0;
        border-bottom: 1px solid #cbd5e0;
        padding-bottom: 6px;
        margin-top: 25px;
        margin-bottom: 15px;
        font-weight: bold;
    }}
    h3 {{
        font-size: 12pt;
        color: #4a5568;
        margin-top: 18px;
        margin-bottom: 10px;
        font-weight: bold;
    }}
    p {{
        margin-bottom: 12px;
        text-align: justify;
    }}
    ul, ol {{
        margin-top: 5px;
        margin-bottom: 12px;
        padding-left: 20px;
    }}
    li {{
        margin-bottom: 6px;
    }}
    table {{
        width: 100%;
        border-collapse: collapse;
        margin-top: 15px;
        margin-bottom: 15px;
    }}
    th, td {{
        border: 1px solid #cbd5e0;
        padding: 8px 10px;
        text-align: left;
        font-size: 10pt;
    }}
    th {{
        background-color: #ebf8ff;
        color: #2b6cb0;
        font-weight: bold;
    }}
    tr:nth-child(even) {{
        background-color: #f7fafc;
    }}
    pre, code {{
        font-family: monospace;
        background-color: #f7fafc;
        border: 1px solid #e2e8f0;
        border-radius: 4px;
        padding: 2px 4px;
        font-size: 9.5pt;
    }}
    pre {{
        padding: 12px;
        display: block;
        margin-top: 12px;
        margin-bottom: 12px;
        white-space: pre-wrap;
    }}
    blockquote {{
        margin: 15px 0;
        padding: 10px 15px;
        background-color: #ebf8ff;
        border-left: 4px solid #3182ce;
        color: #2b6cb0;
    }}
    img {{
        display: block;
        margin: 20px auto;
        width: 450px;
        height: auto;
    }}
    hr {{
        border: 0;
        border-top: 1px solid #e2e8f0;
        margin: 25px 0;
    }}
</style>
</head>
<body>
    {html_content}
</body>
</html>
"""

    # 4. 輸出 PDF 檔案
    print("正在將 HTML 轉換為 PDF...")
    with open(pdf_path, "wb") as pdf_file:
        pisa_status = pisa.CreatePDF(
            full_html.encode("utf-8"),
            dest=pdf_file,
            encoding="utf-8",
            link_callback=link_callback
        )

    if pisa_status.err:
        print("[FAIL] PDF conversion failed!")
    else:
        print(f"[SUCCESS] PDF conversion successful! Output: {pdf_path}")

if __name__ == "__main__":
    convert_md_to_pdf()

#!/usr/bin/env python3
"""
統一所有章節的設置面板CSS樣式（參照第76章標準）
"""
import os
import re

workspace = "/home/openclaw/.openclaw/workspace"
os.chdir(workspace)

# 第76章的標準設置面板CSS
SETTINGS_CSS = """        /* Settings Modal */
        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            display: none;
            justify-content: center;
            align-items: flex-end;
            z-index: 1000;
        }

        .modal-overlay.active {
            display: flex;
        }

        .settings-modal {
            width: 100%;
            max-width: 500px;
            max-height: 85vh;
            background: var(--panel-bg);
            border-radius: 20px 20px 0 0;
            overflow: hidden;
            transform: translateY(100%);
            transition: transform 0.3s ease;
        }

        .modal-overlay.active .settings-modal {
            transform: translateY(0);
        }

        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 16px 20px;
            border-bottom: 1px solid var(--border);
        }

        .modal-header h3 {
            font-size: 1.1rem;
            font-weight: 600;
            color: var(--text);
        }

        .close-btn {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            border: none;
            background: var(--border);
            color: var(--text);
            cursor: pointer;
            font-size: 1.2rem;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .modal-body {
            padding: 20px;
            overflow-y: auto;
            max-height: calc(85vh - 140px);
        }

        .setting-section {
            margin-bottom: 24px;
        }

        .setting-label {
            font-size: 0.9rem;
            font-weight: 500;
            color: var(--text);
            margin-bottom: 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .theme-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 10px;
        }

        .theme-btn {
            aspect-ratio: 1;
            border-radius: 12px;
            border: 2px solid var(--border);
            cursor: pointer;
            position: relative;
            transition: all 0.2s;
        }

        .theme-btn:hover {
            transform: scale(1.05);
        }

        .theme-btn.active {
            border-color: var(--accent);
        }

        .theme-btn.active::after {
            content: '✓';
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: white;
            font-size: 1.2rem;
            text-shadow: 0 1px 3px rgba(0,0,0,0.5);
        }

        .theme-btn.light { background: #FAFBFC; }
        .theme-btn.sepia { background: #F4ECD8; }
        .theme-btn.sky { background: #E8F4FC; }
        .theme-btn.green { background: #E8F5E9; }
        .theme-btn.pink { background: #FCE4EC; }
        .theme-btn.dark { background: #2D3748; }
        .theme-btn.navy { background: #1A202C; }

        .font-size-control {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .font-btn {
            width: 44px;
            height: 44px;
            border-radius: 10px;
            border: 1px solid var(--border);
            background: var(--bg);
            color: var(--text);
            cursor: pointer;
            font-size: 1.1rem;
            font-weight: 600;
            transition: all 0.2s;
        }

        .font-btn:hover {
            background: var(--accent);
            color: white;
            border-color: var(--accent);
        }

        .font-slider {
            flex: 1;
            height: 6px;
            border-radius: 3px;
            background: var(--border);
            -webkit-appearance: none;
            appearance: none;
        }

        .font-slider::-webkit-slider-thumb {
            -webkit-appearance: none;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: var(--accent);
            cursor: pointer;
        }

        .font-preview {
            text-align: center;
            padding: 12px;
            background: var(--bg);
            border-radius: 8px;
            margin-top: 12px;
            font-size: var(--font-size);
        }

        .progress-info {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px;
            background: var(--bg);
            border-radius: 8px;
        }

        .progress-bar {
            flex: 1;
            height: 8px;
            background: var(--border);
            border-radius: 4px;
            margin: 0 16px;
            overflow: hidden;
        }

        .progress-fill {
            height: 100%;
            background: var(--accent);
            border-radius: 4px;
            transition: width 0.3s;
        }

        .modal-footer {
            display: flex;
            gap: 12px;
            padding: 16px 20px;
            border-top: 1px solid var(--border);
        }

        .modal-footer button {
            flex: 1;
            padding: 14px;
            border-radius: 12px;
            font-size: 0.95rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
        }

        .btn-default {
            border: 1px solid var(--border);
            background: var(--bg);
            color: var(--text);
        }

        .btn-default:hover {
            background: var(--border);
        }

        .btn-primary {
            border: none;
            background: #10B981;
            color: white;
        }

        .btn-primary:hover {
            background: #059669;
        }"""

def fix_chapter_settings(chapter_num):
    """修復章節的設置面板CSS"""
    filename = f"chapter-{chapter_num}.html"
    if not os.path.exists(filename):
        return False, "文件不存在"
    
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 檢查是否需要修復
    if "align-items: flex-end" in content and "transform: translateY(100%)" in content:
        return False, "已有正確樣式"
    
    # 方法：找到舊的 .modal-overlay CSS 並替換
    # 找到從 .modal-overlay 開始到某個合理結束點的部分
    
    # 檢查是否有舊的 modal-overlay CSS
    modal_start = content.find('.modal-overlay {')
    if modal_start == -1:
        return False, "找不到 .modal-overlay"
    
    # 找到結束點 - 尋找下一個主要CSS區塊或 </style>
    # 常見的結束點: .nav-btn, .bottom-nav, 或其他主要組件
    
    # 嘗試找到合理的結束點
    end_markers = [
        '.nav-btn {',
        '.bottom-nav {',
        '/* Bottom Navigation */',
        '</style>'
    ]
    
    modal_end = len(content)
    for marker in end_markers:
        pos = content.find(marker, modal_start + 100)
        if pos != -1 and pos < modal_end:
            modal_end = pos
    
    # 替換
    new_content = content[:modal_start] + SETTINGS_CSS + "\n\n        " + content[modal_end:]
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True, "已修復"

# 主程序
print("=" * 60)
print("統一所有章節設置面板CSS（參照第76章標準）")
print("=" * 60)
print()

fixed = 0
skipped = 0
errors = []

for f in sorted(os.listdir('.')):
    if not (f.startswith('chapter-') and f.endswith('.html') and '-av' not in f and 'template' not in f):
        continue
    
    ch = int(f.replace('chapter-', '').replace('.html', ''))
    
    success, msg = fix_chapter_settings(ch)
    
    if success:
        print(f"✅ 第{ch}章: {msg}")
        fixed += 1
    elif msg == "已有正確樣式":
        skipped += 1
    else:
        print(f"❌ 第{ch}章: {msg}")
        errors.append(f"第{ch}章: {msg}")

print()
print("=" * 60)
print(f"修復完成！")
print(f"  - 已修復: {fixed} 個章節")
print(f"  - 跳過（已正確）: {skipped} 個章節")
print(f"  - 錯誤: {len(errors)} 個章節")
print("=" * 60)

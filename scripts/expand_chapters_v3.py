#!/usr/bin/env python3
"""一次性擴充所有短章節到3000+字 (快速批量版)"""
import os, sys, re, time, json
sys.path.append("/home/openclaw/.openclaw/workspace/scripts")
from ai_multimodel import MultiModelAI

OUT = "/home/openclaw/.openclaw/workspace/research"
ai = MultiModelAI()
S = open(f"{OUT}/wangu-chenai-settings.md").read()[:1500]

def cn(t): return sum(1 for c in t if '\u4e00' <= c <= '\u9fff')

def get_title(ch_num):
    """從文件中提取標題"""
    f = f"{OUT}/chapter-{ch_num}.md"
    if os.path.exists(f):
        content = open(f).read()
        m = re.search(r'# 第(\d+)章\s+(.+)', content)
        if m: return m.group(2).strip()
    return ""

def get_summary(ch_num):
    """提取現有內容的前300字作為概要"""
    f = f"{OUT}/chapter-{ch_num}.md"
    if os.path.exists(f):
        content = open(f).read()
        text = re.sub(r'# .+\n', '', content)
        return text[:300]
    return ""

def expand_chapter(ch_num):
    """擴充單一章節到3000+字"""
    title = get_title(ch_num)
    summary = get_summary(ch_num)
    
    if not summary or len(summary) < 50:
        return None
    
    prompt = f'''請擴充《萬古塵埃》第{ch_num}章「{title}」到3000+中文字。

以下是本章現有內容的概要：
{summary}

要求：
1. 輸出完整章節，以「# 第{ch_num}章 {title}」開頭
2. 至少3000中文字（4000字符以上）
3. 保留原有情節框架，在此基礎上增加詳細的場景描寫、對話、心理活動、戰鬥細節
4. 節奏明快，有畫面感
5. 直接輸出正文，無需說明文字'''

    sys_prompt = f'''你是《萬古塵埃》小說作者。{S}

寫作風格：有畫面感、節奏明快、鬥描寫細膩、情感豐富。直接輸出正文。'''

    content = ai.call_deepseek(prompt, sys_prompt, max_tokens=6000)
    if not content:
        content = ai.call_openrouter(prompt, sys_prompt, max_tokens=6000)
    return content

# 找出所有需要擴充的章節（<3000字）
need_expand = []
for i in range(1, 136):
    f = f"{OUT}/chapter-{i}.md"
    if os.path.exists(f):
        chars = cn(open(f).read())
        if chars < 3000:
            need_expand.append((i, chars))

print(f"需要擴充: {len(need_expand)} 章")
avg = sum(c for _, c in need_expand) / len(need_expand)
print(f"平均長度: {avg:.0f} 字")
print()

total_expanded = 0
total_chars_before = sum(c for _, c in need_expand)
total_chars_after = 0

for idx, (ch_num, orig_chars) in enumerate(need_expand):
    print(f"[{idx+1}/{len(need_expand)}] 第{ch_num}章 ({orig_chars}字) -> ", end="", flush=True)
    
    content = expand_chapter(ch_num)
    if content and cn(content) >= 2500:
        path = f"{OUT}/chapter-{ch_num}.md"
        with open(path, "w") as f:
            f.write(content)
        new_chars = cn(content)
        print(f"✅ {new_chars}字 (+{new_chars-orig_chars})")
        total_expanded += 1
        total_chars_after += new_chars
    else:
        print(f"❌ {'API失敗' if not content else f'仍短: {cn(content)}字'}")
        if content:
            total_chars_after += orig_chars  # keep original
        else:
            total_chars_after += orig_chars
    
    # 速率限制
    time.sleep(2)

# 最終統計
print(f"\n{'='*50}")
print(f"完成! 成功擴充 {total_expanded}/{len(need_expand)} 章")
print(f"擴充前總字數: {total_chars_before}")
print(f"擴充後總字數: {total_chars_after} (+{total_chars_after-total_chars_before})")

# 完整統計
good = 0
total = 0
for i in range(1, 136):
    f = f"{OUT}/chapter-{i}.md"
    if os.path.exists(f):
        chars = cn(open(f).read())
        total += chars
        if chars >= 3000: good += 1
print(f"總字數: {total}")
print(f"3000+字章節: {good}/135")

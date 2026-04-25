#!/usr/bin/env python3
"""批量擴充短章 - 5章一批 + 跳過已達標"""
import os, sys, re, time
sys.path.append("/home/openclaw/.openclaw/workspace/scripts")
from ai_multimodel import MultiModelAI

OUT = "/home/openclaw/.openclaw/workspace/research"
ai = MultiModelAI()
S = open(f"{OUT}/wangu-chenai-settings.md").read()[:1500]

def cn(t): return sum(1 for c in t if '\u4e00' <= c <= '\u9fff')

def get_short_chapters():
    """找出所有<3000字的章節"""
    short = []
    for i in range(1, 136):
        f = f"{OUT}/chapter-{i}.md"
        if os.path.exists(f):
            chars = cn(open(f).read())
            if chars < 3000:
                short.append((i, chars, open(f).read()))
    return short

def expand_batch(chapters_batch):
    """擴充一批5章"""
    chapter_info = []
    for ch_num, orig_chars, content in chapters_batch:
        # 提取標題和內容概要
        m1 = re.search(r'# (.+)', content)
        title = m1.group(1).strip() if m1 else f"第{ch_num}章"
        # 取正文前500字
        text = re.sub(r'# .+\n?', '', content)[:500]
        chapter_info.append(f"【第{ch_num}章 {title}】\n現有內容: {text}\n")
    
    prompt = f"""請擴充以下5章《萬古塵埃》內容到每章3000+中文字。

目前故事進展：
第{chapters_batch[0][0]}章之前的故事背景（簡要）：

{' '.join([f'第{c[0]}章' for c in chapters_batch])}

每章現有內容：
{chr(10).join(chapter_info)}

要求：
1. 每章至少3000中文字，用「# 第X章 標題」開頭
2. 用「---」分隔不同章節
3. 保留每章原有情節主線，在此基礎上擴充場景、對話、戰鬥、心理細節
4. 保持故事連貫性
5. 直接輸出，無需說明"""

    sys_prompt = f"""你是《萬古塵埃》小說作者。{S}

寫作風格：有畫面感、節奏明快、描寫細膩。直接輸出正文。"""

    content = ai.call_deepseek(prompt, sys_prompt, max_tokens=12000)
    if not content:
        content = ai.call_openrouter(prompt, sys_prompt, max_tokens=12000)
    return content

def main():
    short_chapters = get_short_chapters()
    print(f"需要擴充: {len(short_chapters)} 章")
    print(f"平均長度: {sum(c for _,c,_ in short_chapters)/len(short_chapters):.0f} 字")
    
    # 分5章一批
    batches = [short_chapters[i:i+5] for i in range(0, len(short_chapters), 5)]
    print(f"分 {len(batches)} 批處理\n")
    
    total_good = 0
    total_before = sum(c for _,c,_ in short_chapters)
    total_after = 0
    
    for idx, batch in enumerate(batches):
        ch_range = f"{batch[0][0]}-{batch[-1][0]}"
        print(f"[{idx+1}/{len(batches)}] 第{ch_range}章...", flush=True)
        
        content = expand_batch(batch)
        if not content:
            print(f"  ❌ API失敗，保留原有")
            for ch_num, orig_chars, _ in batch:
                total_after += orig_chars
            time.sleep(3)
            continue
        
        # 分割並保存
        sections = re.split(r'# 第(\d+)章', content)
        batch_chars = 0
        batch_good = 0
        
        # 構建映射
        ch_nums = [c[0] for c in batch]
        
        for i in range(1, len(sections), 2):
            ch_num = int(sections[i])
            rest = sections[i+1].strip() if i+1 < len(sections) else ""
            if ch_num in ch_nums and rest:
                # 完整構建章節
                full = f"# 第{ch_num}章 {rest}"
                c = cn(full)
                if c >= 2500:
                    path = f"{OUT}/chapter-{ch_num}.md"
                    with open(path, "w") as f:
                        f.write(full)
                    print(f"  ✅ 第{ch_num}章: {c}字")
                    batch_good += 1
                    batch_chars += c
                    total_after += c
                else:
                    # 保持原有
                    print(f"  ⚠️ 第{ch_num}章: {c}字 (仍短，保留原有)")
                    for cn_, oc_, _ in batch:
                        if cn_ == ch_num:
                            batch_chars += oc_
                            total_after += oc_
                            break
            else:
                # 不在batch中或無內容，保持原有
                for cn_, oc_, _ in batch:
                    if cn_ == ch_num:
                        batch_chars += oc_
                        total_after += oc_
                        break
        
        # 處理未匹配的章節（保持原有）
        matched = set()
        for i in range(1, len(sections), 2):
            matched.add(int(sections[i]))
        for ch_num, orig_chars, _ in batch:
            if ch_num not in matched:
                total_after += orig_chars
        
        total_good += batch_good
        time.sleep(3)
    
    # 最終統計
    print(f"\n{'='*50}")
    good_count = 0
    final_total = 0
    for i in range(1, 136):
        f = f"{OUT}/chapter-{i}.md"
        if os.path.exists(f):
            chars = cn(open(f).read())
            final_total += chars
            if chars >= 3000:
                good_count += 1
    
    print(f"✅ 3000+字章節: {good_count}/135")
    print(f"📝 總字數: {final_total}")
    print(f"📈 增長: {final_total - total_before} 字")

if __name__ == "__main__":
    main()

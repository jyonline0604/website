#!/usr/bin/env python3
"""
多模型 AI 調用庫
支持 DeepSeek、MiniMax、OpenRouter、Gemini 等多個模型
實現備用切換機制
"""

import os
import sys
import json
import requests
import time
from typing import Optional, Dict, Any

WORKSPACE = "/home/openclaw/.openclaw/workspace"

class MultiModelAI:
    """多模型 AI 調用類"""
    
    def __init__(self):
        self.workspace = WORKSPACE
        self.load_api_keys()
        
    def load_api_keys(self):
        """加載所有 API 密鑰"""
        self.api_keys = {}
        env_file = os.path.join(self.workspace, ".env")
        
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and '=' in line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        self.api_keys[key] = value
        
        # 檢查關鍵密鑰
        self.has_deepseek = 'DEEPSEEK_API_KEY' in self.api_keys
        self.has_openrouter = 'OPENROUTER_API_KEY' in self.api_keys
        self.has_minimax = 'MINIMAX_API_KEY' in self.api_keys
        self.has_gemini = 'GEMINI_API_KEY' in self.api_keys or 'GOOGLE_API_KEY' in self.api_keys
        
        print(f"[MultiModelAI] 可用 API: DeepSeek={self.has_deepseek}, "
              f"OpenRouter={self.has_openrouter}, MiniMax={self.has_minimax}, "
              f"Gemini={self.has_gemini}")
    
    def call_deepseek(self, prompt: str, system_prompt: str = None, max_tokens: int = 2000) -> Optional[str]:
        """調用 DeepSeek API"""
        if not self.has_deepseek:
            return None
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_keys['DEEPSEEK_API_KEY']}",
                "Content-Type": "application/json"
            }
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            data = {
                "model": "deepseek-chat",
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": 0.7,
                "stream": False
            }
            
            response = requests.post(
                "https://api.deepseek.com/chat/completions",
                headers=headers,
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                print(f"[DeepSeek] API錯誤: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"[DeepSeek] 異常: {str(e)}")
            return None
    
    def call_minimax(self, prompt: str, system_prompt: str = None, max_tokens: int = 2000) -> Optional[str]:
        """調用 MiniMax API (M2.7 模型)"""
        if not self.has_minimax:
            return None
        
        try:
            # MiniMax API 端點
            url = "https://api.minimax.chat/v1/chat/completions"
            
            headers = {
                "Authorization": f"Bearer {self.api_keys['MINIMAX_API_KEY']}",
                "Content-Type": "application/json"
            }
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            data = {
                "model": "MiniMax-M2.7",  # M2.7 模型
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": 0.7,
                "stream": False
            }
            
            response = requests.post(
                url,
                headers=headers,
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                print(f"[MiniMax] API錯誤: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"[MiniMax] 異常: {str(e)}")
            return None
    
    def call_openrouter(self, prompt: str, system_prompt: str = None, max_tokens: int = 2000, model: str = "step-3.5-flash") -> Optional[str]:
        """調用 OpenRouter API"""
        if not self.has_openrouter:
            return None
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_keys['OPENROUTER_API_KEY']}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://openclaw.ai",  # OpenRouter 要求
                "X-Title": "OpenClaw AI Assistant"
            }
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            data = {
                "model": model,  # 可指定模型
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": 0.7,
                "stream": False
            }
            
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                print(f"[OpenRouter] API錯誤: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"[OpenRouter] 異常: {str(e)}")
            return None
    
    def call_gemini(self, prompt: str, system_prompt: str = None, max_tokens: int = 2000) -> Optional[str]:
        """調用 Google Gemini API"""
        # 檢查 laozhang.ai 的 Gemini
        gemini_key = self.api_keys.get('GEMINI_API_KEY') or self.api_keys.get('GOOGLE_API_KEY')
        if not gemini_key:
            return None
        
        try:
            # laozhang.ai 的 Gemini 端點
            url = "https://api.laozhang.ai/v1/chat/completions"
            
            headers = {
                "Authorization": f"Bearer {gemini_key}",
                "Content-Type": "application/json"
            }
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            data = {
                "model": "gemini-3-pro-image-preview",  # laozhang.ai 的 Gemini 模型
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": 0.7,
                "stream": False
            }
            
            response = requests.post(
                url,
                headers=headers,
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                print(f"[Gemini] API錯誤: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"[Gemini] 異常: {str(e)}")
            return None
    
    def generate_with_fallback(self, prompt: str, system_prompt: str = None, max_tokens: int = 2000) -> str:
        """
        使用備用策略生成內容
        順序: DeepSeek → MiniMax → OpenRouter → Gemini → 本地模板
        """
        print(f"[MultiModelAI] 開始生成內容，備用順序: DeepSeek → MiniMax → OpenRouter → Gemini")
        
        # 1. 嘗試 DeepSeek
        if self.has_deepseek:
            print("[MultiModelAI] 嘗試 DeepSeek...")
            result = self.call_deepseek(prompt, system_prompt, max_tokens)
            if result:
                print("[MultiModelAI] DeepSeek 成功")
                return result
        
        # 2. 嘗試 MiniMax (首選備用)
        if self.has_minimax:
            print("[MultiModelAI] DeepSeek 失敗，嘗試 MiniMax...")
            result = self.call_minimax(prompt, system_prompt, max_tokens)
            if result:
                print("[MultiModelAI] MiniMax 成功")
                return result
        
        # 3. 嘗試 OpenRouter step-3.5-flash (次選備用)
        if self.has_openrouter:
            print("[MultiModelAI] MiniMax 失敗，嘗試 OpenRouter step-3.5-flash...")
            result = self.call_openrouter(prompt, system_prompt, max_tokens, model="step-3.5-flash")
            if result:
                print("[MultiModelAI] OpenRouter 成功")
                return result
        
        # 4. 嘗試 Gemini
        if self.has_gemini:
            print("[MultiModelAI] OpenRouter 失敗，嘗試 Gemini...")
            result = self.call_gemini(prompt, system_prompt, max_tokens)
            if result:
                print("[MultiModelAI] Gemini 成功")
                return result
        
        # 5. 所有 API 都失敗，使用本地模板
        print("[MultiModelAI] 所有 API 失敗，使用本地模板")
        return self.generate_local_template(prompt)
    
    def generate_local_template(self, prompt: str) -> str:
        """生成本地模板內容"""
        # 簡單的模板生成
        templates = [
            "（AI生成內容暫時不可用，請稍後再試。）",
            "（系統正在維護中，內容生成功能暫時關閉。）",
            "（網絡連接異常，無法獲取AI生成內容。）",
            "（API服務暫時不可用，請檢查網絡連接。）"
        ]
        
        import random
        return random.choice(templates)
    
    def generate_novel_chapter(self, chapter_num: int, previous_context: str = "", custom_title: str = None) -> Dict[str, Any]:
        """生成小說章節（使用多模型備用）"""
        # 生成標題
        if custom_title:
            chapter_title = custom_title
        else:
            import random
            titles = ["虛空試煉", "時空裂縫", "能量風暴", "系統升級", "遠古密碼",
                     "靈芯共鳴", "科技突破", "修真奇遇", "意識融合", "維度跨越"]
            chapter_title = random.choice(titles)
        
        # 構建提示詞
        prompt = f"""請創作小說《科技修真傳》的第{chapter_num}章，標題為「{chapter_title}」。

故事設定：
- 主角：林塵，擁有神秘的靈芯系統（科技與修真結合的產物）
- 世界觀：未來世界，科技高度發達，但修真文明重新覺醒
- 風格：東方玄幻 + 硬核科幻 + 賽博朋克元素

前一章內容摘要：
{previous_context if previous_context else "這是故事的開始。"}

創作要求：
1. 標題：第{chapter_num}章：{chapter_title}
2. 字數：1000-1500字
3. 內容：必須有完整的劇情推進
4. 直接從「第{chapter_num}章：{chapter_title}」開始寫正文

請創作完整的一章，確保內容豐富、情節緊湊。直接輸出小說正文，不要添加任何解釋或說明。"""
        
        system_prompt = "你是一位專業的網絡小說作家，擅長創作科技修真題材的小說。請直接輸出小說正文，不要添加任何解釋、說明或額外文字。"
        
        # 使用多模型生成
        content = self.generate_with_fallback(prompt, system_prompt, max_tokens=3000)
        
        return {
            "chapter_num": chapter_num,
            "chapter_title": chapter_title,
            "content": content,
            "success": content and not content.startswith("（AI生成內容暫時不可用")
        }


def test_multimodel():
    """測試多模型功能"""
    ai = MultiModelAI()
    
    print("\n" + "="*60)
    print("測試多模型 AI 調用")
    print("="*60)
    
    # 測試提示詞
    test_prompt = "請用中文寫一段關於科技修真的簡短段落，約100字。"
    
    print(f"\n提示詞: {test_prompt}")
    print("\n開始測試備用策略...")
    
    result = ai.generate_with_fallback(test_prompt, max_tokens=500)
    
    print("\n" + "="*60)
    print("生成結果:")
    print("="*60)
    print(result)
    
    return ai


if __name__ == "__main__":
    test_multimodel()
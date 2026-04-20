#!/usr/bin/env python3
"""
更新圖片分析模型配置，嘗試使用DeepSeek的圖片分析模型
"""

import json
import os

def update_config():
    config_file = '/home/openclaw/.openclaw/openclaw.json'
    
    if not os.path.exists(config_file):
        print(f"錯誤: 配置文件不存在: {config_file}")
        return False
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print("更新圖片分析模型配置...")
        
        # 確保agents.defaults存在
        if 'agents' not in config:
            config['agents'] = {}
        if 'defaults' not in config['agents']:
            config['agents']['defaults'] = {}
        
        defaults = config['agents']['defaults']
        
        # 嘗試不同的圖片分析模型方案
        # 方案1: 使用DeepSeek的圖片分析模型（如果支持）
        # 方案2: 使用OpenRouter上的圖片分析模型
        # 方案3: 使用MiniMax的其他模型
        
        # 根據錯誤信息和可用API key，嘗試以下模型：
        # 1. deepseek-chat/deepseek-chat (可能支持圖片)
        # 2. 通過OpenRouter訪問其他圖片模型
        # 3. 嘗試minimax的其他模型
        
        # 先移除有問題的配置
        if 'imageModel' in defaults:
            print(f"移除舊配置: {defaults['imageModel']}")
        
        # 設置新的圖片分析模型配置
        # 嘗試使用deepseek-chat，它可能支持圖片分析
        defaults['imageModel'] = {
            'primary': 'deepseek-chat/deepseek-chat',
            'fallbacks': [
                'minimax/MiniMax-M2.7',  # MiniMax的文本模型，可能也支持圖片
                'openrouter/stepfun/step-3.5-flash:free'  # OpenRouter上的免費模型
            ]
        }
        
        # 同時更新圖片生成模型配置，避免使用有問題的模型
        if 'imageGenerationModel' in defaults:
            print(f"當前圖片生成模型: {defaults['imageGenerationModel']}")
            # 保持不變，因為圖片生成可能還能工作
        
        # 保存配置
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print("\n✅ 配置已更新")
        print("新的 imageModel 配置:")
        print(json.dumps(defaults['imageModel'], indent=2, ensure_ascii=False))
        
        # 創建測試配置
        test_config = {
            '測試的圖片分析模型': [
                'primary: deepseek-chat/deepseek-chat',
                'fallback1: minimax/MiniMax-M2.7',
                'fallback2: openrouter/stepfun/step-3.5-flash:free'
            ],
            '注意事項': [
                '1. DeepSeek可能支持圖片分析，但需要確認',
                '2. 如果失敗，會嘗試fallback模型',
                '3. 可能需要重啟OpenClaw服務'
            ]
        }
        
        print("\n測試配置:")
        for key, value in test_config.items():
            print(f"{key}:")
            for item in value:
                print(f"  - {item}")
        
        return True
        
    except Exception as e:
        print(f"錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=== 更新圖片分析模型配置 ===")
    
    if update_config():
        print("\n🎯 配置更新完成!")
        print("\n下一步:")
        print("1. 需要重啟OpenClaw服務或重新加載配置")
        print("2. 測試圖片分析功能是否正常工作")
        print("3. 如果仍有問題，可能需要:")
        print("   - 確認DeepSeek是否支持圖片分析")
        print("   - 嘗試其他圖片分析模型")
        print("   - 檢查API key權限")
    else:
        print("\n❌ 配置更新失敗")
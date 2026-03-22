import os
import time
import requests
import json
import subprocess
import re

API_KEY = os.environ.get('GEMINI_API_KEY')
# Using Gemini 2.0 Flash for better reliability and quota
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"

SOURCE_DIR = 'Myst,Might,Mayhem'
TARGET_DIR = '怪力亂神'

PROMPT_PREFIX = """
Translate the following chapter into traditional Chinese.
Use a dramatic, concise martial arts novel style (similar to traditional Chinese translations of Korean Wuxia novels).
Output ONLY the translated content, no introduction or conclusion.
Maintain the following terminology:
- 木景雲 (Mok Gyeong-un)
- 大然木劍庄 (Yeon Mok Sword Manor / Mok Sword Manor)
- 大然少主 (Young Master of Yeon Mok Sword Manor)
- 石夫人 (Lady Seok)
- 二少爺 (Second Young Master)
- 虛空 (Void)
- 死之氣 (Breath of Death)
- 紅線/血線 (red thread)
- 天地會 (Heaven & Earth Society)
- 內城 (inner castle)
- 魔僧 (Demonic Monk)
- 九余 (Guyeo)
- 屍血谷 (Corpse Blood Valley)
- 屍血谷主 / 李地炎 (Lee Ji-yeom)
- 影王 (Shadow King)
- 影族/影宗 (Shadow Clan)
- 朱殺洞 (Vermillion Slaughter Cave)
- 廉家 (Yeom Ga)
- 化境 (Transformation Realm)
- 秘寶庫 (Treasure Vault)
- 魏少延 (Wi So-yeon)
- 明刃王孫允 (Bright Blade King Son Yun)
- 太殺閣 (Primal Killing Pavilion)
- 趙義公 (Jo Ui-gong)

Chapter Content:
"""

def translate_text(text):
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{"parts": [{"text": PROMPT_PREFIX + text}]}],
        "generationConfig": {
            "temperature": 0.3,
            "topP": 0.8,
            "topK": 40
        }
    }
    try:
        response = requests.post(API_URL, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            try:
                return result['candidates'][0]['content']['parts'][0]['text']
            except (KeyError, IndexError):
                print("Error parsing response:", json.dumps(result, indent=2))
                return None
        elif response.status_code == 429:
            print("Gemini Rate limit reached (429). Sleeping for 60 seconds...")
            time.sleep(60)
            return None
        else:
            print(f"Gemini API Error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"Request exception: {e}")
        return None

def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split('([0-9]+)', s)]

def process_chapters():
    if not os.path.exists(TARGET_DIR):
        os.makedirs(TARGET_DIR)
        
    source_files = sorted([f for f in os.listdir(SOURCE_DIR) if f.endswith('.txt')], key=natural_sort_key)
    
    new_files_processed = 0
    
    for filename in source_files:
        target_path = os.path.join(TARGET_DIR, filename)
        
        # Only translate if it doesn't exist
        if not os.path.exists(target_path):
            source_path = os.path.join(SOURCE_DIR, filename)
            print(f"Translating {filename} using Gemini 2.0 Flash...")
            
            with open(source_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            translation = translate_text(content)
            
            if translation and len(translation.strip()) > 0:
                with open(target_path, 'w', encoding='utf-8') as f:
                    f.write(translation)
                print(f"Saved translation to {target_path}")
                
                # Commit and push
                subprocess.run(['git', 'add', target_path])
                subprocess.run(['git', 'commit', '-m', f'Add translated {filename} (Gemini 2.0)'])
                subprocess.run(['git', 'push', 'origin', 'main'])
                
                new_files_processed += 1
                time.sleep(4) # Rate limiting for Gemini 2.0 Flash (usually higher, but let's be safe)
            else:
                print(f"Failed to translate {filename}. Stopping batch.")
                break
                
    return new_files_processed

if __name__ == "__main__":
    print("Starting translation watcher (Gemini 2.0 Flash)...")
    while True:
        try:
            processed = process_chapters()
            if processed > 0:
                print(f"Processed {processed} chapters.")
        except Exception as e:
            print(f"Error occurred: {e}")
        time.sleep(30)

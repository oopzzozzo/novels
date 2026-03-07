import os
import time
import subprocess
import re
import json

SOURCE_DIR = 'Myst,Might,Mayhem'
TARGET_DIR = '怪力亂神'
INDEX_FILE = 'chapters.json'

PROMPT_PREFIX = """
Translate the following chapter into traditional Chinese.
Use a dramatic, concise martial arts novel style (similar to traditional Chinese translations of Korean Wuxia novels).
Output ONLY the translated content, no introduction or conclusion.
Maintain the following terminology:
- 木景雲 (Mok Gyeong-un)
- 然木劍庄 (Yeon Mok Sword Manor / Mok Sword Manor)
- 大然少主 (Young Master of Yeon Mok Sword Manor)
- 石夫人 (Lady Seok)
- 二少爺 (Second Young Master)
- 虛空 (Void)
- 死氣 (Breath of Death)
- 犰狳 (Guyeo)
- 天地會 (Heaven & Earth Society)
- 內城 (inner castle)
- 魔僧 (Demonic Monk)
- 屍血谷 (Corpse Blood Valley)
- 屍血谷主 / 李地炎 (Lee Ji-yeom)
- 影王 (Shadow King)
- 影族/影宗 (Shadow Clan)
- 朱殺洞 (Vermillion Slaughter Cave)
- 廉家 (Yeom Ga)
- 化境 (Transformation Realm)
- 秘寶庫 (Treasure Vault)
- 魏昭妍 (Wi So-yeon)
- 明刃王孫允 (Bright Blade King Son Yun)
- 原殺閣 (Primal Killing Pavilion)
- 趙義公 (Jo Ui-gong)

Chapter Content:
"""

def update_index():
    files = sorted([f for f in os.listdir(TARGET_DIR) if f.endswith('.txt')], key=natural_sort_key)
    with open(os.path.join(TARGET_DIR, INDEX_FILE), 'w', encoding='utf-8') as f:
        json.dump(files, f, ensure_ascii=False, indent=2)
    print(f"Updated {INDEX_FILE}")

def translate_text(text):
    prompt = PROMPT_PREFIX + text
    try:
        process = subprocess.Popen(
            ['claude', '-p'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate(input=prompt)
        
        if process.returncode == 0:
            result = stdout.strip()
            if result.startswith("```") and result.endswith("```"):
                result = re.sub(r'^```[^\n]*\n', '', result)
                result = re.sub(r'\n```$', '', result)
            return result
        else:
            print(f"Claude Error: {stderr}")
            return None
    except Exception as e:
        print(f"Subprocess exception: {e}")
        return None

def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split('([0-9]+)', s)]

def process_new_chapters():
    if not os.path.exists(TARGET_DIR):
        os.makedirs(TARGET_DIR)
        
    source_files = sorted([f for f in os.listdir(SOURCE_DIR) if f.endswith('.txt')], key=natural_sort_key)
    
    new_files_translated = 0
    
    for filename in source_files:
        # Check if the renamed version exists (this is tricky because we renamed them)
        # For simplicity, we check if ANY file starting with 第NNN話 exists
        match = re.search(r'^(\d+)_', filename)
        if match:
            idx = match.group(1).zfill(3)
            exists = any(f.startswith(f"第{idx}話") for f in os.listdir(TARGET_DIR))
            if exists:
                continue

        source_path = os.path.join(SOURCE_DIR, filename)
        print(f"Translating new chapter: {filename} using Claude...")
        
        with open(source_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        translation = translate_text(content)
        
        if translation and len(translation.strip()) > 0:
            # We'll use a temporary name and let rename script handle it, 
            # or just generate the correct name here.
            # Let's generate the correct name.
            first_line = translation.split('\n')[0].strip()
            name_match = re.search(r'第(\d+)章[：\s]*(.*)', first_line)
            if name_match:
                chap_num = name_match.group(1).zfill(3)
                title = re.sub(r'[*#_]', '', name_match.group(2)).strip()
                target_filename = f"第{chap_num}話. {title}.txt"
            else:
                target_filename = filename # Fallback
                
            target_path = os.path.join(TARGET_DIR, target_filename)
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(translation)
            print(f"Saved translation to {target_path}")
            
            subprocess.run(['git', 'add', target_path])
            subprocess.run(['git', 'commit', '-m', f'Add translated {target_filename} (Claude)'])
            subprocess.run(['git', 'push', 'origin', 'main'])
            
            new_files_translated += 1
            update_index()
            time.sleep(2) 
        else:
            print(f"Failed to translate {filename}. Stopping batch.")
            break
                
    return new_files_translated

if __name__ == "__main__":
    print("Starting translation watcher (Claude Code - Reader Support)...")
    # Initial index update
    if os.path.exists(TARGET_DIR):
        update_index()
        
    while True:
        try:
            processed = process_new_chapters()
            if processed > 0:
                print(f"Processed {processed} new chapters.")
        except Exception as e:
            print(f"Error occurred: {e}")
        time.sleep(30)

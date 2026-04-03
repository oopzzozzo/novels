import asyncio
import json
import websockets
import requests
import time
import os
import sys

def log(msg):
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] {msg}", flush=True)

def sanitize(name):
    return name.replace(':', '_').replace('/', '_')

def get_ws_url():
    pages = requests.get('http://localhost:9222/json').json()
    target = next((p for p in pages if p.get('type') == 'page'), None)
    if not target:
        raise RuntimeError("No page target found in Chrome on port 9222")
    return target['webSocketDebuggerUrl']

async def call_cdp(ws, method, params=None):
    call_id = int(time.time() * 1000000) % 2**31
    await ws.send(json.dumps({'id': call_id, 'method': method, 'params': params or {}}))
    async for message in ws:
        resp = json.loads(message)
        if resp.get('id') == call_id:
            return resp.get('result', {})

EXTRACT_JS = """
(() => {
    const text = document.body.innerText;
    // Find breadcrumb "Myst,Might,Mayhem / Chapter..."
    const bcIdx = text.indexOf('Myst,Might,Mayhem / ');
    if (bcIdx === -1) return '';
    const afterBc = text.substring(bcIdx);
    const bcEnd = afterBc.indexOf('\\n');
    let content = afterBc.substring(bcEnd + 1).trim();
    // Skip header lines (ORIGINAL, Author, copyright) until chapter title "Chapter N:"
    const lines = content.split('\\n');
    let chTitleLine = -1;
    for (let i = 0; i < Math.min(lines.length, 15); i++) {
        if (/^Chapter \\d+:/.test(lines[i].trim())) { chTitleLine = i; break; }
    }
    if (chTitleLine >= 0) {
        content = lines.slice(chTitleLine + 1).join('\\n');
    }
    // Cut off footer
    const cut = content.search(/\\nCOMMENT\\n|\\nReport chapter/);
    if (cut > 0) content = content.substring(0, cut);
    // Clean whitespace artifacts
    content = content.replace(/\\u00a0/g, '').replace(/\\n \\n/g, '\\n').trim();
    return content;
})()
"""

async def crawl():
    log("=== Crawler Started ===")

    os.makedirs('Myst,Might,Mayhem', exist_ok=True)

    chapters = []
    with open('all_chapters.txt', 'r') as f:
        for line in f:
            parts = line.strip().split('|')
            if len(parts) == 3:
                chapters.append((int(parts[0]), parts[1], parts[2]))
    log(f"Loaded {len(chapters)} chapters.")

    ws_url = get_ws_url()
    log(f"Connecting to Chrome: {ws_url}")

    async with websockets.connect(ws_url, max_size=20*1024*1024) as ws:
        log("Connected.")

        for idx, ch_id, ch_name in chapters:
            filename = f'Myst,Might,Mayhem/{idx+1:03d}_{sanitize(ch_name)}.txt'

            # Skip if already crawled (real content, not just metadata)
            if os.path.exists(filename) and os.path.getsize(filename) > 500:
                log(f"Skip [{idx+1}/311] {ch_name}")
                continue

            url = f'https://www.webnovel.com/book/32821474008195805/{ch_id}'
            log(f"[{idx+1}/311] {ch_name} ...")

            # Navigate
            await call_cdp(ws, 'Page.navigate', {'url': url})

            # Wait for content to appear (up to ~40s)
            content = ''
            for attempt in range(10):
                await asyncio.sleep(4)
                res = await call_cdp(ws, 'Runtime.evaluate', {'expression': EXTRACT_JS})
                text = (res.get('result', {}).get('value') or '')
                if len(text) > 500:
                    content = text
                    break
                log(f"  attempt {attempt+1}: {len(text)} chars")

            if content:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"{ch_name}\n\n{content}")
                log(f"  SAVED {filename} ({len(content)} chars)")
            else:
                log(f"  FAILED {ch_name}")

            await asyncio.sleep(2)

    log("=== Done ===")

if __name__ == "__main__":
    asyncio.run(crawl())

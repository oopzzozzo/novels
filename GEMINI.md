# Crawling New Chapters for "Myst, Might, Mayhem"

This project uses the Gemini CLI browser tools to extract chapter content from Webnovel. To bypass persistent security challenges (CAPTCHAs/Turnstile), a manual session establishment is required.

## How to Find the Chapter ID

To crawl a new chapter, you first need its unique `chapter-id`:
- **Desktop URL:** `https://www.webnovel.com/book/32821474008195805/<CHAPTER_ID>`
- **Catalog:** Check `https://www.webnovel.com/book/myst-might-mayhem_32821474008195805/catalog`

## Procedure for New Chapters

Follow these steps exactly to ensure a successful crawl:

### 1. Launch Interactive Session
Launch the browser in non-headless mode.
```javascript
browser_launch(headless=False)
```

### 2. Manual Login & Verification
Navigate to the Webnovel home page and perform any required manual actions in the browser window:
1. Navigate: `browser_navigate(url="https://www.webnovel.com/")`
2. **User Action:** Manually solve any CAPTCHAs or "Verify you are human" challenges.
3. **User Action:** Manually log in to your Webnovel account. This establishes the necessary cookies and session headers.

### 3. Navigate to Target Chapter
Once logged in, navigate to the specific chapter:
```javascript
browser_navigate(url="https://www.webnovel.com/book/32821474008195805/<CHAPTER_ID>")
```
**Wait Time:** Allow 10-15 seconds for the content to fully render.

### 4. Content Extraction
Target the main content container.
- **Primary Selector:** `div[class*="content"]`
- **Secondary Selector:** `div.cha-words`

```javascript
browser_find(selector="div[class*='content']")
```

### 5. Saving and Cleanup
Save the extracted text to the `Myst,Might,Mayhem/` directory using the `NNN_Chapter Name.txt` format. Ensure UI elements and bot-detection markers are removed.

## Troubleshooting
- **Session Timeout:** If extraction fails, return to the home page or catalog to refresh the session.
- **Lazy Loading:** If the text is incomplete, use `browser_click` on the navigation footer to trigger a scroll event before extraction.

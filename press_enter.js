const { chromium } = require('playwright');
(async () => {
    const browser = await chromium.launch();
    const page = await browser.newPage();
    await page.goto('https://www.google.com');
    await page.type('[name="q"]', 'Myst, Might & Mayhem read online');
    await page.keyboard.press('Enter');
    await page.waitForTimeout(5000);
    const links = await page.evaluate(() => {
        return Array.from(document.querySelectorAll('a')).map(a => ({
            text: a.innerText.trim(),
            href: a.href
        }));
    });
    console.log(JSON.stringify(links, null, 2));
    await browser.close();
})();

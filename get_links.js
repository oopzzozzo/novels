const { chromium } = require('playwright');
(async () => {
    const browser = await chromium.launch();
    const page = await browser.newPage();
    await page.goto('https://m.webnovel.com/book/myst-might-mayhem_32821474008195805');
    const links = await page.evaluate(() => {
        return Array.from(document.querySelectorAll('a')).map(a => ({
            text: a.innerText.trim(),
            href: a.href
        }));
    });
    console.log(JSON.stringify(links, null, 2));
    await browser.close();
})();

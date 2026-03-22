const puppeteer = require('puppeteer');
(async () => {
    try {
        const browser = await puppeteer.launch();
        const page = await browser.newPage();
        await page.goto('https://m.webnovel.com/book/myst-might-mayhem_32821474008195805');
        const content = await page.content();
        process.stdout.write(content);
        await browser.close();
    } catch (err) {
        process.stderr.write(err.message);
        process.exit(1);
    }
})();

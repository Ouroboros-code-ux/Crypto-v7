const { chromium } = require('playwright');
const path = require('path');

(async () => {
    // We launch chromium. We must allow file:// access if we are testing locally without a server,
    // but the graph fetches data from http://127.0.0.1:8001/graph, so it's better to just open the file.
    const browser = await chromium.launch({ headless: true });
    
    const page = await browser.newPage();
    
    // Listen for console events
    page.on('console', msg => console.log(`[Browser Console]: ${msg.text()}`));
    page.on('pageerror', error => console.error(`[Browser Error]: ${error.message}`));
    
    const fileUrl = 'file:///' + path.resolve(__dirname, 'index.html').replace(/\\/g, '/');
    console.log("Loading page: " + fileUrl);
    
    await page.goto(fileUrl, { waitUntil: 'networkidle' });
    
    // Click the START SCAN button for demo data
    await page.fill('#walletInput', '0x742d35Cc6634C0532925a3b844Bc454e4438f44e');
    await page.click('.scan-btn');
    
    console.log("Waiting for scan to finish...");
    // Wait for the risk result to show up
    await page.waitForSelector('#chartScore', { timeout: 10000 });
    
    console.log("Scan finished. Clicking LOAD GRAPH button...");
    // The VISUAL GRAPH button is the 3rd one in the action row
    await page.evaluate(() => {
        const btns = document.querySelectorAll('.secondary-btn');
        for (let b of btns) {
            if (b.innerText.includes('VISUAL GRAPH')) {
                b.click();
                return;
            }
        }
    });
    
    console.log("Waiting for graph to load...");
    
    // Wait for a few seconds to let Cytoscape animation or loading happen
    await page.waitForTimeout(3000);
    
    // Take a screenshot to verify what it actually looks like
    await page.screenshot({ path: 'graph_test.png', fullPage: true });
    
    console.log("Graph screenshot saved to graph_test.png");
    
    await browser.close();
})();

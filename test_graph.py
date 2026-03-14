from playwright.sync_api import sync_playwright
import os

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    def handle_console(msg):
        print(f"[Browser Console]: {msg.text}")
    
    def handle_error(err):
        print(f"[Browser Error]: {err}")
        
    page.on("console", handle_console)
    page.on("pageerror", handle_error)
    
    file_path = f"file:///{os.path.abspath('index.html').replace(chr(92), '/')}"
    print(f"Loading {file_path}")
    
    page.goto(file_path, wait_until="networkidle")
    
    # Fill in address and scan
    page.fill("#walletInput", "0x742d35Cc6634C0532925a3b844Bc454e4438f44e")
    page.click(".scan-btn")
    
    print("Waiting for scan result...")
    page.wait_for_selector("#chartScore", timeout=10000)
    
    print("Clicking visual graph...")
    # Click VISUAL GRAPH button
    page.evaluate('''() => {
        const btns = document.querySelectorAll('.secondary-btn');
        for (let b of btns) {
            if (b.innerText.includes('VISUAL GRAPH')) {
                b.click();
                return;
            }
        }
    }''')
    
    print("Waiting 3 seconds for load...")
    page.wait_for_timeout(3000)
    
    page.screenshot(path="graph_test_py.png", full_page=True)
    print("Saved screenshot to graph_test_py.png")
    
    browser.close()

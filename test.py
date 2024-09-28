from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as playwright:
        
        chromium = playwright.chromium 

        browser = chromium.launch(headless=False)
        page = browser.new_page()

        page.goto("https://linxonline.co.pierce.wa.us")
        input("Log in now...")
        page.goto("https://linxonline.co.pierce.wa.us/linxweb/Case/CaseFiling/documentSelect.cfm?cn=17-2-04302-3")



        page.locator('a:text("select all")').click()
        print("select all")

        page.locator("input[name='btnDownload']").click()
        print("Found download?")

        input("Satisfied?")
        browser.close()

if __name__ == "__main__":
    run()
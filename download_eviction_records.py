from playwright.sync_api import sync_playwright
import pandas as pd
import os

def run(case_numbers: list[str]):

    with sync_playwright() as playwright:
        
        chromium = playwright.chromium 

        browser = chromium.launch(headless=False)
        page = browser.new_page()

        scraped_cases = os.listdir("./Records/")
        scraped_cases = [ s.replace(".zip", "") for s in scraped_cases ]

        page.goto("https://linxonline.co.pierce.wa.us")
        input("Log in now...")

        for c in case_numbers:

            if c in scraped_cases:
                pass
            else:
                page.goto("https://linxonline.co.pierce.wa.us/linxweb/Case/CaseFiling/documentSelect.cfm?cn=" + c)

                page.locator('a:text("select all")').click()
                print("Case Number: " + c)

                # Start waiting for the download
                with page.expect_download() as download_info:
                    # Perform the action that initiates download
                    page.locator("input[name='btnDownload']").click(timeout=240000)
                download = download_info.value

                # Wait for the download process to complete and save the downloaded file somewhere
                download.save_as("./Records/" + c + ".zip")

        browser.close()

if __name__ == "__main__":

    df = pd.read_csv("CaseNumber.csv")

    run(df["CaseNumber"].to_list())
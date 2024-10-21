import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import os
import time
import logging

LOG_FILENAME = 'timeout.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)

async def run(case_numbers: list[str]):

    async with async_playwright() as playwright:
        
        chromium = playwright.chromium 

        browser = await chromium.launch(headless=False, timeout=0)
        page = await browser.new_page()

        scraped_cases = os.listdir("./Records/")
        scraped_cases = [ s.replace(".zip", "") for s in scraped_cases ]

        await page.goto("https://linxonline.co.pierce.wa.us")
        input("Log in now...")

        for c in case_numbers:

            if c in scraped_cases:
                pass
            else:
                await page.goto("https://linxonline.co.pierce.wa.us/linxweb/Case/CaseFiling/documentSelect.cfm?cn=" + c)

                await page.locator('a:text("select all")').click()
                print("Case Number: " + c)

                try:
                    # Start waiting for the download
                    async with page.expect_download(timeout=0) as download_info:
                        # Perform the action that initiates download
                        await page.locator("input[name='btnDownload']").click(timeout=0)

                    download = await download_info.value
                    print("Saved!")
                    # Wait for the download process to complete and save the downloaded file somewhere
                    await download.save_as("./Records/" + c + ".zip")
                
                except:
                    
                    print("Timeout")
                    logging.debug(c)
                
        await browser.close()

async def main():

    df = pd.read_csv("CaseNumber.csv")

    scraped_cases = os.listdir("./Records/")
    scraped_cases = [ s.replace(".zip", "") for s in scraped_cases ]

    cases_left = [c for c in df["CaseNumber"].to_list() if c not in scraped_cases]

    print("We have ", len(cases_left), " left!") 

    await run(cases_left)

asyncio.run(main())

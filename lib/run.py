import random
import time
from lib.utils import human_type
from playwright.async_api import (
    BrowserContext,
    Page,
    ElementHandle,
    Frame,
    Locator
)
import asyncio
from typing import List
import json

async def get_palantir_job_data(context : BrowserContext) -> List[str]:
    
    job_interest_categories = ["New Graduates", "Internships", "US Government", "International Government", "Product Development", "Information Security", "Mission Operations", "Production Infrastructure", "Reliability & Operations", "Technical Operations"]
    page : Page = await context.new_page()
    await page.goto("https://www.palantir.com/careers/")
    await page.wait_for_load_state(state="domcontentloaded")
    await page.wait_for_timeout(5000)
    print("The page has been successfully loaded!")

    header_locators : List[Locator] = await page.locator('h2').all()
    found_jobs = []

    for header in header_locators:
        header_text = await header.inner_text()
        if header_text in job_interest_categories:
            # Careful with this
            # TODO - Implement a better approach than grabbing the parent element
            parent_container = header.locator('..')
            buttons = await parent_container.locator('button').all()

            # Get the parent container of each button
            # job = {
            #     "job" : "job text",
            #     "links" : [{
            #         "location" : "location",
            #         "link" : "link",
            #     },
            #     ...
            #     ]
            # }
            for button in buttons:
                parent_of_button = button.locator('..')

                job = {}
                job['job'] = await button.inner_text()
                links = await parent_of_button.locator('a').all()
                job['links'] = [""] * len(links)
                for i,link in enumerate(links):
                    link_text = await link.text_content()
                    link_hrefs = await link.get_attribute('href')
                    job['links'][i] = {
                        "location" : link_text,
                        "link" : link_hrefs,
                    }
                found_jobs.append(job)
    with open("jobs.json", "w", encoding="utf-8") as f:
        json.dump(found_jobs, f, indent=4, ensure_ascii=False)

async def run(context : BrowserContext):

        
    await get_palantir_job_data(context)

    await asyncio.sleep(30000)
    await context.close()


import random
import time

from playwright.async_api import (
    BrowserContext,
    Page,
    ElementHandle,
    Frame,
    Locator
)
import asyncio
from typing import List, Dict, Union
import json

from .models import JobInfo, Link
from .database import JobDatabase
from .start_camoufox import startCamoufox
from .logger import logger

async def get_palantir_job_data(context : BrowserContext) -> List[JobInfo]:
    
    company_name = "Palantir"
    job_interest_categories = ["New Graduates", "Internships", "US Government", "International Government", "Product Development", "Information Security", "Mission Operations", "Production Infrastructure", "Reliability & Operations", "Technical Operations"]
    page : Page = await context.new_page()
    await page.goto("https://www.palantir.com/careers/")
    await page.wait_for_load_state(state="domcontentloaded")
    await page.wait_for_timeout(5000)

    header_locators : List[Locator] = await page.locator("h2:visible").all()
    found_jobs = []
    job_names = set()
    # Loop over headers that contain all jobs of interest
    for header in header_locators:
        header_text = await header.inner_text()
        if header_text in job_interest_categories:
            # Careful with this
            # TODO - Implement a better approach than grabbing the parent element
            # TODO - Possible solution - Grab all buttons on the page that have links to there job site nested in them and sort the jobs out we don't wait
            parent_container = header.locator('..')
            buttons = await parent_container.locator('button').all()

            for button in buttons:
                parent_of_button = button.locator('..')

                job_name_text = await button.inner_text()
                # Sometime there is duplicate jobs, I have no idea why
                if job_name_text in job_names:
                    continue

                job_names.add(job_name_text)
                links = await parent_of_button.locator('a').all()
                
                # Easy place to store additional data when the time comes
                job_info = JobInfo(
                    company = company_name,
                    job_name = job_name_text[:-2].strip(),
                    links = []
                )

                for link in links:
                    link_text = await link.text_content()
                    clean_location = link_text.replace("↳", "").strip() if link_text else ""
                    link_hrefs = await link.get_attribute('href')
                    link = Link(
                        location = clean_location,
                        link = link_hrefs
                    )
                    job_info.links.append(link)

                found_jobs.append(job_info)
    
    return found_jobs

async def run_palantir_scrape(context : BrowserContext):
    db = JobDatabase()
    try:

        job_data = await get_palantir_job_data(context)
        await db.init_db()
        summary = await db.add_or_update_job_list(job_data)
        return summary
    except Exception as e:
        logger.error(f"Scraper error: {e}", exc_info=True)
    finally:
        # Close database connection safely
        await db.close()
import os
import sys
import asyncio
from contextlib import asynccontextmanager
from playwright.async_api import async_playwright

@asynccontextmanager
async def start_persistent_browser():
    user_data_dir = 'context'
    
    # Ensure the user data directory exists for persistence
    if not os.path.exists(user_data_dir):
        try:
            os.makedirs(user_data_dir, exist_ok=True)
            print(f"Created persistent browser context directory: {user_data_dir}")
        except OSError as e:
            print(f"Error creating directory {user_data_dir}: {e}", file=sys.stderr)

    # Launch Playwright and the persistent Firefox context
    async with async_playwright() as p:
        try:
            browser_context = await p.firefox.launch_persistent_context(
                user_data_dir,
                headless=True, 
            )
            
            # Set a common user agent for consistency
            await browser_context.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0"
            })

            print("Playwright browser context launched successfully.")
            yield browser_context

        except Exception as e:
            print(f"ERROR: Failed to launch Playwright browser: {e}", file=sys.stderr)
            yield None
            
        finally:
            if 'browser_context' in locals():
                print("Closing Playwright browser context.")
                await browser_context.close()
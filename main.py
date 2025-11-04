from camoufox.async_api import AsyncCamoufox
import asyncio

from lib.run import run

async def main():
    async with AsyncCamoufox(
        # Don't delete data between runs
        persistent_context=True,
        # Stores user data in local folder
        user_data_dir='context/',
        # Randomizes mouse cursor movements
        humanize=True,
        # Opens window for control
        headless=False,
        # Allow browser to store data in cache to make look less automated
        enable_cache=True,
        # Contrain the screen so I can see buttons and inputs, doesn't really work anyways

        # window=(1920, 1080),
        # Keep device and user agent settings the same so linkedin doesnt log me out
        os="windows",
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0",
    ) as context:
         await run(context)
        

asyncio.run(main())        


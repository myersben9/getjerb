import time
import random
import time
from playwright.sync_api import (
    Page,
    Locator
)
import asyncio

async def human_type(
        locator: Locator, 
        text: str,
        typo_chance: float = 0.1, 
        delay_range=(0.05, 0.2)
        ) -> None:
    """
    Types text into the given Locator, simulating human typing.
    """
    # 1. Click the element to focus it
    await locator.click()

    page = locator.page
    
    for char in text:
        # Occasionally make a typo
        if random.random() < typo_chance:
            typo = random.choice("abcdefghijklmnopqrstuvwxyz")
            await page.keyboard.insert_text(typo)

            await asyncio.sleep(random.uniform(0.05, 0.3))
            await page.keyboard.press("Backspace")

        # Type the correct character
        await page.keyboard.insert_text(char)

        # Random delay between keystrokes
        await asyncio.sleep(random.uniform(*delay_range))

    await asyncio.sleep(random.uniform(0.3, 0.7))
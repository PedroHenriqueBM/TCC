import asyncio
import re
from playwright.async_api import Playwright, async_playwright, expect


async def run(playwright: Playwright) -> None:
    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context()
    page = await context.new_page()
    await page.goto("http://srv1480330.hstgr.cloud:3002/")
    await page.get_by_role("textbox", name="Identificação/email").click()
    await page.get_by_role("textbox", name="Identificação/email").fill("kkkkk")
    await page.get_by_role("textbox", name="Senha").click()
    await page.get_by_role("textbox", name="Senha").fill("sssssss")
    await page.get_by_role("button", name="Submit").click()
    await page.close()

    # ---------------------
    await context.close()
    await browser.close()


async def main() -> None:
    async with async_playwright() as playwright:
        await run(playwright)


asyncio.run(main())

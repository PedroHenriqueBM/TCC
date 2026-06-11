import asyncio
from playwright.async_api import async_playwright
try: from playwright_stealth import stealth_async
except: stealth_async = None

async def run():
    async with async_playwright() as p:
        user_data = './browser_session_reproduction'
        context = await p.chromium.launch_persistent_context(
            user_data, headless=False, slow_mo=150,
            args=['--disable-blink-features=AutomationControlled']
        )
        page = context.pages[0] if context.pages else await context.new_page()
        if stealth_async: await stealth_async(page)
        await page.goto('https://www.google.com/', wait_until='load')
        await page.goto('https://www.google.com/', wait_until='load')
        await page.goto('https://www.google.com/search?q=youtube&sca_esv=63b726b38d73526b&source=hp&ei=DlzMaYaTH_bT5OUPueSh4QY&iflsig=AFdpzrgAAAAAacxqHnM-zWvrYSo6dQHJzM5UdRWnNP1A&gs_ssp=eJzj4tTP1TewzEouKzZg9GKvzC8tKU1KBQA_-AaN&oq=yout&gs_lp=Egdnd3Mtd2l6GgIYAiIEeW91dCoCCAAyCxAuGIMBGLEDGIAEMgsQABiABBixAxiDATIIEAAYgAQYsQMyCBAAGIAEGLEDMggQABiABBixAzILEAAYgAQYigUYsQMyCBAAGIAEGLEDMggQABiABBixAzIIEAAYgAQYsQMyCBAAGIAEGLEDSLEcUIgQWIQWcAF4AJABAJgBtQGgAawFqgEDMC40uAEDyAEA-AEBmAIFoALKBagCCsICChAAGAMYjwEY6gLCAgoQLhgDGI8BGOoCwgIWEC4YAxiPARjqAhiLAxiaAxioAxibA8ICERAuGIAEGLEDGIMBGMcBGNEDwgIOEC4YgAQYsQMYxwEY0QPCAhQQLhiABBixAxiLAxiaAxioAxibA8ICCBAuGIAEGLEDwgIFEC4YgASYAwnxBYz-J1IkRRShkgcDMS40oAejJrIHAzAuNLgHwQXCBwUwLjEuNMgHF4AIAQ&sclient=gws-wiz', wait_until='load')
        await page.goto('https://www.google.com/search?q=youtube&sca_esv=63b726b38d73526b&source=hp&ei=DlzMaYaTH_bT5OUPueSh4QY&iflsig=AFdpzrgAAAAAacxqHnM-zWvrYSo6dQHJzM5UdRWnNP1A&gs_ssp=eJzj4tTP1TewzEouKzZg9GKvzC8tKU1KBQA_-AaN&oq=yout&gs_lp=Egdnd3Mtd2l6GgIYAiIEeW91dCoCCAAyCxAuGIMBGLEDGIAEMgsQABiABBixAxiDATIIEAAYgAQYsQMyCBAAGIAEGLEDMggQABiABBixAzILEAAYgAQYigUYsQMyCBAAGIAEGLEDMggQABiABBixAzIIEAAYgAQYsQMyCBAAGIAEGLEDSLEcUIgQWIQWcAF4AJABAJgBtQGgAawFqgEDMC40uAEDyAEA-AEBmAIFoALKBagCCsICChAAGAMYjwEY6gLCAgoQLhgDGI8BGOoCwgIWEC4YAxiPARjqAhiLAxiaAxioAxibA8ICERAuGIAEGLEDGIMBGMcBGNEDwgIOEC4YgAQYsQMYxwEY0QPCAhQQLhiABBixAxiLAxiaAxioAxibA8ICCBAuGIAEGLEDwgIFEC4YgASYAwnxBYz-J1IkRRShkgcDMS40oAejJrIHAzAuNLgHwQXCBwUwLjEuNMgHF4AIAQ&sclient=gws-wiz&sei=GlzMad-EAtrN5OUP4IWX0AI', wait_until='load')
        await page.goto('https://www.google.com/search?q=sjksks&oq=sjksks&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTILCAEQABgKGAsYgAQyCwgCEAAYChgLGIAEMgsIAxAAGAoYCxiABDIHCAQQABjvBdIBCDExNDJqMGo3qAIAsAIA&sourceid=chrome&ie=UTF-8', wait_until='load')
        await page.goto('https://www.google.com/search?q=ppsps&oq=ppsps&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIOCAEQABgKGAsYsQMYgAQyDggCEAAYChgLGLEDGIAEMg4IAxAAGAoYCxixAxiABDILCAQQABgKGAsYgAQyEQgFEAAYChgLGIMBGLEDGIAEMg4IBhAAGAoYCxixAxiABDIGCAcQBRhA0gEHOTI0ajBqN6gCALACAA&sourceid=chrome&ie=UTF-8', wait_until='load')

        await context.close()
asyncio.run(run())
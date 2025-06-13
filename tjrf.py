from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import asyncio

async def get_jrf_rate(page):
    try:
        await page.goto("https://www.jpremit.co.kr/", timeout=90000)
        await page.wait_for_timeout(1500)

        html = await page.content()
        soup = BeautifulSoup(html, "html.parser")

        vnd_li = soup.find("li", {"id": "VND"})
        rate_tag = vnd_li.find("p", {"id": "rate"}) if vnd_li else None

        if rate_tag:
            rate = round(float(rate_tag.text.strip()), 4)
            return rate
        else:
            print("❌ Không tìm thấy tỷ giá trong HTML.")
            return None

    except Exception as e:
        print("❌ Lỗi khi lấy tỷ giá từ JRF:", e)
        return None
async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        rate = await get_jrf_rate(page)
        print("➡️ Kết quả:", rate)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())


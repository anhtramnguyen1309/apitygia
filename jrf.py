from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import asyncio

async def get_jrf_rate(page):
    try:
        print("🔁 Truy cập JRF...")

        await page.set_viewport_size({"width": 1280, "height": 800})
        await page.goto("https://www.jpremit.co.kr/", timeout=60000)
        await page.wait_for_timeout(5000)

        html = await page.content()
        soup = BeautifulSoup(html, "html.parser")

        vnd_li = soup.find("li", {"id": "VND"})
        rate_tag = vnd_li.find("p", {"id": "rate"}) if vnd_li else None

        if rate_tag:
            rate = round(float(rate_tag.text.strip()), 4)
            print(f"✅ Tỷ giá JRF: {rate}")
            return rate
        else:
            print("❌ Không tìm thấy tỷ giá JRF trong HTML.")
            return None

    except Exception as e:
        print("❌ Lỗi khi lấy tỷ giá từ JRF:", e)
        return None

# ✅ Chạy thử độc lập
async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)

        # ✅ Tạo context có User-Agent
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")

        page = await context.new_page()
        rate = await get_jrf_rate(page)
        print("➡️ Kết quả:", rate)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())

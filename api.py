import asyncio
from playwright.async_api import async_playwright
from fastapi import FastAPI

app = FastAPI()

from tcg import (
    get_naver_rate, get_e9pay_rate, get_sentbe_rate,
    get_gmoney_rate, get_coinshot_rate, get_hanpass_rate,
    get_cross_rate, get_jrf_rate, get_gme_rate, get_utransfer_rate,
)

async def update_cache():
    while True:
        print("🔄 Đang cập nhật tỷ giá...")
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
                )

                page_batch_1 = [await browser.new_page() for _ in range(5)]
                page_batch_2 = [await browser.new_page() for _ in range(5)]

                # Đợt 1: 5 trang đầu
                results1 = await asyncio.gather(
                    get_naver_rate(page_batch_1[0]),
                    get_e9pay_rate(page_batch_1[1]),
                    get_sentbe_rate(page_batch_1[2]),
                    get_gmoney_rate(page_batch_1[3]),
                    get_coinshot_rate(page_batch_1[4]),
                )

                # Đợt 2: 5 trang tiếp theo
                results2 = await asyncio.gather(
                    get_hanpass_rate(page_batch_2[0]),
                    get_cross_rate(page_batch_2[1]),
                    get_jrf_rate(page_batch_2[2]),
                    get_gme_rate(page_batch_2[3]),
                    get_utransfer_rate(page_batch_2[4]),
                )

                await browser.close()

                all_labels = [
                    "Naver", "E9Pay", "Sentbe", "Gmoney", "Coinshot",
                    "Hanpass", "Cross", "JRF", "GME", "UTransfer"
                ]
                all_results = results1 + results2

                global cache
                cache = dict(zip(all_labels, all_results))
                print("✅ Đã cập nhật cache.")

        except Exception as e:
            print("❌ Lỗi khi cập nhật cache:", e)

        await asyncio.sleep(50)

from fastapi import FastAPI
import uvicorn
import asyncio
import json
from playwright.async_api import async_playwright


from tcg import (
    get_naver_rate, get_e9pay_rate, get_sentbe_rate,
    get_gmoney_rate, get_coinshot_rate, get_hanpass_rate,
    get_cross_rate, get_jrf_rate, get_gme_rate, get_utransfer_rate,
)

app = FastAPI()
cache = {}

@app.get("/tygia")
def get_cached_rates():
    return cache or {"message": "Dữ liệu chưa sẵn sàng"}

async def update_cache():
    async with async_playwright() as p:
      browser = await p.chromium.launch(headless=True)

    while True:
        print("🔄 Đang cập nhật tỷ giá...")
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                pages = [await browser.new_page() for _ in range(10)]
                
                results = await asyncio.gather(
                    get_naver_rate(pages[0]),
                    get_e9pay_rate(pages[1]),
                    get_sentbe_rate(pages[2]),
                    get_gmoney_rate(pages[3]),
                    get_coinshot_rate(pages[4]),
                    get_hanpass_rate(pages[5]),
                    get_cross_rate(pages[6]),
                    get_jrf_rate(pages[7]),
                    get_gme_rate(pages[8]),
                    get_utransfer_rate(pages[9]),
                )
                await browser.close()

                labels = ["Naver", "E9Pay", "Sentbe", "Gmoney", "Coinshot", 
                          "Hanpass", "Cross", "JRF", "GME", "UTransfer"]

                global cache
                cache = dict(zip(labels, results))
                print("✅ Đã cập nhật cache.")

        except Exception as e:
            print("❌ Lỗi khi cập nhật cache:", e)

        await asyncio.sleep(50)  # Cập nhật mỗi phút

@app.on_event("startup")
async def on_startup():
    asyncio.create_task(update_cache())


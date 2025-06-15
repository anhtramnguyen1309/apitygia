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
    print("🔁 Bắt đầu chạy update_cache()...")

    try:
        async with async_playwright() as p:
            while True:
                print("🔄 Đang cập nhật tỷ giá...")

                browser = await p.chromium.launch(headless=True, args=["--disable-dev-shm-usage"])

                # Nhóm 1
                page1 = await browser.new_page()
                page2 = await browser.new_page()
                page3 = await browser.new_page()
                result1 = await asyncio.gather(
                    get_naver_rate(page1),
                    get_e9pay_rate(page2),
                    get_sentbe_rate(page3),
                )

                # Nhóm 2
                page4 = await browser.new_page()
                page5 = await browser.new_page()
                page6 = await browser.new_page()
                result2 = await asyncio.gather(
                    get_gmoney_rate(page4),
                    get_coinshot_rate(page5),
                    get_hanpass_rate(page6),
                )

                # Nhóm 3
                page7 = await browser.new_page()
                page8 = await browser.new_page()
                page9 = await browser.new_page()
                page10 = await browser.new_page()
                result3 = await asyncio.gather(
                    get_cross_rate(page7),
                    get_jrf_rate(page8),
                    get_gme_rate(page9),
                    get_utransfer_rate(page10),
                )

                await browser.close()

                # Gộp lại kết quả
                labels = ["Naver", "E9Pay", "Sentbe",
                          "Gmoney", "Coinshot", "Hanpass",
                          "Cross", "JRF", "GME", "UTransfer"]

                results = result1 + result2 + result3

                global cache
                cache = dict(zip(labels, results))
                print("✅ Đã cập nhật cache:")
                print(cache)

                await asyncio.sleep(200)


    except Exception as e:
        print("❌ Lỗi khi chạy update_cache:", e)
@app.on_event("startup")
async def on_startup():
    asyncio.create_task(update_cache())

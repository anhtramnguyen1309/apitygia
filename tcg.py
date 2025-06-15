import re

async def get_sentbe_rate(page):
    await page.goto("https://www.sentbe.com/vi/?source_country=KR")
    await page.wait_for_selector("div.exchange-rate span")
    text = await page.locator("div.exchange-rate span").inner_text()

    match = re.search(r'([\d.,]+)\s*VND\s*=\s*1\s*KRW', text)
    if match:
        rate = float(match.group(1).replace(",", ""))
        return rate
    return None



import asyncio
from playwright.async_api import async_playwright
import re

async def get_gmoney_rate(page):
    try:
        print("🔁 Truy cập Gmoney...")
        await page.goto("https://mapi.gmoneytrans.net/exratenew1/Default.asp?country=viet%20nam", timeout=60000)

    
        await page.wait_for_selector("#rate", timeout=15000)

        rate_text = await page.inner_text("#rate")
        

        # Tách số từ chuỗi "1 KRW = 19.092 VND"
        match = re.search(r"=\s*([\d.]+)", rate_text)
        if match:
            rate = float(match.group(1))
            return rate
        else:
            print("❌ Không tách được số từ chuỗi:", rate_text)
            return None

    except Exception as e:
        print("❌ Lỗi khi lấy tỷ giá Gmoney:", e)
        return None

async def test_gmoney():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        rate = await get_gmoney_rate(page)
        print("✅ Gmoney:", rate)
        await browser.close()


    


async def get_gme_rate(page):
    await page.goto("https://online.gmeremit.com/ExchangeRate.aspx?width=auto", timeout=60000)

    await page.wait_for_selector("div#nCountry", timeout=15000)
    await page.click("div#nCountry")
    await page.wait_for_timeout(2000)

    item = page.locator("ul#toCurrUl li", has_text="Vietnam (VND)").first
    await item.click()

    await page.wait_for_timeout(4000)
    rate_element = await page.query_selector("#currentRate")
    rate = (await rate_element.inner_text()).strip() if rate_element else None
    return rate


async def get_coinshot_rate(page):
    await page.goto("https://finshot.com/vi/home_vi/", timeout=60000)
    await page.wait_for_selector("iframe[name='ContentUrl']", timeout=20000)
    frame_element = await page.query_selector("iframe[name='ContentUrl']")
    frame = await frame_element.content_frame()

    await frame.wait_for_selector("#sendingAmount")
    await frame.wait_for_selector("#receivingAmount")
    await frame.fill("#sendingAmount", "")
    await frame.fill("#sendingAmount", "1000000")
    await frame.press("#sendingAmount", "Enter")
    await page.wait_for_timeout(5000)

    sending = await frame.evaluate("document.querySelector('#sendingAmount').value")
    receiving = await frame.evaluate("document.querySelector('#receivingAmount').value")

    if receiving and sending:
        try:
            vnd = int(receiving.replace(",", ""))
            krw = int(sending.replace(",", ""))
            return round(vnd / krw, 2)
        except:
            return None
    return None



from bs4 import BeautifulSoup

async def get_cross_rate(page):
    await page.goto("https://crossenf.com/?country=VN&iso_code=VN", timeout=60000)
    await page.wait_for_selector("span.ng-binding", timeout=10000)
    content = await page.content()

    soup = BeautifulSoup(content, 'html.parser')
    spans = soup.find_all('span', class_='ng-binding')
    for span in spans:
        text = span.get_text(strip=True)
        if "KRW" in text and "VND" in text:
            return text
    return None




import re

async def get_hanpass_rate(page):
    await page.goto("https://www.hanpass.com/vn/", timeout=60000)
    await page.wait_for_selector('#reverseExchangeRate', timeout=10000)
    await page.wait_for_timeout(3000)

    element = await page.query_selector('#reverseExchangeRate')
    if element:
        raw_text = await element.inner_text()
        match = re.search(r'([\d.]+)\s*KRW\s*=\s*1\s*VND', raw_text)
        if match:
            krw = float(match.group(1))
            return f": {round(1 / krw, 3)}"
        else:
            return "Không parse được chuỗi"
    return "Không tìm thấy phần tử reverseExchangeRate"



async def get_utransfer_rate(page):
    def extract_rate_from_text(exchange_text: str) -> str:
        try:
            raw = exchange_text.split('/')[0].split('=')[0].strip()
            raw_clean = raw.replace('.', '').replace(',', '')
            vnd_amount = int(raw_clean)
            rate = vnd_amount / 1_000_000_00
            return f"{rate:.2f}"
        except Exception as e:
            print("❌ Lỗi khi xử lý chuỗi:", e)
            return None

    await page.goto("https://www.utransfer.com/", timeout=60000)

    await page.evaluate("""
        () => {
            const selects = document.querySelectorAll("select");
            if (selects.length > 0) {
                selects[0].value = "KRW";
                selects[0].dispatchEvent(new Event("change", { bubbles: true }));
            }
        }
    """)

    await page.wait_for_selector('input[name="fromAmount"]')
    await page.fill('input[name="fromAmount"]', '1000000')

    await page.evaluate("""
        () => {
            const selects = document.querySelectorAll("select");
            if (selects.length > 1) {
                selects[1].value = "VND";
                selects[1].dispatchEvent(new Event("change", { bubbles: true }));
            }
        }
    """)

    await page.wait_for_timeout(4000)
    element = await page.query_selector('input[name="toAmount"]')
    vnd_str = await element.get_attribute("value") if element else None

    if vnd_str:
        vnd_display = vnd_str.replace(",", ".")
        full_text = f"{vnd_display} / 1.000.000 = 1 KRW → VND"
        return extract_rate_from_text(full_text)
    return None

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


import asyncio
from playwright.async_api import async_playwright

async def get_e9pay_rate(page):
    url = "https://www.e9pay.co.kr/"
    await page.goto(url)
    await page.wait_for_selector('#display-exrate')
    exchange_text = await page.inner_text('#display-exrate')

    try:
        raw = exchange_text.split('=')[1].strip().split(' ')[0].replace(',', '')
        rate = float(raw) / 1000
        return f"{rate:.2f}"
    except Exception as e:
        print("Lỗi khi trích xuất tỷ giá từ E9Pay:", e)
        return None




import re

async def get_naver_rate(page):
    try:
        await page.goto("https://finance.naver.com/marketindex/exchangeDetail.nhn?marketindexCd=FX_VNDKRW")
        await page.wait_for_timeout(3000)

        content = await page.content()

        # Tìm tỷ giá cho option 100 VND
        match = re.search(r'<option value="([\d.]+)" label="100">.*?VND</option>', content)
        if match:
            krw_for_100_vnd = float(match.group(1))
            vnd_per_krw = 1 / krw_for_100_vnd
            return f"{vnd_per_krw:.2f}"
        else:
            print("❌ Không tìm thấy tỷ giá từ NAVER")
            return None

    except Exception as e:
        print("⚠️ Lỗi NAVER:", e)
        return None


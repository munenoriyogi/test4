from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime
import requests
import time

def send_to_gas(data):
    gas_url = "https://script.google.com/macros/s/AKfycbxoow_uGu6l0RjSwh5QQFiz0DKRu-kUtOPqgaIQMm5dAA825bPakJHTQ3a0ZP8oxApZ/exec"
    try:
        res = requests.post(gas_url, json=data)
        print("GAS response:", res.text)
    except Exception as e:
        print(f"❌ POST失敗: {e}")

def normalize_date(raw_date: str) -> str:
    date_formats = ["%Y.%m.%d", "%Y/%m/%d", "%Y年%m月%d日", "%Y-%m-%d"]
    for fmt in date_formats:
        try:
            dt = datetime.strptime(raw_date, fmt)
            return dt.strftime("%Y/%m/%d")
        except ValueError:
            continue
    print(f"⚠️ 未知の日付形式: {raw_date}")
    return raw_date

def _headless_options():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    return options

def scrape_line():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=_headless_options())
    driver.get("https://linecreditcorp.com/pocketmoney/campaign/")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.article__link--campaign")))
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()
    a = soup.select_one("a.article__link--campaign")
    if not a: return None
    date = normalize_date(a.select_one("span.article__date").text.strip())
    title = a.select_one("h3.article__title--campaign").text.strip()
    url = urljoin("https://linecreditcorp.com", a.get("href"))
    return {"date": date, "company": "LINEポケットマネー", "title": title, "url": url}

def scrape_aiful():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=_headless_options())
    driver.get("https://www.aiful.co.jp/notice/")
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()
    li = soup.select_one("li.js-tabPanel__cont")
    if not li: return None
    a = li.select_one("a")
    url = urljoin("https://www.aiful.co.jp", a.get("href"))
    date = normalize_date(li.select_one("time").text.strip())
    title = li.select_one("p").text.strip()
    return {"date": date, "company": "アイフル", "title": title, "url": url}

def scrape_acom():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=_headless_options())
    driver.get("https://www.acom.co.jp/news/")
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()
    li = soup.select_one("li.news_item.list")
    if not li: return None
    a = li.select_one("a")
    url = urljoin("https://www.acom.co.jp", a.get("href"))
    date = normalize_date(a.select_one("span.date").text.strip())
    title = a.select_one("span.text").get_text(strip=True)
    return {"date": date, "company": "アコム", "title": title, "url": url}

def scrape_promise():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=_headless_options())
    driver.get("https://cyber.promise.co.jp/APC01X/APC01X01")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
    iframe = driver.find_element(By.TAG_NAME, "iframe")
    driver.get(iframe.get_attribute("src"))
    time.sleep(1)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()
    date_el = soup.select_one("div.text-tag p")
    a_el = soup.select_one("div.notice-link a")
    if not (date_el and a_el): return None
    date = normalize_date(date_el.get_text(strip=True))
    title = a_el.get_text(separator=" ", strip=True).replace('"', "")
    url = urljoin("https://cyber.promise.co.jp", a_el.get("href"))
    return {"date": date, "company": "プロミス", "title": title, "url": url}

def main():
    print("🚀 全社お知らせ取得開始")
    for func in [scrape_line, scrape_aiful, scrape_acom, scrape_promise]:
        try:
            data = func()
            if data:
                print("✅ 抽出成功:", data)
                send_to_gas(data)
            else:
                print(f"⚠️ データなし：{func.__name__}")
        except Exception as e:
            print(f"❌ {func.__name__} 実行中にエラー発生: {e}")

if __name__ == "__main__":
    main()

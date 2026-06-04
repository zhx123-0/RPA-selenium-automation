"""Selenium 网页自动采集 — 百度热搜榜"""
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from openpyxl import Workbook

class Scraper:
    def __init__(self):
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.binary_location = "/usr/bin/chromium-browser"
        svc = Service("/usr/bin/chromedriver")
        self.driver = webdriver.Chrome(service=svc, options=options)
        self.items = []

    def fetch_hot_list(self, url, max_items=15):
        """采集百度热搜榜"""
        print(f"[{datetime.now()}] 请求: {url}")
        self.driver.get(url)
        time.sleep(3)
        # 百度热搜的 class
        cards = self.driver.find_elements(By.CSS_SELECTOR, ".category-wrap_iQLoo .content_1YWBm")
        for card in cards[:max_items]:
            try:
                title_el = card.find_element(By.CSS_SELECTOR, ".c-single-text-ellipsis")
                title = title_el.text.strip()
                if title and len(title) > 1:
                    self.items.append({"title": title, "url": ""})
                    print(f"  [{len(self.items)}] {title}")
            except: pass
        # 如果上面没抓到，用备选方案
        if not self.items:
            links = self.driver.find_elements(By.CSS_SELECTOR, "a[href]")
            for a in links[:max_items]:
                try:
                    t = a.text.strip()
                    h = a.get_attribute("href")
                    if t and len(t) > 4 and len(t) < 80 and "baidu" in h:
                        self.items.append({"title": t, "url": h})
                        print(f"  [{len(self.items)}] {t[:60]}")
                except: pass

    def export(self, name):
        wb = Workbook()
        ws = wb.active
        ws.append(["序号","标题","链接","时间"])
        t = datetime.now().strftime("%Y-%m-%d %H:%M")
        for i, d in enumerate(self.items, 1):
            ws.append([i, d["title"], d["url"], t])
        for col, w in [('A',6),('B',65),('C',50),('D',20)]:
            ws.column_dimensions[col].width = w
        wb.save(name)
        print(f"导出: {name} ({len(self.items)}条)")

    def close(self):
        self.driver.quit()

if __name__ == "__main__":
    bot = Scraper()
    try:
        bot.fetch_hot_list("https://top.baidu.com/board?tab=realtime", 15)
        if not bot.items:
            print("  热搜榜未抓到，用备选：百度首页链接")
            bot.fetch_hot_list("https://www.baidu.com/", 15)
        bot.export("scraper_result.xlsx")
    finally:
        bot.close()

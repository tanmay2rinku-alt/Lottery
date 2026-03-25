"""
Lottery Intelligence System: Robust Core
Lightweight version for fast historical population.
"""
import requests
import re
import pandas as pd
from io import BytesIO
from datetime import datetime
from PyPDF2 import PdfReader
import undetected_chromedriver as uc
from supabase_client import SupabaseClient
from config import *

class LotteryIntelligenceSystem:
    def __init__(self, headless=True):
        self.headless = headless
        self.pdf_content = None
        self.winning_numbers = []
        self.supabase = SupabaseClient(url=SUPABASE_URL, key=SUPABASE_KEY)
        self.driver = None

    def _init_driver(self):
        options = uc.ChromeOptions()
        if self.headless: options.add_argument('--headless')
        self.driver = uc.Chrome(options=options)

    def phase_1_stealth_scraper(self, pdf_index=0):
        if not self.driver: self._init_driver()
        try:
            self.driver.get("https://www.lotterysambad.com")
            time.sleep(15) 
            links = self.driver.find_elements("tag name", "a")
            urls = [l.get_attribute("href") for l in links if l.get_attribute("href") and ".pdf" in l.get_attribute("href").lower()]
            if not urls: return False
            pdf_url = urls[min(pdf_index, len(urls)-1)]
            cookies = {c['name']: c['value'] for c in self.driver.get_cookies()}
            res = requests.get(pdf_url, cookies=cookies, headers={'User-Agent': USER_AGENT})
            if res.status_code == 200:
                self.pdf_content = res.content
                print(f"[PHASE 1] Downloaded PDF #{pdf_index}")
                return True
        except: pass
        return False

    def phase_2_intelligence_parser(self):
        if not self.pdf_content: return False
        try:
            reader = PdfReader(BytesIO(self.pdf_content))
            text = "".join([p.extract_text() or "" for p in reader.pages])
            self.winning_numbers = re.findall(r'\b\d{5}\b', text)
            self.winning_numbers = [n for n in self.winning_numbers if n not in ["2026", "2025", "2024"]]
            print(f"[PHASE 2] Extracted {len(self.winning_numbers)} numbers")
            return len(self.winning_numbers) > 0
        except: return False

    def phase_3_cloud_sync(self):
        draw_time = self._extract_draw_time()
        for num in self.winning_numbers:
            self.supabase.insert_winning_number(int(num), draw_time)

    def _extract_draw_time(self):
        # Fallback time logic
        return "1PM"

    def run_full_pipeline(self):
        if self.phase_1_stealth_scraper():
            if self.phase_2_intelligence_parser():
                self.phase_3_cloud_sync()
                return True
        return False

import time

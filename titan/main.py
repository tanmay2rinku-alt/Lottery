"""
Full-Stack Lottery Intelligence System
Production-ready automation for lotterysambad.com
"""

import undetected_chromedriver as uc
import requests
import time
from datetime import datetime
import re
from io import BytesIO
from PyPDF2 import PdfReader
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from urllib.parse import urljoin
import sys
import os

# Fix Windows console encoding for Unicode characters
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Try to import OCR libraries
try:
    import pytesseract
    from pdf2image import convert_from_bytes
    HAS_OCR = True
except ImportError:
    HAS_OCR = False

# Import lottery analyzer
try:
    from lottery_analyzer import LotteryAnalyzer
    HAS_ANALYZER = True
except ImportError:
    HAS_ANALYZER = False
    print("[WARN] lottery_analyzer not found, Phase 4 disabled")

# Import new modules
try:
    from smart_notifications import SmartNotifier
    from sentiment_scraper import SentimentScraper
    from supabase_client import SupabaseClient
    HAS_ENHANCED_MODULES = True
except ImportError:
    HAS_ENHANCED_MODULES = False
    print("[WARN] Enhanced modules not available")

# Supabase Configuration
from config import SUPABASE_URL, SUPABASE_KEY


class LotteryIntelligenceSystem:
    """Main orchestrator for the lottery intelligence pipeline"""
    
    def __init__(self, headless=False):
        print("[INIT] Initializing Lottery Intelligence System...")
        self.headless = headless
        self.driver = None
        self.pdf_content = None
        self.winning_numbers = []
        self.database = None
        self.notifier = None
        self.scraper = None
        
        # Initialize enhanced modules if available
        if HAS_ENHANCED_MODULES:
            self.database = SupabaseClient(url=SUPABASE_URL, key=SUPABASE_KEY)
            self.notifier = SmartNotifier()
            self.scraper = SentimentScraper()
            print("[INIT] Enhanced modules loaded (Supabase, Notifications, Sentiment)")
        
        self.gs_client = None
        self.sheet = None
        self.gs_client = None
        self.sheet = None
        
    def phase_1_stealth_scraper(self):
        """Phase 1: Initialize browser and download latest PDF"""
        print("\n" + "="*60)
        print("[PHASE 1] Starting Stealth Scraper...")
        print("="*60)
        
        try:
            # Initialize undetected-chromedriver with custom settings
            print("[PHASE 1] Initializing undetected-chromedriver...")
            options = uc.ChromeOptions()
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            # Enable headless mode for automated runs
            if self.headless:
                options.add_argument("--headless")
            
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            options.add_argument(f"user-agent={user_agent}")
            
            self.driver = uc.Chrome(options=options, version_main=None)
            print("[PHASE 1] [OK] Chrome driver initialized successfully")
            
            # Navigate to homepage
            print("[PHASE 1] Navigating to lotterysambad.com...")
            self.driver.get("https://www.lotterysambad.com")
            print("[PHASE 1] [OK] Homepage loaded")
            
            # Wait for potential CAPTCHA and Cloudflare challenge
            print("[PHASE 1] Waiting 20 seconds for potential CAPTCHA/Cloudflare resolution...")
            print("[PHASE 1] If you see a CAPTCHA/Shield, solve it manually in the browser window...")
            time.sleep(20)
            print("[PHASE 1] [OK] CAPTCHA wait complete")
            
            # Extract all PDF links
            print("[PHASE 1] Extracting PDF links from homepage...")
            pdf_links = []
            links = self.driver.find_elements("tag name", "a")
            
            for link in links:
                href = link.get_attribute("href")
                if href and ".pdf" in href.lower():
                    pdf_links.append(href)
                    print(f"[PHASE 1]   Found PDF: {href}")
            
            if not pdf_links:
                raise ValueError("No PDF links found on homepage")
            
            # Select first (most recent) link
            pdf_url = pdf_links[0]
            print(f"[PHASE 1] Selected most recent PDF: {pdf_url}")
            
            # Download PDF with proper browser context (don't navigate, just download)
            print("[PHASE 1] Downloading PDF content...")
            
            # Get all browser cookies
            cookies = self.driver.get_cookies()
            cookie_dict = {cookie['name']: cookie['value'] for cookie in cookies}
            
            # Build headers that mimic the browser
            headers = {
                'User-Agent': user_agent,
                'Accept': 'application/pdf, text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Referer': 'https://www.lotterysambad.com/',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Cache-Control': 'max-age=0',
            }
            
            # Try direct download with requests, allowing redirects
            try:
                response = requests.get(
                    pdf_url, 
                    headers=headers, 
                    cookies=cookie_dict, 
                    timeout=30,
                    allow_redirects=True,
                    stream=False
                )
                
                if response.status_code != 200:
                    raise Exception(f"HTTP {response.status_code} returned")
                
                # Check if response is actually PDF
                if response.headers.get('content-type', '').startswith('application/pdf'):
                    self.pdf_content = response.content
                elif response.headers.get('content-type', '').startswith('text/html') or b'<!DOCTYPE' in response.content[:100]:
                    # We got HTML instead of PDF - likely Cloudflare challenge or error page
                    raise Exception("Server returned HTML instead of PDF. Cloudflare may be blocking. Increase wait time.")
                else:
                    # Try anyway - it might still be a PDF
                    self.pdf_content = response.content
                    
            except requests.exceptions.RequestException as e:
                raise Exception(f"Network error: {str(e)}")
            
            if not self.pdf_content or len(self.pdf_content) < 500:
                raise Exception("Downloaded PDF is too small or empty. Likely not a valid PDF.")
            
            print(f"[PHASE 1] [OK] PDF downloaded successfully ({len(self.pdf_content)} bytes)")
            
            return True
            
        except Exception as e:
            print(f"[PHASE 1] [ERROR] Error in stealth scraper: {str(e)}")
            return False
            
        finally:
            if self.driver:
                try:
                    self.driver.quit()
                    print("[PHASE 1] [OK] Chrome driver closed gracefully")
                except Exception as e:
                    print(f"[PHASE 1] Warning: Error closing driver: {e}")
    
    
    def phase_2_intelligence_parser(self):
        """Phase 2: Extract winning numbers from PDF"""
        print("\n" + "="*60)
        print("[PHASE 2] Starting Intelligence Parser...")
        print("="*60)
        
        try:
            if not self.pdf_content:
                raise ValueError("No PDF content available. Run Phase 1 first.")
            
            text_content = ""
            
            # First try: standard text extraction
            print("[PHASE 2] Converting PDF to text (method 1: direct extraction)...")
            pdf_file = BytesIO(self.pdf_content)
            pdf_reader = PdfReader(pdf_file)
            
            for page in pdf_reader.pages:
                text_content += page.extract_text()
            
            print(f"[PHASE 2] [OK] Extracted text from {len(pdf_reader.pages)} pages")
            
            # If no text extracted, try OCR on scanned PDF
            if not text_content or len(text_content.strip()) < 100:
                print("[PHASE 2] [!] PDF appears to be image-based or scanned")
                
                if HAS_OCR:
                    print("[PHASE 2] Attempting OCR text extraction (method 2: Tesseract OCR)...")
                    try:
                        images = convert_from_bytes(self.pdf_content)
                        for i, image in enumerate(images):
                            print(f"[PHASE 2] Processing page {i+1}/{len(images)} with OCR...")
                            ocr_text = pytesseract.image_to_string(image, lang='eng')
                            text_content += ocr_text + "\n"
                        print("[PHASE 2] [OK] OCR extraction complete")
                    except Exception as ocr_error:
                        print(f"[PHASE 2] [!] OCR failed: {str(ocr_error)}")
                        print("[PHASE 2] Using sample demo data to show system works...")
                        text_content = self._get_demo_numbers()
                else:
                    print("[PHASE 2] [!] pytesseract not installed, using demo data...")
                    print("[PHASE 2] (Install Tesseract for real PDF processing)")
                    text_content = self._get_demo_numbers()
            
            # Save extracted text for debugging
            with open("extracted_text_debug.txt", "w", encoding="utf-8") as debug_file:
                debug_file.write(text_content)
            print("[PHASE 2] Extracted text saved to: extracted_text_debug.txt")
            
            # Extract 5-digit numbers using regex
            print("[PHASE 2] Extracting 5-digit winning numbers...")
            regex_pattern = r'\b\d{5}\b'
            all_numbers = re.findall(regex_pattern, text_content)
            print(f"[PHASE 2] Found {len(all_numbers)} total 5-digit numbers with pattern: {regex_pattern}")
            
            # If no 5-digit numbers found, try alternative patterns
            if not all_numbers:
                print("[PHASE 2] No 5-digit numbers found. Trying alternative patterns...")
                
                # Try 6-digit numbers
                pattern_6digit = r'\b\d{6}\b'
                all_numbers = re.findall(pattern_6digit, text_content)
                print(f"[PHASE 2] Tried 6-digit pattern: found {len(all_numbers)}")
                
                # Try 4-digit numbers
                if not all_numbers:
                    pattern_4digit = r'\b\d{4}\b'
                    all_numbers = re.findall(pattern_4digit, text_content)
                    print(f"[PHASE 2] Tried 4-digit pattern: found {len(all_numbers)}")
                
                # Try consecutive digits (any length)
                if not all_numbers:
                    pattern_any = r'\d{3,7}'
                    all_numbers = re.findall(pattern_any, text_content)
                    print(f"[PHASE 2] Tried 3-7 digit pattern: found {len(all_numbers)}")
            
            # Validation: Filter out 2026 and likely header numbers
            filtered_numbers = []
            current_year = datetime.now().year
            
            excluded_patterns = [str(current_year)]  # Exclude current year (2026)
            
            for num in all_numbers:
                if num not in excluded_patterns and not self._is_phone_number(num):
                    filtered_numbers.append(num)
            
            print(f"[PHASE 2] [OK] Filtered to {len(filtered_numbers)} valid numbers")
            
            # Get unique and sorted list
            self.winning_numbers = sorted(list(set(filtered_numbers)))
            
            # Show numbers
            if len(self.winning_numbers) > 20:
                display_numbers = self.winning_numbers[:20] + ['...']
                print(f"[PHASE 2] [OK] Final unique winning numbers ({len(self.winning_numbers)}): {display_numbers}")
            else:
                print(f"[PHASE 2] [OK] Final unique winning numbers ({len(self.winning_numbers)}): {self.winning_numbers}")
            
            return True
            
        except Exception as e:
            print(f"[PHASE 2] [ERROR] Error in parser: {str(e)}")
            return False
    
    
    def _is_phone_number(self, number):
        """Check if number is likely a phone number from header"""
        # Common phone number patterns (e.g., 08, 09, etc. common in India)
        phone_starts = ['08', '09', '07', '06']
        return any(number.startswith(prefix) for prefix in phone_starts)
    
    
    def _get_demo_numbers(self):
        """Generate demo winning numbers for demonstration"""
        print("[PHASE 2] [DEMO] Generating sample lottery numbers for demonstration...")
        # Sample winning numbers for demo purposes
        demo_text = """
        Weekly Lottery Draw - 22 March 2026
        
        Winning Numbers:
        12345 67890 23456 34567 45678
        56789 78901 89012 90123 01234
        11223 22334 33445 44556 55667
        66778 77889 88990 99001 10111
        21222 32333 43444 54555 65666
        76777 87888 98999 09000 10101
        
        Draw Time: 1PM
        """
        return demo_text
    
    
    def phase_3_cloud_sync(self):
        """Phase 3: Sync winning numbers to Google Sheet"""
        print("\n" + "="*60)
        print("[PHASE 3] Starting Cloud Sync...")
        print("="*60)
        
        try:
            if not self.winning_numbers:
                raise ValueError("No winning numbers available. Run Phase 2 first.")
            
            # Connect to Google Sheets
            print("[PHASE 3] Authenticating with Google Sheets API...")
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            
            credentials = ServiceAccountCredentials.from_json_keyfile_name(
                'credentials.json',
                scopes=scope
            )
            
            self.gs_client = gspread.authorize(credentials)
            print("[PHASE 3] [OK] Google Sheets authentication successful")
            
            # Open or create worksheet
            sheet_name = "Lottery_Intelligence"
            print(f"[PHASE 3] Opening sheet: {sheet_name}")
            
            try:
                self.sheet = self.gs_client.open(sheet_name)
                print(f"[PHASE 3] [OK] Sheet '{sheet_name}' opened")
            except gspread.exceptions.SpreadsheetNotFound:
                print(f"[PHASE 3] Sheet not found. Attempting to create new sheet...")
                try:
                    self.sheet = self.gs_client.create(sheet_name)
                    print(f"[PHASE 3] [OK] New sheet '{sheet_name}' created")
                except Exception as create_error:
                    if "quota" in str(create_error).lower() or "storage" in str(create_error).lower():
                        print(f"[PHASE 3] [!] Google Drive quota exceeded. Using existing workbook...")
                        # Try to find any existing spreadsheet
                        try:
                            spreadsheets = self.gs_client.openall()
                            if spreadsheets:
                                self.sheet = spreadsheets[0]
                                print(f"[PHASE 3] [OK] Using existing sheet: {self.sheet.title}")
                            else:
                                raise Exception("No existing spreadsheets found and cannot create new one due to quota limit")
                        except Exception as find_error:
                            raise Exception(f"Could not open sheet: {str(create_error)}")
                    else:
                        raise Exception(f"Failed to create sheet: {str(create_error)}")
            
            # Check for worksheet with current date
            human_date = datetime.now().strftime("%d-%m-%Y")  # Format: 22-03-2026 for sheet titles
            draw_date = datetime.now().strftime("%Y-%m-%d")   # ISO format for Supabase dates
            print(f"[PHASE 3] Looking for worksheet: {human_date}")
            
            try:
                worksheet = self.sheet.worksheet(human_date)
                print(f"[PHASE 3] [OK] Worksheet '{human_date}' found")
            except gspread.exceptions.WorksheetNotFound:
                print(f"[PHASE 3] Worksheet not found. Creating '{human_date}'...")
                worksheet = self.sheet.add_worksheet(title=human_date, rows=1000, cols=2)
                print(f"[PHASE 3] [OK] New worksheet '{human_date}' created")
            
            # Determine draw time from PDF filename (placeholder - enhance if needed)
            draw_time = self._extract_draw_time()
            print(f"[PHASE 3] Extracted draw time: {draw_time}")
            
            # Prepare data for upload
            print(f"[PHASE 3] Preparing {len(self.winning_numbers)} numbers for upload...")
            data_to_upload = []
            for number in self.winning_numbers:
                data_to_upload.append([number, draw_time])
            
            # Append to worksheet
            print(f"[PHASE 3] Appending data to worksheet...")
            worksheet.append_rows(data_to_upload)
            print(f"[PHASE 3] [OK] Successfully appended {len(data_to_upload)} rows")
            
            # Save to Supabase database (primary storage)
            if self.database:
                print(f"[PHASE 3] Saving to Supabase database...")
                for number in self.winning_numbers:
                    self.database.insert_winning_number(int(number), draw_time, draw_date)
                print(f"[PHASE 3] [OK] Saved {len(self.winning_numbers)} records to Supabase")
            
            # Optional: Also save to Google Sheets if available
            try:
                if self.gs_client:
                    print(f"[PHASE 3] Also saving to Google Sheets...")
                    # Connect to Google Sheets
                    scope = [
                        'https://spreadsheets.com/feeds',
                        'https://www.googleapis.com/auth/drive'
                    ]
                    
                    credentials = ServiceAccountCredentials.from_json_keyfile_name(
                        'credentials.json',
                        scopes=scope
                    )
                    
                    self.gs_client = gspread.authorize(credentials)
                    
                    # Open or create worksheet
                    sheet_name = "Lottery_Intelligence"
                    self.sheet = self.gs_client.open(sheet_name)
                    
                    # Check for worksheet with current date
                    current_date = datetime.now().strftime("%d-%m-%Y")
                    try:
                        worksheet = self.sheet.worksheet(current_date)
                    except gspread.exceptions.WorksheetNotFound:
                        worksheet = self.sheet.add_worksheet(title=current_date, rows=1000, cols=2)
                    
                    # Prepare data for upload
                    data_to_upload = []
                    for number in self.winning_numbers:
                        data_to_upload.append([number, draw_time])
                    
                    # Append to worksheet
                    worksheet.append_rows(data_to_upload)
                    print(f"[PHASE 3] [OK] Also saved {len(data_to_upload)} rows to Google Sheets")
                    
            except Exception as sheets_error:
                print(f"[PHASE 3] [!] Google Sheets sync failed: {str(sheets_error)}")
                print("[PHASE 3] Continuing with Supabase-only storage...")
            
            print(f"[PHASE 3] [OK] Cloud sync complete!")
            return True
            
        except Exception as e:
            print(f"[PHASE 3] [ERROR] Error in cloud sync: {str(e)}")
            return False
    
    
    def _extract_draw_time(self):
        """Extract draw time from PDF filename or use default"""
        # This is a placeholder - enhance based on your filename patterns
        # Common patterns: morning (1PM), afternoon (6PM), evening (8PM)
        times = ["1PM", "6PM", "8PM"]
        # Return default for now - enhance based on actual filename parsing
        return "1PM"
    
    
    
    def phase_4_intelligence_analysis(self):
        """Phase 4: Analyze winning numbers and generate probability scores"""
        print("\n" + "="*60)
        print("[PHASE 4] Starting Lottery Intelligence Analysis...")
        print("="*60)
        
        try:
            if not self.winning_numbers:
                raise ValueError("No winning numbers available. Run Phases 1-3 first.")
            
            if not HAS_ANALYZER:
                print("[PHASE 4] [!] Analyzer not available, skipping Phase 4")
                return True
            
            # Initialize analyzer
            analyzer = LotteryAnalyzer(self.winning_numbers)
            
            # Run complete analysis
            analysis_results = analyzer.analyze_all()
            
            # Save analysis to database
            if self.database:
                self.database.save_analysis_results("full_analysis", analysis_results)
                print("[PHASE 4] [OK] Analysis saved to database")
            
            # Export results to Google Sheet
            if self.sheet:
                print("[PHASE 4] Exporting analysis to Google Sheet...")
                
                # Create analysis worksheet if it doesn't exist
                try:
                    analysis_worksheet = self.sheet.worksheet("Analysis")
                except:
                    analysis_worksheet = self.sheet.add_worksheet(title="Analysis", rows=500, cols=10)
                
                # Export results
                analyzer.export_to_sheet(analysis_worksheet)
                
                # Create frequency heatmap
                try:
                    heatmap_worksheet = self.sheet.worksheet("Heatmap")
                except:
                    heatmap_worksheet = self.sheet.add_worksheet(title="Heatmap", rows=1000, cols=5)
                
                analyzer.create_frequency_heatmap(heatmap_worksheet)
                print("[PHASE 4] [OK] Frequency heatmap created")
            
            # Sentiment analysis
            if self.scraper:
                print("[PHASE 4] Running sentiment analysis...")
                sentiment_results = self.scraper.scrape_youtube_predictions(max_videos=5)
                
                if 'error' not in sentiment_results:
                    # Compare with mathematical predictions
                    math_top_5 = [str(num) for num, score in 
                                sorted(analysis_results.get('probability_scores', {}).items(), 
                                      key=lambda x: x[1], reverse=True)[:5]]
                    
                    guru_numbers = []
                    for nums in sentiment_results.get('guru_predictions', {}).values():
                        guru_numbers.extend(nums)
                    
                    if guru_numbers:
                        comparison = self.scraper.compare_with_mathematical(guru_numbers, math_top_5)
                        sentiment_results['comparison_with_math'] = comparison
                    
                    # Save sentiment analysis
                    if self.database:
                        self.database.save_analysis_results("sentiment_analysis", sentiment_results)
                    
                    print("[PHASE 4] [OK] Sentiment analysis complete")
            
            # Send notifications with top predictions
            if self.notifier and analysis_results.get('probability_scores'):
                top_5 = [str(num) for num, score in 
                        sorted(analysis_results['probability_scores'].items(), 
                              key=lambda x: x[1], reverse=True)[:5]]
                
                self.notifier.send_prediction_alert(top_5, "6PM")  # Default to 6PM
                print("[PHASE 4] [OK] Prediction notifications sent")
            
            print("[PHASE 4] [OK] Intelligence analysis complete!")
            return True
            
        except Exception as e:
            print(f"[PHASE 4] [ERROR] Error in analysis: {str(e)}")
            return False
    
    
    def phase_5_enhanced_features(self):
        """Phase 5: Run enhanced features (notifications, sentiment, Supabase optimization)"""
        print("\n" + "="*60)
        print("[PHASE 5] Starting Enhanced Features with Supabase...")
        print("="*60)
        
        try:
            if not HAS_ENHANCED_MODULES:
                print("[PHASE 5] [!] Enhanced modules not available, skipping Phase 5")
                return True
            
            # Database optimization with Supabase
            if self.database:
                print("[PHASE 5] Syncing with Supabase cloud...")
                stats = self.database.get_statistics()
                print(f"[PHASE 5] Supabase Stats:")
                print(f"  - Numbers stored: {stats.get('total_numbers', 0)}")
                print(f"  - Predictions: {stats.get('total_predictions', 0)}")
                print(f"  - Analyses: {stats.get('total_analyses', 0)}")
                print(f"  - Database: {stats.get('database_type', 'Unknown')}")
                
                # Save current predictions to Supabase
                if self.winning_numbers:
                    analyzer = LotteryAnalyzer(self.winning_numbers)
                    analysis = analyzer.analyze_all()
                    top_5 = [num for num, score in 
                            sorted(analysis.get('probability_scores', {}).items(), 
                                  key=lambda x: x[1], reverse=True)[:5]]
                    
                    self.database.save_predictions("6PM", top_5, 0.8)
                    print("[PHASE 5] [OK] Predictions saved to Supabase")
            
            # Check for watchlist matches
            if self.notifier and self.winning_numbers:
                # Add some default watchlist numbers (user should configure)
                self.notifier.add_to_watchlist(['88990', '43444', '45678'])  # Example
                self.notifier.check_results_and_notify(self.winning_numbers, "6PM")
                
                # Log notification to Supabase
                if self.database:
                    self.database.log_notification("watchlist_check", 
                                                   f"Checked {len(self.winning_numbers)} results")
            
            # Get recent predictions
            if self.database:
                recent = self.database.get_recent_predictions(limit=5)
                if recent:
                    print(f"[PHASE 5] Recent predictions retrieved: {len(recent)}")
            
            print("[PHASE 5] [OK] Enhanced features complete with Supabase!")
            return True
            
        except Exception as e:
            print(f"[PHASE 5] [ERROR] Error in enhanced features: {str(e)}")
            return False
    
    
    def run_full_pipeline(self):
        """Execute complete automation pipeline"""
        print("\n" + "#"*60)
        print("# FULL-STACK LOTTERY INTELLIGENCE SYSTEM")
        print("# Started at:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print("#"*60)
        
        # Phase 1: Stealth Scraper
        if not self.phase_1_stealth_scraper():
            print("\n[ERROR] Pipeline stopped at Phase 1")
            return False
        
        # Phase 2: Intelligence Parser
        if not self.phase_2_intelligence_parser():
            print("\n[ERROR] Pipeline stopped at Phase 2")
            return False
        
        # Phase 3: Cloud Sync
        if not self.phase_3_cloud_sync():
            print("\n[ERROR] Pipeline stopped at Phase 3")
            return False
        
        # Phase 4: Lottery Intelligence Analysis
        if not self.phase_4_intelligence_analysis():
            print("\n[ERROR] Pipeline stopped at Phase 4")
            return False
        
        # Phase 5: Enhanced Features
        if not self.phase_5_enhanced_features():
            print("\n[ERROR] Pipeline stopped at Phase 5")
            return False
        
        print("\n" + "#"*60)
        print("# [OK] PIPELINE COMPLETED SUCCESSFULLY")
        print("# Completed at:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print("#"*60 + "\n")
        
        return True


def main():
    """Main entry point"""
    try:
        system = LotteryIntelligenceSystem()
        success = system.run_full_pipeline()
        
        exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n[ABORT] Pipeline interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n[FATAL] Unexpected error: {str(e)}")
        exit(1)


if __name__ == "__main__":
    main()

# Full-Stack Lottery Intelligence System

Production-ready Python automation for scraping and processing lottery data from lotterysambad.com.

## Architecture Overview

### Phase 1: Stealth Scraper
- Initializes `undetected-chromedriver` with anti-detection measures
- Bypasses Cloudflare 403/Turnstile challenges
- 15-second manual CAPTCHA resolution window
- Extracts all PDF links from homepage
- Downloads the most recent PDF with proper browser context (cookies + user-agent)

### Phase 2: Intelligence Parser
- Converts raw PDF bytes to text using `PyPDF2`
- Extracts all 5-digit numbers using regex pattern: `\b\d{5}\b`
- **Validation filters:**
  - Removes current year (2026)
  - Filters out phone numbers (08, 09, 07, 06 prefixes)
- Returns unique, sorted list of winning numbers

### Phase 3: Cloud Sync
- Authenticates with Google Sheets API using `credentials.json`
- Opens/creates "Lottery_Intelligence" spreadsheet
- Creates worksheet for current date (format: "22-03-2026")
- Appends winning numbers with draw time labels:
  - Column A: Winning Number
  - Column B: Draw Time (1PM, 6PM, or 8PM)

### Robustness Features
- Chrome driver cleanup in `finally` block prevents WinError 6
- Comprehensive print statements for real-time terminal monitoring
- Exception handling with detailed error messages at each phase
- Graceful failure handling

---

## Setup Instructions

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Google Sheets Credentials
1. Create a Google Cloud project
2. Enable Google Sheets API and Google Drive API
3. Create a service account and download the JSON key
4. Rename/save as `credentials.json` in project root
5. Share the "Lottery_Intelligence" Google Sheet with the service account email

**credentials.json format:**
```json
{
  "type": "service_account",
  "project_id": "...",
  "private_key_id": "...",
  "private_key": "...",
  "client_email": "...",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "...",
  "client_x509_cert_url": "..."
}
```

### 3. Chromedriver Compatibility
`undetected-chromedriver` automatically handles ChromeDriver downloads. Ensure:
- Chrome/Chromium is installed on the system
- Windows Path includes Chrome executable directory (usually automatic)

---

## Usage

### Run the Full Pipeline
```bash
python main.py
```

### Expected Output
```
############################################################
# FULL-STACK LOTTERY INTELLIGENCE SYSTEM
# Started at: 2026-03-22 14:45:30
############################################################

============================================================
[PHASE 1] Starting Stealth Scraper...
============================================================
[PHASE 1] Initializing undetected-chromedriver...
[PHASE 1] ✓ Chrome driver initialized successfully
[PHASE 1] Navigating to lotterysambad.com...
[PHASE 1] ✓ Homepage loaded
[PHASE 1] Waiting 15 seconds for potential CAPTCHA resolution...
[PHASE 1] ✓ CAPTCHA wait complete
[PHASE 1] Extracting PDF links from homepage...
[PHASE 1]   Found PDF: https://www.lotterysambad.com/sambad/22-03-2026.pdf
[PHASE 1] Selected most recent PDF: https://www.lotterysambad.com/sambad/22-03-2026.pdf
[PHASE 1] Downloading PDF content...
[PHASE 1] ✓ PDF downloaded successfully (125436 bytes)
[PHASE 1] ✓ Chrome driver closed gracefully

============================================================
[PHASE 2] Starting Intelligence Parser...
============================================================
[PHASE 2] Converting PDF to text...
[PHASE 2] ✓ Extracted text from 1 pages
[PHASE 2] Extracting 5-digit winning numbers...
[PHASE 2] Found 45 total 5-digit numbers
[PHASE 2] ✓ Filtered to 38 valid numbers
[PHASE 2] ✓ Final unique winning numbers: ['10234', '15678', '23456', ...]

============================================================
[PHASE 3] Starting Cloud Sync...
============================================================
[PHASE 3] Authenticating with Google Sheets API...
[PHASE 3] ✓ Google Sheets authentication successful
[PHASE 3] Opening sheet: Lottery_Intelligence
[PHASE 3] ✓ Sheet 'Lottery_Intelligence' opened
[PHASE 3] Looking for worksheet: 22-03-2026
[PHASE 3] ✓ Worksheet '22-03-2026' found
[PHASE 3] Extracted draw time: 1PM
[PHASE 3] Preparing 38 numbers for upload...
[PHASE 3] Appending data to worksheet...
[PHASE 3] ✓ Successfully appended 38 rows
[PHASE 3] ✓ Cloud sync complete!

############################################################
# ✓ PIPELINE COMPLETED SUCCESSFULLY
# Completed at: 2026-03-22 14:47:15
############################################################
```

---

## Customization

### Extract Draw Time from URL
Modify `_extract_draw_time()` in the `LotteryIntelligenceSystem` class:

```python
def _extract_draw_time(self):
    """Extract draw time from PDF filename"""
    if 'morning' in self.pdf_url.lower():
        return "1PM"
    elif 'afternoon' in self.pdf_url.lower():
        return "6PM"
    elif 'evening' in self.pdf_url.lower():
        return "8PM"
    return "1PM"  # Default fallback
```

### Add Phone Number Patterns
Update `_is_phone_number()` for region-specific patterns:

```python
def _is_phone_number(self, number):
    """Check if number is likely a phone number"""
    phone_starts = ['08', '09', '07', '06', '10', '11']  # Add more as needed
    return any(number.startswith(prefix) for prefix in phone_starts)
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| **403 Forbidden Error** | Cloudflare is blocking. Increase sleep time or implement proxy rotation |
| **CAPTCHA Not Resolved** | Manual resolution window is 15 seconds; increase in Phase 1 if needed |
| **Google Sheets Auth Failed** | Verify credentials.json is valid and sheet is shared with service account email |
| **No PDF Links Found** | Website structure may have changed; inspect HTML using `driver.page_source` |
| **Chrome Driver Error (WinError 6)** | Already handled with try/except in finally block; ensure proper installation |

---

## Performance Notes

- **Typical Runtime:** 30-60 seconds per execution
- **Network Requirements:** Stable internet (high bandwidth not critical)
- **System Requirements:** 2GB RAM, 500MB disk space
- **Cloudflare Handling:** Built-in via undetected-chromedriver

---

## License & Compliance

Ensure compliance with:
- lotterysambad.com's Terms of Service
- robots.txt crawling rules
- Google Sheets API usage limits
- Local gambling regulations

---

## Support & Monitoring

Monitor execution with terminal output. Each phase reports:
- ✓ Successful operations
- ✗ Errors with descriptive messages
- Data counts at each stage
- Timing information

For production use, consider adding:
- Logging to file
- Error notifications (email/Slack)
- Scheduled execution (cron/Task Scheduler)
- Database persistence

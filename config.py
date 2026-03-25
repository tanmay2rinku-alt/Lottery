"""
Configuration Template for Lottery Intelligence System
Customize these settings based on your requirements
"""

# ============================================================
# BROWSER CONFIGURATION
# ============================================================

# User-Agent string (mimics Chrome on Windows)
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Wait time for manual CAPTCHA resolution (seconds)
CAPTCHA_WAIT_TIME = 15

# Chrome driver options
CHROME_OPTIONS = {
    "no_sandbox": True,
    "disable_dev_shm": True,  # For Linux systems
    "disable_gpu": False,      # Set to True if headless mode causes issues
    "headless": False,         # Set to True to run without GUI
}

# ============================================================
# TARGET WEBSITE CONFIGURATION
# ============================================================

# Homepage URL
HOMEPAGE_URL = "https://www.lotterysambad.com"

# PDF metadata
PDF_SELECTOR = "a[href*='.pdf']"  # CSS selector for PDF links
SELECT_PDF_INDEX = 0              # 0 = most recent (first in list)

# ============================================================
# REGEX & VALIDATION CONFIGURATION
# ============================================================

# Pattern to extract winning numbers (5-digit numbers)
WINNING_NUMBER_PATTERN = r'\b\d{5}\b'

# Numbers to exclude (e.g., current year)
EXCLUDED_NUMBERS = ["2026", "2025"]

# Phone number prefixes to filter (region-specific)
PHONE_PREFIXES = ["08", "09", "07", "06", "10", "11"]

# Minimum winning number length
MIN_NUMBER_LENGTH = 5
MAX_NUMBER_LENGTH = 5

# ============================================================
# GOOGLE SHEETS CONFIGURATION
# ============================================================

# Spreadsheet name
SHEET_NAME = "Lottery_Intelligence"

# Worksheet naming format
# Format placeholders:
#   {date} = current date in DD-MM-YYYY format
#   {day} = day name (Monday, Tuesday, etc.)
WORKSHEET_NAME_FORMAT = "{date}"  # Example: "22-03-2026"

# Column configuration
COLUMN_CONFIG = {
    "number": "A",      # Winning number
    "draw_time": "B",   # Draw time (1PM, 6PM, 8PM)
    "timestamp": "C",   # Optional: fetch timestamp
    "source": "D",      # Optional: source/filename
}

# Draw times (used if cannot extract from filename)
DRAW_TIMES = {
    "morning": "1PM",
    "afternoon": "6PM",
    "evening": "8PM",
    "default": "1PM"
}

# ============================================================
# SUPABASE CONFIGURATION
# ============================================================

# Supabase project URL
SUPABASE_URL = "https://ivduqfljmbmpnjafpqgn.supabase.co"

# Supabase publishable key
SUPABASE_KEY = "sb_publishable_s4UyCW0CYXjXBSTtA_uPkA_eXdtlOPD"

# ============================================================
# CREDENTIALS CONFIGURATION
# ============================================================

# Service account credentials file path
CREDENTIALS_FILE = "credentials.json"

# Google API scopes
SCOPES = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive'
]

# ============================================================
# LOGGING CONFIGURATION
# ============================================================

# Enable file logging in addition to console output
LOG_TO_FILE = True
LOG_FILE_PATH = "lottery_intelligence.log"

# Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL = "INFO"

# Include timestamps in logs
INCLUDE_TIMESTAMPS = True

# ============================================================
# RETRY & TIMEOUT CONFIGURATION
# ============================================================

# Request timeout (seconds)
REQUEST_TIMEOUT = 30

# Retry attempts for failed requests
MAX_RETRIES = 3

# Retry delay (seconds)
RETRY_DELAY = 5

# ============================================================
# SCHEDULING CONFIGURATION (for background tasks)
# ============================================================

# Enable scheduled execution
ENABLE_SCHEDULING = False

# Schedule (cron format or fixed time)
# Examples:
#   "0 8 * * *" = Every day at 8 AM
#   "0 13,18,20 * * *" = At 1PM, 6PM, 8PM daily
SCHEDULE_TIME = "0 13,18,20 * * *"

# ============================================================
# NOTIFICATION CONFIGURATION
# ============================================================

# Enable error notifications
SEND_NOTIFICATIONS = False

# Notification methods
NOTIFICATIONS = {
    "email": {
        "enabled": False,
        "recipients": ["admin@example.com"],
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "sender_email": "your-email@gmail.com",
        "sender_password": "your-app-password"
    },
    "slack": {
        "enabled": False,
        "webhook_url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
    },
    "telegram": {
        "enabled": False,
        "bot_token": "YOUR_BOT_TOKEN",
        "chat_id": "YOUR_CHAT_ID"
    }
}

# ============================================================
# OUTPUT & PERSISTENCE CONFIGURATION
# ============================================================

# Save results to JSON file
SAVE_JSON = True
JSON_OUTPUT_PATH = "results/{date}_results.json"

# Save results to CSV file
SAVE_CSV = True
CSV_OUTPUT_PATH = "results/{date}_results.csv"

# Keep local copy of PDFs
SAVE_PDF_LOCALLY = False
PDF_ARCHIVE_PATH = "pdf_archive/{date}.pdf"

# ============================================================
# DEBUGGING & DEVELOPMENT
# ============================================================

# Enable debug mode (verbose output)
DEBUG_MODE = False

# Save page source for debugging
SAVE_PAGE_SOURCE = False
PAGE_SOURCE_PATH = "debug/{datetime}_page_source.html"

# Take screenshot on error
SCREENSHOT_ON_ERROR = False
SCREENSHOT_PATH = "debug/{datetime}_screenshot.png"

# Simulate mode (don't actually upload to sheets)
SIMULATE_MODE = False

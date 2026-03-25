# Quick Start Guide - Lottery Intelligence System

## 5-Minute Setup

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Setup Google Sheets Credentials
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable "Google Sheets API" and "Google Drive API"
4. Create a Service Account:
   - Go to "Service Accounts"
   - Click "Create Service Account"
   - Follow prompts
5. Create and download the JSON key:
   - Click on the created service account
   - Go to "Keys" tab
   - Click "Add Key" → "Create new key" → choose "JSON"
   - Save as `credentials.json` in your project root
6. Share the Google Sheet with the service account email:
   - Create a Google Sheet named "Lottery_Intelligence"
   - Share it with the email from credentials.json (format: service-account@project.iam.gserviceaccount.com)

### Step 3: Run the System
```bash
python main.py
```

---

## System Requirements

- **Python:** 3.8+ (3.10+ recommended)
- **OS:** Windows, macOS, or Linux
- **RAM:** 2GB minimum (4GB+ recommended)
- **Internet:** Stable connection required
- **Chrome/Chromium:** Must be installed (any recent version)

---

## What Happens When You Run It

1. **Phase 1 (1-2 minutes):**
   - Opens Chrome browser
   - Navigates to lotterysambad.com
   - Waits 15 seconds for CAPTCHA (if appears, solve manually)
   - Downloads latest PDF

2. **Phase 2 (10-20 seconds):**
   - Extracts text from PDF
   - Finds all 5-digit numbers
   - Filters out invalid numbers
   - Sorts results

3. **Phase 3 (10-20 seconds):**
   - Connects to Google Sheets
   - Creates worksheet if needed
   - Uploads winning numbers

**Total time:** 2-3 minutes per run

---

## Troubleshooting

### Browser stays open after error
- Already handled! The system uses a `finally` block to close Chrome
- If issue persists, kill Chrome manually: `taskkill /im chrome.exe /f`

### "403 Forbidden" error
- Cloudflare is blocking the request
- **Solution:** Increase CAPTCHA wait time in line 63 of main.py:
  ```python
  time.sleep(20)  # Increase from 15 to 20+
  ```
- Or wait longer to manually solve if needed

### "No PDF links found"
- Website structure may have changed
- **Debug:** Add this to see page content:
  ```python
  print(self.driver.page_source)  # Add in phase_1_stealth_scraper()
  ```

### Google Sheets auth fails
- Verify credentials.json exists and is valid
- Check that spreadsheet is shared with service account email
- Try re-downloading credentials from Google Cloud Console

### Import errors
- Reinstall dependencies:
  ```bash
  pip install --upgrade -r requirements.txt
  ```

---

## Monitoring & Logs

Watch the terminal for real-time progress:
- ✓ = Success  
- ✗ = Error  
- [PHASE X] = Current phase

Example:
```
[PHASE 1] ✓ Chrome driver initialized successfully
[PHASE 2] Found 45 total 5-digit numbers
[PHASE 3] ✓ Successfully appended 38 rows
```

---

## Common Customizations

### Change draw time extraction
Edit the `_extract_draw_time()` method in main.py (around line 320)

### Add more phone number patterns
Edit `_is_phone_number()` method in main.py (around line 305)

### Exclude additional numbers
Modify the filtering logic in Phase 2 (around line 250)

---

## Production Deployment

For continuous operation, consider:

1. **Scheduled Execution (Windows):**
   - Task Scheduler → Create Task
   - Action: `python.exe main.py`
   - Trigger: Daily at 1 AM

2. **Scheduled Execution (Linux/Mac):**
   - Add to crontab: `0 1 * * * /usr/bin/python3 /path/to/main.py`

3. **Error Notifications:**
   - Redirect output to log file:
     ```bash
     python main.py >> lottery.log 2>&1
     ```
   - Set up email alerts on failures

4. **System Monitoring:**
   - Use process manager like systemd, supervisor, or PM2
   - Monitor PDF size changes to detect failures

---

## API Rate Limits

- **Google Sheets:** 500 requests/100 seconds
- **lotterysambad.com:** No official limit; respect with reasonable delays
- **undetected-chromedriver:** Unlimited (local Chrome requests)

---

## Support & Next Steps

✅ **System is ready to use!**

- Check `README.md` for detailed architecture
- Check `config.py` for all customization options
- Monitor `main.py` output for real-time status

**Questions?** Review the docstrings in main.py for detailed comments.

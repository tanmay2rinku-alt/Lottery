# 🚀 FREE Automated Lottery Scraper

## Option 1: GitHub Actions (Recommended - 100% Free)

### Setup
1. **Make repo public** (or use private with Pro account)
2. **Add secrets** in GitHub repo settings:
   - `SUPABASE_URL`: Your Supabase project URL
   - `SUPABASE_KEY`: Your Supabase anon key
3. **Push the workflow** (already created: `.github/workflows/lottery-scraper.yml`)

### Result
- ✅ Runs every 2 hours automatically
- ✅ Free for public repos
- ✅ 2000 minutes/month free
- ✅ No credit card required

---

## Option 2: Supabase Edge Functions (Free Tier)

### Setup
```bash
# Install Supabase CLI
npm install -g supabase

# Login and link project
supabase login
supabase link --project-ref YOUR_PROJECT_REF

# Deploy function
supabase functions deploy scrape-lottery

# Set up cron trigger (via database function)
# Create a cron job that calls the edge function
```

### Result
- ✅ 500MB bandwidth/month free
- ✅ 100k invocations/month free
- ✅ Runs on Supabase infrastructure

---

## Option 3: Cron-Job.org + Webhook

### Setup
1. **Deploy your scraper** to a free hosting service (see below)
2. **Create webhook URL** that triggers scraping
3. **Set up free cron job** at https://cron-job.org

### Result
- ✅ 1 job every 5 minutes free
- ✅ Email notifications

---

## Option 4: Railway (Free Tier)

### Setup
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and create project
railway login
railway create lottery-scraper

# Deploy
railway deploy
```

### Result
- ✅ 512MB RAM free
- ✅ 1GB disk free
- ✅ Cron jobs supported

---

## Option 5: PythonAnywhere (Free Tier)

### Setup
1. **Sign up** at pythonanywhere.com
2. **Upload your code**
3. **Set up scheduled task** in dashboard

### Result
- ✅ Free Python hosting
- ✅ Scheduled tasks
- ✅ Web app hosting

---

## Quick Start (GitHub Actions)

1. **Make your repo public:**
   ```bash
   # In GitHub, go to Settings → Danger Zone → Make public
   ```

2. **Add Supabase secrets:**
   - Go to: Settings → Secrets and variables → Actions
   - Add: `SUPABASE_URL` and `SUPABASE_KEY`

3. **Push and enable:**
   ```bash
   git add .
   git commit -m "Add automated scraper"
   git push
   ```

4. **Check Actions tab** - it will run automatically!

---

## 💡 Why GitHub Actions?

- **Free forever** for public repos
- **Reliable** - runs on GitHub's infrastructure
- **Version controlled** - your automation code is in git
- **Logs** - see all runs and debug easily
- **Manual trigger** - can run on-demand too

**Your scraper will run every 2 hours automatically, storing data in Supabase, completely free!** 🎉
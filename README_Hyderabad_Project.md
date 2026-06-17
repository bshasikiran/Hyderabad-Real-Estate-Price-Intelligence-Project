# Project 1 — Hyderabad Real Estate Price Intelligence

## Why This Project Stands Out
- Live scraping from 99acres (real-time data, not Kaggle CSV)
- Full ETL pipeline (Extract → Transform → Load)
- Business-focused questions with actionable insights
- Deployed Streamlit app with ML model

## Current Status (as of 2026)
99acres uses strong anti-bot protection (reCAPTCHA + WAF). Direct `requests` scraping often returns 403.

**Recommended Approach for Portfolio:**
1. Use the scraper code below (educational)
2. When blocked → Use the **Sample Data Generator** provided
3. Build the full pipeline (cleaning, EDA, modeling, Streamlit)
4. In LinkedIn post: "Built a live scraper + fallback realistic dataset for demonstration"

---

## Step-by-Step Execution Guide

### Step 1: Scraper (Live Attempt)

The file `hyderabad_scraper.py` contains the scraper.

**To run live scraping:**
```bash
python hyderabad_scraper.py
```

It will likely hit CAPTCHA/403. If successful, it saves `hyderabad_properties.csv`.

### Step 2: Generate Realistic Sample Data (Recommended for Demo)

Run the sample data generator to create a high-quality dataset that mimics real 99acres data.
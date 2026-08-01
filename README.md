# QuickBucks - 5 Scrappy Weekend Projects

## What's Inside

```
quickbucks/
├── affiliate-blog/     # VPN review affiliate site (static HTML)
├── api-wrapper/        # Weather API micro-SaaS (Node.js + Stripe)
├── data-broker/        # H1B salary data broker (Python scraper + site)
├── gumroad-farm/       # Spreadsheet/Notion templates for Gumroad
├── resale-bot/         # Discord/Twitter product drop monitor (Python CLI)
└── deploy.sh           # One-click deploy script
```

## Deploy Your Sites (Free)

### Option A: GitHub Pages (2 clicks each)
1. Go to https://github.com/dodontommy/vpnreviews-blog/settings/pages
2. Set Source → "Deploy from branch" → master → / (root) → Save
3. Your site at `https://dodontommy.github.io/vpnreviews-blog`

4. Go to https://github.com/dodontommy/h1b-data-broker/settings/pages
5. Same settings → your site at `https://dodontommy.github.io/h1b-data-broker`

### Option B: Netlify (drag & drop)
1. Go to https://netlify.com
2. Drag `affiliate-blog/` folder → instant deploy
3. Drag `data-broker/site/` folder → instant deploy
4. Attach custom domain if you have one

### Option C: Surge.sh (1 command)
```bash
npx surge affiliate-blog/ vpnreviews-2026.surge.sh
npx surge data-broker/site/ h1b-data-2026.surge.sh
```

## Making Money

### 1. Affiliate Blog (`affiliate-blog/`)
- **How**: Replace placeholder affiliate links with your real ones
- **Where**: Search for "best vpn affiliate program" - ExpressVPN pays $35+/sale
- **Traffic**: Post to Reddit (r/VPN, r/Privacy), Pinterest, SEO grind
- **Potential**: $200-500/mo with 50-100 visitors/day

### 2. API Wrapper (`api-wrapper/`)
- **How**: Deploy on Railway/Render ($5-7/mo), add your Stripe + OpenWeatherMap keys
- **Pricing**: Free tier (100 req/day), Pro $9/mo (1000 req/day)
- **Traffic**: List on RapidAPI marketplace, ProductHunt
- **Potential**: $50-200/mo with 20-30 paid users

### 3. Data Broker (`data-broker/`)
- **How**: Run scraper, sell CSV on Gumroad + your own site
- **Pricing**: Full CSV $19, filtered query $5
- **Traffic**: Post on Reddit (r/data, r/datasets), LinkedIn for recruiters
- **Potential**: $100-300/mo, one-time purchases

### 4. Gumroad Templates (`gumroad-farm/`)
- **How**: Upload to gumroad.com (free account)
- **Pricing**: $5-15 each, bundle $19
- **Traffic**: Pinterest pins, Twitter, Etsy cross-list
- **Potential**: $50-200/mo passive

### 5. Resale Bot (`resale-bot/`)
- **How**: Add Twitter/Discord API keys, set keywords
- **Target**: GPU/PS5 drops, limited sneakers, concert tickets
- **Setup**: Needs 2captcha ($1/1k solves), browser automation
- **Potential**: $200-1000+ per flip, high variance

## One-Time Setup

```bash
# API Wrapper
cd api-wrapper
cp .env.example .env
# Edit .env with your keys
npm install
npm start

# Data Broker
cd data-broker
pip install -r requirements.txt
python scraper.py  # generates 5000 records

# Resale Bot
cd resale-bot
cp .env.example .env
pip install -r requirements.txt
python bot.py monitor
```

## Need Stripe?
Sign up at https://stripe.com (5 min, free).
For the API wrapper, you need:
- STRIPE_SECRET_KEY (from Stripe dashboard)
- STRIPE_WEBHOOK_SECRET (from Stripe > Webhooks)

## Repos
- Main: https://github.com/dodontommy/quickbucks
- Affiliate Blog: https://github.com/dodontommy/vpnreviews-blog
- Data Broker: https://github.com/dodontommy/h1b-data-broker
# H1B Salary Database — Data Broker Micro-Site

Scrapes publicly available H1B visa salary data from USCIS disclosures and
packages it as a clean CSV for sale.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the scraper
make scrape
# or: python scraper.py

# Preview the landing page
make serve
# then open http://localhost:8000 in your browser
```

## What the Scraper Does

`scraper.py` attempts to fetch live data from the USCIS employer data hub.
If the live fetch fails (the site uses JavaScript or blocks scrapers), it
falls back to generating **realistic synthetic data** modeled on public
H1B filings — accurate company names, job titles, salary distributions,
and locations.

Output is written to `data/h1b_salary_data_2026.csv` (default: 5,000 rows).

### Columns

| Column    | Description                                      |
|-----------|--------------------------------------------------|
| company   | Employer name (e.g. GOOGLE LLC)                  |
| job_title | Role (e.g. Senior Software Engineer)             |
| salary    | Annual salary in USD                             |
| location  | City, State (e.g. Mountain View, CA)             |
| year      | Filing year (2024–2026)                          |

## Landing Page

`site/index.html` is a self-contained, responsive marketing page with:

- Hero with key stats (record count, median salary, etc.)
- Features grid explaining the data
- Sample data table (5 rows)
- Pricing cards ($5 filtered query / $19 full dataset)
- Buy buttons (placeholder — replace `alert()` with Stripe/Gumroad)
- Contact / About section

## Deploying the Site

Upload the `site/` directory to any static host:

| Platform       | How                                         |
|----------------|---------------------------------------------|
| **Netlify**    | Drag `site/` onto deploy                    |
| **Vercel**     | `vercel --cwd site`                         |
| **GitHub Pages** | Push to `username.github.io` repo          |
| **S3 / CloudFront** | `aws s3 sync site/ s3://your-bucket` |

The page is 100% static — no build step, no framework, no backend needed.

## Directory Structure

```
data-broker/
├── scraper.py          # Main scraper script
├── requirements.txt    # Python dependencies
├── Makefile            # Targets: scrape, serve, clean
├── README.md           # This file
├── data/               # Generated CSVs go here
└── site/               # Static landing page
    ├── index.html      # Marketing page (all inline CSS)
    └── sample_data.json # Auto-generated sample rows
```

## License

Data sourced from public USCIS filings (FOIA). The scraper code is MIT.
The dataset itself has no restrictions — distribute freely.
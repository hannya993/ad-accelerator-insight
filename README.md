# A&D Accelerator Insight Dashboard

An interactive portfolio intelligence dashboard built to map and analyse 
the Starburst Aerospace & Defense accelerator's 91 portfolio companies 
across 19 countries and 3 continents.

**Live Dashboard → [View Here](https://yourusername.github.io/ad-accelerator-insight)**

---

## What This Project Does

- Scrapes live startup data directly from the Starburst accelerator website
- Cleans and standardises inconsistent location data across 91 companies
- Classifies each startup into one of 8 technology sectors
- Visualises everything on an interactive drill-down world map
- Continent → Country → Startup navigation with smooth zoom animations
- Click-to-explore pie chart showing category distribution by continent
- Startup detail panel with summary and location data

---

## How It Was Built — End to End

### Step 1 — Web Scraping (`scraper.py`)

The Starburst portfolio page loads startups dynamically via WordPress AJAX 
pagination — meaning a standard scrape of the HTML wouldn't work. 

The scraper reverse-engineered the AJAX endpoint (`wp-admin/admin-ajax.php`) 
by inspecting the network requests in the browser, then looped through all 
pages posting the correct payload until no new startups were returned.

For each startup it extracted:
- **Name** — from the anchor tag
- **Location** — from the `startup__location` div
- **Summary** — from the `startup__excerpt` div

Output: `starburst_portfolio.xlsx` — 91 startups across 4 columns

This step alone required multiple iterations to handle:
- Dynamic JavaScript rendering (not static HTML)
- Pagination via AJAX POST requests rather than URL parameters
- Deduplication of startups across pages
- Missing or malformed HTML in some cards

---

### Step 2 — Data Cleaning (`cleaning_pipeline.py`)

The raw location data was completely inconsistent. Examples of what we were 
dealing with:

| Raw Location | Problem |
|---|---|
| `Ile-de-France region FRANCE` | Region not city, inconsistent caps |
| `Bangalo India` | Typo (Bangalore) |
| `USA USA` | Duplicate, no city |
| `Salt Lake City, Utah, USA` | Comma-separated vs space-separated |
| `Tel Aviv Israel` | No comma separator |
| `Fomebu Norway` | Misspelling (Fornebu) |

Built a manual lookup table mapping all 91 unique raw location strings to 
clean structured fields: `city`, `state`, `country`, `continent`, `lat`, `lng`.

Also added precise GPS coordinates for every city to enable map placement.

Output: `starburst_clean.csv`

---

### Step 3 — Category Classification (`cleaning_pipeline.py`)

No category data existed in the source. Built a keyword-based classifier 
that matched each startup's summary against 8 sector keyword lists:

| Category | Example Keywords |
|---|---|
| Space & Launch | satellite, orbit, launch, constellation |
| Drones & UAV | drone, uav, vtol, autopilot |
| Propulsion | engine, thruster, fuel, hydrogen |
| AI & Software | ai, platform, autonomous, data |
| Comms & Sensing | radar, antenna, sensor, bandwidth |
| Cybersecurity | encryption, jamming, zero-trust |
| Aviation | aircraft, flight, airspace, pilot |
| Manufacturing | composite, 3d printing, materials |

Manually reviewed and corrected all 91 classifications after the automated 
pass to fix edge cases where keyword matching was ambiguous.

Output: `starburst_portfolio_categorised.xlsx`, `startups_with_categories.json`

---

### Step 4 — Dashboard (`index.html`)

Built a single self-contained HTML/JS file — no backend, no framework, 
no build step. All 91 startups are embedded directly in the file.

Key technical decisions:
- **Leaflet.js** for the interactive map with custom div markers
- **Chart.js** for the portfolio breakdown pie chart  
- **CartoDBs dark_nolabels tile** as the base map with custom English 
  continent labels rendered as Leaflet markers (to avoid the default 
  multi-language tile labels)
- Pure CSS flexbox layout so it works in any browser without dependencies
- Drill-down state machine: world → continent → country → startup

---

## Repo Structure

| File | Description |
|---|---|
| `index.html` | The live dashboard — open in any browser |
| `scraper.py` | Web scraper that pulls data from starburst.aero |
| `cleaning_pipeline.py` | Location cleaning, coordinate mapping, category classification |
| `starburst_portfolio.xlsx` | Raw scraped data |
| `starburst_clean.csv` | Cleaned data with coordinates and geography |
| `starburst_portfolio_categorised.xlsx` | Data with category classification for review |
| `startups_with_categories.json` | Final structured data used by the dashboard |

---

## How to Re-run the Pipeline

```bash
# Install dependencies
pip install requests beautifulsoup4 openpyxl pandas

# Step 1 — scrape fresh data from starburst.aero
python scraper.py
# outputs: starburst_portfolio.xlsx

# Step 2 — clean locations and classify categories
python cleaning_pipeline.py
# outputs: starburst_clean.csv, startups_with_categories.json

# Step 3 — open the dashboard
# Just open index.html in any browser
```

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Python — requests, BeautifulSoup | Web scraping |
| Python — Pandas, openpyxl | Data cleaning and Excel output |
| HTML / CSS / JavaScript | Dashboard |
| Leaflet.js | Interactive map |
| Chart.js | Pie chart |
| GitHub Pages | Hosting |

---

## Why This Project

Built as a personal research project to understand the Starburst A&D 
accelerator portfolio — what sectors they back, where their companies 
are concentrated, and how the portfolio breaks down geographically. 
The goal was to produce something a VC analyst would actually find 
useful, not just a visualisation exercise.

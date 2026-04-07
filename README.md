# A&D Accelerator Insight Dashboard

An interactive portfolio intelligence dashboard built to map and analyze aerospace & defense accelerator portfolios. Currently loaded with Starburst Aerospace & Defense as the first accelerator — architected from the start to support multiple accelerators as the platform grows.

**Live Dashboard → [View Here](https://hannya993.github.io/ad-accelerator-insight)**

---

## What This Project Does

- Scrapes live startup data directly from accelerator websites
- Cleans and standardizes inconsistent location data across portfolio companies
- Classifies each startup into one of 8 technology sectors
- Visualizes everything on an interactive drill-down world map
- Continent → Country → Startup navigation with smooth zoom animations
- Click-to-explore pie chart showing category distribution by continent
- Startup detail panel with summary and location data
- Dropdown menu ready to plug in additional accelerators

---

## Current Coverage

| Accelerator | Portfolio Size | Countries | Continents |
|---|---|---|---|
| Starburst Aerospace & Defense | 91 companies | 19 | 3 |
| More coming soon | — | — | — |

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

This step required multiple iterations to handle:
- Dynamic JavaScript rendering (not static HTML)
- Pagination via AJAX POST requests rather than URL parameters
- Deduplication of startups across pages
- Missing or malformed HTML in some cards

---

### Step 2 — Data Cleaning (`cleaning_pipeline.py`)

The raw location data was completely inconsistent. Examples of what needed fixing:

| Raw Location | Problem |
|---|---|
| `Ile-de-France region FRANCE` | Region not city, inconsistent capitalization |
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
no build step required. All data is embedded directly in the file.

Key technical decisions:
- **Leaflet.js** for the interactive map with custom div markers
- **Chart.js** for the portfolio breakdown pie chart
- **CartoDBs dark_nolabels tile** as the base map with custom English
  continent labels rendered as Leaflet markers
- Pure CSS flexbox layout so it works in any browser without dependencies
- Drill-down state machine: world → continent → country → startup
- Accelerator dropdown in the header built to scale as more datasets are added

---

## Repo Structure

| File | Description |
|---|---|
| `index.html` | The live dashboard — open in any browser |
| `scraper.py` | Web scraper that pulls data from accelerator websites |
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

# Step 1 — scrape fresh data
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

## Roadmap

- [ ] Add additional A&D accelerators (Founder's Factory, Air Force Accelerator, etc.)
- [ ] Add funding stage and amount raised per startup
- [ ] Add latest news headlines per startup via news API
- [ ] Add performance insights panel (revenue signals, funding progression)
- [ ] Build accelerator comparison view across portfolios

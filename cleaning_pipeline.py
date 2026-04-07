"""
cleaning_pipeline.py
--------------------
Takes the raw starburst_portfolio.xlsx scraped file and produces:
  - starburst_clean.csv        : cleaned locations with coordinates
  - startups_with_categories.json : final data used by the dashboard
  - starburst_portfolio_categorised.xlsx : Excel with category column for review
"""

import pandas as pd
import json
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
from collections import Counter

# ── STEP 1: LOAD RAW DATA ─────────────────────────────────────────────────────

df = pd.read_excel('starburst_portfolio.xlsx')
print(f"Loaded {len(df)} startups")

# ── STEP 2: LOCATION LOOKUP TABLE ────────────────────────────────────────────
# Maps every raw location string exactly as scraped → (city, state, country, continent)
# Required because the raw data has no consistent format

location_map = {
    "Hollister CA":                               ("Hollister", "California", "USA", "North America"),
    "Austin TX":                                  ("Austin", "Texas", "USA", "North America"),
    "Philadelphia PA":                            ("Philadelphia", "Pennsylvania", "USA", "North America"),
    "New York NY":                                ("New York", "New York", "USA", "North America"),
    "San Leandro CA":                             ("San Leandro", "California", "USA", "North America"),
    "San Francisco CA":                           ("San Francisco", "California", "USA", "North America"),
    "Hawthorne CA":                               ("Hawthorne", "California", "USA", "North America"),
    "Pasadena CA":                                ("Pasadena", "California", "USA", "North America"),
    "Santa Clara CA":                             ("Santa Clara", "California", "USA", "North America"),
    "Culver City CA":                             ("Culver City", "California", "USA", "North America"),
    "Santa Monica CA":                            ("Santa Monica", "California", "USA", "North America"),
    "Los Angeles CA":                             ("Los Angeles", "California", "USA", "North America"),
    "West Jordan UT":                             ("West Jordan", "Utah", "USA", "North America"),
    "San Luis Obispo CA":                         ("San Luis Obispo", "California", "USA", "North America"),
    "Richmond CA":                                ("Richmond", "California", "USA", "North America"),
    "Atlanta GA":                                 ("Atlanta", "Georgia", "USA", "North America"),
    "Seattle WA":                                 ("Seattle", "Washington", "USA", "North America"),
    "San Diego CA":                               ("San Diego", "California", "USA", "North America"),
    "Pittsburgh PA":                              ("Pittsburgh", "Pennsylvania", "USA", "North America"),
    "Brooklyn NY":                                ("Brooklyn", "New York", "USA", "North America"),
    "Long Beach United States":                   ("Long Beach", "California", "USA", "North America"),
    "Salt Lake City, Utah, USA":                  ("Salt Lake City", "Utah", "USA", "North America"),
    "Daytona Beach, FL, USA":                     ("Daytona Beach", "Florida", "USA", "North America"),
    "USA USA":                                    ("Unknown", "", "USA", "North America"),
    "Syracuse, NY, USA":                          ("Syracuse", "New York", "USA", "North America"),
    "Aiken, South Carolina, USA":                 ("Aiken", "South Carolina", "USA", "North America"),
    "Montreal Canada":                            ("Montreal", "Quebec", "Canada", "North America"),
    "Bangkok Thailand":                           ("Bangkok", "", "Thailand", "Asia"),
    "Tel Aviv Israel":                            ("Tel Aviv", "", "Israel", "Asia"),
    "Caesarea, Israel":                           ("Caesarea", "", "Israel", "Asia"),
    "Ra'anana Israel":                            ("Ra'anana", "", "Israel", "Asia"),
    "Tel-Aviv Israel":                            ("Tel Aviv", "", "Israel", "Asia"),
    "Natanya Israel":                             ("Natanya", "", "Israel", "Asia"),
    "Yokne'am Israel":                            ("Yokne'am", "", "Israel", "Asia"),
    "London UK":                                  ("London", "", "UK", "Europe"),
    "London, UK":                                 ("London", "", "UK", "Europe"),
    "Fomebu Norway":                              ("Fornebu", "", "Norway", "Europe"),
    "Tartu Estonia":                              ("Tartu", "", "Estonia", "Europe"),
    "Paris France":                               ("Paris", "", "France", "Europe"),
    "Paris, France":                              ("Paris", "", "France", "Europe"),
    "Grenoble France":                            ("Grenoble", "", "France", "Europe"),
    "Orsay France":                               ("Orsay", "", "France", "Europe"),
    "Toulouse France":                            ("Toulouse", "", "France", "Europe"),
    "Aix-en-Provence France":                     ("Aix-en-Provence", "", "France", "Europe"),
    "Ile-de-France region FRANCE":                ("Paris", "Ile-de-France", "France", "Europe"),
    "Ile-de-France region France":                ("Paris", "Ile-de-France", "France", "Europe"),
    "Merignac, Nouvelle-Aquitaine France":        ("Merignac", "Nouvelle-Aquitaine", "France", "Europe"),
    "Sylphaero":                                  ("Merignac", "Nouvelle-Aquitaine", "France", "Europe"),
    "Toulouse, Occitanie France":                 ("Toulouse", "Occitanie", "France", "Europe"),
    "Bordeaux, Nouvelle-Aquitaine France":        ("Bordeaux", "Nouvelle-Aquitaine", "France", "Europe"),
    "Reims, Grand-Est France":                    ("Reims", "Grand Est", "France", "Europe"),
    "Poitiers, Nouvelle-Aquitaine France":        ("Poitiers", "Nouvelle-Aquitaine", "France", "Europe"),
    "Brest, Bretagne France":                     ("Brest", "Bretagne", "France", "Europe"),
    "Pertuis, Provence-Alpes-Cote d'Azur France": ("Pertuis", "Provence-Alpes-Cote d'Azur", "France", "Europe"),
    "Germany":                                    ("Unknown", "", "Germany", "Europe"),
    "Dresden, Germany":                           ("Dresden", "Saxony", "Germany", "Europe"),
    "Munich GERMANY":                             ("Munich", "Bavaria", "Germany", "Europe"),
    "Hamburg Germany":                            ("Hamburg", "", "Germany", "Europe"),
    "Netherlands Netherlands":                    ("Unknown", "", "Netherlands", "Europe"),
    "Madrid Spain":                               ("Madrid", "", "Spain", "Europe"),
    "Coimbra Portugal":                           ("Coimbra", "", "Portugal", "Europe"),
    "Rzeszow Poland":                             ("Rzeszow", "", "Poland", "Europe"),
    "Athens Greece":                              ("Athens", "", "Greece", "Europe"),
    "Singapore Singapore":                        ("Singapore", "", "Singapore", "Asia"),
    "Tokyo Japan":                                ("Tokyo", "", "Japan", "Asia"),
    "Bangalo India":                              ("Bangalore", "Karnataka", "India", "Asia"),
    "Hyderabad India":                            ("Hyderabad", "Telangana", "India", "Asia"),
    "Vizag India":                                ("Visakhapatnam", "Andhra Pradesh", "India", "Asia"),
    "South Korea":                                ("Unknown", "", "South Korea", "Asia"),
}

# GPS coordinates for each city
city_coords = {
    "Hollister": (36.85, -121.40), "Austin": (30.27, -97.74),
    "Philadelphia": (39.95, -75.17), "New York": (40.71, -74.01),
    "San Leandro": (37.73, -122.16), "San Francisco": (37.77, -122.42),
    "Hawthorne": (33.89, -118.35), "Pasadena": (34.15, -118.14),
    "Santa Clara": (37.35, -121.95), "Culver City": (34.02, -118.40),
    "Santa Monica": (34.02, -118.49), "Los Angeles": (34.05, -118.24),
    "West Jordan": (40.60, -111.99), "San Luis Obispo": (35.28, -120.66),
    "Richmond": (37.94, -122.35), "Atlanta": (33.75, -84.39),
    "Seattle": (47.61, -122.33), "San Diego": (32.72, -117.15),
    "Pittsburgh": (40.44, -79.99), "Brooklyn": (40.65, -73.95),
    "Long Beach": (33.77, -118.19), "Salt Lake City": (40.76, -111.89),
    "Daytona Beach": (29.21, -81.02), "Syracuse": (43.05, -76.15),
    "Aiken": (33.56, -81.72), "Montreal": (45.50, -73.57),
    "Bangkok": (13.76, 100.50), "Tel Aviv": (32.09, 34.79),
    "Caesarea": (32.50, 34.90), "Ra'anana": (32.18, 34.87),
    "Natanya": (32.32, 34.86), "Yokne'am": (32.66, 35.11),
    "London": (51.51, -0.13), "Fornebu": (59.90, 10.62),
    "Tartu": (58.38, 26.72), "Paris": (48.86, 2.35),
    "Grenoble": (45.19, 5.72), "Orsay": (48.70, 2.19),
    "Toulouse": (43.60, 1.44), "Aix-en-Provence": (43.53, 5.45),
    "Merignac": (44.83, -0.64), "Bordeaux": (44.84, -0.58),
    "Reims": (49.26, 4.03), "Poitiers": (46.58, 0.34),
    "Brest": (48.39, -4.49), "Pertuis": (43.69, 5.50),
    "Dresden": (51.05, 13.74), "Munich": (48.14, 11.58),
    "Hamburg": (53.55, 9.99), "Madrid": (40.42, -3.70),
    "Coimbra": (40.21, -8.43), "Rzeszow": (50.04, 22.00),
    "Athens": (37.98, 23.73), "Singapore": (1.35, 103.82),
    "Tokyo": (35.69, 139.69), "Bangalore": (12.97, 77.59),
    "Hyderabad": (17.39, 78.49), "Visakhapatnam": (17.69, 83.22),
    "Unknown": (0.0, 0.0),
}

# ── STEP 3: APPLY MAPPING ─────────────────────────────────────────────────────

rows = []
unmapped = []
for _, row in df.iterrows():
    loc = str(row['Location']).strip() if pd.notna(row['Location']) else ""
    mapped = location_map.get(loc)
    if mapped:
        city, state, country, continent = mapped
    else:
        unmapped.append(loc)
        city, state, country, continent = ("Unknown", "", "Unknown", "Unknown")
    lat, lng = city_coords.get(city, (0.0, 0.0))
    rows.append({
        "id": int(row['#']),
        "name": str(row['Startup Name']),
        "location_raw": loc,
        "city": city,
        "state": state,
        "country": country,
        "continent": continent,
        "lat": lat,
        "lng": lng,
        "summary": str(row['Summary']) if pd.notna(row['Summary']) else ""
    })

if unmapped:
    print(f"WARNING: {len(unmapped)} unmapped locations: {unmapped}")

clean_df = pd.DataFrame(rows)
clean_df.to_csv('starburst_clean.csv', index=False)
print(f"Saved starburst_clean.csv")

# ── STEP 4: CATEGORY CLASSIFICATION ──────────────────────────────────────────
# Keyword-based classifier — priority ordered, first match wins

CATS = [
    ('Space & Launch',  '#00d4ff', ['satellite','space','orbit','launch','launcher','nanosat','in-space','spacecraft','constellation','earth observation','micro-launcher']),
    ('Drones & UAV',    '#ff6b35', ['drone','uav','vtol','evtol','unmanned','uas','docking','autopilot','aam','airside','aerial']),
    ('Propulsion',      '#7fff6b', ['propulsion','engine','thruster','rocket','fuel','hydrogen','battery','lithium','electric propulsion','plasma','hybrid rocket','cryogenic']),
    ('AI & Software',   '#ffd166', ['ai','artificial intelligence','software','platform','data','analytics','framework','management','autonomy','autonomous','computing','quantum computing','prediction']),
    ('Comms & Sensing', '#c77dff', ['communication','sensor','rf','radar','antenna','bandwidth','laser','connectivity','wireless','isr','monitoring','detection','observation','imaging']),
    ('Cybersecurity',   '#ff4d6d', ['cyber','security','encryption','authentication','jamming','zero-trust','blockchain','cryptograph']),
    ('Aviation',        '#48cae4', ['aviation','aircraft','flight','airspace','maintenance','atc','air traffic','landing','pilot','air taxi']),
    ('Manufacturing',   '#f4a261', ['manufacturing','composite','printing','3d','supply chain','parts','materials','additive']),
]

def classify(summary):
    s = summary.lower()
    for name, color, kws in CATS:
        if any(k in s for k in kws):
            return name, color
    return 'Other', '#888888'

# Manual overrides where keyword matching was wrong
OVERRIDES = {
    'Clarvoyant':                       ('AI & Software',   '#ffd166'),
    'Limatech':                         ('Propulsion',      '#7fff6b'),
    'Ampaire':                          ('Aviation',        '#48cae4'),
    'Red 6':                            ('Aviation',        '#48cae4'),
    'Odys Aviation':                    ('Drones & UAV',    '#ff6b35'),
    'Stratolia':                        ('Space & Launch',  '#00d4ff'),
    'Miratlas':                         ('Comms & Sensing', '#c77dff'),
    'Whitefox Defense Technologies':    ('Drones & UAV',    '#ff6b35'),
    'Prime Lightworks':                 ('Propulsion',      '#7fff6b'),
    'Near Earth Autonomy':              ('Drones & UAV',    '#ff6b35'),
    'SeRo Systems':                     ('Comms & Sensing', '#c77dff'),
    'ResilienX':                        ('Aviation',        '#48cae4'),
    'Emproof':                          ('Cybersecurity',   '#ff4d6d'),
    'Arkane':                           ('Comms & Sensing', '#c77dff'),
    'Disaitek':                         ('AI & Software',   '#ffd166'),
    'Meoss':                            ('Comms & Sensing', '#c77dff'),
    'SpacEngineer':                     ('Manufacturing',   '#f4a261'),
    'precursor SPC':                    ('Comms & Sensing', '#c77dff'),
}

final = []
for r in rows:
    if r['name'] in OVERRIDES:
        cat, color = OVERRIDES[r['name']]
    else:
        cat, color = classify(r['summary'])
    final.append({**r, 'category': cat, 'cat_color': color})

# ── STEP 5: EXPORT JSON ───────────────────────────────────────────────────────

with open('startups_with_categories.json', 'w') as f:
    json.dump(final, f, indent=2)
print(f"Saved startups_with_categories.json")

# ── STEP 6: EXPORT CATEGORISED EXCEL FOR REVIEW ───────────────────────────────

review_df = pd.DataFrame(final)[['id','name','city','state','country','continent','summary','category']]
review_df.columns = ['#','Startup Name','City','State','Country','Continent','Summary','Category']
review_df.to_excel('starburst_portfolio_categorised.xlsx', index=False)
print(f"Saved starburst_portfolio_categorised.xlsx")

# ── SUMMARY ───────────────────────────────────────────────────────────────────

counts = Counter(r['category'] for r in final)
print("\n=== CATEGORY BREAKDOWN ===")
for cat, count in sorted(counts.items(), key=lambda x: -x[1]):
    print(f"  {cat:25s} {count:3d}  ({round(count/len(final)*100)}%)")

print(f"\nContinent breakdown:")
cont_counts = Counter(r['continent'] for r in final)
for cont, count in sorted(cont_counts.items(), key=lambda x: -x[1]):
    print(f"  {cont:20s} {count}")

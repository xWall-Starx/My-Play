import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import requests
import json
import re
import io
import hashlib
import html
import os
import math
import uuid
import mimetypes
import subprocess
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from supabase import create_client


try:
    from openai import OpenAI
    OPENAI_STT_AVAILABLE = True
except Exception:
    OpenAI = None
    OPENAI_STT_AVAILABLE = False

try:
    from streamlit_geolocation import streamlit_geolocation
    GEOLOCATION_AVAILABLE = True
except Exception:
    GEOLOCATION_AVAILABLE = False

# ============================================================
# MY PLAY V4 — MY PLAYER V1
# Internet-connected Personal Golf Caddie
# ============================================================

st.set_page_config(
    page_title="My Play",
    page_icon="⛳",
    layout="wide"
)

st.markdown(
    """
    <style>
    /* My Play design system: calm, spacious, mobile-first. */
    :root {
        --myplay-green: #39775d;
        --myplay-green-soft: color-mix(in srgb, var(--primary-color) 5%, var(--background-color));
        --myplay-ink: var(--text-color);
        --myplay-muted: color-mix(in srgb, var(--text-color) 68%, transparent);
        --myplay-border: color-mix(in srgb, var(--text-color) 16%, transparent);
        --myplay-surface: var(--secondary-background-color);
    }
    .block-container { max-width: 1180px; padding-top: 1.4rem; padding-bottom: 4rem; }
    h1, h2, h3 { color: var(--myplay-ink); letter-spacing: -0.02em; }
    p, label, .stCaption { line-height: 1.55; }
    div[data-testid="stAlert"] { margin-top: 0.25rem; margin-bottom: 0.25rem; }
    div[data-testid="stMetric"] { padding: 0.1rem 0; }
    div[data-testid="stExpander"] {
        margin-bottom: 0.75rem;
        border: 1px solid var(--myplay-border);
        border-radius: 1rem;
        background: color-mix(in srgb, var(--secondary-background-color) 98%, var(--text-color) 2%);
        box-shadow: 0 5px 18px rgba(0, 0, 0, 0.07);
        overflow: hidden;
        transition: border-color 140ms ease, box-shadow 140ms ease, transform 140ms ease;
    }
    div[data-testid="stExpander"]:hover {
        border-color: color-mix(in srgb, var(--primary-color) 34%, var(--myplay-border));
        box-shadow: 0 9px 24px rgba(0, 0, 0, 0.11);
        transform: translateY(-1px);
    }
    div[data-testid="stExpander"] details { border: 0; border-radius: 1rem; }
    div[data-testid="stExpander"] summary {
        min-height: 3.6rem;
        padding: 0.45rem 0.85rem;
        font-weight: 720;
        letter-spacing: -0.01em;
    }
    div[data-testid="stExpander"] summary:hover {
        background: color-mix(in srgb, var(--text-color) 4%, transparent);
    }
    .stButton > button { min-height: 2.75rem; border-radius: 0.75rem; font-weight: 650; }
    .stButton > button[kind="primary"] { background: var(--myplay-green); border-color: var(--myplay-green); }
    div[data-baseweb="select"] > div, .stTextInput input, .stNumberInput input,
    .stTextArea textarea {
        border-radius: 0.9rem;
        border-color: var(--myplay-border);
        background: var(--secondary-background-color);
    }
    div[data-testid="stDataFrame"] { border: 1px solid var(--myplay-border); border-radius: 0.8rem; overflow: hidden; }
    div[data-baseweb="tab-list"] { gap: 0.4rem; }
    button[data-baseweb="tab"] { border-radius: 0.7rem 0.7rem 0 0; padding-left: 1rem; padding-right: 1rem; }
    .myplay-hero {
        padding: 1.25rem 1.35rem;
        border: 1px solid var(--myplay-border);
        border-radius: 1rem;
        background: linear-gradient(135deg, var(--myplay-surface) 0%, var(--myplay-green-soft) 100%);
        margin-bottom: 1rem;
    }
    .myplay-hero h2 { margin: 0 0 0.25rem 0; }
    .myplay-hero p { color: var(--myplay-muted); margin: 0; }
    .myplay-card {
        min-height: 126px;
        padding: 1rem;
        border: 1px solid var(--myplay-border);
        border-radius: 0.9rem;
        background: var(--myplay-surface);
        box-shadow: 0 4px 18px rgba(19, 49, 33, 0.05);
    }
    .myplay-card h4 { margin: 0 0 0.35rem 0; color: var(--myplay-ink); }
    .myplay-card p { margin: 0; color: var(--myplay-muted); font-size: 0.92rem; }
    .myplay-profile-banner {
        padding: 1.2rem 1.3rem;
        border: 1px solid var(--myplay-border);
        border-radius: 1rem;
        background: linear-gradient(125deg, var(--myplay-surface), var(--myplay-green-soft));
        margin-bottom: 0.85rem;
    }
    .myplay-profile-banner h2 { margin: 0 0 0.25rem 0; }
    .myplay-profile-banner p { margin: 0; color: var(--myplay-muted); }
    .myplay-eyebrow { color: var(--myplay-green); font-weight: 750; letter-spacing: 0.08em; font-size: 0.78rem; }
    .myplay-insight {
        padding: 0.85rem 0;
        border-bottom: 1px solid var(--myplay-border);
    }
    .myplay-insight:last-child { border-bottom: 0; }
    .myplay-insight strong { display: block; margin-bottom: 0.16rem; }
    .myplay-insight span { color: var(--myplay-muted); }
    .myplay-brandbar { display: flex; align-items: center; gap: 0.85rem; }
    .myplay-brandmark {
        width: 3rem;
        height: 3rem;
        display: grid;
        place-items: center;
        border-radius: 0.9rem;
        background: color-mix(in srgb, var(--text-color) 10%, var(--secondary-background-color));
        color: var(--text-color);
        font-weight: 900;
        letter-spacing: -0.08em;
        box-shadow: 0 7px 20px rgba(0, 0, 0, 0.10);
    }
    .myplay-brandcopy h1 { margin: 0; }
    .myplay-brandcopy p { margin: 0; color: var(--myplay-muted); font-size: 0.88rem; }
    [class*="st-key-club_card_"] button {
        min-height: 8.5rem;
        width: 100%;
        padding: 1rem 1.05rem;
        justify-content: flex-start;
        text-align: left;
        white-space: pre-line;
        line-height: 1.45;
        border: 1px solid color-mix(in srgb, var(--text-color) 16%, transparent);
        border-radius: 1rem;
        background: var(--secondary-background-color);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
        transition: border-color 120ms ease, transform 120ms ease, box-shadow 120ms ease;
    }
    [class*="st-key-club_card_"] button:hover {
        border-color: var(--primary-color);
        transform: translateY(-2px);
        box-shadow: 0 8px 22px rgba(0, 0, 0, 0.13);
    }
    [class*="st-key-club_card_"] button p {
        white-space: pre-line;
        text-align: left;
        width: 100%;
    }
    div[data-testid="stAudioInput"] { margin-top: 0.2rem; margin-bottom: 0.2rem; }
    div[data-testid="stChatMessage"] { padding-top: 0.35rem; padding-bottom: 0.35rem; }
    @media (max-width: 700px) {
        .block-container { padding: 0.8rem 0.8rem 3rem; }
        .myplay-card { min-height: auto; }
        button[data-baseweb="tab"] { padding-left: 0.55rem; padding-right: 0.55rem; }
    }
    </style>
    """,
    unsafe_allow_html=True
)

PROFILE_FILE = "player_profile.json"
GAME_PROFILE_FILE = "my_game_profile.json"
BAG_FILE = "my_bag.json"
SHOT_FILE = "shot_history.csv"
REMINDER_FILE = "swing_reminders.txt"
COURSE_CACHE_FILE = "course_cache.json"
ACTIVE_ROUND_FILE = "active_round.json"
ROUND_HISTORY_FILE = "round_history.csv"
PLAYER_EVIDENCE_FILE = "player_evidence.csv"
RAW_IMPORT_DIR = "raw_imports"
SWING_VIDEO_FILE = "swing_video_history.csv"
SWING_VIDEO_DIR = "swing_videos"
LOCAL_COURSE_FILE = "opengolfapi-us.csv.gz"
LOCAL_COURSE_URL = "https://raw.githubusercontent.com/opengolfapi/data/main/opengolfapi-us.csv.gz"
CUSTOM_COURSE_LIBRARY_FILE = "community_course_library.json"
COURSE_SUBMISSION_FILE = "course_submissions.json"

OPEN_GOLF_BASE = "https://api.opengolfapi.org"
NOMINATIM_BASE = "https://nominatim.openstreetmap.org/search"
OVERPASS_URL = "https://overpass-api.de/api/interpreter"

DEFAULT_PROFILE = {
    "display_name": "",
    "handedness": "Right-handed",
    "handicap": "",
    "typical_score": "",
    "experience_level": "Developing",
    "preferred_scoring_leave": 100,
    "default_course": "",
    "default_state": "NJ"
}

DEFAULT_GAME_PROFILE = {
    "driver_miss": "unknown",
    "wood_miss": "unknown",
    "iron_miss": "unknown",
    "wedge_miss": "unknown",
    "normal_shot_shape": "Unknown",
    "strongest_area": "Not selected",
    "weakest_area": "Not selected",
    "preferred_approach_distance": 100,
    "trouble_tendency": "Not selected",
    "playing_priority": "Balanced",
}

DEFAULT_BAG = [
    {"Club": "Driver", "Brand / Model": "Callaway", "Loft": "10°", "Stock Carry": 265, "Typical Miss": "fade right"},
    {"Club": "3 Wood", "Brand / Model": "Ping", "Loft": "", "Stock Carry": 220, "Typical Miss": "fade right"},
    {"Club": "3 Hybrid", "Brand / Model": "Callaway", "Loft": "", "Stock Carry": 210, "Typical Miss": "low liner"},
    {"Club": "5 Iron", "Brand / Model": "TaylorMade P790", "Loft": "", "Stock Carry": 200, "Typical Miss": "slight pull"},
    {"Club": "6 Iron", "Brand / Model": "TaylorMade P790", "Loft": "", "Stock Carry": 185, "Typical Miss": "slight pull"},
    {"Club": "7 Iron", "Brand / Model": "TaylorMade P790", "Loft": "", "Stock Carry": 175, "Typical Miss": "slight pull"},
    {"Club": "8 Iron", "Brand / Model": "TaylorMade P790", "Loft": "", "Stock Carry": 165, "Typical Miss": "slight pull"},
    {"Club": "9 Iron", "Brand / Model": "TaylorMade P790", "Loft": "", "Stock Carry": 150, "Typical Miss": "slight fade"},
    {"Club": "48° Wedge", "Brand / Model": "Titleist Vokey", "Loft": "48°", "Stock Carry": 135, "Typical Miss": "slight pull"},
    {"Club": "52° Wedge", "Brand / Model": "Titleist Vokey", "Loft": "52°", "Stock Carry": 125, "Typical Miss": "slight pull"},
    {"Club": "56° Wedge", "Brand / Model": "Mizuno", "Loft": "56°", "Stock Carry": 110, "Typical Miss": "slight pull"},
    {"Club": "60° Wedge", "Brand / Model": "Titleist Vokey", "Loft": "60°", "Stock Carry": 100, "Typical Miss": "slight pull"}
]


# Controlled club vocabulary. Display labels stay friendly while canonical IDs
# keep analytics, imports, voice commands, and the caddie consistent.
CLUB_CATALOG = {
    "Driver": ["Driver", "Mini Driver"],
    "Fairway Wood": [f"{number} Wood" for number in range(2, 16)],
    "Hybrid / Rescue": [f"{number} Hybrid" for number in range(1, 10)],
    "Utility / Driving Iron": [
        f"{number} Utility Iron" for number in range(1, 7)
    ] + [f"{number} Driving Iron" for number in range(1, 7)],
    "Iron": [f"{number} Iron" for number in range(1, 10)],
    "Wedge": [
        "Pitching Wedge",
        "Approach Wedge",
        "Gap Wedge",
        "Sand Wedge",
        "Lob Wedge",
    ] + [f"{loft}° Wedge" for loft in range(40, 73)],
    "Chipper": ["Chipper"],
    "Putter": [
        "Blade Putter",
        "Mallet Putter",
        "Mid-Mallet Putter",
        "Armlock Putter",
        "Broomstick Putter",
        "Putter",
    ],
    "Other / Custom": ["Custom Club"],
}

CLUB_BRANDS = ["Select Brand"] + sorted([
    "Adams", "Argolf", "Armour", "Axis1", "Ben Hogan", "Bettinardi",
    "Boccieri", "BombTech", "Bridgestone", "Browning", "Burke",
    "Byron Morgan", "Callaway", "Cleveland", "Cobra", "Costco Kirkland",
    "Cure", "Edel", "Fourteen", "Founders Club", "Gauge Design", "Geek Golf",
    "GigaGolf", "Haywood", "Honma", "Inesis", "KZG", "LAB Golf", "Lazrus",
    "MacGregor", "Majek", "Maltby", "Miura", "Mizuno", "National Custom Works",
    "Never Compromise", "Nike", "Odyssey", "OnOff", "Orka", "Orlimar",
    "Parsons Xtreme Golf (PXG)", "Ping", "PowerBilt", "PRGR", "PXG", "Ram",
    "Ray Cook", "Robin Golf", "Royal Collection", "Scotty Cameron", "SeeMore",
    "Snake Eyes", "Solus", "Spalding", "Srixon", "Sub 70", "Takomo",
    "TaylorMade", "TearDrop", "Titleist", "Tommy Armour", "Top Flite",
    "Tour Edge", "Vega", "Vice", "Wilson", "Wishon", "XXIO", "Yonex",
    "Other / Custom",
])

# Brand-aware model choices. The final fallback keeps unusual, vintage, junior,
# women's, component, and newly released equipment available without forcing
# every golfer to type a model.
BRAND_MODEL_CATALOG = {
    "Callaway": {
        "Driver": ["Quantum", "Elyte", "Paradym Ai Smoke", "Paradym", "Rogue ST", "Epic", "Mavrik", "Big Bertha", "XR", "X2 Hot"],
        "Fairway Wood": ["Quantum", "Elyte", "Paradym Ai Smoke", "Paradym", "Rogue ST", "Epic", "Mavrik", "Big Bertha", "Apex Utility Wood"],
        "Hybrid / Rescue": ["Quantum", "Elyte", "Paradym Ai Smoke", "Paradym", "Apex", "Rogue ST", "Mavrik", "Big Bertha"],
        "Utility / Driving Iron": ["Apex UT", "X Forged UT", "Apex Utility Wood"],
        "Iron": ["Apex", "Apex Pro", "Apex CB", "Apex MB", "Elyte", "Paradym", "Paradym Ai Smoke", "Rogue ST", "Mavrik", "Big Bertha", "X Forged", "X-20", "X-22", "X-24 Hot"],
        "Wedge": ["Opus", "Opus Platinum", "Jaws Raw", "Mack Daddy CB", "Mack Daddy 5 Jaws", "Mack Daddy 4"],
    },
    "TaylorMade": {
        "Driver": ["Qi4D", "Qi35", "Qi10", "BRNR Mini", "Stealth 2", "Stealth", "SIM2", "SIM", "M6", "M5", "M4", "M3", "M2", "R15", "SLDR", "RBZ"],
        "Fairway Wood": ["Qi4D", "Qi35", "Qi10", "Stealth 2", "Stealth", "SIM2", "SIM", "M6", "M5", "M4", "M2", "RBZ"],
        "Hybrid / Rescue": ["Qi4D Rescue", "Qi35 Rescue", "Qi10 Rescue", "Stealth 2 Rescue", "Stealth Rescue", "SIM2 Rescue", "SIM Rescue", "M6 Rescue", "M4 Rescue", "RBZ Rescue"],
        "Utility / Driving Iron": ["P-UDI", "P-DHY", "Stealth UDI", "SIM UDI", "GAPR Lo", "GAPR Mid", "GAPR Hi"],
        "Iron": ["P790", "P770", "P7CB", "P7MC", "P7MB", "P7TW", "Qi", "Qi HL", "Stealth", "SIM2 Max", "SIM Max", "M6", "M4", "M2", "RocketBladez", "RBZ"],
        "Wedge": ["Milled Grind 5", "Milled Grind 4", "Milled Grind 3", "Hi-Toe 4", "Hi-Toe 3", "Hi-Toe Raw", "Tour Preferred"],
        "Putter": ["Spider Tour", "Spider ZT", "Spider 5K-ZT", "Spider GTX", "Spider GT", "Spider X", "Spider EX", "TP Reserve", "TP Hydro Blast"],
    },
    "Titleist": {
        "Driver": ["GTS2", "GTS3", "GTS4", "GTS300 Mini", "GT1", "GT2", "GT3", "GT4", "TSR1", "TSR2", "TSR3", "TSR4", "TSi1", "TSi2", "TSi3", "TSi4", "TS2", "TS3", "917", "915", "913", "910"],
        "Fairway Wood": ["GTS2", "GTS3", "GT1", "GT2", "GT3", "TSR1", "TSR2", "TSR3", "TSi1", "TSi2", "TSi3", "TS2", "TS3", "917", "915"],
        "Hybrid / Rescue": ["GT1", "GT2", "GT3", "TSR1", "TSR2", "TSR3", "TSi1", "TSi2", "TSi3", "818 H1", "818 H2", "816 H1", "816 H2"],
        "Utility / Driving Iron": ["U•505", "T200 Utility", "U500", "U510", "712U"],
        "Iron": ["T100", "T150", "T200", "T250", "T350", "620 CB", "620 MB", "AP1", "AP2", "AP3", "CB", "MB", "DCI"],
        "Wedge": ["Vokey SM11", "Vokey SM10", "Vokey SM9", "Vokey SM8", "Vokey SM7", "Vokey SM6", "Vokey WedgeWorks"],
    },
    "Ping": {
        "Driver": ["G440", "G430", "G425", "G410", "G400", "G", "G30", "Anser", "i25"],
        "Fairway Wood": ["G440", "G430", "G425", "G410", "G400", "G", "G30", "i25"],
        "Hybrid / Rescue": ["G440", "G430", "G425", "G410", "G400", "G30", "Anser", "i25"],
        "Utility / Driving Iron": ["iCrossover", "G430 Crossover", "G425 Crossover", "G410 Crossover"],
        "Iron": ["i240", "i230", "i530", "i525", "i500", "Blueprint S", "Blueprint T", "G440", "G430", "G425", "G410", "G400", "G30", "i210", "i200", "Eye2"],
        "Wedge": ["s159", "Glide 4.0", "Glide 3.0", "Glide Forged Pro", "Glide 2.0", "Eye2"],
        "Putter": ["PLD Milled", "Scottsdale", "Sigma 2", "Heppler", "Vault", "Anser", "Tyne", "Fetch"],
    },
    "Cobra": {
        "Driver": ["OPTM", "DS-ADAPT", "DARKSPEED", "AEROJET", "LTDx", "RADSPEED", "SPEEDZONE", "F9 Speedback", "LTD", "Bio Cell", "AMP Cell"],
        "Fairway Wood": ["OPTM", "DS-ADAPT", "DARKSPEED", "AEROJET", "LTDx", "RADSPEED", "SPEEDZONE", "F9 Speedback"],
        "Hybrid / Rescue": ["DS-ADAPT", "DARKSPEED", "AEROJET", "LTDx", "RADSPEED", "KING TEC", "T-Rail"],
        "Utility / Driving Iron": ["KING TEC Utility", "KING Utility", "KING Forged Tec Utility"],
        "Iron": ["KING TEC", "KING Forged Tec", "KING Tour", "KING CB", "KING MB", "DS-ADAPT", "DARKSPEED", "AEROJET", "LTDx", "T-Rail", "F9 Speedback"],
        "Wedge": ["KING", "KING-X", "SNAKEBITE", "SNAKEBITE-X", "KING MIM"],
        "Putter": ["3D Printed", "Vintage", "KING", "Supernova", "Agera", "Grandsport"],
    },
    "Mizuno": {
        "Driver": ["ST-MAX 230", "ST-Z 230", "ST-X 230", "ST-Z 220", "ST-X 220", "ST200", "ST190", "JPX 900"],
        "Fairway Wood": ["ST-MAX 230", "ST-Z 230", "ST-X 220", "ST-Z 220", "ST200", "ST190", "JPX 900"],
        "Hybrid / Rescue": ["ST-MAX 230", "ST-Z 230", "ST-X 220", "CLK", "JPX Fli-Hi"],
        "Utility / Driving Iron": ["Mizuno Pro Fli-Hi", "MP-20 HMB", "JPX Fli-Hi"],
        "Iron": ["JPX 925 Hot Metal", "JPX 925 Hot Metal Pro", "JPX 925 Forged", "JPX 925 Tour", "Mizuno Pro 245", "Mizuno Pro 243", "Mizuno Pro 241", "Mizuno Pro 225", "Mizuno Pro 223", "Mizuno Pro 221", "JPX 923", "JPX 921", "JPX 919", "MP-20", "MP-18"],
        "Wedge": ["T-1", "T-3", "T24", "S23", "T22", "T20", "S18"],
        "Putter": ["M.Craft OMOI", "M.Craft", "M.Craft X"],
    },
    "Srixon": {
        "Driver": ["ZXi", "ZX Mk II", "ZX5", "ZX7", "Z 785", "Z 765", "Z 565"],
        "Fairway Wood": ["ZXi", "ZX Mk II", "ZX", "Z F85", "Z F65"],
        "Hybrid / Rescue": ["ZXi", "ZX Mk II", "ZX", "Z H85", "Z H65"],
        "Utility / Driving Iron": ["ZXiU", "ZX Mk II Utility", "ZX Utility", "Z U85", "Z U65"],
        "Iron": ["ZXi4", "ZXi5", "ZXi7", "Z-Forged II", "ZX4 Mk II", "ZX5 Mk II", "ZX7 Mk II", "ZX4", "ZX5", "ZX7", "Z 585", "Z 785", "Z 565", "Z 765"],
    },
    "Cleveland": {
        "Driver": ["Launcher XL 2", "Launcher XL", "Launcher HB Turbo", "Launcher HB"],
        "Fairway Wood": ["Launcher XL 2", "Launcher XL Halo", "Launcher HB Turbo", "Launcher HB"],
        "Hybrid / Rescue": ["Launcher XL 2 Halo", "Launcher XL Halo", "Launcher Halo", "Launcher HB"],
        "Iron": ["ZipCore XL", "Launcher XL", "Launcher XL Halo", "Launcher UHX", "Launcher HB Turbo", "Launcher HB"],
        "Wedge": ["RTZ", "RTX 6 ZipCore", "RTX ZipCore", "CBX 4 ZipCore", "CBX Full-Face 2", "CBX ZipCore", "Smart Sole Full-Face", "Smart Sole 4"],
        "Chipper": ["Smart Sole Chipper"],
        "Putter": ["HB SOFT 2", "Frontline Elite", "Frontline", "Huntington Beach SOFT", "Huntington Beach"],
    },
    "Wilson": {
        "Driver": ["DYNAPWR Max", "DYNAPWR Carbon", "DYNAPWR LS", "DYNAPWR", "Launch Pad", "Staff Model", "C300", "Triton"],
        "Fairway Wood": ["DYNAPWR", "Launch Pad", "Staff Model", "C300"],
        "Hybrid / Rescue": ["DYNAPWR", "Launch Pad", "Staff Model", "D9", "D7"],
        "Utility / Driving Iron": ["Staff Model Utility", "Staff Model Driving Iron"],
        "Iron": ["DYNAPWR", "DYNAPWR Forged", "Staff Model CB", "Staff Model Blade", "Staff Model RB Utility", "Launch Pad", "D9", "D7", "C300 Forged", "FG Tour"],
        "Wedge": ["Staff Model ZM", "Staff Model", "Staff Model HT", "Harmonized"],
        "Putter": ["Infinite", "Staff Model", "Buckingham", "The Bean", "The L", "West Loop"],
    },
    "PXG": {
        "Driver": ["Black Ops", "Black Ops Tour-1", "0311 GEN6", "0311 GEN5", "0311 GEN4", "0811 X", "0811 XF", "Secret Weapon Mini"],
        "Fairway Wood": ["Black Ops", "0311 GEN6", "0311 GEN5", "0311 GEN4", "0341 X"],
        "Hybrid / Rescue": ["Black Ops", "0311 GEN6", "0311 GEN5", "0311 GEN4", "0317 X"],
        "Utility / Driving Iron": ["0311 X GEN6", "0311 X GEN5", "0311 X GEN4", "0311 X Driving Iron"],
        "Iron": ["0311 GEN7 P", "0311 GEN7 XP", "0311 GEN7 T", "0317 CB", "0317 ST", "0317 T", "0311 GEN6 P", "0311 GEN6 XP", "0311 GEN6 T", "0211 XCOR2", "0211 ST"],
        "Wedge": ["Sugar Daddy III", "Sugar Daddy II", "Sugar Daddy", "0311 Forged", "0311 Milled"],
        "Putter": ["Battle Ready II", "Battle Ready", "Allan", "Brandon", "Bat Attack", "Blackbird", "Closer", "Gunboat", "Hellcat", "Mustang"],
    },
    "Tour Edge": {
        "Driver": ["Exotics C725", "Exotics E725", "Exotics C723", "Exotics E723", "Hot Launch C524", "Hot Launch E524", "Hot Launch C523", "Hot Launch E523"],
        "Fairway Wood": ["Exotics C725", "Exotics E725", "Exotics C723", "Exotics E723", "Hot Launch C524", "Hot Launch E524"],
        "Hybrid / Rescue": ["Exotics C725", "Exotics E725", "Exotics C723", "Exotics E723", "Hot Launch C524", "Hot Launch E524", "Hot Launch Iron-Wood"],
        "Utility / Driving Iron": ["Exotics C725 Ti-Utility", "Exotics C723 Utility", "Hot Launch Iron-Wood"],
        "Iron": ["Exotics C725", "Exotics E725", "Exotics C723", "Exotics E723", "Hot Launch C524", "Hot Launch E524", "Hot Launch Iron-Wood"],
        "Wedge": ["Exotics Wingman", "Hot Launch Super Spin"],
        "Putter": ["Wingman", "Template Series"],
    },
    "Odyssey": {
        "Putter": ["Ai-ONE", "Ai-ONE Milled", "Square 2 Square", "Square 2 Square TRI-HOT", "White Hot OG", "White Hot Versa", "Tri-Hot 5K", "Eleven", "Ten", "Stroke Lab", "O-Works", "Toulon Design"],
    },
    "Scotty Cameron": {
        "Putter": ["Studio Style", "Phantom", "Super Select", "Special Select", "Select", "Futura", "GOLO", "California", "Studio Stainless", "Circa 62", "Newport", "Newport 2"],
    },
    "Bettinardi": {
        "Putter": ["BB Series", "Queen B", "INOVAI", "Studio Stock", "HLX", "Antidote", "Signature Series"],
        "Wedge": ["HLX 6.0", "HLX 5.0", "HLX 3.0"],
    },
    "LAB Golf": {
        "Putter": ["OZ.1i", "OZ.1", "DF3", "MEZZ.1 MAX", "MEZZ.1", "LINK.1", "Directed Force 2.1"],
    },
    "Miura": {
        "Iron": ["CB-302", "MC-502", "TC-201", "MB-101", "KM-700", "PI-401", "IC-602", "CB-301", "MC-501"],
        "Wedge": ["Tour Wedge High Bounce", "Tour Wedge Low Bounce", "Milled Tour Wedge", "K-Grind 2.0", "Y-Grind"],
    },
    "Sub 70": {
        "Driver": ["859 Pro", "849 Pro", "849D", "839D"],
        "Fairway Wood": ["949X Pro", "949X", "939X"],
        "Hybrid / Rescue": ["949X Pro", "949X", "939X"],
        "Utility / Driving Iron": ["699 Pro Utility", "699 Utility"],
        "Iron": ["699 v2", "699 Pro v2", "659 CB", "659 TC", "659 MB", "639 CB", "639 MB", "TAIII", "799", "Sycamore 005"],
        "Wedge": ["286", "JB Forged", "TAIII Wedge"],
        "Putter": ["004", "005 Wide Blade", "007", "008", "Sycamore"],
    },
    "Takomo": {
        "Iron": ["Iron 101", "Iron 101T", "Iron 201", "Iron 301 CB", "Iron 301 MB"],
        "Utility / Driving Iron": ["Iron 101U"],
        "Wedge": ["Skyforger Wedge"],
    },
    "Honma": {
        "Driver": ["TW767", "TW757", "Beres", "Tour World GS", "XP-1"],
        "Fairway Wood": ["TW767", "TW757", "Beres", "Tour World GS", "XP-1"],
        "Hybrid / Rescue": ["TW767", "TW757", "Beres", "Tour World GS", "XP-1"],
        "Iron": ["TW767", "TW757", "Beres", "Tour World GS", "TR20", "XP-1"],
        "Wedge": ["TW-W", "Beres Wedge"],
    },
    "XXIO": {
        "Driver": ["XXIO 14", "XXIO 13", "XXIO 12", "XXIO Prime", "XXIO X"],
        "Fairway Wood": ["XXIO 14", "XXIO 13", "XXIO 12", "XXIO Prime", "XXIO X"],
        "Hybrid / Rescue": ["XXIO 14", "XXIO 13", "XXIO 12", "XXIO Prime", "XXIO X"],
        "Iron": ["XXIO 14", "XXIO 13", "XXIO 12", "XXIO Prime", "XXIO X"],
    },
    "Nike": {
        "Driver": ["Vapor Fly", "Vapor Speed", "Vapor Pro", "Covert 2.0", "Covert", "VR_S Covert", "VR Pro", "SQ Machspeed", "SQ Sumo"],
        "Fairway Wood": ["Vapor Fly", "Vapor Speed", "Covert 2.0", "Covert", "VR_S", "SQ Machspeed"],
        "Hybrid / Rescue": ["Vapor Fly", "Vapor Speed", "Covert 2.0", "Covert", "VR_S", "SQ Machspeed"],
        "Utility / Driving Iron": ["Vapor Fly Pro", "VR Pro Combo"],
        "Iron": ["Vapor Fly", "Vapor Fly Pro", "Vapor Pro Combo", "Vapor Pro", "VR Pro Combo", "VR Pro Blade", "VR_S Covert", "SQ Machspeed", "Slingshot"],
        "Wedge": ["Engage", "VR Forged", "SV Tour"],
        "Putter": ["Method Origin", "Method Core", "Method", "IC"],
    },
    "Adams": {
        "Driver": ["XTD", "Speedline Super LS", "Speedline Fast 12", "Speedline"],
        "Fairway Wood": ["Tight Lies", "XTD", "Speedline Super LS", "Speedline"],
        "Hybrid / Rescue": ["Idea", "Tight Lies", "XTD", "Super Proto", "Pro Black"],
        "Iron": ["Idea", "XTD", "CB3", "CB2", "CMB", "A-Tour"],
    },
}

MODEL_FALLBACKS = ["Model unknown", "Other / Model not listed"]


def model_choices_for(brand, category, existing_model=""):
    brand = {
        "Parsons Xtreme Golf (PXG)": "PXG",
    }.get(brand, brand)
    choices = list(BRAND_MODEL_CATALOG.get(brand, {}).get(category, []))
    existing_model = str(existing_model or "").strip()
    if existing_model and existing_model not in choices:
        choices.insert(0, existing_model)
    for fallback in MODEL_FALLBACKS:
        if fallback not in choices:
            choices.append(fallback)
    return choices

SHOT_SHAPES = [
    "Unknown", "Straight", "Draw", "Fade", "High", "Low", "Low liner",
    "Variable / Both ways",
]

TYPICAL_MISSES = [
    "unknown", "straight", "slight pull", "pull", "pull hook", "hook",
    "slight fade", "fade right", "push", "push fade", "slice", "thin",
    "fat", "toe", "heel", "short", "long", "variable / both ways",
]

CONFIDENCE_LEVELS = ["Low", "Developing", "Comfortable", "High", "Go-to club"]


def canonical_club_id(club_name):
    """Return a stable analytics ID for friendly labels such as 3 Wood."""
    normalized = re.sub(r"[^a-z0-9]+", "_", str(club_name or "").lower()).strip("_")
    aliases = {
        "3w": "3_wood",
        "three_wood": "3_wood",
        "pw": "pitching_wedge",
        "aw": "approach_wedge",
        "gw": "gap_wedge",
        "sw": "sand_wedge",
        "lw": "lob_wedge",
    }
    return aliases.get(normalized, normalized)


def infer_club_category(club_name):
    target = canonical_club_id(club_name)
    for category, choices in CLUB_CATALOG.items():
        if any(canonical_club_id(choice) == target for choice in choices):
            return category
    return "Other / Custom"


def split_brand_model(club):
    brand = str(club.get("Brand", "") or "").strip()
    model = str(club.get("Model", "") or "").strip()
    combined = str(club.get("Brand / Model", "") or "").strip()
    if brand in CLUB_BRANDS and brand != "Select Brand":
        return brand, model
    if brand and not model:
        combined = brand
    elif brand and model:
        combined = f"{brand} {model}".strip()
    if not combined:
        return brand, model
    for candidate in sorted(CLUB_BRANDS, key=len, reverse=True):
        if candidate == "Other / Custom":
            continue
        if combined.lower() == candidate.lower():
            return candidate, ""
        if combined.lower().startswith(candidate.lower() + " "):
            return candidate, combined[len(candidate):].strip()
    return combined, ""


def build_club_record(category, club_name, brand, model, loft, carry,
                      typical_miss, shot_shape, confidence):
    loft_text = ""
    if loft not in (None, ""):
        loft_text = f"{float(loft):g}°"
    brand_model = " ".join(value for value in [brand, model] if value).strip()
    return {
        "Club": club_name,
        "Category": category,
        "Canonical ID": canonical_club_id(club_name),
        "Brand": brand,
        "Model": model,
        "Brand / Model": brand_model,
        "Loft": loft_text,
        "Stock Carry": float(carry),
        "Typical Miss": typical_miss,
        "Shot Shape": shot_shape,
        "Confidence": confidence,
    }


def render_club_builder(prefix, existing=None):
    """Render a progressive, click-first club editor and return its current record."""
    existing = existing or {}
    current_name = str(existing.get("Club", "") or "")
    current_category = existing.get("Category") or infer_club_category(current_name)
    categories = list(CLUB_CATALOG.keys())
    if current_category not in categories:
        current_category = "Other / Custom"

    category = st.selectbox(
        "1. Club category", categories, index=categories.index(current_category),
        key=f"{prefix}_category",
    )
    club_choices = list(CLUB_CATALOG[category])
    if current_name and current_name not in club_choices and category != "Other / Custom":
        club_choices.append(current_name)
    club_name = st.selectbox(
        "2. Exact club", club_choices,
        index=club_choices.index(current_name) if current_name in club_choices else 0,
        key=f"{prefix}_club_name",
    )
    if category == "Other / Custom":
        club_name = st.text_input(
            "Custom club name", value=current_name if current_name != "Custom Club" else "",
            placeholder="Example: One-length 7 Iron", key=f"{prefix}_custom_club_name",
        ).strip()

    existing_brand, existing_model = split_brand_model(existing)
    brand_choices = list(CLUB_BRANDS)
    if existing_brand and existing_brand not in brand_choices:
        brand_choices.insert(0, existing_brand)
    brand = st.selectbox(
        "3. Brand", brand_choices,
        index=brand_choices.index(existing_brand) if existing_brand in brand_choices else 0,
        key=f"{prefix}_brand",
    )
    if brand == "Other / Custom":
        brand = st.text_input(
            "Custom brand", placeholder="Enter the manufacturer",
            key=f"{prefix}_custom_brand",
        ).strip()
    elif brand == "Select Brand":
        brand = ""
    model_choices = model_choices_for(brand, category, existing_model)
    model = st.selectbox(
        "4. Model", model_choices,
        index=(
            model_choices.index(existing_model)
            if existing_model in model_choices
            else model_choices.index("Model unknown")
        ),
        key=f"{prefix}_model_choice",
        help="Models are filtered by the selected brand and club category.",
    )
    if model == "Other / Model not listed":
        model = st.text_input(
            "Enter model", value="",
            placeholder="Type the model only when it is not listed",
            key=f"{prefix}_custom_model",
        ).strip()

    loft_text = str(existing.get("Loft", "") or "").replace("°", "").strip()
    try:
        loft_default = float(loft_text) if loft_text else None
    except Exception:
        loft_default = None
    detail_col1, detail_col2 = st.columns(2)
    with detail_col1:
        loft = st.number_input(
            "Loft (optional)", min_value=0.0, max_value=80.0,
            value=loft_default, step=0.5, key=f"{prefix}_loft",
        )
        carry = st.number_input(
            "Normal carry (yards)", min_value=1.0, max_value=400.0,
            value=float(existing.get("Stock Carry", 150) or 150), step=1.0,
            key=f"{prefix}_carry",
        )
        shape_default = existing.get("Shot Shape", "Unknown")
        if shape_default not in SHOT_SHAPES:
            shape_default = "Unknown"
        shot_shape = st.selectbox(
            "Normal shot shape", SHOT_SHAPES, index=SHOT_SHAPES.index(shape_default),
            key=f"{prefix}_shape",
        )
    with detail_col2:
        miss_default = str(existing.get("Typical Miss", "unknown") or "unknown").lower()
        if miss_default not in TYPICAL_MISSES:
            TYPICAL_MISSES.append(miss_default)
        typical_miss = st.selectbox(
            "Typical miss", TYPICAL_MISSES, index=TYPICAL_MISSES.index(miss_default),
            key=f"{prefix}_miss",
        )
        confidence_default = existing.get("Confidence", "Developing")
        if confidence_default not in CONFIDENCE_LEVELS:
            confidence_default = "Developing"
        confidence = st.selectbox(
            "Confidence", CONFIDENCE_LEVELS,
            index=CONFIDENCE_LEVELS.index(confidence_default), key=f"{prefix}_confidence",
        )

    return build_club_record(
        category, club_name, brand, model, loft, carry,
        typical_miss, shot_shape, confidence,
    )


# ============================================================
# SUPABASE AUTHENTICATION
# ============================================================

def get_supabase_client():
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
    except Exception:
        st.error(
            "My Play cannot find .streamlit/secrets.toml."
        )
        st.stop()

    client = create_client(
        url,
        key
    )

    access_token = st.session_state.get(
        "supabase_access_token"
    )
    refresh_token = st.session_state.get(
        "supabase_refresh_token"
    )

    if access_token and refresh_token:
        try:
            client.auth.set_session(
                access_token,
                refresh_token
            )
        except Exception:
            for session_key in [
                "supabase_access_token",
                "supabase_refresh_token",
                "supabase_user_id",
                "supabase_user_email"
            ]:
                st.session_state.pop(
                    session_key,
                    None
                )

    return client

def store_auth_session(
    response
):
    session = getattr(
        response,
        "session",
        None
    )
    user = getattr(
        response,
        "user",
        None
    )

    if session is not None:
        st.session_state[
            "supabase_access_token"
        ] = session.access_token
        st.session_state[
            "supabase_refresh_token"
        ] = session.refresh_token

    if user is not None:
        st.session_state[
            "supabase_user_id"
        ] = str(
            user.id
        )
        st.session_state[
            "supabase_user_email"
        ] = user.email or ""

def ensure_cloud_profile(
    client
):
    user_id = st.session_state.get(
        "supabase_user_id"
    )

    if not user_id:
        return

    email = st.session_state.get(
        "supabase_user_email",
        ""
    )

    existing = (
        client
        .table(
            "profiles"
        )
        .select(
            "id,user_id"
        )
        .eq(
            "user_id",
            user_id
        )
        .limit(
            1
        )
        .execute()
    )

    if not existing.data:
        (
            client
            .table(
                "profiles"
            )
            .insert({
                "user_id": user_id,
                "display_name": (
                    email.split("@")[0]
                    if email
                    else "Golfer"
                ),
                "handedness": "Right-handed"
            })
            .execute()
        )

def sign_out_cloud(
    client
):
    try:
        client.auth.sign_out()
    except Exception:
        pass

    for session_key in [
        "supabase_access_token",
        "supabase_refresh_token",
        "supabase_user_id",
        "supabase_user_email"
    ]:
        st.session_state.pop(
            session_key,
            None
        )

def auth_confirmation_redirect_url():
    """
    Return the exact URL the user is currently using for My Play.
    Supabase sends email-confirmation users back here.
    """
    try:
        base_url = str(
            st.context.url
        ).strip()
    except Exception:
        base_url = ""

    if not base_url:
        # Local fallback for development. Streamlit Cloud should provide
        # st.context.url automatically.
        base_url = "http://localhost:8501"

    separator = "&" if "?" in base_url else "?"

    return (
        base_url
        + separator
        + "email_confirmed=1"
    )


def authentication_screen(
    client
):
    if "auth_view" not in st.session_state:
        st.session_state[
            "auth_view"
        ] = "welcome"

    email_confirmed_return = str(
        st.query_params.get(
            "email_confirmed",
            ""
        )
        or ""
    ).lower() in [
        "1",
        "true",
        "yes",
    ]

    if email_confirmed_return:
        st.session_state[
            "auth_view"
        ] = "signin"

        st.session_state[
            "email_confirmed_message"
        ] = True

        try:
            del st.query_params[
                "email_confirmed"
            ]
        except Exception:
            pass

    auth_view = st.session_state.get(
        "auth_view",
        "welcome"
    )

    # ========================================================
    # WELCOME / HOME
    # ========================================================
    if auth_view == "welcome":
        st.title(
            "⛳ My Play"
        )

        st.subheader(
            "Your game. Your data. Your caddie."
        )

        st.write(
            "My Play is a personal AI golf caddie that learns how you actually play and helps you make smarter decisions on the course."
        )

        feature_col1, feature_col2, feature_col3 = st.columns(
            3
        )

        with feature_col1:
            with st.container(
                border=True
            ):
                st.markdown(
                    "### 🗣️ Ask Your Caddie"
                )
                st.caption(
                    "Talk naturally during a round and get club, target, and strategy recommendations."
                )

        with feature_col2:
            with st.container(
                border=True
            ):
                st.markdown(
                    "### 📈 Learns Your Game"
                )
                st.caption(
                    "My Play uses your bag, real shot history, range data, and rounds to improve over time."
                )

        with feature_col3:
            with st.container(
                border=True
            ):
                st.markdown(
                    "### ⛳ Play Anywhere"
                )
                st.caption(
                    "Use full course data when available or keep your caddie active in Limited-Data Mode."
                )

        st.markdown(
            "### Ready to play?"
        )

        welcome_col1, welcome_col2 = st.columns(
            2
        )

        with welcome_col1:
            if st.button(
                "Sign In",
                type="primary",
                use_container_width=True,
                key="welcome_sign_in"
            ):
                st.session_state[
                    "auth_view"
                ] = "signin"
                st.rerun()

        with welcome_col2:
            if st.button(
                "Create Account",
                use_container_width=True,
                key="welcome_create_account"
            ):
                st.session_state[
                    "auth_view"
                ] = "signup"
                st.rerun()

        st.caption(
            "Built for golfers who want a caddie that gets smarter from their real game."
        )

        st.stop()

    # ========================================================
    # SIGN IN
    # ========================================================
    if auth_view == "signin":
        st.title(
            "⛳ My Play"
        )

        st.subheader(
            "Welcome back"
        )

        if st.session_state.pop(
            "email_confirmed_message",
            False
        ):
            st.success(
                "Email confirmed. Sign in below to enter My Play."
            )

        if st.button(
            "← Back",
            key="signin_back_to_welcome"
        ):
            st.session_state[
                "auth_view"
            ] = "welcome"
            st.rerun()

        email = st.text_input(
            "Email",
            key="auth_login_email"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="auth_login_password"
        )

        if st.button(
            "Sign In",
            type="primary",
            use_container_width=True,
            key="auth_login_button"
        ):
            try:
                response = client.auth.sign_in_with_password({
                    "email": email.strip(),
                    "password": password
                })

                store_auth_session(
                    response
                )

                st.rerun()

            except Exception as exc:
                st.error(
                    f"Could not sign in: {exc}"
                )

        st.caption(
            "New to My Play?"
        )

        if st.button(
            "Create an Account",
            use_container_width=True,
            key="signin_go_signup"
        ):
            st.session_state[
                "auth_view"
            ] = "signup"
            st.rerun()

        st.stop()

    # ========================================================
    # CREATE ACCOUNT
    # ========================================================
    st.title(
        "⛳ My Play"
    )

    st.subheader(
        "Create your account"
    )

    if st.button(
        "← Back",
        key="signup_back_to_welcome"
    ):
        st.session_state[
            "auth_view"
        ] = "welcome"
        st.rerun()

    signup_email = st.text_input(
        "Email",
        key="auth_signup_email"
    )

    signup_password = st.text_input(
        "Password",
        type="password",
        key="auth_signup_password"
    )

    signup_confirm = st.text_input(
        "Confirm Password",
        type="password",
        key="auth_signup_confirm"
    )

    if st.button(
        "Create My Play Account",
        type="primary",
        use_container_width=True,
        key="auth_signup_button"
    ):
        if len(
            signup_password
        ) < 6:
            st.warning(
                "Use a password with at least 6 characters."
            )

        elif signup_password != signup_confirm:
            st.warning(
                "The passwords do not match."
            )

        else:
            try:
                response = client.auth.sign_up({
                    "email": signup_email.strip(),
                    "password": signup_password,
                    "options": {
                        "email_redirect_to": auth_confirmation_redirect_url()
                    }
                })

                store_auth_session(
                    response
                )

                if getattr(
                    response,
                    "session",
                    None
                ) is None:
                    st.session_state[
                        "signup_confirmation_sent"
                    ] = True

                    st.success(
                        "Account created. Check your email and tap Confirm. My Play will bring you back to Sign In."
                    )

                else:
                    st.rerun()

            except Exception as exc:
                st.error(
                    f"Could not create account: {exc}"
                )

    if st.session_state.get(
        "signup_confirmation_sent"
    ):
        if st.button(
            "Go to Sign In",
            use_container_width=True,
            key="signup_go_signin"
        ):
            st.session_state[
                "auth_view"
            ] = "signin"

            st.session_state[
                "signup_confirmation_sent"
            ] = False

            st.rerun()

    st.stop()


# ============================================================
# LOCAL -> SUPABASE MIGRATION
# ============================================================

def _safe_number(value):
    try:
        if value is None or str(value).strip() == "":
            return None
        numeric = pd.to_numeric(
            pd.Series([value]),
            errors="coerce"
        ).iloc[0]
        if pd.isna(numeric):
            return None
        return float(numeric)
    except Exception:
        return None

def _safe_int(value):
    number = _safe_number(value)
    if number is None:
        return None
    return int(number)

def cloud_table_count(client, table_name):
    try:
        response = (
            client
            .table(table_name)
            .select("id")
            .execute()
        )
        return len(response.data or [])
    except Exception:
        return 0

def migrate_profile_to_cloud(client, user_id):
    local_profile = local_load_json(
        PROFILE_FILE,
        DEFAULT_PROFILE
    )

    payload = {
        "user_id": user_id,
        "handedness": local_profile.get(
            "handedness",
            "Right-handed"
        ),
        "handicap": str(
            local_profile.get(
                "handicap",
                ""
            )
        ),
        "default_course": local_profile.get(
            "default_course",
            ""
        ),
        "default_state": str(
            local_profile.get(
                "default_state",
                "NJ"
            )
        ).upper()
    }

    (
        client
        .table("profiles")
        .update(payload)
        .eq("user_id", user_id)
        .execute()
    )

    return 1

def migrate_bag_to_cloud(client, user_id):
    if cloud_table_count(
        client,
        "golf_bag"
    ) > 0:
        return 0, "already_has_cloud_data"

    local_bag = local_load_json(
        BAG_FILE,
        DEFAULT_BAG
    )

    rows = []

    for club in local_bag:
        brand_model = str(
            club.get(
                "Brand / Model",
                ""
            )
        ).strip()

        rows.append({
            "user_id": user_id,
            "club_name": str(
                club.get(
                    "Club",
                    ""
                )
            ).strip(),
            "brand": brand_model,
            "model": None,
            "loft": _safe_number(
                str(
                    club.get(
                        "Loft",
                        ""
                    )
                ).replace(
                    "°",
                    ""
                )
            ),
            "stock_carry": _safe_number(
                club.get(
                    "Stock Carry"
                )
            ),
            "stock_miss": str(
                club.get(
                    "Typical Miss",
                    ""
                )
            ),
            "active": True
        })

    rows = [
        row
        for row in rows
        if row["club_name"]
    ]

    if rows:
        (
            client
            .table("golf_bag")
            .insert(rows)
            .execute()
        )

    return len(rows), "migrated"

def migrate_evidence_to_cloud(client, user_id):
    if cloud_table_count(
        client,
        "player_evidence"
    ) > 0:
        return 0, "already_has_cloud_data"

    local_shots = local_load_shots()
    stored_local = local_load_player_evidence()
    on_course_local = shot_history_as_evidence(
        local_shots
    )

    frames = []

    if not stored_local.empty:
        frames.append(
            stored_local
        )

    if not on_course_local.empty:
        frames.append(
            on_course_local
        )

    evidence = (
        pd.concat(
            frames,
            ignore_index=True,
            sort=False
        )
        if frames
        else pd.DataFrame()
    )

    if evidence.empty:
        return 0, "no_local_data"

    rows = []

    for _, row in evidence.iterrows():
        recorded = str(
            row.get(
                "Date",
                ""
            )
        ).strip()

        payload = {
            "user_id": user_id,
            "source": str(
                row.get(
                    "Source",
                    "Manual"
                )
            ) or "Manual",
            "club_name": str(
                row.get(
                    "Club",
                    ""
                )
            ).strip(),
            "carry": _safe_number(
                row.get(
                    "Carry"
                )
            ),
            "total_distance": _safe_number(
                row.get(
                    "Total"
                )
            ),
            "offline": _safe_number(
                row.get(
                    "Offline"
                )
            ),
            "ball_speed": _safe_number(
                row.get(
                    "Ball Speed"
                )
            ),
            "club_speed": _safe_number(
                row.get(
                    "Club Speed"
                )
            ),
            "launch_angle": _safe_number(
                row.get(
                    "Launch"
                )
            ),
            "spin_rate": _safe_number(
                row.get(
                    "Spin"
                )
            ),
            "apex": _safe_number(
                row.get(
                    "Apex"
                )
            ),
            "result": str(
                row.get(
                    "Result",
                    ""
                )
            ),
            "contact_quality": str(
                row.get(
                    "Contact",
                    ""
                )
            ),
            "course_name": str(
                row.get(
                    "Course",
                    ""
                )
            ),
            "hole_number": _safe_int(
                row.get(
                    "Hole"
                )
            ),
            "shot_type": str(
                row.get(
                    "Shot Type",
                    ""
                )
            ),
            "notes": str(
                row.get(
                    "Notes",
                    row.get(
                        "Note",
                        ""
                    )
                )
            )
        }

        if recorded:
            # Postgres can parse the existing yyyy-mm-dd HH:MM timestamps.
            payload[
                "recorded_at"
            ] = recorded

        if payload[
            "club_name"
        ]:
            rows.append(
                payload
            )

    # Insert in chunks so larger simulator files do not create a huge request.
    chunk_size = 250

    for start in range(
        0,
        len(rows),
        chunk_size
    ):
        (
            client
            .table("player_evidence")
            .insert(
                rows[
                    start:start + chunk_size
                ]
            )
            .execute()
        )

    return len(rows), "migrated"

def migrate_reminders_to_cloud(client, user_id):
    if cloud_table_count(
        client,
        "swing_reminders"
    ) > 0:
        return 0, "already_has_cloud_data"

    reminders = []

    if os.path.exists(
        REMINDER_FILE
    ):
        try:
            with open(
                REMINDER_FILE,
                "r",
                encoding="utf-8"
            ) as f:
                reminders = [
                    line.strip()
                    for line in f.read().splitlines()
                    if line.strip()
                ]
        except Exception:
            reminders = []

    rows = [
        {
            "user_id": user_id,
            "reminder": reminder,
            "active": True
        }
        for reminder in reminders
    ]

    if rows:
        (
            client
            .table("swing_reminders")
            .insert(rows)
            .execute()
        )

    return len(rows), "migrated"

def migrate_rounds_to_cloud(client, user_id):
    if cloud_table_count(
        client,
        "rounds"
    ) > 0:
        return 0, "already_has_cloud_data"

    if not os.path.exists(
        ROUND_HISTORY_FILE
    ):
        return 0, "no_local_data"

    try:
        history = pd.read_csv(
            ROUND_HISTORY_FILE
        )
    except Exception:
        return 0, "no_local_data"

    rows = []

    for _, row in history.iterrows():
        started = str(
            row.get(
                "Date",
                ""
            )
        ).strip()

        ended = str(
            row.get(
                "Ended At",
                ""
            )
        ).strip()

        payload = {
            "user_id": user_id,
            "course_name": str(
                row.get(
                    "Course",
                    "Unknown Course"
                )
            ) or "Unknown Course",
            "tee_name": str(
                row.get(
                    "Tee",
                    ""
                )
            ),
            "total_score": _safe_int(
                row.get(
                    "Total Score"
                )
            ),
            "total_putts": _safe_int(
                row.get(
                    "Total Putts"
                )
            ),
            "notes": (
                f"Migrated local round. "
                f"Holes completed: {row.get('Holes Completed', '')}; "
                f"Fairways hit: {row.get('Fairways Hit', '')}; "
                f"Greens hit: {row.get('Greens Hit', '')}."
            )
        }

        if started:
            payload[
                "started_at"
            ] = started

        if ended:
            payload[
                "completed_at"
            ] = ended

        rows.append(
            payload
        )

    if rows:
        (
            client
            .table("rounds")
            .insert(rows)
            .execute()
        )

    return len(rows), "migrated"

def migrate_swing_metadata_to_cloud(client, user_id):
    if cloud_table_count(
        client,
        "swing_videos"
    ) > 0:
        return 0, "already_has_cloud_data"

    if not os.path.exists(
        SWING_VIDEO_FILE
    ):
        return 0, "no_local_data"

    try:
        history = pd.read_csv(
            SWING_VIDEO_FILE
        )
    except Exception:
        return 0, "no_local_data"

    rows = []

    for _, row in history.iterrows():
        baseline = str(
            row.get(
                "Baseline",
                "False"
            )
        ).lower() in (
            "true",
            "1",
            "yes"
        )

        recorded = str(
            row.get(
                "Date",
                ""
            )
        ).strip()

        payload = {
            "user_id": user_id,
            "club_name": str(
                row.get(
                    "Club",
                    ""
                )
            ),
            "session_type": str(
                row.get(
                    "Session Type",
                    ""
                )
            ),
            "label": str(
                row.get(
                    "Label",
                    ""
                )
            ),
            # Local Windows paths are intentionally NOT copied as cloud paths.
            "storage_path": None,
            "is_baseline": baseline,
            "tempo": str(
                row.get(
                    "Tempo",
                    ""
                )
            ),
            "setup": str(
                row.get(
                    "Setup",
                    ""
                )
            ),
            "balance": str(
                row.get(
                    "Balance",
                    ""
                )
            ),
            "backswing": str(
                row.get(
                    "Backswing",
                    ""
                )
            ),
            "transition": str(
                row.get(
                    "Transition",
                    ""
                )
            ),
            "finish": str(
                row.get(
                    "Finish",
                    ""
                )
            ),
            "observation_notes": str(
                row.get(
                    "Observation Notes",
                    ""
                )
            )
        }

        if recorded:
            payload[
                "recorded_at"
            ] = recorded

        rows.append(
            payload
        )

    if rows:
        (
            client
            .table("swing_videos")
            .insert(rows)
            .execute()
        )

    return len(rows), "migrated"

def migrate_all_local_data_to_cloud(
    client
):
    user_id = st.session_state.get(
        "supabase_user_id"
    )

    if not user_id:
        raise RuntimeError(
            "No signed-in golfer."
        )

    results = {}

    results[
        "Profile"
    ] = (
        migrate_profile_to_cloud(
            client,
            user_id
        ),
        "migrated"
    )

    results[
        "Bag"
    ] = migrate_bag_to_cloud(
        client,
        user_id
    )

    results[
        "Player evidence"
    ] = migrate_evidence_to_cloud(
        client,
        user_id
    )

    results[
        "Rounds"
    ] = migrate_rounds_to_cloud(
        client,
        user_id
    )

    results[
        "Swing reminders"
    ] = migrate_reminders_to_cloud(
        client,
        user_id
    )

    results[
        "Swing video metadata"
    ] = migrate_swing_metadata_to_cloud(
        client,
        user_id
    )

    return results

def cloud_data_status(
    client
):
    return {
        "Bag clubs": cloud_table_count(
            client,
            "golf_bag"
        ),
        "Evidence shots": cloud_table_count(
            client,
            "player_evidence"
        ),
        "Rounds": cloud_table_count(
            client,
            "rounds"
        ),
        "Reminders": cloud_table_count(
            client,
            "swing_reminders"
        ),
        "Swing videos": cloud_table_count(
            client,
            "swing_videos"
        )
    }


# ============================================================
# STORAGE
# ============================================================

def local_load_json(filename, default_value):
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default_value
    return default_value

def local_save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def local_load_shots():
    if os.path.exists(SHOT_FILE):
        try:
            return pd.read_csv(SHOT_FILE)
        except Exception:
            return pd.DataFrame()
    return pd.DataFrame()

def local_save_shot(row):
    new_row = pd.DataFrame([row])
    if os.path.exists(SHOT_FILE):
        try:
            old = pd.read_csv(SHOT_FILE)
            data = pd.concat([old, new_row], ignore_index=True)
        except Exception:
            data = new_row
    else:
        data = new_row
    data.to_csv(SHOT_FILE, index=False)




# ============================================================
# CLOUD-FIRST STORAGE ADAPTERS
# ============================================================

def _cloud_ready():
    return bool(
        globals().get("supabase")
        and st.session_state.get(
            "supabase_user_id"
        )
    )

def _cloud_user_id():
    return st.session_state.get(
        "supabase_user_id"
    )

def load_json(filename, default_value):
    if not _cloud_ready():
        return local_load_json(
            filename,
            default_value
        )

    user_id = _cloud_user_id()

    try:
        if filename == PROFILE_FILE:
            try:
                response = (
                    supabase.table("profiles")
                    .select(
                        "display_name,handedness,handicap,typical_score,"
                        "experience_level,preferred_scoring_leave,"
                        "default_course,default_state"
                    )
                    .eq("user_id", user_id).limit(1).execute()
                )
                st.session_state["my_player_schema_ready"] = True
            except Exception:
                st.session_state["my_player_schema_ready"] = False
                response = (
                    supabase.table("profiles")
                    .select("handedness,handicap,default_course,default_state")
                    .eq("user_id", user_id).limit(1).execute()
                )

            if response.data:
                row = response.data[0]
                return {
                    "display_name": row.get("display_name") or "",
                    "handedness": row.get("handedness") or "Right-handed",
                    "handicap": row.get("handicap") or "",
                    "typical_score": row.get("typical_score") or "",
                    "experience_level": row.get("experience_level") or "Developing",
                    "preferred_scoring_leave": int(
                        row.get("preferred_scoring_leave") or 100
                    ),
                    "default_course": row.get("default_course") or "",
                    "default_state": row.get("default_state") or "NJ"
                }

            return dict(DEFAULT_PROFILE)

        if filename == BAG_FILE:
            try:
                response = (
                    supabase.table("golf_bag")
                    .select(
                        "club_name,club_category,canonical_club_id,brand,model,"
                        "loft,stock_carry,stock_miss,shot_shape,confidence,active"
                    )
                    .eq("user_id", user_id).eq("active", True).execute()
                )
            except Exception:
                response = (
                    supabase.table("golf_bag")
                    .select("club_name,brand,model,loft,stock_carry,stock_miss,active")
                    .eq("user_id", user_id).eq("active", True).execute()
                )

            rows = []

            for row in (
                response.data
                or []
            ):
                brand_model = " ".join(
                    value
                    for value in [
                        str(row.get("brand") or "").strip(),
                        str(row.get("model") or "").strip()
                    ]
                    if value
                )

                loft = row.get("loft")

                rows.append({
                    "Club": row.get("club_name", ""),
                    "Category": row.get("club_category") or infer_club_category(
                        row.get("club_name", "")
                    ),
                    "Canonical ID": row.get("canonical_club_id") or canonical_club_id(
                        row.get("club_name", "")
                    ),
                    "Brand": str(row.get("brand") or "").strip(),
                    "Model": str(row.get("model") or "").strip(),
                    "Brand / Model": brand_model,
                    "Loft": (
                        f"{float(loft):g}°"
                        if loft is not None
                        else ""
                    ),
                    "Stock Carry": float(
                        row.get("stock_carry") or 0
                    ),
                    "Typical Miss": row.get("stock_miss") or "unknown",
                    "Shot Shape": row.get("shot_shape") or "Unknown",
                    "Confidence": row.get("confidence") or "Developing",
                })

            # Critical multi-user isolation:
            # an empty cloud bag means this golfer has no bag yet.
            return rows

    except Exception as exc:
        st.error(
            f"Cloud read failed for this account: {exc}"
        )

        # Never expose another golfer's local fallback while authenticated.
        if _cloud_ready():
            return default_value

    return local_load_json(
        filename,
        default_value
    )

def save_json(filename, data):
    if not _cloud_ready():
        return local_save_json(
            filename,
            data
        )

    user_id = _cloud_user_id()

    try:
        if filename == PROFILE_FILE:
            legacy_payload = {
                "handedness": data.get("handedness", "Right-handed"),
                "handicap": str(data.get("handicap", "")),
                "default_course": data.get("default_course", ""),
                "default_state": str(data.get("default_state", "NJ")).upper(),
            }
            expanded_payload = {
                **legacy_payload,
                "display_name": data.get("display_name", ""),
                "typical_score": str(data.get("typical_score", "")),
                "experience_level": data.get("experience_level", "Developing"),
                "preferred_scoring_leave": int(
                    data.get("preferred_scoring_leave", 100) or 100
                ),
            }
            try:
                (
                    supabase.table("profiles").update(expanded_payload)
                    .eq("user_id", user_id).execute()
                )
            except Exception:
                (
                    supabase.table("profiles").update(legacy_payload)
                    .eq("user_id", user_id).execute()
                )

            local_save_json(
                filename,
                data
            )
            return

        if filename == BAG_FILE:
            (
                supabase
                .table("golf_bag")
                .delete()
                .eq(
                    "user_id",
                    user_id
                )
                .execute()
            )

            rows = []
            legacy_rows = []

            for club in data:
                club_name = str(
                    club.get(
                        "Club",
                        ""
                    )
                ).strip()

                if not club_name:
                    continue

                loft_text = str(
                    club.get(
                        "Loft",
                        ""
                    )
                ).replace(
                    "°",
                    ""
                ).strip()

                try:
                    loft_value = float(
                        loft_text
                    ) if loft_text else None
                except Exception:
                    loft_value = None

                brand, model = split_brand_model(club)
                legacy_row = {
                    "user_id": user_id,
                    "club_name": club_name,
                    "brand": brand,
                    "model": model or None,
                    "loft": loft_value,
                    "stock_carry": float(
                        club.get(
                            "Stock Carry",
                            0
                        )
                    ),
                    "stock_miss": str(
                        club.get(
                            "Typical Miss",
                            ""
                        )
                    ),
                    "active": True
                }
                legacy_rows.append(legacy_row)
                rows.append({
                    **legacy_row,
                    "club_category": club.get("Category") or infer_club_category(club_name),
                    "canonical_club_id": club.get("Canonical ID") or canonical_club_id(club_name),
                    "shot_shape": club.get("Shot Shape", "Unknown"),
                    "confidence": club.get("Confidence", "Developing"),
                })

            if rows:
                try:
                    supabase.table("golf_bag").insert(rows).execute()
                except Exception:
                    supabase.table("golf_bag").delete().eq("user_id", user_id).execute()
                    supabase.table("golf_bag").insert(legacy_rows).execute()

            local_save_json(
                filename,
                data
            )
            return

    except Exception as exc:
        st.error(
            f"Cloud save failed: {exc}"
        )
        return

    local_save_json(
        filename,
        data
    )


def load_game_profile():
    if not _cloud_ready():
        return local_load_json(GAME_PROFILE_FILE, DEFAULT_GAME_PROFILE)
    try:
        response = (
            supabase.table("player_game_profiles").select("game_data")
            .eq("user_id", _cloud_user_id()).limit(1).execute()
        )
        if response.data:
            saved = response.data[0].get("game_data") or {}
            return {**DEFAULT_GAME_PROFILE, **saved}
    except Exception:
        return dict(DEFAULT_GAME_PROFILE)
    return dict(DEFAULT_GAME_PROFILE)


def save_game_profile(game_data):
    cleaned = {**DEFAULT_GAME_PROFILE, **(game_data or {})}
    if not _cloud_ready():
        local_save_json(GAME_PROFILE_FILE, cleaned)
        return True
    try:
        supabase.table("player_game_profiles").upsert(
            {
                "user_id": _cloud_user_id(),
                "game_data": cleaned,
                "updated_at": datetime.now().isoformat(),
            },
            on_conflict="user_id",
        ).execute()
        return True
    except Exception:
        return False

def _evidence_to_shot_dataframe(rows):
    return pd.DataFrame(
        [
            {
                "Date": row.get("recorded_at", ""),
                "Course": row.get("course_name", ""),
                "Hole": row.get("hole_number", ""),
                "Club Used": row.get("club_name", ""),
                "Actual Carry": row.get("carry"),
                "Result": row.get("result", ""),
                "Contact": row.get("contact_quality", ""),
                "Note": row.get("notes", ""),
                "Shot Type": row.get("shot_type", ""),
                "Round ID": row.get("round_id", "")
            }
            for row in (rows or [])
        ]
    )

def load_shots():
    if not _cloud_ready():
        return local_load_shots()

    try:
        response = (
            supabase
            .table("player_evidence")
            .select(
                "recorded_at,source,club_name,carry,result,contact_quality,"
                "course_name,hole_number,round_id,shot_type,notes"
            )
            .eq(
                "user_id",
                _cloud_user_id()
            )
            .in_(
                "source",
                [
                    "Live Round",
                    "On Course",
                    "Previous Round"
                ]
            )
            .order(
                "recorded_at"
            )
            .execute()
        )

        return _evidence_to_shot_dataframe(
            response.data
        )

    except Exception as exc:
        st.error(
            f"Cloud shot history read failed for this account: {exc}"
        )
        return pd.DataFrame()

def save_shot(row):
    if not _cloud_ready():
        return local_save_shot(
            row
        )

    (
        supabase
        .table("player_evidence")
        .insert({
            "user_id": _cloud_user_id(),
            "source": (
                "Live Round"
                if str(
                    row.get(
                        "Note",
                        ""
                    )
                ) == "Live Round"
                else "On Course"
            ),
            "recorded_at": row.get(
                "Date"
            ) or datetime.now().isoformat(),
            "club_name": str(
                row.get(
                    "Club Used",
                    ""
                )
            ),
            "carry": _safe_number(
                row.get(
                    "Actual Carry"
                )
            ),
            "result": str(
                row.get(
                    "Result",
                    ""
                )
            ),
            "contact_quality": str(
                row.get(
                    "Contact",
                    ""
                )
            ),
            "course_name": str(
                row.get(
                    "Course",
                    ""
                )
            ),
            "hole_number": _safe_int(
                row.get(
                    "Hole"
                )
            ),
            "round_id": (
                row.get(
                    "Round ID"
                )
                or None
            ),
            "shot_type": str(
                row.get(
                    "Shot Type",
                    ""
                )
            ),
            "notes": str(
                row.get(
                    "Note",
                    ""
                )
            )
        })
        .execute()
    )

    local_save_shot(
        row
    )

def load_player_evidence():
    if not _cloud_ready():
        return local_load_player_evidence()

    try:
        response = (
            supabase
            .table("player_evidence")
            .select(
                "recorded_at,source,club_name,carry,total_distance,offline,"
                "ball_speed,club_speed,launch_angle,spin_rate,apex,result,"
                "contact_quality,course_name,hole_number,round_id,shot_type,notes"
            )
            .eq(
                "user_id",
                _cloud_user_id()
            )
            .in_(
                "source",
                [
                    "Simulator",
                    "Launch Monitor",
                    "Driving Range",
                    "Previous Round",
                    "Manual"
                ]
            )
            .order(
                "recorded_at"
            )
            .execute()
        )

        rows = []

        for row in response.data or []:
            rows.append({
                "Date": row.get("recorded_at", ""),
                "Source": row.get("source", ""),
                "Club": row.get("club_name", ""),
                "Carry": row.get("carry"),
                "Total": row.get("total_distance"),
                "Offline": row.get("offline"),
                "Ball Speed": row.get("ball_speed"),
                "Club Speed": row.get("club_speed"),
                "Launch": row.get("launch_angle"),
                "Spin": row.get("spin_rate"),
                "Apex": row.get("apex"),
                "Result": row.get("result", ""),
                "Contact": row.get("contact_quality", ""),
                "Course": row.get("course_name", ""),
                "Hole": row.get("hole_number", ""),
                "Round ID": row.get("round_id", ""),
                "Shot Type": row.get("shot_type", ""),
                "Notes": row.get("notes", "")
            })

        return pd.DataFrame(
            rows
        )

    except Exception as exc:
        st.error(
            f"Cloud evidence read failed for this account: {exc}"
        )
        return pd.DataFrame()

def append_player_evidence(rows):
    if not rows:
        return

    if not _cloud_ready():
        return local_append_player_evidence(
            rows
        )

    payloads = []

    for row in rows:
        payloads.append({
            "user_id": _cloud_user_id(),
            "source": row.get(
                "Source",
                "Manual"
            ),
            "recorded_at": row.get(
                "Date"
            ) or datetime.now().isoformat(),
            "club_name": str(
                row.get(
                    "Club",
                    ""
                )
            ),
            "carry": _safe_number(
                row.get(
                    "Carry"
                )
            ),
            "total_distance": _safe_number(
                row.get(
                    "Total"
                )
            ),
            "offline": _safe_number(
                row.get(
                    "Offline"
                )
            ),
            "ball_speed": _safe_number(
                row.get(
                    "Ball Speed"
                )
            ),
            "club_speed": _safe_number(
                row.get(
                    "Club Speed"
                )
            ),
            "launch_angle": _safe_number(
                row.get(
                    "Launch"
                )
            ),
            "spin_rate": _safe_number(
                row.get(
                    "Spin"
                )
            ),
            "apex": _safe_number(
                row.get(
                    "Apex"
                )
            ),
            "result": str(
                row.get(
                    "Result",
                    ""
                )
            ),
            "contact_quality": str(
                row.get(
                    "Contact",
                    ""
                )
            ),
            "notes": str(
                row.get(
                    "Notes",
                    ""
                )
            )
        })

    (
        supabase
        .table("player_evidence")
        .insert(
            payloads
        )
        .execute()
    )

    local_append_player_evidence(
        rows
    )


# ============================================================
# LIVE ROUND STORAGE
# ============================================================

def load_active_round():
    return st.session_state.get(
        "active_round_cloud_session",
        {}
    )

def save_active_round(round_data):
    st.session_state[
        "active_round_cloud_session"
    ] = round_data

def clear_active_round():
    st.session_state.pop(
        "active_round_cloud_session",
        None
    )

def append_round_history(round_data):
    if _cloud_ready():
        user_id = _cloud_user_id()
        round_id = round_data.get(
            "round_id"
        ) or str(
            uuid.uuid4()
        )

        scores = round_data.get(
            "scores",
            {}
        )
        putts = round_data.get(
            "putts",
            {}
        )

        (
            supabase
            .table("rounds")
            .upsert({
                "id": round_id,
                "user_id": user_id,
                "course_name": round_data.get(
                    "course_name",
                    ""
                ) or "Unknown Course",
                "tee_name": round_data.get(
                    "tee",
                    ""
                ),
                "started_at": round_data.get(
                    "started_at"
                ) or datetime.now().isoformat(),
                "completed_at": datetime.now().isoformat(),
                "total_score": sum(
                    int(v)
                    for v in scores.values()
                    if str(v).isdigit()
                ),
                "total_putts": sum(
                    int(v)
                    for v in putts.values()
                    if str(v).isdigit()
                )
            })
            .execute()
        )

        hole_numbers = set()

        for container in [
            scores,
            putts,
            round_data.get(
                "fairways",
                {}
            ),
            round_data.get(
                "greens",
                {}
            )
        ]:
            hole_numbers.update(
                str(key)
                for key in container.keys()
            )

        hole_rows = []

        for hole_key in hole_numbers:
            hole_number = _safe_int(
                hole_key
            )

            if hole_number is None:
                continue

            hole_rows.append({
                "user_id": user_id,
                "round_id": round_id,
                "hole_number": hole_number,
                "score": _safe_int(
                    scores.get(
                        hole_key
                    )
                ),
                "putts": _safe_int(
                    putts.get(
                        hole_key
                    )
                ),
                "fairway_result": round_data.get(
                    "fairways",
                    {}
                ).get(
                    hole_key,
                    ""
                ),
                "green_result": round_data.get(
                    "greens",
                    {}
                ).get(
                    hole_key,
                    ""
                )
            })

        if hole_rows:
            (
                supabase
                .table("round_holes")
                .upsert(
                    hole_rows,
                    on_conflict="round_id,hole_number"
                )
                .execute()
            )

    row = {
        "Round ID": round_data.get(
            "round_id",
            ""
        ),
        "Date": round_data.get(
            "started_at",
            ""
        ),
        "Course": round_data.get(
            "course_name",
            ""
        ),
        "Tee": round_data.get(
            "tee",
            ""
        ),
        "Holes Completed": len(
            round_data.get(
                "scores",
                {}
            )
        ),
        "Total Score": sum(
            int(v)
            for v in round_data.get(
                "scores",
                {}
            ).values()
            if str(v).isdigit()
        ),
        "Total Putts": sum(
            int(v)
            for v in round_data.get(
                "putts",
                {}
            ).values()
            if str(v).isdigit()
        ),
        "Fairways Hit": sum(
            1
            for v in round_data.get(
                "fairways",
                {}
            ).values()
            if v == "Hit"
        ),
        "Greens Hit": sum(
            1
            for v in round_data.get(
                "greens",
                {}
            ).values()
            if v == "Hit"
        ),
        "Ended At": datetime.now().strftime(
            "%Y-%m-%d %H:%M"
        )
    }

    new_row = pd.DataFrame(
        [
            row
        ]
    )

    if os.path.exists(
        ROUND_HISTORY_FILE
    ):
        try:
            old = pd.read_csv(
                ROUND_HISTORY_FILE
            )
            combined = pd.concat(
                [
                    old,
                    new_row
                ],
                ignore_index=True
            )
        except Exception:
            combined = new_row
    else:
        combined = new_row

    combined.to_csv(
        ROUND_HISTORY_FILE,
        index=False
    )

def load_round_history():
    if _cloud_ready():
        try:
            response = (
                supabase
                .table("rounds")
                .select(
                    "id,started_at,completed_at,course_name,tee_name,total_score,total_putts"
                )
                .eq(
                    "user_id",
                    _cloud_user_id()
                )
                .order(
                    "started_at",
                    desc=True
                )
                .execute()
            )

            return pd.DataFrame(
                [
                    {
                        "Round ID": row.get("id", ""),
                        "Date": row.get("started_at", ""),
                        "Course": row.get("course_name", ""),
                        "Tee": row.get("tee_name", ""),
                        "Total Score": row.get("total_score"),
                        "Total Putts": row.get("total_putts"),
                        "Ended At": row.get("completed_at", "")
                    }
                    for row in (response.data or [])
                ]
            )
        except Exception as exc:
            st.error(
                f"Cloud round history read failed for this account: {exc}"
            )
            return pd.DataFrame()

    if os.path.exists(
        ROUND_HISTORY_FILE
    ):
        try:
            return pd.read_csv(
                ROUND_HISTORY_FILE
            )
        except Exception:
            return pd.DataFrame()

    return pd.DataFrame()

def new_round(
    course_name,
    course_id,
    tee_name=""
):
    return {
        "round_id": str(
            uuid.uuid4()
        ),
        "started_at": datetime.now().strftime(
            "%Y-%m-%d %H:%M"
        ),
        "course_name": course_name,
        "course_id": str(
            course_id
            or ""
        ),
        "tee": tee_name,
        "current_hole": 1,
        "scores": {},
        "putts": {},
        "fairways": {},
        "greens": {}
    }



# ============================================================
# UNIFIED PLAYER MODEL
# ============================================================

SOURCE_WEIGHTS = {
    "Live Round": 1.00,
    "On Course": 0.95,
    "Previous Round": 0.90,
    "Driving Range": 0.75,
    "Launch Monitor": 0.72,
    "Simulator": 0.70,
    "Manual": 0.60
}

def local_load_player_evidence():
    if os.path.exists(
        PLAYER_EVIDENCE_FILE
    ):
        try:
            return pd.read_csv(
                PLAYER_EVIDENCE_FILE
            )
        except Exception:
            return pd.DataFrame()

    return pd.DataFrame()

def local_append_player_evidence(rows):
    if not rows:
        return

    new_data = pd.DataFrame(
        rows
    )

    if os.path.exists(
        PLAYER_EVIDENCE_FILE
    ):
        try:
            old = pd.read_csv(
                PLAYER_EVIDENCE_FILE
            )

            combined = pd.concat(
                [
                    old,
                    new_data
                ],
                ignore_index=True
            )
        except Exception:
            combined = new_data
    else:
        combined = new_data

    combined.to_csv(
        PLAYER_EVIDENCE_FILE,
        index=False
    )


def preserve_raw_import(df, file_name, source_label):
    """Preserve every uploaded column before My Play normalizes known metrics."""
    if df is None or df.empty:
        return False, "The uploaded file did not contain any rows."

    safe_df = df.copy()
    safe_df.columns = [str(column) for column in safe_df.columns]
    safe_df = safe_df.astype(object).where(pd.notna(safe_df), None)
    raw_rows = safe_df.to_dict(orient="records")
    raw_columns = list(safe_df.columns)
    payload_text = json.dumps(raw_rows, default=str, sort_keys=True)
    raw_rows = json.loads(payload_text)
    import_hash = hashlib.sha256(payload_text.encode("utf-8")).hexdigest()
    payload = {
        "user_id": _cloud_user_id() if _cloud_ready() else None,
        "file_name": str(file_name or "uploaded_data"),
        "source": str(source_label or "Imported"),
        "import_hash": import_hash,
        "row_count": len(raw_rows),
        "raw_columns": raw_columns,
        "raw_rows": raw_rows,
        "uploaded_at": datetime.now().isoformat(),
    }

    os.makedirs(RAW_IMPORT_DIR, exist_ok=True)
    local_path = os.path.join(RAW_IMPORT_DIR, f"{import_hash}.json")
    if os.path.exists(local_path):
        return False, "This exact file has already been imported."

    cloud_saved = False
    if _cloud_ready():
        try:
            existing = (
                supabase.table("data_imports").select("id")
                .eq("user_id", _cloud_user_id())
                .eq("import_hash", import_hash).limit(1).execute()
            )
            if existing.data:
                return False, "This exact file has already been imported."
            supabase.table("data_imports").insert(payload).execute()
            cloud_saved = True
        except Exception:
            cloud_saved = False

    with open(local_path, "w", encoding="utf-8") as raw_file:
        json.dump(payload, raw_file, ensure_ascii=False, indent=2, default=str)

    if _cloud_ready() and not cloud_saved:
        return True, (
            "Every original column was preserved locally. Complete the My Player "
            "database upgrade to preserve raw imports in the golfer's cloud account too."
        )
    return True, "Every original column and value was preserved before mapping."

def shot_history_as_evidence(
    shots
):
    if shots.empty:
        return pd.DataFrame()

    rows = []

    for _, row in shots.iterrows():
        source = "On Course"

        if str(
            row.get(
                "Note",
                ""
            )
        ) == "Live Round":
            source = "Live Round"

        carry = pd.to_numeric(
            pd.Series(
                [
                    row.get(
                        "Actual Carry"
                    )
                ]
            ),
            errors="coerce"
        ).iloc[0]

        if pd.isna(
            carry
        ):
            carry = None

        rows.append({
            "Date": row.get(
                "Date",
                ""
            ),
            "Source": source,
            "Club": row.get(
                "Club Used",
                ""
            ),
            "Carry": carry,
            "Result": row.get(
                "Result",
                ""
            ),
            "Contact": row.get(
                "Contact",
                ""
            ),
            "Course": row.get(
                "Course",
                ""
            ),
            "Hole": row.get(
                "Hole",
                ""
            ),
            "Round ID": row.get(
                "Round ID",
                ""
            ),
            "Shot Type": row.get(
                "Shot Type",
                ""
            ),
            "Notes": row.get(
                "Note",
                ""
            )
        })

    return pd.DataFrame(
        rows
    )

def combined_player_evidence(
    shots
):
    stored = load_player_evidence()
    on_course = shot_history_as_evidence(
        shots
    )

    frames = []

    if not stored.empty:
        frames.append(
            stored
        )

    if not on_course.empty:
        frames.append(
            on_course
        )

    if not frames:
        return pd.DataFrame()

    combined = pd.concat(
        frames,
        ignore_index=True,
        sort=False
    )

    for col in [
        "Source",
        "Club",
        "Carry",
        "Result",
        "Contact",
        "Course",
        "Hole",
        "Round ID",
        "Shot Type",
        "Notes",
        "Date"
    ]:
        if col not in combined.columns:
            combined[
                col
            ] = ""

    combined[
        "Carry"
    ] = pd.to_numeric(
        combined[
            "Carry"
        ],
        errors="coerce"
    )

    return combined


def player_snapshot(round_history, evidence):
    scores = pd.Series(dtype="float64")
    if isinstance(round_history, pd.DataFrame) and not round_history.empty:
        score_column = "Total Score" if "Total Score" in round_history.columns else None
        if score_column:
            scores = pd.to_numeric(round_history[score_column], errors="coerce")
            scores = scores[(scores > 0) & (scores < 200)].dropna()

    shot_count = len(evidence) if isinstance(evidence, pd.DataFrame) else 0
    round_count = int(len(scores))
    confidence = "Building"
    if round_count >= 8 and shot_count >= 150:
        confidence = "Established"
    elif round_count >= 3 or shot_count >= 50:
        confidence = "Developing"

    return {
        "rounds": round_count,
        "average_score": float(scores.mean()) if not scores.empty else None,
        "recent_average": float(scores.head(5).mean()) if not scores.empty else None,
        "best_score": int(scores.min()) if not scores.empty else None,
        "shots": int(shot_count),
        "confidence": confidence,
    }


def normalized_miss_label(value):
    text = str(value or "").strip().lower()
    if not text or text in {"nan", "none", "unknown", "on target", "good"}:
        return ""
    if any(token in text for token in ["left", "pull", "hook", "draw"]):
        return "Left"
    if any(token in text for token in ["right", "push", "slice", "fade"]):
        return "Right"
    if "short" in text:
        return "Short"
    if "long" in text:
        return "Long"
    if any(token in text for token in ["thin", "fat", "heavy", "top", "poor", "mishit"]):
        return "Contact"
    return str(value).strip()


def learned_profile_insights(evidence):
    result = {
        "primary_tendency": "More shot results needed",
        "primary_count": 0,
        "reliable_club": "More club data needed",
        "reliable_club_count": 0,
        "data_note": "My Play will replace setup assumptions with learned patterns as evidence grows.",
    }
    if not isinstance(evidence, pd.DataFrame) or evidence.empty:
        return result

    work = evidence.copy()
    if "Result" in work.columns:
        misses = work["Result"].map(normalized_miss_label)
        misses = misses[misses.astype(str).str.strip() != ""]
        if not misses.empty:
            counts = misses.value_counts()
            result["primary_tendency"] = f"{counts.index[0]} is the most common recorded miss"
            result["primary_count"] = int(counts.iloc[0])

    if {"Club", "Carry"}.issubset(work.columns):
        work["Carry"] = pd.to_numeric(work["Carry"], errors="coerce")
        club_groups = work.dropna(subset=["Carry"]).groupby("Club")["Carry"].agg(["count", "std"])
        club_groups = club_groups[club_groups["count"] >= 3]
        if not club_groups.empty:
            club_groups["std"] = club_groups["std"].fillna(999)
            club_groups = club_groups.sort_values(["std", "count"], ascending=[True, False])
            result["reliable_club"] = str(club_groups.index[0])
            result["reliable_club_count"] = int(club_groups.iloc[0]["count"])
    return result


def endurance_phase_table(evidence):
    columns = [
        "Session phase", "Comparable shots", "Carry change",
        "Carry dispersion", "Solid contact", "Emerging tendency"
    ]
    if not isinstance(evidence, pd.DataFrame) or evidence.empty:
        return pd.DataFrame(columns=columns)

    required = {"Round ID", "Club", "Carry"}
    if not required.issubset(evidence.columns):
        return pd.DataFrame(columns=columns)

    work = evidence.copy()
    work["Round ID"] = work["Round ID"].fillna("").astype(str).str.strip()
    work = work[~work["Round ID"].isin(["", "nan", "None"])]
    work["Carry"] = pd.to_numeric(work["Carry"], errors="coerce")
    work = work.dropna(subset=["Carry"])
    if work.empty:
        return pd.DataFrame(columns=columns)

    work["Shot Sequence"] = work.groupby("Round ID").cumcount() + 1
    club_baselines = work.groupby("Club")["Carry"].median()
    work["Carry Delta"] = work.apply(
        lambda row: row["Carry"] - club_baselines.get(row["Club"], row["Carry"]), axis=1
    )
    phase_order = ["Opening · 1–20", "Middle · 21–40", "Late · 41–60", "Extended · 61+"]
    work["Session phase"] = pd.cut(
        work["Shot Sequence"], bins=[0, 20, 40, 60, float("inf")], labels=phase_order
    )

    rows = []
    for phase in phase_order:
        group = work[work["Session phase"].astype(str) == phase]
        if group.empty:
            continue
        misses = group.get("Result", pd.Series(dtype="object")).map(normalized_miss_label)
        misses = misses[misses.astype(str).str.strip() != ""]
        tendency = "No clear tendency"
        if not misses.empty:
            tendency = str(misses.value_counts().index[0])
        contact = group.get("Contact", pd.Series(dtype="object")).astype(str).str.lower()
        solid_rate = float(contact.str.contains("solid").mean() * 100) if len(contact) else None
        carry_delta = float(group["Carry Delta"].mean())
        dispersion = float(group["Carry Delta"].std()) if len(group) > 1 else None
        rows.append({
            "Session phase": phase,
            "Comparable shots": int(len(group)),
            "Carry change": f"{carry_delta:+.1f} yd",
            "Carry dispersion": f"{dispersion:.1f} yd" if dispersion is not None else "Need data",
            "Solid contact": f"{solid_rate:.0f}%" if solid_rate is not None else "Need data",
            "Emerging tendency": tendency,
        })
    return pd.DataFrame(rows, columns=columns)


def recommended_training(insights, endurance_table, evidence):
    recommendation = {
        "title": "Build a trustworthy baseline",
        "summary": "Record a focused 20-shot session with one mid-iron so My Play can measure carry and dispersion.",
        "time": "20 minutes",
        "location": "Driving range",
        "clubs": "One mid-iron",
        "steps": [
            "Hit 5 comfortable warm-up shots.",
            "Hit 10 shots to the same target and record every result.",
            "Finish with 5 shots using your normal on-course routine.",
        ],
        "reason": "More comparable evidence is needed before prescribing a narrower weakness.",
        "source_label": "My Play Original",
        "source_url": "",
    }

    if isinstance(endurance_table, pd.DataFrame) and not endurance_table.empty:
        late = endurance_table[endurance_table["Session phase"].str.contains("Late|Extended", regex=True)]
        if not late.empty and int(late["Comparable shots"].sum()) >= 8:
            recommendation.update({
                "title": "Late-round target-window training",
                "summary": "Recreate the point where your pattern changes and protect accuracy under accumulated swings.",
                "time": "25 minutes",
                "location": "Driving range",
                "clubs": "7 Iron and Driver",
                "steps": [
                    "Warm up normally, then hit 20 mixed shots.",
                    "Hit 10 seven-irons through a defined target window.",
                    "Finish with 5 driver and 5 seven-iron shots using a full pre-shot routine.",
                    "Save the complete session so My Play can compare early and late performance.",
                ],
                "reason": "Your stored rounds contain enough late-session shots to begin testing endurance.",
            })
            return recommendation

    tendency = str(insights.get("primary_tendency", ""))
    if any(direction in tendency for direction in ["Left", "Right"]):
        recommendation.update({
            "title": "Alignment and start-line checkpoint",
            "summary": "Use a defined target line to separate setup errors from the miss pattern My Play recorded.",
            "time": "15 minutes",
            "location": "Driving range",
            "clubs": "7 Iron",
            "steps": [
                "Place one alignment aid on the target line and one parallel to your feet.",
                "Hit 5 half-swings, then 10 normal shots to the same target.",
                "Record the starting direction and final miss for every shot.",
            ],
            "reason": tendency + ".",
            "source_label": "Adapted from a PGA professional strategy",
            "source_url": "https://www.pga.com/story/get-your-golf-game-ready-4-easy-drills-for-a-better-start-to-the-season",
        })
    return recommendation


def build_round_biography(round_row, evidence, all_rounds):
    row = round_row.to_dict() if hasattr(round_row, "to_dict") else dict(round_row or {})
    round_id = str(row.get("Round ID", "") or "").strip()
    course = str(row.get("Course", "") or "Unknown course")
    score = pd.to_numeric(pd.Series([row.get("Total Score")]), errors="coerce").iloc[0]
    round_shots = pd.DataFrame()
    if isinstance(evidence, pd.DataFrame) and not evidence.empty and "Round ID" in evidence.columns and round_id:
        round_shots = evidence[evidence["Round ID"].fillna("").astype(str) == round_id].copy()

    scores = pd.Series(dtype="float64")
    if isinstance(all_rounds, pd.DataFrame) and "Total Score" in all_rounds.columns:
        scores = pd.to_numeric(all_rounds["Total Score"], errors="coerce")
        scores = scores[(scores > 0) & (scores < 200)].dropna()
    comparison = ""
    if pd.notna(score) and len(scores) >= 2:
        baseline = float(scores.mean())
        difference = float(score - baseline)
        if abs(difference) < 0.6:
            comparison = "right around your recorded scoring average"
        elif difference < 0:
            comparison = f"{abs(difference):.1f} strokes better than your recorded average"
        else:
            comparison = f"{difference:.1f} strokes above your recorded average"

    opening = f"At {course}, you posted {int(score) if pd.notna(score) else 'a recorded round'}"
    if comparison:
        opening += f"—{comparison}."
    else:
        opening += "."

    details = []
    if not round_shots.empty:
        details.append(f"My Play registered {len(round_shots)} shots connected to this round.")
        misses = round_shots.get("Result", pd.Series(dtype="object")).map(normalized_miss_label)
        misses = misses[misses.astype(str).str.strip() != ""]
        if not misses.empty:
            details.append(f"The most frequent recorded outcome was {str(misses.value_counts().index[0]).lower()}.")
    else:
        details.append("Detailed shot-by-shot conclusions will appear when shots are saved to this round.")

    return {
        "title": f"{course} · {int(score) if pd.notna(score) else 'Round'}",
        "story": " ".join([opening] + details),
        "shots": int(len(round_shots)),
        "course": course,
        "score": int(score) if pd.notna(score) else None,
    }

def evidence_weight(
    source,
    contact=""
):
    weight = SOURCE_WEIGHTS.get(
        str(
            source
        ),
        0.60
    )

    contact_text = str(
        contact
    ).lower()

    if "solid" in contact_text:
        weight *= 1.10

    elif "poor" in contact_text:
        weight *= 0.45

    elif "mishit" in contact_text:
        weight *= 0.70

    return weight

def unified_club_profile(
    club_name,
    stock_carry,
    shots
):
    evidence = combined_player_evidence(
        shots
    )

    profile = {
        "club": club_name,
        "stock_carry": float(
            stock_carry
        ),
        "carry": float(
            stock_carry
        ),
        "sample_count": 0,
        "effective_weight": 0.0,
        "carry_std": None,
        "left_rate": 0.0,
        "right_rate": 0.0,
        "short_rate": 0.0,
        "long_rate": 0.0,
        "dominant_miss": "Not enough data",
        "source_breakdown": {}
    }

    if evidence.empty:
        return profile

    data = evidence[
        evidence[
            "Club"
        ].astype(
            str
        ) == str(
            club_name
        )
    ].copy()

    data = data.dropna(
        subset=[
            "Carry"
        ]
    )

    data = data[
        data[
            "Carry"
        ] > 0
    ]

    if data.empty:
        return profile

    weights = []

    for _, row in data.iterrows():
        weights.append(
            evidence_weight(
                row.get(
                    "Source",
                    "Manual"
                ),
                row.get(
                    "Contact",
                    ""
                )
            )
        )

    data[
        "_weight"
    ] = weights

    total_weight = float(
        data[
            "_weight"
        ].sum()
    )

    if total_weight > 0:
        weighted_carry = float(
            (
                data[
                    "Carry"
                ]
                * data[
                    "_weight"
                ]
            ).sum()
            / total_weight
        )

        # Blend with stock until enough trusted evidence exists.
        evidence_strength = min(
            1.0,
            total_weight / 5.0
        )

        profile[
            "carry"
        ] = (
            float(
                stock_carry
            )
            * (
                1.0 - evidence_strength
            )
            + weighted_carry
            * evidence_strength
        )

    profile[
        "sample_count"
    ] = len(
        data
    )

    profile[
        "effective_weight"
    ] = round(
        total_weight,
        2
    )

    if len(
        data
    ) >= 3:
        mean = profile[
            "carry"
        ]

        variance_weight = float(
            (
                data[
                    "_weight"
                ]
                * (
                    data[
                        "Carry"
                    ]
                    - mean
                ) ** 2
            ).sum()
            / max(
                total_weight,
                0.0001
            )
        )

        profile[
            "carry_std"
        ] = variance_weight ** 0.5

    results = (
        data[
            "Result"
        ]
        .fillna("")
        .astype(str)
        .str.lower()
    )

    if len(
        results
    ):
        left = results.str.contains(
            "left"
        )
        right = results.str.contains(
            "right"
        )
        short = results.str.contains(
            "short"
        )
        long = results.str.contains(
            "long"
        )

        result_weights = data[
            "_weight"
        ]

        denom = max(
            float(
                result_weights.sum()
            ),
            0.0001
        )

        profile[
            "left_rate"
        ] = float(
            result_weights[
                left
            ].sum()
            / denom
        )

        profile[
            "right_rate"
        ] = float(
            result_weights[
                right
            ].sum()
            / denom
        )

        profile[
            "short_rate"
        ] = float(
            result_weights[
                short
            ].sum()
            / denom
        )

        profile[
            "long_rate"
        ] = float(
            result_weights[
                long
            ].sum()
            / denom
        )

        rates = {
            "Left": profile[
                "left_rate"
            ],
            "Right": profile[
                "right_rate"
            ],
            "Short": profile[
                "short_rate"
            ],
            "Long": profile[
                "long_rate"
            ]
        }

        dominant = max(
            rates,
            key=rates.get
        )

        if (
            total_weight >= 4
            and rates[
                dominant
            ] >= 0.28
        ):
            profile[
                "dominant_miss"
            ] = dominant

    source_counts = (
        data[
            "Source"
        ]
        .fillna(
            "Unknown"
        )
        .astype(str)
        .value_counts()
        .to_dict()
    )

    profile[
        "source_breakdown"
    ] = source_counts

    return profile

def unified_game_model(
    bag,
    shots
):
    model = {}

    for club in bag:
        model[
            club[
                "Club"
            ]
        ] = unified_club_profile(
            club[
                "Club"
            ],
            float(
                club.get(
                    "Stock Carry",
                    0
                )
            ),
            shots
        )

    return model

def imported_session_to_evidence(
    df,
    club_col,
    carry_col,
    source_name,
    result_col=None,
    contact_col=None,
    optional_metric_columns=None
):
    rows = []

    for _, row in df.iterrows():
        club_value = str(
            row.get(
                club_col,
                ""
            )
        ).strip()

        carry_value = pd.to_numeric(
            pd.Series(
                [
                    row.get(
                        carry_col
                    )
                ]
            ),
            errors="coerce"
        ).iloc[0]

        if (
            not club_value
            or pd.isna(
                carry_value
            )
            or float(
                carry_value
            ) <= 0
        ):
            continue

        evidence_row = {
            "Date": datetime.now().strftime(
                "%Y-%m-%d %H:%M"
            ),
            "Source": source_name,
            "Club": club_value,
            "Carry": float(
                carry_value
            ),
            "Result": (
                str(
                    row.get(
                        result_col,
                        ""
                    )
                )
                if result_col
                else ""
            ),
            "Contact": (
                str(
                    row.get(
                        contact_col,
                        ""
                    )
                )
                if contact_col
                else ""
            ),
            "Course": "",
            "Hole": "",
            "Round ID": "",
            "Notes": (
                f"Imported {source_name} session"
            )
        }

        optional_metric_columns = (
            optional_metric_columns
            or {}
        )

        for target_name, source_column in optional_metric_columns.items():
            if (
                source_column
                and source_column != "None"
            ):
                value = pd.to_numeric(
                    pd.Series(
                        [
                            row.get(
                                source_column
                            )
                        ]
                    ),
                    errors="coerce"
                ).iloc[0]

                if not pd.isna(
                    value
                ):
                    evidence_row[
                        target_name
                    ] = float(
                        value
                    )

        rows.append(
            evidence_row
        )

    return rows

def unified_context_summary(
    club_name,
    bag,
    shots,
    hole_memory=None,
    weather=None,
    gps_green_distance=None
):
    club = next(
        (
            c
            for c in bag
            if c[
                "Club"
            ] == club_name
        ),
        None
    )

    if not club:
        return []

    profile = unified_club_profile(
        club_name,
        float(
            club.get(
                "Stock Carry",
                0
            )
        ),
        shots
    )

    notes = []

    if profile[
        "sample_count"
    ]:
        sources = ", ".join(
            f"{k}: {v}"
            for k, v in profile[
                "source_breakdown"
            ].items()
        )

        notes.append(
            f"Unified club model uses {profile['sample_count']} data points ({sources})."
        )

    if profile[
        "dominant_miss"
    ] != "Not enough data":
        notes.append(
            f"Weighted miss tendency: {profile['dominant_miss']}."
        )

    category = infer_club_category(club_name)
    tendency_key = {
        "Driver": "driver_miss",
        "Fairway Wood": "wood_miss",
        "Hybrid / Rescue": "wood_miss",
        "Utility / Driving Iron": "iron_miss",
        "Iron": "iron_miss",
        "Wedge": "wedge_miss",
    }.get(category)
    saved_miss = game_profile.get(tendency_key, "unknown") if tendency_key else "unknown"
    if saved_miss not in ("", "unknown", None):
        notes.append(f"Saved {category.lower()} tendency: {saved_miss}.")

    if hole_memory and hole_memory.get(
        "common_result"
    ):
        notes.append(
            f"Hole history trend: {hole_memory['common_result']}."
        )

    if weather:
        notes.append(
            f"Live weather: {round(float(weather.get('temperature_2m', 70)))}°F, "
            f"{round(float(weather.get('wind_speed_10m', 0)))} mph wind."
        )

    if gps_green_distance is not None:
        notes.append(
            f"GPS green-center distance: about {round(gps_green_distance)} yards."
        )

    return notes[:4]




def require_bag_for_feature(
    feature_name
):
    if bag:
        return True

    st.info(
        f"Add at least one club in **My Bag** before using {feature_name}."
    )

    return False

# ============================================================
# CLUB ANALYTICS / CADDIE NUMBERS
# ============================================================

def weighted_percentile(values, weights, percentile):
    if not values:
        return None

    pairs = sorted(
        zip(
            values,
            weights
        ),
        key=lambda item: item[0]
    )

    total = sum(
        max(
            float(weight),
            0.0
        )
        for _, weight in pairs
    )

    if total <= 0:
        return None

    target = total * percentile
    running = 0.0

    for value, weight in pairs:
        running += max(
            float(weight),
            0.0
        )

        if running >= target:
            return float(
                value
            )

    return float(
        pairs[-1][0]
    )

def comprehensive_club_analytics(
    club,
    shots
):
    club_name = club[
        "Club"
    ]

    stock_carry = float(
        club.get(
            "Stock Carry",
            0
        )
    )

    evidence = combined_player_evidence(
        shots
    )

    base = unified_club_profile(
        club_name,
        stock_carry,
        shots
    )

    data = pd.DataFrame()

    if not evidence.empty:
        data = evidence[
            evidence[
                "Club"
            ].astype(
                str
            ) == str(
                club_name
            )
        ].copy()

    if not data.empty:
        data[
            "Carry"
        ] = pd.to_numeric(
            data[
                "Carry"
            ],
            errors="coerce"
        )

        data = data.dropna(
            subset=[
                "Carry"
            ]
        )

        data = data[
            data[
                "Carry"
            ] > 0
        ]

    weights = []
    carries = []

    if not data.empty:
        for _, row in data.iterrows():
            carries.append(
                float(
                    row[
                        "Carry"
                    ]
                )
            )

            weights.append(
                evidence_weight(
                    row.get(
                        "Source",
                        "Manual"
                    ),
                    row.get(
                        "Contact",
                        ""
                    )
                )
            )

    reliable_carry = weighted_percentile(
        carries,
        weights,
        0.20
    )

    median_carry = weighted_percentile(
        carries,
        weights,
        0.50
    )

    upper_carry = weighted_percentile(
        carries,
        weights,
        0.80
    )

    if reliable_carry is None:
        reliable_carry = stock_carry

    if median_carry is None:
        median_carry = base[
            "carry"
        ]

    if upper_carry is None:
        upper_carry = base[
            "carry"
        ]

    sample_count = base[
        "sample_count"
    ]

    carry_std = base[
        "carry_std"
    ]

    if sample_count >= 20:
        confidence = "Very High"
    elif sample_count >= 10:
        confidence = "High"
    elif sample_count >= 5:
        confidence = "Medium"
    elif sample_count >= 1:
        confidence = "Developing"
    else:
        confidence = "Baseline"

    if (
        carry_std is not None
        and carry_std > 15
        and confidence in (
            "Very High",
            "High"
        )
    ):
        confidence = "Medium"

    solid_contact_rate = None

    if (
        not data.empty
        and "Contact" in data.columns
    ):
        contact = (
            data[
                "Contact"
            ]
            .fillna("")
            .astype(str)
            .str.lower()
        )

        known = contact != ""

        if known.any():
            solid_contact_rate = float(
                contact[
                    known
                ]
                .str.contains(
                    "solid"
                )
                .mean()
            )

    recent_carry = None
    recent_vs_baseline = None

    if not data.empty:
        recent = data.tail(
            min(
                10,
                len(
                    data
                )
            )
        )

        recent_weights = [
            evidence_weight(
                row.get(
                    "Source",
                    "Manual"
                ),
                row.get(
                    "Contact",
                    ""
                )
            )
            for _, row in recent.iterrows()
        ]

        if sum(
            recent_weights
        ) > 0:
            recent_carry = float(
                (
                    recent[
                        "Carry"
                    ]
                    * recent_weights
                ).sum()
                / sum(
                    recent_weights
                )
            )

            recent_vs_baseline = (
                recent_carry
                - float(
                    base[
                        "carry"
                    ]
                )
            )

    source_performance = {}

    if not data.empty:
        for source_name, group in data.groupby(
            "Source"
        ):
            source_performance[
                str(
                    source_name
                )
            ] = {
                "count": len(
                    group
                ),
                "carry": round(
                    float(
                        group[
                            "Carry"
                        ].mean()
                    ),
                    1
                )
            }

    optional_metrics = {}

    metric_columns = [
        ("Total", "Average Total"),
        ("Offline", "Average Offline"),
        ("Ball Speed", "Ball Speed"),
        ("Club Speed", "Club Speed"),
        ("Launch", "Launch Angle"),
        ("Spin", "Spin Rate"),
        ("Apex", "Apex")
    ]

    for column, label in metric_columns:
        if (
            not data.empty
            and column in data.columns
        ):
            numeric = pd.to_numeric(
                data[
                    column
                ],
                errors="coerce"
            ).dropna()

            if len(
                numeric
            ):
                optional_metrics[
                    label
                ] = round(
                    float(
                        numeric.mean()
                    ),
                    1
                )

    return {
        "club": club_name,
        "stock_carry": stock_carry,
        "playing_carry": round(
            float(
                base[
                    "carry"
                ]
            ),
            1
        ),
        "reliable_carry": round(
            float(
                reliable_carry
            ),
            1
        ),
        "median_carry": round(
            float(
                median_carry
            ),
            1
        ),
        "upper_carry": round(
            float(
                upper_carry
            ),
            1
        ),
        "sample_count": sample_count,
        "carry_std": (
            round(
                float(
                    carry_std
                ),
                1
            )
            if carry_std is not None
            else None
        ),
        "confidence": confidence,
        "dominant_miss": base[
            "dominant_miss"
        ],
        "left_rate": base[
            "left_rate"
        ],
        "right_rate": base[
            "right_rate"
        ],
        "short_rate": base[
            "short_rate"
        ],
        "long_rate": base[
            "long_rate"
        ],
        "solid_contact_rate": solid_contact_rate,
        "recent_carry": (
            round(
                recent_carry,
                1
            )
            if recent_carry is not None
            else None
        ),
        "recent_vs_baseline": (
            round(
                recent_vs_baseline,
                1
            )
            if recent_vs_baseline is not None
            else None
        ),
        "source_performance": source_performance,
        "source_breakdown": base[
            "source_breakdown"
        ],
        "optional_metrics": optional_metrics
    }

def bag_gapping_table(
    bag,
    shots
):
    rows = []

    analytics = [
        comprehensive_club_analytics(
            club,
            shots
        )
        for club in bag
    ]

    analytics = sorted(
        analytics,
        key=lambda item: item[
            "playing_carry"
        ],
        reverse=True
    )

    previous_carry = None

    for item in analytics:
        gap = None

        if previous_carry is not None:
            gap = round(
                previous_carry
                - item[
                    "playing_carry"
                ],
                1
            )

        rows.append({
            "Club": item[
                "club"
            ],
            "Reliable Carry": item[
                "reliable_carry"
            ],
            "Playing Carry": item[
                "playing_carry"
            ],
            "Upper Carry": item[
                "upper_carry"
            ],
            "Gap From Club Above": (
                gap
                if gap is not None
                else ""
            ),
            "Carry SD": (
                item[
                    "carry_std"
                ]
                if item[
                    "carry_std"
                ] is not None
                else ""
            ),
            "Dominant Miss": item[
                "dominant_miss"
            ],
            "Confidence": item[
                "confidence"
            ],
            "Evidence": item[
                "sample_count"
            ]
        })

        previous_carry = item[
            "playing_carry"
        ]

    return pd.DataFrame(
        rows
    )

def caddie_number_guidance(
    analytics
):
    guidance = []

    guidance.append(
        f"Use about {round(analytics['reliable_carry'])} yards as the conservative carry number "
        f"when you absolutely must cover a front hazard."
    )

    guidance.append(
        f"Use about {round(analytics['playing_carry'])} yards as the normal planning carry."
    )

    if analytics[
        "upper_carry"
    ] > analytics[
        "playing_carry"
    ] + 2:
        guidance.append(
            f"A flushed shot can reach roughly {round(analytics['upper_carry'])} yards, "
            f"but My Play should not assume that number for a forced carry."
        )

    if analytics[
        "dominant_miss"
    ] != "Not enough data":
        guidance.append(
            f"Build targets around the learned {analytics['dominant_miss'].lower()} miss."
        )

    if analytics[
        "carry_std"
    ] is not None:
        if analytics[
            "carry_std"
        ] <= 7:
            guidance.append(
                "Distance control is currently tight for this club."
            )
        elif analytics[
            "carry_std"
        ] >= 15:
            guidance.append(
                "Distance dispersion is wide; favor larger landing areas and safer fronts."
            )

    return guidance[:4]

def caddie_essentials_summary(
    bag,
    shots
):
    gap_df = bag_gapping_table(
        bag,
        shots
    )

    notes = []

    if not gap_df.empty:
        numeric_gaps = pd.to_numeric(
            gap_df[
                "Gap From Club Above"
            ],
            errors="coerce"
        ).dropna()

        large_gaps = gap_df[
            pd.to_numeric(
                gap_df[
                    "Gap From Club Above"
                ],
                errors="coerce"
            ) >= 20
        ]

        tiny_gaps = gap_df[
            pd.to_numeric(
                gap_df[
                    "Gap From Club Above"
                ],
                errors="coerce"
            ) <= 7
        ]

        if len(
            large_gaps
        ):
            clubs = ", ".join(
                large_gaps[
                    "Club"
                ].astype(
                    str
                ).tolist()
            )

            notes.append(
                f"Potential large bag gap near: {clubs}."
            )

        if len(
            tiny_gaps
        ):
            clubs = ", ".join(
                tiny_gaps[
                    "Club"
                ].astype(
                    str
                ).tolist()
            )

            notes.append(
                f"Potential carry overlap near: {clubs}."
            )

    low_confidence = []

    for club in bag:
        item = comprehensive_club_analytics(
            club,
            shots
        )

        if item[
            "confidence"
        ] in (
            "Baseline",
            "Developing"
        ):
            low_confidence.append(
                item[
                    "club"
                ]
            )

    if low_confidence:
        notes.append(
            "My Play needs more real data for: "
            + ", ".join(
                low_confidence[:5]
            )
            + (
                "..."
                if len(
                    low_confidence
                ) > 5
                else ""
            )
        )

    return notes[:4]




# ============================================================
# SUPABASE SWING VIDEO STORAGE
# ============================================================

SWING_VIDEO_BUCKET = "Swing-Videos"
SWING_VIDEO_CACHE_DIR = "swing_video_cache"

def upload_swing_video_to_cloud(
    local_path,
    filename
):
    if not _cloud_ready():
        return None

    user_id = _cloud_user_id()
    storage_path = f"{user_id}/{filename}"

    try:
        mime_type, _ = mimetypes.guess_type(
            filename
        )

        if not mime_type:
            mime_type = "video/mp4"

        with open(
            local_path,
            "rb"
        ) as file_handle:
            (
                supabase
                .storage
                .from_(
                    SWING_VIDEO_BUCKET
                )
                .upload(
                    path=storage_path,
                    file=file_handle,
                    file_options={
                        "content-type": mime_type,
                        "cache-control": "3600",
                        "upsert": "false"
                    }
                )
            )

        cloud_files = (
            supabase
            .storage
            .from_(
                SWING_VIDEO_BUCKET
            )
            .list(
                user_id,
                {
                    "limit": 100,
                    "offset": 0
                }
            )
        )

        cloud_names = [
            str(
                item.get(
                    "name",
                    ""
                )
            )
            for item in (
                cloud_files
                or []
            )
        ]

        if filename not in cloud_names:
            raise RuntimeError(
                "Upload call returned, but the file was not visible in "
                "your private Supabase folder."
            )

        st.session_state[
            "last_video_cloud_upload"
        ] = f"Cloud upload verified: {storage_path}"

        st.session_state.pop(
            "last_video_cloud_error",
            None
        )

        return storage_path

    except Exception as exc:
        st.session_state[
            "last_video_cloud_error"
        ] = str(
            exc
        )

        return None

def signed_swing_video_url(
    storage_path,
    expires_seconds=3600
):
    if (
        not _cloud_ready()
        or not storage_path
    ):
        return None

    try:
        response = (
            supabase
            .storage
            .from_(
                SWING_VIDEO_BUCKET
            )
            .create_signed_url(
                storage_path,
                expires_seconds
            )
        )

        if isinstance(
            response,
            dict
        ):
            return (
                response.get(
                    "signedURL"
                )
                or response.get(
                    "signedUrl"
                )
                or response.get(
                    "signed_url"
                )
            )

        return None

    except Exception as exc:
        st.warning(
            f"Could not open cloud swing video: {exc}"
        )
        return None

def delete_swing_video_from_cloud(
    storage_path
):
    if (
        not _cloud_ready()
        or not storage_path
    ):
        return

    try:
        (
            supabase
            .storage
            .from_(
                SWING_VIDEO_BUCKET
            )
            .remove(
                [
                    storage_path
                ]
            )
        )
    except Exception:
        pass


# ============================================================
# SWING VIDEO BETA
# ============================================================

def ensure_swing_video_dir():
    os.makedirs(
        SWING_VIDEO_DIR,
        exist_ok=True
    )


def local_swing_video_path_for_id(
    video_id
):
    if not os.path.exists(
        SWING_VIDEO_FILE
    ):
        return None

    try:
        local_history = pd.read_csv(
            SWING_VIDEO_FILE
        )

        if (
            local_history.empty
            or "Video ID" not in local_history.columns
        ):
            return None

        match = local_history[
            local_history[
                "Video ID"
            ].astype(
                str
            ) == str(
                video_id
            )
        ]

        if match.empty:
            return None

        local_path = str(
            match.iloc[-1].get(
                "Path",
                ""
            )
        ).strip()

        if (
            local_path
            and os.path.exists(
                local_path
            )
        ):
            return local_path

    except Exception:
        pass

    return None

def load_swing_video_history():
    if _cloud_ready():
        try:
            response = (
                supabase
                .table("swing_videos")
                .select(
                    "id,recorded_at,club_name,session_type,label,storage_path,"
                    "is_baseline,tempo,setup,balance,backswing,transition,finish,"
                    "observation_notes"
                )
                .eq(
                    "user_id",
                    _cloud_user_id()
                )
                .order(
                    "recorded_at"
                )
                .execute()
            )

            cloud_rows = []

            for row in (
                response.data
                or []
            ):
                video_id = row.get(
                    "id",
                    ""
                )

                stored_path = str(
                    row.get(
                        "storage_path",
                        ""
                    )
                    or ""
                ).strip()

                # If an earlier cloud upload failed, recover the working
                # local H.264/original path from the backup history.
                if not stored_path:
                    stored_path = (
                        local_swing_video_path_for_id(
                            video_id
                        )
                        or ""
                    )

                cloud_rows.append({
                    "Video ID": video_id,
                    "Date": row.get("recorded_at", ""),
                    "Club": row.get("club_name", ""),
                    "Session Type": row.get("session_type", ""),
                    "Label": row.get("label", ""),
                    "Path": stored_path,
                    "Baseline": row.get("is_baseline", False),
                    "Tempo": row.get("tempo", ""),
                    "Setup": row.get("setup", ""),
                    "Balance": row.get("balance", ""),
                    "Backswing": row.get("backswing", ""),
                    "Transition": row.get("transition", ""),
                    "Finish": row.get("finish", ""),
                    "Observation Notes": row.get("observation_notes", "")
                })

            return pd.DataFrame(
                cloud_rows
            )
        except Exception as exc:
            st.error(
                f"Cloud swing metadata read failed for this account: {exc}"
            )
            return pd.DataFrame()

    if os.path.exists(
        SWING_VIDEO_FILE
    ):
        try:
            return pd.read_csv(
                SWING_VIDEO_FILE
            )
        except Exception:
            return pd.DataFrame()

    return pd.DataFrame()

def save_swing_video_history(
    history
):
    history.to_csv(
        SWING_VIDEO_FILE,
        index=False
    )


def normalize_swing_video_for_web(
    source_path
):
    """Create an H.264/AAC MP4 with fast-start metadata for browser playback."""
    try:
        import imageio_ffmpeg
    except Exception:
        return (
            source_path,
            False,
            "Video conversion support is not installed. Run: pip install imageio-ffmpeg"
        )

    source = Path(
        source_path
    )

    normalized_path = source.with_name(
        source.stem + "_web.mp4"
    )

    try:
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

        command = [
            ffmpeg_exe,
            "-y",
            "-i",
            str(source),
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "23",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            str(normalized_path)
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False
        )

        if (
            result.returncode == 0
            and normalized_path.exists()
            and normalized_path.stat().st_size > 0
        ):
            return (
                str(normalized_path),
                True,
                None
            )

        error_text = (
            result.stderr[-1200:]
            if result.stderr
            else "Unknown FFmpeg conversion error."
        )

        return (
            source_path,
            False,
            error_text
        )

    except Exception as exc:
        return (
            source_path,
            False,
            str(exc)
        )

def save_uploaded_swing_video(
    uploaded_file,
    club_name,
    session_type,
    label,
    make_baseline=False
):
    ensure_swing_video_dir()

    extension = Path(
        uploaded_file.name
    ).suffix.lower()

    if extension not in (
        ".mp4",
        ".mov",
        ".m4v",
        ".avi",
        ".webm"
    ):
        extension = ".mp4"

    video_id = str(
        uuid.uuid4()
    )

    safe_club = (
        str(
            club_name
        )
        .replace(
            "/",
            "-"
        )
        .replace(
            "\\",
            "-"
        )
        .replace(
            " ",
            "_"
        )
    )

    filename = (
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_"
        f"{safe_club}_{video_id[:8]}{extension}"
    )

    path = os.path.join(
        SWING_VIDEO_DIR,
        filename
    )

    with open(
        path,
        "wb"
    ) as f:
        f.write(
            uploaded_file.getbuffer()
        )

    normalized_path, normalized_ok, normalize_error = normalize_swing_video_for_web(
        path
    )

    upload_path = (
        normalized_path
        if normalized_ok
        else path
    )

    upload_filename = os.path.basename(
        upload_path
    )

    if not normalized_ok and normalize_error:
        st.warning(
            "My Play saved the original video, but could not create the "
            "browser-safe H.264 copy. "
            f"{normalize_error}"
        )

    history = load_swing_video_history()

    if make_baseline and not history.empty:
        if "Baseline" not in history.columns:
            history[
                "Baseline"
            ] = False

        history.loc[
            history[
                "Club"
            ].astype(
                str
            ) == str(
                club_name
            ),
            "Baseline"
        ] = False

    cloud_storage_path = upload_swing_video_to_cloud(
        upload_path,
        upload_filename
    )

    row = {
        "Video ID": video_id,
        "Date": datetime.now().strftime(
            "%Y-%m-%d %H:%M"
        ),
        "Club": club_name,
        "Session Type": session_type,
        "Label": label,
        "Path": (
            cloud_storage_path
            or upload_path
        ),
        "Baseline": bool(
            make_baseline
        ),
        "Tempo": "",
        "Setup": "",
        "Balance": "",
        "Backswing": "",
        "Transition": "",
        "Finish": "",
        "Observation Notes": ""
    }

    history = pd.concat(
        [
            history,
            pd.DataFrame(
                [
                    row
                ]
            )
        ],
        ignore_index=True
    )

    if _cloud_ready():
        (
            supabase
            .table("swing_videos")
            .insert({
                "id": video_id,
                "user_id": _cloud_user_id(),
                "recorded_at": row["Date"],
                "club_name": club_name,
                "session_type": session_type,
                "label": label,
                "storage_path": (
                    cloud_storage_path
                    or upload_path
                ),
                "is_baseline": bool(
                    make_baseline
                )
            })
            .execute()
        )

    save_swing_video_history(
        history
    )

    return video_id

def set_swing_video_baseline(
    video_id
):
    history = load_swing_video_history()

    if history.empty:
        return

    match = history[
        history[
            "Video ID"
        ].astype(
            str
        ) == str(
            video_id
        )
    ]

    if match.empty:
        return

    club_name = str(
        match.iloc[0].get(
            "Club",
            ""
        )
    )

    if "Baseline" not in history.columns:
        history[
            "Baseline"
        ] = False

    history.loc[
        history[
            "Club"
        ].astype(
            str
        ) == club_name,
        "Baseline"
    ] = False

    history.loc[
        history[
            "Video ID"
        ].astype(
            str
        ) == str(
            video_id
        ),
        "Baseline"
    ] = True

    if _cloud_ready():
        (
            supabase
            .table("swing_videos")
            .update({
                "is_baseline": False
            })
            .eq(
                "user_id",
                _cloud_user_id()
            )
            .eq(
                "club_name",
                club_name
            )
            .execute()
        )

        (
            supabase
            .table("swing_videos")
            .update({
                "is_baseline": True
            })
            .eq(
                "id",
                video_id
            )
            .execute()
        )

    save_swing_video_history(
        history
    )

def save_swing_observations(
    video_id,
    observations
):
    history = load_swing_video_history()

    if history.empty:
        return

    mask = (
        history[
            "Video ID"
        ].astype(
            str
        )
        == str(
            video_id
        )
    )

    for key, value in observations.items():
        if key not in history.columns:
            history[
                key
            ] = ""

        history.loc[
            mask,
            key
        ] = value

    if _cloud_ready():
        mapping = {
            "Tempo": "tempo",
            "Setup": "setup",
            "Balance": "balance",
            "Backswing": "backswing",
            "Transition": "transition",
            "Finish": "finish",
            "Observation Notes": "observation_notes"
        }

        payload = {
            cloud_key: observations[local_key]
            for local_key, cloud_key in mapping.items()
            if local_key in observations
        }

        if payload:
            (
                supabase
                .table("swing_videos")
                .update(
                    payload
                )
                .eq(
                    "id",
                    video_id
                )
                .execute()
            )

    save_swing_video_history(
        history
    )



def swing_video_mime_type(
    stored_path
):
    mime_type, _ = mimetypes.guess_type(
        str(
            stored_path
            or ""
        )
    )

    if mime_type and mime_type.startswith(
        "video/"
    ):
        return mime_type

    return "video/mp4"

def materialize_cloud_video(
    storage_path
):
    if (
        not _cloud_ready()
        or not storage_path
    ):
        return None

    try:
        os.makedirs(
            SWING_VIDEO_CACHE_DIR,
            exist_ok=True
        )

        filename = os.path.basename(
            storage_path
        )

        if not filename.lower().endswith(
            (
                ".mp4",
                ".mov",
                ".m4v",
                ".avi",
                ".webm"
            )
        ):
            filename += ".mp4"

        cache_path = os.path.join(
            SWING_VIDEO_CACHE_DIR,
            filename
        )

        video_bytes = (
            supabase
            .storage
            .from_(
                SWING_VIDEO_BUCKET
            )
            .download(
                storage_path
            )
        )

        if not video_bytes:
            return None

        with open(
            cache_path,
            "wb"
        ) as f:
            f.write(
                video_bytes
            )

        if (
            os.path.exists(
                cache_path
            )
            and os.path.getsize(
                cache_path
            ) > 0
        ):
            return cache_path

        return None

    except Exception as exc:
        st.warning(
            f"Could not materialize private swing video: {exc}"
        )
        return None

def resolve_swing_video_source(
    stored_path
):
    stored_path = str(
        stored_path
        or ""
    ).strip()

    if not stored_path:
        return None, "video/mp4"

    mime_type = swing_video_mime_type(
        stored_path
    )

    # Existing local file: use it directly.
    if os.path.exists(
        stored_path
    ):
        return stored_path, mime_type

    # Cloud file: download to a real local file first.
    if _cloud_ready():
        local_cache_path = materialize_cloud_video(
            stored_path
        )

        if local_cache_path:
            return (
                local_cache_path,
                swing_video_mime_type(
                    local_cache_path
                )
            )

    return None, mime_type

def display_swing_video(
    stored_path,
    label=None
):
    source, mime_type = resolve_swing_video_source(
        stored_path
    )

    if label:
        st.caption(
            label
        )

    if source is None:
        st.warning(
            "The swing video file could not be opened."
        )
        return False

    try:
        st.video(
            source,
            format=mime_type
        )

        st.caption(
            f"Playback file: {source} · {mime_type}"
        )

        return True

    except Exception as exc:
        st.warning(
            f"The video file was found, but the player could not display it: {exc}"
        )
        return False


def delete_saved_swing_video(
    video_id,
    stored_path
):
    stored_path = str(
        stored_path
        or ""
    ).strip()

    # Remove cloud object when the saved path points to the private bucket.
    if (
        _cloud_ready()
        and stored_path
        and "/" in stored_path
        and not os.path.exists(
            stored_path
        )
    ):
        try:
            (
                supabase
                .storage
                .from_(
                    SWING_VIDEO_BUCKET
                )
                .remove(
                    [
                        stored_path
                    ]
                )
            )
        except Exception:
            pass

    # Remove metadata from Supabase.
    if _cloud_ready():
        try:
            (
                supabase
                .table(
                    "swing_videos"
                )
                .delete()
                .eq(
                    "id",
                    str(
                        video_id
                    )
                )
                .execute()
            )
        except Exception as exc:
            st.warning(
                f"Could not remove cloud video record: {exc}"
            )

    # Remove a local file only when the path is actually local.
    if (
        stored_path
        and os.path.exists(
            stored_path
        )
    ):
        try:
            os.remove(
                stored_path
            )
        except Exception:
            pass

    # Remove from local metadata backup too.
    if os.path.exists(
        SWING_VIDEO_FILE
    ):
        try:
            history = pd.read_csv(
                SWING_VIDEO_FILE
            )

            if (
                not history.empty
                and "Video ID" in history.columns
            ):
                history = history[
                    history[
                        "Video ID"
                    ].astype(
                        str
                    ) != str(
                        video_id
                    )
                ]

                history.to_csv(
                    SWING_VIDEO_FILE,
                    index=False
                )
        except Exception:
            pass

def baseline_for_club(
    club_name,
    history
):
    if history.empty:
        return None

    if "Baseline" not in history.columns:
        return None

    club_rows = history[
        history[
            "Club"
        ].astype(
            str
        ) == str(
            club_name
        )
    ].copy()

    if club_rows.empty:
        return None

    baseline_mask = (
        club_rows[
            "Baseline"
        ]
        .astype(str)
        .str.lower()
        .isin(
            [
                "true",
                "1",
                "yes"
            ]
        )
    )

    baseline_rows = club_rows[
        baseline_mask
    ]

    if baseline_rows.empty:
        return None

    return baseline_rows.iloc[-1]

def swing_comparison_points(
    current_row,
    baseline_row
):
    if current_row is None or baseline_row is None:
        return []

    labels = [
        "Tempo",
        "Setup",
        "Balance",
        "Backswing",
        "Transition",
        "Finish"
    ]

    points = []

    for label in labels:
        current_value = str(
            current_row.get(
                label,
                ""
            )
        ).strip()

        baseline_value = str(
            baseline_row.get(
                label,
                ""
            )
        ).strip()

        if (
            current_value
            and baseline_value
            and current_value != baseline_value
        ):
            points.append(
                f"{label}: baseline '{baseline_value}' → current '{current_value}'."
            )

    return points[:5]


# ============================================================
# LOCAL OPEN COURSE CATALOG
# ============================================================

def ensure_local_course_catalog():
    if os.path.exists(LOCAL_COURSE_FILE):
        return True, None

    try:
        headers = {
            "User-Agent": "MyPlayGolfCaddie/1.0 (local course catalog)"
        }

        response = requests.get(
            LOCAL_COURSE_URL,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()

        with open(
            LOCAL_COURSE_FILE,
            "wb"
        ) as f:
            f.write(
                response.content
            )

        return True, None

    except Exception as error:
        return False, str(error)

@st.cache_data(show_spinner=False)
def load_local_course_catalog():
    if not os.path.exists(
        LOCAL_COURSE_FILE
    ):
        return pd.DataFrame()

    try:
        df = pd.read_csv(
            LOCAL_COURSE_FILE,
            compression="gzip",
            low_memory=False
        )

        for col in [
            "name",
            "city",
            "state",
            "country"
        ]:
            if col not in df.columns:
                df[col] = ""

        return df

    except Exception:
        return pd.DataFrame()

def search_local_courses(
    query,
    state="",
    limit=30
):
    df = load_local_course_catalog()

    if df.empty:
        return []

    q = normalize_name(
        query
    )

    raw_query = str(
        query or ""
    ).strip()

    zip_query = (
        raw_query
        if raw_query.isdigit()
        and len(
            raw_query
        ) == 5
        else ""
    )

    work = df.copy()

    if state.strip():
        work = work[
            work["state"]
            .fillna("")
            .astype(str)
            .str.upper()
            == state.strip().upper()
        ]

    def row_score(row):
        name = normalize_name(
            row.get(
                "name",
                ""
            )
        )

        city = normalize_name(
            row.get(
                "city",
                ""
            )
        )

        postal = str(
            row.get(
                "zip",
                ""
            )
            or row.get(
                "zipcode",
                ""
            )
            or row.get(
                "postal_code",
                ""
            )
            or row.get(
                "postal",
                ""
            )
            or ""
        ).strip()

        # CSVs sometimes parse ZIPs as numbers/floats.
        if postal.endswith(
            ".0"
        ):
            postal = postal[
                :-2
            ]

        postal = postal.zfill(
            5
        ) if postal.isdigit() else postal

        score = 0

        # ZIP should be the strongest local-search signal.
        if zip_query and postal == zip_query:
            score += 250

        if name == q:
            score += 100

        if q and name.startswith(
            q
        ):
            score += 60

        if q and q in name:
            score += 40

        if q and city == q:
            score += 90

        if q and q in city:
            score += 40

        terms = [
            t
            for t in q.split()
            if t
        ]

        matched = sum(
            1
            for term in terms
            if (
                term in name
                or term in city
                or term in normalize_name(
                    postal
                )
            )
        )

        score += matched * 10

        return score

    work["_myplay_score"] = work.apply(
        row_score,
        axis=1
    )

    work = work[
        work["_myplay_score"] > 0
    ]

    work = work.sort_values(
        by=[
            "_myplay_score",
            "name"
        ],
        ascending=[
            False,
            True
        ]
    ).head(
        limit
    )

    results = []

    for _, row in work.iterrows():
        result = row.to_dict()
        result["source"] = (
            "My Play Local Catalog"
        )
        result["raw"] = row.to_dict()
        results.append(
            result
        )

    return results

def local_scorecard_from_row(row):
    scorecard = []

    for hole in range(
        1,
        19
    ):
        par_key = f"hole_{hole}_par"
        hcp_keys = [
            f"hole_{hole}_handicap",
            f"hole_{hole}_hcp",
            f"hole_{hole}_stroke_index"
        ]

        par = row.get(
            par_key
        )

        if pd.isna(par):
            par = None

        hcp = None

        for key in hcp_keys:
            if key in row:
                value = row.get(
                    key
                )

                if not pd.isna(
                    value
                ):
                    hcp = value
                    break

        if par is not None or hcp is not None:
            scorecard.append({
                "hole": hole,
                "par": (
                    int(par)
                    if par is not None
                    and str(par).replace(".", "", 1).isdigit()
                    else par
                ),
                "handicap": hcp
            })

    return scorecard

def catalog_stats():
    df = load_local_course_catalog()

    if df.empty:
        return {
            "count": 0,
            "states": 0
        }

    return {
        "count": len(
            df
        ),
        "states": (
            df[
                "state"
            ]
            .dropna()
            .astype(str)
            .nunique()
            if "state"
            in df.columns
            else 0
        )
    }

def find_column(df, candidates):
    for candidate in candidates:
        if candidate in df.columns:
            return candidate
    return None

def coordinate_columns(df):
    lat_col = find_column(
        df,
        [
            "latitude",
            "lat",
            "course_latitude",
            "courseLatitude"
        ]
    )

    lon_col = find_column(
        df,
        [
            "longitude",
            "lng",
            "lon",
            "long",
            "course_longitude",
            "courseLongitude"
        ]
    )

    return lat_col, lon_col

def address_column(df):
    return find_column(
        df,
        [
            "address",
            "street_address",
            "streetAddress",
            "formatted_address",
            "formattedAddress"
        ]
    )

@st.cache_data(ttl=86400, show_spinner=False)
def geocode_location_text(location_text):
    params = {
        "q": location_text,
        "format": "jsonv2",
        "limit": 1,
        "countrycodes": "us"
    }

    headers = {
        "User-Agent": "MyPlayGolfCaddie/1.0 (ZIP and location lookup)"
    }

    response = requests.get(
        NOMINATIM_BASE,
        params=params,
        headers=headers,
        timeout=12
    )
    response.raise_for_status()

    results = response.json()

    if not results:
        return None

    return {
        "latitude": float(
            results[0]["lat"]
        ),
        "longitude": float(
            results[0]["lon"]
        ),
        "display_name": results[0].get(
            "display_name",
            location_text
        )
    }

def haversine_miles(
    lat1,
    lon1,
    lat2,
    lon2
):
    earth_radius_miles = 3958.7613

    phi1 = math.radians(
        float(lat1)
    )
    phi2 = math.radians(
        float(lat2)
    )

    delta_phi = math.radians(
        float(lat2) - float(lat1)
    )
    delta_lambda = math.radians(
        float(lon2) - float(lon1)
    )

    a = (
        math.sin(
            delta_phi / 2
        ) ** 2
        + math.cos(
            phi1
        )
        * math.cos(
            phi2
        )
        * math.sin(
            delta_lambda / 2
        ) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(
            a
        ),
        math.sqrt(
            1 - a
        )
    )

    return earth_radius_miles * c

def course_row_to_result(
    row,
    distance_miles=None
):
    item = row.to_dict()

    item["source"] = (
        "My Play Local Catalog"
    )
    item["raw"] = row.to_dict()

    if distance_miles is not None:
        item["distance_miles"] = round(
            float(
                distance_miles
            ),
            1
        )

    return item

def browse_courses_by_state(
    state,
    limit=300
):
    df = load_local_course_catalog()

    if df.empty:
        return []

    state = state.strip().upper()

    work = df[
        df["state"]
        .fillna("")
        .astype(str)
        .str.upper()
        == state
    ].copy()

    if "city" in work.columns:
        work = work.sort_values(
            by=[
                "city",
                "name"
            ],
            na_position="last"
        )
    else:
        work = work.sort_values(
            by="name"
        )

    return [
        course_row_to_result(
            row
        )
        for _, row in work.head(
            limit
        ).iterrows()
    ]

def browse_courses_by_city(
    city,
    state="",
    limit=150
):
    df = load_local_course_catalog()

    if df.empty:
        return []

    q = normalize_name(
        city
    )

    work = df.copy()

    if state.strip():
        work = work[
            work["state"]
            .fillna("")
            .astype(str)
            .str.upper()
            == state.strip().upper()
        ]

    city_norm = (
        work["city"]
        .fillna("")
        .astype(str)
        .map(
            normalize_name
        )
    )

    work = work[
        city_norm.str.contains(
            q,
            regex=False
        )
    ].copy()

    work = work.sort_values(
        by=[
            "city",
            "name"
        ],
        na_position="last"
    )

    return [
        course_row_to_result(
            row
        )
        for _, row in work.head(
            limit
        ).iterrows()
    ]

def browse_courses_near_location(
    latitude,
    longitude,
    radius_miles=25,
    limit=100
):
    df = load_local_course_catalog()

    if df.empty:
        return []

    lat_col, lon_col = coordinate_columns(
        df
    )

    if not lat_col or not lon_col:
        return []

    work = df.copy()

    work[lat_col] = pd.to_numeric(
        work[lat_col],
        errors="coerce"
    )

    work[lon_col] = pd.to_numeric(
        work[lon_col],
        errors="coerce"
    )

    work = work.dropna(
        subset=[
            lat_col,
            lon_col
        ]
    )

    distances = []

    for _, row in work.iterrows():
        try:
            miles = haversine_miles(
                latitude,
                longitude,
                row[lat_col],
                row[lon_col]
            )
        except Exception:
            miles = None

        distances.append(
            miles
        )

    work["_distance_miles"] = distances

    work = work.dropna(
        subset=[
            "_distance_miles"
        ]
    )

    work = work[
        work["_distance_miles"]
        <= float(
            radius_miles
        )
    ]

    work = work.sort_values(
        by="_distance_miles"
    ).head(
        limit
    )

    return [
        course_row_to_result(
            row,
            row[
                "_distance_miles"
            ]
        )
        for _, row in work.iterrows()
    ]


# ============================================================
# OPEN GOLF API
# ============================================================

def api_get(path, params=None, timeout=12):
    url = f"{OPEN_GOLF_BASE}{path}"
    headers = {
        "User-Agent": "MyPlayGolfCaddie/1.0"
    }

    response = requests.get(
        url,
        params=params,
        headers=headers,
        timeout=timeout
    )
    response.raise_for_status()
    return response.json()

def payload_list(payload):
    if isinstance(payload, list):
        return payload

    if not isinstance(payload, dict):
        return []

    for key in [
        "courses", "results", "data", "items",
        "holes", "tees", "nearby"
    ]:
        value = payload.get(key)
        if isinstance(value, list):
            return value

    return []

def get_first(d, keys, default=None):
    if not isinstance(d, dict):
        return default

    for key in keys:
        if key in d and d[key] not in (None, ""):
            return d[key]

    return default

def course_id(course):
    return get_first(
        course,
        ["id", "course_id", "courseId", "courseID", "public_id", "publicId"],
        ""
    )

def course_name_from_obj(course):
    return str(get_first(
        course,
        ["name", "course_name", "courseName", "facility_name", "facilityName"],
        "Unknown Course"
    ))

def course_location(course):
    parts = []

    city = get_first(course, ["city", "locality", "town"])
    state = get_first(course, ["state", "region", "state_code", "stateCode"])
    country = get_first(course, ["country", "country_code", "countryCode"])

    for item in [city, state, country]:
        if item:
            parts.append(str(item))

    return ", ".join(parts)

@st.cache_data(ttl=3600, show_spinner=False)
def search_courses_online(query, state=""):
    params = {
        "q": query,
        "limit": 20
    }

    if state.strip():
        params["state"] = state.strip().upper()

    payload = api_get(
        "/v1/courses/search",
        params=params
    )

    return payload_list(payload)

def search_all_free_sources(
    query,
    state=""
):
    custom_results = []
    local_results = []
    open_results = []
    osm_results = []
    errors = []

    try:
        custom_results = search_custom_courses(
            query,
            state
        )
    except Exception as error:
        errors.append(
            f"My Play course library: {error}"
        )

    try:
        local_results = search_local_courses(
            query,
            state
        )
    except Exception as error:
        errors.append(
            f"Local catalog: {error}"
        )

    # Live OpenGolf is useful for extra international/updated matches,
    # but local U.S. catalog is the primary search source.
    try:
        open_results = search_courses_online(
            query,
            state
        )
    except Exception as error:
        errors.append(
            f"OpenGolfAPI: {error}"
        )

    try:
        osm_results = search_osm_courses(
            query,
            state
        )
    except Exception as error:
        errors.append(
            f"OpenStreetMap: {error}"
        )

    merged = []
    seen_ids = set()
    seen_names = []

    def add_item(item):
        item_id = str(
            item.get(
                "id",
                ""
            )
        )

        name = normalize_name(
            result_name(
                item
            )
        )

        city = normalize_name(
            get_first(
                item,
                [
                    "city",
                    "locality",
                    "town"
                ],
                item.get(
                    "city",
                    ""
                )
            )
        )

        if item_id and item_id in seen_ids:
            return

        for existing_name, existing_city in seen_names:
            if (
                name
                and existing_name
                and (
                    name == existing_name
                    or name in existing_name
                    or existing_name in name
                )
            ):
                if (
                    not city
                    or not existing_city
                    or city == existing_city
                ):
                    return

        merged.append(
            item
        )

        if item_id:
            seen_ids.add(
                item_id
            )

        seen_names.append(
            (
                name,
                city
            )
        )

    # My Play saved courses win because they are golfer-confirmed.
    for item in custom_results:
        add_item(
            item
        )

    # Local data wins next because it makes the result stable and instant.
    for item in local_results:
        add_item(
            item
        )

    for item in open_results:
        enriched = dict(
            item
        )
        enriched["source"] = (
            "OpenGolfAPI Live"
        )
        enriched["raw"] = item
        add_item(
            enriched
        )

    for item in osm_results:
        add_item(
            item
        )

    return merged, errors

@st.cache_data(ttl=86400, show_spinner=False)
def fetch_course_detail(cid):
    return api_get(f"/v1/courses/{cid}")

@st.cache_data(ttl=86400, show_spinner=False)
def fetch_course_holes(cid):
    return api_get(f"/v1/courses/{cid}/holes")

@st.cache_data(ttl=86400, show_spinner=False)
def fetch_course_tees(cid):
    return api_get(f"/v1/courses/{cid}/tees")

@st.cache_data(ttl=86400, show_spinner=False)
def fetch_course_climate(cid):
    return api_get(f"/v1/courses/{cid}/climate")

def normalize_holes(payload):
    holes = payload_list(payload)

    if not holes and isinstance(payload, dict):
        scorecard = payload.get("scorecard")

        if isinstance(scorecard, list):
            holes = scorecard

        elif isinstance(scorecard, dict):
            for key in ["holes", "data", "items"]:
                if isinstance(scorecard.get(key), list):
                    holes = scorecard[key]
                    break

    rows = []

    for index, hole in enumerate(holes, start=1):
        if not isinstance(hole, dict):
            continue

        number = get_first(
            hole,
            ["hole", "number", "hole_number", "holeNumber", "num"],
            index
        )

        par = get_first(
            hole,
            ["par", "hole_par", "holePar"],
            None
        )

        handicap = get_first(
            hole,
            ["handicap", "hcp", "stroke_index", "strokeIndex", "hdcp"],
            None
        )

        yardage = get_first(
            hole,
            ["yardage", "yards", "distance", "length"],
            None
        )

        rows.append({
            "Hole": number,
            "Par": par,
            "Handicap": handicap,
            "Yardage": yardage,
            "Raw": hole
        })

    return rows

def normalize_tees(payload):
    tees = payload_list(payload)
    rows = []

    for tee in tees:
        if not isinstance(tee, dict):
            continue

        name = get_first(
            tee,
            ["name", "tee_name", "teeName", "color", "label"],
            "Tee"
        )

        rating = get_first(
            tee,
            ["rating", "course_rating", "courseRating"],
            None
        )

        slope = get_first(
            tee,
            ["slope", "slope_rating", "slopeRating"],
            None
        )

        total = get_first(
            tee,
            ["yardage", "yards", "total_yards", "totalYards", "length"],
            None
        )

        rows.append({
            "Tee": name,
            "Rating": rating,
            "Slope": slope,
            "Total Yardage": total,
            "Raw": tee
        })

    return rows

def hole_yardage_from_tee(tee_raw, hole_number):
    if not isinstance(tee_raw, dict):
        return None

    for key in ["holes", "yardages", "hole_yardages", "holeYardages"]:
        value = tee_raw.get(key)

        if isinstance(value, list):
            for idx, item in enumerate(value, start=1):
                if isinstance(item, dict):
                    num = get_first(
                        item,
                        ["hole", "number", "hole_number", "holeNumber"],
                        idx
                    )
                    if str(num) == str(hole_number):
                        return get_first(
                            item,
                            ["yardage", "yards", "distance", "length"],
                            None
                        )
                elif idx == int(hole_number):
                    return item

    return None

def cache_selected_course(course_data):
    save_json(COURSE_CACHE_FILE, course_data)

def load_cached_course():
    return load_json(COURSE_CACHE_FILE, {})


# ============================================================
# OPENSTREETMAP FREE FALLBACK
# ============================================================

def normalize_name(value):
    text = str(value or "").lower().strip()
    keep = []
    for ch in text:
        if ch.isalnum() or ch.isspace():
            keep.append(ch)
    return " ".join("".join(keep).split())

@st.cache_data(ttl=3600, show_spinner=False)
def search_osm_courses(query, state=""):
    q = query.strip()
    if state.strip():
        q = f"{q} golf course, {state.strip()}"
    else:
        q = f"{q} golf course"

    params = {
        "q": q,
        "format": "jsonv2",
        "limit": 15,
        "addressdetails": 1,
        "extratags": 1
    }

    headers = {
        "User-Agent": "MyPlayGolfCaddie/1.0 (course search)"
    }

    response = requests.get(
        NOMINATIM_BASE,
        params=params,
        headers=headers,
        timeout=12
    )
    response.raise_for_status()

    raw = response.json()
    results = []

    for item in raw:
        category = str(item.get("category", "")).lower()
        item_type = str(item.get("type", "")).lower()
        display = str(item.get("display_name", ""))

        # Keep golf-ish results only.
        if (
            "golf" not in display.lower()
            and "golf" not in category
            and "golf" not in item_type
        ):
            continue

        address = item.get("address", {}) or {}

        name = (
            item.get("name")
            or address.get("golf_course")
            or address.get("leisure")
            or display.split(",")[0]
        )

        results.append({
            "source": "OpenStreetMap",
            "id": f"osm:{item.get('osm_type')}:{item.get('osm_id')}",
            "name": name,
            "city": (
                address.get("city")
                or address.get("town")
                or address.get("village")
                or address.get("municipality")
                or ""
            ),
            "state": (
                address.get("state")
                or address.get("state_code")
                or ""
            ),
            "country": address.get("country_code", "").upper(),
            "latitude": item.get("lat"),
            "longitude": item.get("lon"),
            "display_name": display,
            "raw": item
        })

    return results

@st.cache_data(ttl=86400, show_spinner=False)
def fetch_osm_golf_features(lat, lon):
    query = f"""
    [out:json][timeout:20];
    (
      way(around:2500,{lat},{lon})["golf"="hole"];
      relation(around:2500,{lat},{lon})["golf"="hole"];
      way(around:2500,{lat},{lon})["golf"="green"];
      way(around:2500,{lat},{lon})["golf"="bunker"];
      way(around:2500,{lat},{lon})["golf"="tee"];
    );
    out center tags;
    """

    headers = {
        "User-Agent": "MyPlayGolfCaddie/1.0 (course features)"
    }

    response = requests.post(
        OVERPASS_URL,
        data=query,
        headers=headers,
        timeout=25
    )
    response.raise_for_status()
    return response.json()

def normalize_osm_features(payload):
    if not isinstance(payload, dict):
        return {
            "holes": [],
            "greens": [],
            "bunkers": [],
            "tees": []
        }

    grouped = {
        "holes": [],
        "greens": [],
        "bunkers": [],
        "tees": []
    }

    for element in payload.get("elements", []):
        tags = element.get("tags", {}) or {}
        golf_type = str(tags.get("golf", "")).lower()

        center = element.get(
            "center",
            {}
        ) or {}

        record = {
            "ref": tags.get("ref"),
            "name": tags.get("name"),
            "par": tags.get("par"),
            "handicap": tags.get("handicap"),
            "length": (
                tags.get("length")
                or tags.get("yardage")
                or tags.get("distance")
            ),
            "latitude": (
                center.get("lat")
                if center
                else element.get("lat")
            ),
            "longitude": (
                center.get("lon")
                if center
                else element.get("lon")
            ),
            "osm_id": element.get("id")
        }

        if golf_type == "hole":
            grouped["holes"].append(record)
        elif golf_type == "green":
            grouped["greens"].append(record)
        elif golf_type == "bunker":
            grouped["bunkers"].append(record)
        elif golf_type == "tee":
            grouped["tees"].append(record)

    def hole_sort_key(item):
        try:
            return int(item.get("ref"))
        except Exception:
            return 999

    grouped["holes"] = sorted(
        grouped["holes"],
        key=hole_sort_key
    )

    return grouped

def merge_course_results(open_results, osm_results):
    merged = []
    seen = set()

    # Prefer OpenGolf when a near-duplicate exists because it can have scorecards.
    for item in open_results:
        name = course_name_from_obj(item)
        city = str(get_first(item, ["city", "locality", "town"], ""))
        key = (normalize_name(name), normalize_name(city))

        enriched = dict(item)
        enriched["source"] = "OpenGolfAPI"
        enriched["raw"] = item

        merged.append(enriched)
        seen.add(key)

    for item in osm_results:
        key = (
            normalize_name(item.get("name")),
            normalize_name(item.get("city"))
        )

        # Basic fuzzy-ish duplicate suppression.
        duplicate = False
        for existing_key in seen:
            if key[0] and existing_key[0]:
                if (
                    key[0] == existing_key[0]
                    or key[0] in existing_key[0]
                    or existing_key[0] in key[0]
                ):
                    if not key[1] or not existing_key[1] or key[1] == existing_key[1]:
                        duplicate = True
                        break

        if not duplicate:
            merged.append(item)
            seen.add(key)

    return merged

def result_source(item):
    return item.get("source", "OpenGolfAPI")

def result_name(item):
    if result_source(item) == "OpenStreetMap":
        return str(item.get("name", "Unknown Course"))
    return course_name_from_obj(item)

def result_location(item):
    if result_source(item) == "OpenStreetMap":
        parts = [
            str(item.get("city", "")).strip(),
            str(item.get("state", "")).strip(),
            str(item.get("country", "")).strip()
        ]
        return ", ".join([p for p in parts if p])

    return course_location(item)



# ============================================================
# GPS + WEATHER
# ============================================================

@st.cache_data(ttl=600, show_spinner=False)
def fetch_current_weather(
    latitude,
    longitude
):
    url = (
        "https://api.open-meteo.com/v1/forecast"
    )

    params = {
        "latitude": float(
            latitude
        ),
        "longitude": float(
            longitude
        ),
        "current": (
            "temperature_2m,"
            "wind_speed_10m,"
            "wind_direction_10m,"
            "wind_gusts_10m,"
            "weather_code"
        ),
        "temperature_unit": "fahrenheit",
        "wind_speed_unit": "mph",
        "timezone": "auto"
    }

    response = requests.get(
        url,
        params=params,
        timeout=12
    )

    response.raise_for_status()

    payload = response.json()

    return payload.get(
        "current",
        {}
    )

def degrees_to_cardinal(
    degrees
):
    try:
        value = float(
            degrees
        ) % 360
    except Exception:
        return "—"

    directions = [
        "N",
        "NNE",
        "NE",
        "ENE",
        "E",
        "ESE",
        "SE",
        "SSE",
        "S",
        "SSW",
        "SW",
        "WSW",
        "W",
        "WNW",
        "NW",
        "NNW"
    ]

    index = int(
        (
            value + 11.25
        ) / 22.5
    ) % 16

    return directions[
        index
    ]

def weather_code_text(
    code
):
    mapping = {
        0: "Clear",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Rime fog",
        51: "Light drizzle",
        53: "Drizzle",
        55: "Heavy drizzle",
        61: "Light rain",
        63: "Rain",
        65: "Heavy rain",
        71: "Light snow",
        73: "Snow",
        75: "Heavy snow",
        80: "Rain showers",
        81: "Rain showers",
        82: "Heavy showers",
        95: "Thunderstorm"
    }

    try:
        return mapping.get(
            int(code),
            "Current conditions"
        )
    except Exception:
        return "Current conditions"

def selected_course_coordinates(
    selected_course
):
    if not selected_course:
        return None, None

    result = selected_course.get(
        "search_result",
        {}
    ) or {}

    lat_keys = [
        "latitude",
        "lat",
        "course_latitude",
        "courseLatitude"
    ]

    lon_keys = [
        "longitude",
        "lng",
        "lon",
        "long",
        "course_longitude",
        "courseLongitude"
    ]

    lat = get_first(
        result,
        lat_keys,
        None
    )

    lon = get_first(
        result,
        lon_keys,
        None
    )

    try:
        return float(
            lat
        ), float(
            lon
        )
    except Exception:
        return None, None

def mapped_green_for_hole(
    selected_course,
    hole_number
):
    if not selected_course:
        return None

    features = selected_course.get(
        "osm_features",
        {}
    ) or {}

    greens = features.get(
        "greens",
        []
    )

    target_ref = str(
        hole_number
    )

    for green in greens:
        if str(
            green.get(
                "ref",
                ""
            )
        ) == target_ref:
            if (
                green.get(
                    "latitude"
                ) is not None
                and green.get(
                    "longitude"
                ) is not None
            ):
                return green

    # Only use positional fallback when the mapping looks like a complete 18-hole set.
    if len(
        greens
    ) == 18:
        index = int(
            hole_number
        ) - 1

        if (
            0 <= index < len(
                greens
            )
        ):
            green = greens[
                index
            ]

            if (
                green.get(
                    "latitude"
                ) is not None
                and green.get(
                    "longitude"
                ) is not None
            ):
                return green

    return None

def gps_distance_yards(
    lat1,
    lon1,
    lat2,
    lon2
):
    return haversine_miles(
        lat1,
        lon1,
        lat2,
        lon2
    ) * 1760

# ============================================================
# LEARNED DISPERSION
# ============================================================

def learned_dispersion_for_club(
    club_name,
    shots
):
    club = next(
        (
            c
            for c in bag
            if c[
                "Club"
            ] == club_name
        ),
        None
    )

    stock = float(
        club.get(
            "Stock Carry",
            0
        )
    ) if club else 0.0

    profile = unified_club_profile(
        club_name,
        stock,
        shots
    )

    return {
        "sample_count": profile[
            "sample_count"
        ],
        "carry_std": profile[
            "carry_std"
        ],
        "left_rate": profile[
            "left_rate"
        ],
        "right_rate": profile[
            "right_rate"
        ],
        "short_rate": profile[
            "short_rate"
        ],
        "long_rate": profile[
            "long_rate"
        ],
        "dominant_miss": profile[
            "dominant_miss"
        ]
    }

def learned_aim_compensation(
    dispersion
):
    # Positive = move aim right. Negative = move aim left.
    if dispersion.get(
        "sample_count",
        0
    ) < 5:
        return 0.0

    left_rate = dispersion.get(
        "left_rate",
        0
    )

    right_rate = dispersion.get(
        "right_rate",
        0
    )

    difference = (
        left_rate
        - right_rate
    )

    # Frequent left misses -> aim farther right.
    if difference >= 0.15:
        return min(
            2.5,
            difference * 5
        )

    # Frequent right misses -> aim farther left.
    if difference <= -0.15:
        return max(
            -2.5,
            difference * 5
        )

    return 0.0


# ============================================================
# CLUB LEARNING
# ============================================================

def club_display_name(club):
    brand = str(club.get("Brand / Model", "")).strip()
    return f"{club['Club']} - {brand}" if brand else club["Club"]

def learned_carry_for_club(club_name, stock_carry, shots):
    profile = unified_club_profile(
        club_name,
        stock_carry,
        shots
    )

    return (
        float(
            profile[
                "carry"
            ]
        ),
        int(
            profile[
                "sample_count"
            ]
        )
    )

# ============================================================
# LIE + ENVIRONMENT
# ============================================================

def lie_adjustment(surface, lie_type, stance, severity):
    yards = 0.0
    penalty = 0
    notes = []

    sev_mult = {
        "Slight": 0.5,
        "Moderate": 1.0,
        "Severe": 1.5
    }.get(severity, 1.0)

    surface_map = {
        "Fairway": (0, 0, ""),
        "Light Rough": (3, 1, "Light rough can reduce spin and strike consistency."),
        "Heavy Rough": (8, 2, "Heavy rough can reduce speed, spin, and distance control."),
        "Fairway Bunker": (6, 2, "Prioritize clean contact and enough loft to clear the lip."),
        "Greenside Bunker": (12, 3, "Greenside bunker distance is highly lie-dependent."),
        "Hardpan": (-2, 1, "Hardpan lowers margin for strike error."),
        "Wet / Soft Turf": (3, 1, "Soft turf reduces rollout and punishes heavy contact."),
        "Recovery": (10, 3, "Prioritize getting the ball back into a safe position.")
    }

    dy, dp, note = surface_map[surface]
    yards += dy
    penalty += dp

    if note:
        notes.append(note)

    if lie_type == "Sitting Up":
        yards -= 2
        notes.append(
            "The ball is sitting up, so launch should be easier."
        )

    elif lie_type == "Flyer":
        yards -= 6
        penalty += 2
        notes.append(
            "Flyer lie: expect less spin and possible extra carry."
        )

    elif lie_type == "Buried":
        yards += 8
        penalty += 3
        notes.append(
            "Buried lie: expect reduced speed and unpredictable carry."
        )

    if stance == "Uphill Lie":
        yards += 4 * sev_mult
        penalty += round(sev_mult)
        notes.append(
            f"{severity} uphill lie: expect higher launch and slightly reduced carry."
        )

    elif stance == "Downhill Lie":
        yards += 3 * sev_mult
        penalty += round(1.5 * sev_mult)
        notes.append(
            f"{severity} downhill lie: expect lower launch and harder contact."
        )

    elif stance in (
        "Ball Above Feet",
        "Ball Below Feet"
    ):
        penalty += max(
            1,
            round(sev_mult)
        )
        notes.append(
            f"{severity} sidehill lie increases directional and strike uncertainty."
        )

    return yards, penalty, notes

def playing_distance(
    distance,
    temperature,
    wind_direction,
    wind_speed,
    elevation,
    green_firmness,
    lie_yards
):
    adjusted = float(distance)
    reasons = []

    temp = (
        70 - temperature
    ) * 0.15

    adjusted += temp

    if abs(temp) >= 0.5:
        reasons.append(
            f"Temperature: {temp:+.1f} yds"
        )

    wind = 0.0

    if wind_direction == "Into":
        wind = wind_speed * 1.5

    elif wind_direction == "Helping":
        wind = -(wind_speed * 1.0)

    adjusted += wind

    if wind:
        reasons.append(
            f"Wind: {wind:+.1f} yds"
        )

    elev = elevation * 0.30
    adjusted += elev

    if abs(elev) >= 0.5:
        reasons.append(
            f"Elevation: {elev:+.1f} yds"
        )

    adjusted += lie_yards

    if lie_yards:
        reasons.append(
            f"Ball lie: {lie_yards:+.1f} yds"
        )

    firmness = 0

    if green_firmness == "Soft":
        firmness = 2

    elif green_firmness == "Firm":
        firmness = -2

    adjusted += firmness

    if firmness:
        reasons.append(
            f"Green firmness: {firmness:+} yds"
        )

    return max(
        1.0,
        adjusted
    ), reasons

# ============================================================
# CLUB CHOICE
# ============================================================

def choose_club(
    bag,
    shots,
    target_yards
):
    options = []

    for club in bag:
        carry, count = learned_carry_for_club(
            club["Club"],
            float(
                club.get(
                    "Stock Carry",
                    0
                )
            ),
            shots
        )

        options.append({
            "club": club,
            "carry": carry,
            "sample_count": count
        })

    options = sorted(
        options,
        key=lambda x: x["carry"]
    )

    wedge_options = [
        x
        for x in options
        if "Wedge" in x["club"]["Club"]
        or "°" in x["club"]["Club"]
    ]

    if target_yards < 100 and wedge_options:
        best_wedge = min(
            wedge_options,
            key=lambda x: abs(
                x["carry"] - max(
                    target_yards,
                    40
                )
            )
        )

        pct = max(
            45,
            min(
                95,
                round(
                    (
                        target_yards
                        / best_wedge["carry"]
                    )
                    * 100
                    / 5
                )
                * 5
            )
        )

        return (
            best_wedge,
            f"Partial wedge — about {pct}%."
        )

    enough = [
        x
        for x in options
        if x["carry"] >= target_yards - 2
    ]

    if enough:
        selected = min(
            enough,
            key=lambda x: x["carry"]
        )
    else:
        selected = max(
            options,
            key=lambda x: x["carry"]
        )

    diff = (
        selected["carry"]
        - target_yards
    )

    if abs(diff) <= 3:
        swing = "Stock swing"

    elif 3 < diff <= 10:
        swing = (
            "Controlled swing — you have a little extra club."
        )

    elif diff > 10:
        swing = (
            "Between clubs — favor control instead of forcing distance."
        )

    else:
        swing = (
            "Requires a very solid strike to cover the number."
        )

    return selected, swing

# ============================================================
# TARGET + HAZARDS
# ============================================================

def directional_score(
    handedness,
    player_miss,
    wind_direction,
    wind_speed,
    stance,
    severity
):
    score = 0.0
    miss = str(player_miss).lower()

    sev = {
        "Slight": 1.0,
        "Moderate": 2.0,
        "Severe": 3.0
    }.get(
        severity,
        1.0
    )

    if "fade" in miss:
        score += (
            1.5
            if handedness == "Right-handed"
            else -1.5
        )

    if "right" in miss:
        score += 1.5

    if "pull" in miss:
        score += (
            -1.5
            if handedness == "Right-handed"
            else 1.5
        )

    if "left" in miss:
        score -= 1.5

    if stance == "Ball Above Feet":
        score += (
            -sev
            if handedness == "Right-handed"
            else sev
        )

    elif stance == "Ball Below Feet":
        score += (
            sev
            if handedness == "Right-handed"
            else -sev
        )

    wind_weight = min(
        wind_speed / 8,
        2.5
    )

    if wind_direction == "Left to Right":
        score += wind_weight

    elif wind_direction == "Right to Left":
        score -= wind_weight

    return score

def hazard_adjust(
    score,
    trouble_type,
    trouble_location,
    safe_side
):
    catastrophic = trouble_type in (
        "Water",
        "OB",
        "Penalty Area"
    )

    moderate = trouble_type in (
        "Bunker",
        "Trees"
    )

    weight = (
        5.0
        if catastrophic
        else 3.0
        if moderate
        else 0.0
    )

    if trouble_type != "None":
        if trouble_location == "Left":
            score += weight

        elif trouble_location == "Right":
            score -= weight

    if safe_side == "Left":
        score -= 1.5

    elif safe_side == "Right":
        score += 1.5

    return score, catastrophic

def aim_from_score(score):
    if score >= 5:
        return "right side"

    if score >= 2:
        return "center-right"

    if score <= -5:
        return "left side"

    if score <= -2:
        return "center-left"

    return "center"

def miss_windows(
    trouble_type,
    trouble_location,
    safe_side,
    pin_position
):
    if trouble_type != "None":
        if trouble_location == "Left":
            return (
                "Center-right"
                if safe_side == "Right"
                else "Right side",
                f"Left into {trouble_type.lower()}"
            )

        if trouble_location == "Right":
            return (
                "Center-left"
                if safe_side == "Left"
                else "Left side",
                f"Right into {trouble_type.lower()}"
            )

        if trouble_location == "Center":
            return (
                "Safely short or fully beyond it",
                f"Center {trouble_type.lower()} landing zone"
            )

        if trouble_location == "Short":
            return (
                "Pin-high or slightly long",
                f"Short into {trouble_type.lower()}"
            )

        return (
            "Pin-high or slightly short",
            f"Long into {trouble_type.lower()}"
        )

    if pin_position == "Back":
        return (
            "Slightly short",
            "Long"
        )

    if pin_position == "Front":
        return (
            "Center-green",
            "Short-sided"
        )

    return (
        "Center-green",
        "No major dead-side hazard"
    )

def setup_advice(
    stance,
    handedness,
    severity
):
    if stance == "Level":
        return (
            "Normal setup. Use your normal posture, balance, and tempo."
        )

    if stance == "Uphill Lie":
        return (
            f"{severity} uphill lie: match your shoulders to the slope, "
            "stay balanced, expect higher launch, and avoid forcing extra distance."
        )

    if stance == "Downhill Lie":
        return (
            f"{severity} downhill lie: match your shoulders to the slope, "
            "move with the slope, expect lower launch, and prioritize clean contact."
        )

    if stance == "Ball Above Feet":
        direction = (
            "left"
            if handedness == "Right-handed"
            else "right"
        )

        return (
            f"{severity} ball-above-feet lie: stand slightly taller, "
            f"choke down if needed, stay balanced, and expect the ball to move {direction}."
        )

    direction = (
        "right"
        if handedness == "Right-handed"
        else "left"
    )

    return (
        f"{severity} ball-below-feet lie: add knee flex, avoid reaching, "
        f"stay balanced, and expect the ball to leak {direction}."
    )

# ============================================================
# HOLE MEMORY
# ============================================================

def hole_memory_summary(
    shots,
    course_name,
    hole_number
):
    if shots.empty or not course_name.strip():
        return None

    required = {
        "Course",
        "Hole"
    }

    if not required.issubset(
        set(shots.columns)
    ):
        return None

    hole = shots[
        shots["Course"]
        .astype(str)
        .str.lower()
        .str.strip()
        == course_name.lower().strip()
    ].copy()

    hole["Hole_num"] = pd.to_numeric(
        hole["Hole"],
        errors="coerce"
    )

    hole = hole[
        hole["Hole_num"]
        == hole_number
    ]

    if hole.empty:
        return None

    summary = {
        "count": len(hole),
        "last_club": None,
        "last_result": None,
        "common_result": None
    }

    last = hole.iloc[-1]

    if "Club Used" in hole.columns:
        summary["last_club"] = last.get(
            "Club Used"
        )

    if "Result" in hole.columns:
        summary["last_result"] = last.get(
            "Result"
        )

        vals = hole[
            "Result"
        ].dropna().astype(str)

        if not vals.empty:
            summary["common_result"] = (
                vals.mode().iloc[0]
            )

    return summary

# ============================================================
# CLOUD ACCOUNT GATE
# ============================================================

supabase = get_supabase_client()

if not st.session_state.get(
    "supabase_user_id"
):
    authentication_screen(
        supabase
    )

try:
    ensure_cloud_profile(
        supabase
    )
except Exception as exc:
    st.error(
        f"Signed in, but My Play could not initialize your cloud profile: {exc}"
    )
    st.stop()

# ============================================================
# LOAD
# ============================================================

profile = load_json(
    PROFILE_FILE,
    DEFAULT_PROFILE
)

bag = load_json(
    BAG_FILE,
    DEFAULT_BAG
)

game_profile = load_game_profile()

shots = load_shots()
all_player_evidence = combined_player_evidence(shots)

cached_course = load_cached_course()

catalog_ready, catalog_error = ensure_local_course_catalog()

if catalog_ready:
    # Clear Streamlit's cached loader only on fresh sessions where needed.
    local_catalog = load_local_course_catalog()
else:
    local_catalog = pd.DataFrame()

if "course_search_results" not in st.session_state:
    st.session_state["course_search_results"] = []

if "selected_course" not in st.session_state:
    st.session_state["selected_course"] = (
        cached_course
        if cached_course
        else None
    )

if "selected_tee" not in st.session_state:
    st.session_state["selected_tee"] = None

if "gps_latitude" not in st.session_state:
    st.session_state["gps_latitude"] = None

if "gps_longitude" not in st.session_state:
    st.session_state["gps_longitude"] = None

# ============================================================
# HEADER
# ============================================================

header_left, header_right = st.columns(
    [
        5,
        1
    ],
    vertical_alignment="center"
)

with header_left:
    st.markdown(
        """
        <div class="myplay-brandbar">
            <div class="myplay-brandmark" aria-label="My Play emblem">MP</div>
            <div class="myplay-brandcopy">
                <h1>My Play</h1>
                <p>Your game. Your data. Your caddie.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with header_right:
    with st.popover(
        "⚙️",
        use_container_width=True
    ):
        st.caption(
            st.session_state.get(
                "supabase_user_email",
                "Signed-in golfer"
            )
        )

        if st.button(
            "Sign Out",
            use_container_width=True,
            key="cloud_sign_out"
        ):
            sign_out_cloud(
                supabase
            )
            st.rerun()


# ============================================================
# FREE VOICE SHOT INPUT
# ============================================================

VOICE_MAX_SECONDS = 25.0
VOICE_DAILY_LIMIT = 50
VOICE_COOLDOWN_SECONDS = 5.0
VOICE_TIMEZONE = ZoneInfo("America/New_York")


def voice_input_ready():
    return (
        OPENAI_STT_AVAILABLE
        and OpenAI is not None
    )


def get_openai_voice_client():
    if not voice_input_ready():
        return None, (
            "The OpenAI Python package is not installed. "
            "Run: pip install openai"
        )

    try:
        api_key = str(
            st.secrets[
                "openai"
            ][
                "api_key"
            ]
        ).strip()
    except Exception:
        return None, (
            "OpenAI voice is not configured. Add [openai] api_key "
            "to .streamlit/secrets.toml."
        )

    if not api_key:
        return None, "The OpenAI API key is empty."

    try:
        return OpenAI(
            api_key=api_key
        ), None
    except Exception as exc:
        return None, str(exc)


def audio_duration_seconds(
    audio_value
):
    """
    Streamlit audio_input currently supplies WAV audio.
    Calculate duration locally before any OpenAI request is made.
    """
    if audio_value is None:
        return 0.0

    raw = audio_value.getvalue()

    try:
        import wave

        with wave.open(
            io.BytesIO(
                raw
            ),
            "rb"
        ) as wav_file:
            frames = wav_file.getnframes()
            rate = wav_file.getframerate()

            if rate <= 0:
                return 0.0

            return float(
                frames
            ) / float(
                rate
            )

    except Exception:
        # Conservative fallback based on the 16 kHz mono PCM recording
        # requested by the app. If duration cannot be verified, reject it.
        return -1.0


def voice_usage_date():
    return datetime.now(
        VOICE_TIMEZONE
    ).date().isoformat()


def get_voice_usage_count():
    """
    Daily command usage is stored in Supabase so refreshing/reopening
    the app does not reset the user's limit.
    """
    if not _cloud_ready():
        return None, (
            "Voice commands require a signed-in My Play account."
        )

    user_id = _cloud_user_id()

    if not user_id:
        return None, (
            "Voice commands require a signed-in My Play account."
        )

    try:
        response = (
            supabase
            .table(
                "voice_usage"
            )
            .select(
                "command_count"
            )
            .eq(
                "user_id",
                user_id
            )
            .eq(
                "usage_date",
                voice_usage_date()
            )
            .limit(
                1
            )
            .execute()
        )

        if not response.data:
            return 0, None

        return int(
            response.data[
                0
            ].get(
                "command_count",
                0
            )
            or 0
        ), None

    except Exception as exc:
        return None, (
            "Voice usage limits are not configured yet. "
            "My Play blocked the transcription instead of making an "
            "unlimited API request. "
            f"Details: {exc}"
        )


def increment_voice_usage_count():
    user_id = _cloud_user_id()
    today = voice_usage_date()

    current_count, error = get_voice_usage_count()

    if error:
        return False, error

    new_count = int(
        current_count
        or 0
    ) + 1

    try:
        existing = (
            supabase
            .table(
                "voice_usage"
            )
            .select(
                "id"
            )
            .eq(
                "user_id",
                user_id
            )
            .eq(
                "usage_date",
                today
            )
            .limit(
                1
            )
            .execute()
        )

        if existing.data:
            (
                supabase
                .table(
                    "voice_usage"
                )
                .update({
                    "command_count": new_count,
                    "updated_at": datetime.now(
                        VOICE_TIMEZONE
                    ).isoformat()
                })
                .eq(
                    "user_id",
                    user_id
                )
                .eq(
                    "usage_date",
                    today
                )
                .execute()
            )
        else:
            (
                supabase
                .table(
                    "voice_usage"
                )
                .insert({
                    "user_id": user_id,
                    "usage_date": today,
                    "command_count": new_count,
                    "updated_at": datetime.now(
                        VOICE_TIMEZONE
                    ).isoformat()
                })
                .execute()
            )

        return True, None

    except Exception as exc:
        return False, str(
            exc
        )


def voice_usage_status():
    count, error = get_voice_usage_count()

    if error:
        return {
            "ok": False,
            "count": None,
            "remaining": 0,
            "error": error,
        }

    remaining = max(
        0,
        VOICE_DAILY_LIMIT - int(
            count
            or 0
        )
    )

    return {
        "ok": True,
        "count": int(
            count
            or 0
        ),
        "remaining": remaining,
        "error": None,
    }


def transcribe_protected_openai_voice(
    audio_value
):
    """
    Cost-protected transcription:
    - authenticated golfer only
    - maximum 25 seconds before upload
    - 50 commands per golfer per day
    - 5-second cooldown
    - usage stored in Supabase
    """
    if not _cloud_ready():
        return None, (
            "Please sign in before using voice commands."
        )

    duration = audio_duration_seconds(
        audio_value
    )

    if duration < 0:
        return None, (
            "My Play could not verify the recording length, so it was "
            "not sent for transcription."
        )

    if duration <= 0:
        return None, "No recording was received."

    if duration > VOICE_MAX_SECONDS:
        return None, (
            f"Recording is {duration:.1f} seconds, which is over the "
            f"{int(VOICE_MAX_SECONDS)}-second voice limit. "
            "Nothing was sent to OpenAI and this did not use one of your daily commands. "
            "Try again with a shorter command."
        )

    usage = voice_usage_status()

    if not usage[
        "ok"
    ]:
        return None, usage[
            "error"
        ]

    if usage[
        "remaining"
    ] <= 0:
        return None, (
            f"Daily voice limit reached: {VOICE_DAILY_LIMIT} of "
            f"{VOICE_DAILY_LIMIT} commands used today. "
            "No audio was sent to OpenAI. Voice access resets tomorrow."
        )

    now_ts = datetime.now(
        VOICE_TIMEZONE
    ).timestamp()

    last_ts = float(
        st.session_state.get(
            "last_openai_voice_request_ts",
            0.0
        )
        or 0.0
    )

    seconds_since = now_ts - last_ts

    if (
        last_ts > 0
        and seconds_since < VOICE_COOLDOWN_SECONDS
    ):
        wait_for = max(
            1,
            int(
                math.ceil(
                    VOICE_COOLDOWN_SECONDS
                    - seconds_since
                )
            )
        )

        return None, (
            f"Voice cooldown active. Try again in {wait_for} second"
            + (
                "s."
                if wait_for != 1
                else "."
            )
            + " Nothing was sent to OpenAI."
        )

    client, client_error = get_openai_voice_client()

    if client_error:
        return None, client_error

    audio_bytes = io.BytesIO(
        audio_value.getvalue()
    )

    audio_bytes.name = "my_play_voice.wav"

    bag_names = ", ".join(
        str(
            club.get(
                "Club",
                ""
            )
        )
        for club in bag
        if club.get(
            "Club"
        )
    )

    transcription_prompt = (
        "My Play golf caddie voice command. "
        "Transcribe exactly and preserve golf terminology, numbers, tee colors, "
        "club names, yardages, wind direction, lies, hazards, and commands. "
        f"This golfer's current clubs include: {bag_names}. "
        "Common phrases include hole, par, white tees, blue tees, carry, "
        "driver, wood, hybrid, iron, wedge, fairway, rough, bunker, water, "
        "left, right, uphill, downhill, and wind."
    )

    try:
        # Mark the cooldown at the moment an API request is actually attempted.
        st.session_state[
            "last_openai_voice_request_ts"
        ] = now_ts

        transcript = client.audio.transcriptions.create(
            model="gpt-transcribe",
            file=audio_bytes,
            prompt=transcription_prompt
        )

        text = str(
            getattr(
                transcript,
                "text",
                ""
            )
            or ""
        ).strip()

        # A successful API transcription consumes one daily command.
        incremented, usage_error = increment_voice_usage_count()

        if not incremented:
            # Fail closed for subsequent calls. The current call already occurred,
            # so show the transcript but tell the user usage tracking failed.
            if text:
                return text, (
                    "The command was transcribed, but My Play could not record "
                    f"the usage count: {usage_error}"
                )

            return None, usage_error

        if not text:
            return None, "No speech was detected."

        return text, None

    except Exception as exc:
        return None, str(
            exc
        )


# ============================================================
# FREE BROWSER TALK-BACK
# ============================================================

def speak_in_browser(
    text,
    key="my_play_talk_back"
):
    """
    Uses the browser's built-in Web Speech Synthesis API.
    No OpenAI or paid TTS API call is made.
    """
    spoken_text = str(
        text or ""
    ).strip()

    if not spoken_text:
        return

    safe_text = json.dumps(
        spoken_text
    )

    html = f"""
    <script>
    (function() {{
        const text = {safe_text};

        function speakMyPlay() {{
            if (!('speechSynthesis' in window)) {{
                return;
            }}

            window.speechSynthesis.cancel();

            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = 'en-US';
            utterance.rate = 1.0;
            utterance.pitch = 1.0;
            utterance.volume = 1.0;

            const voices = window.speechSynthesis.getVoices();
            const preferred = voices.find(v =>
                v.lang && v.lang.toLowerCase().startsWith('en-us')
            ) || voices.find(v =>
                v.lang && v.lang.toLowerCase().startsWith('en')
            );

            if (preferred) {{
                utterance.voice = preferred;
            }}

            window.speechSynthesis.speak(utterance);
        }}

        if (window.speechSynthesis.getVoices().length === 0) {{
            window.speechSynthesis.onvoiceschanged = speakMyPlay;
        }} else {{
            speakMyPlay();
        }}
    }})();
    </script>
    """

    components.html(
        html,
        height=0,
        width=0,
        scrolling=False
    )



def normalize_tee_name(value):
    return str(
        value or ""
    ).strip().lower()


def current_course_record():
    """
    Reuse the course selection already present in My Play.
    This intentionally avoids inventing a course from voice alone.
    """
    selected = st.session_state.get(
        "selected_course"
    )

    if selected:
        return selected

    try:
        active_round = load_active_round()
    except Exception:
        active_round = None

    if active_round:
        return {
            "course_name": active_round.get(
                "course_name",
                ""
            ),
            "holes": active_round.get(
                "holes",
                []
            ),
            "tees": active_round.get(
                "tees",
                []
            ),
        }

    return None


def extract_course_holes(course_record):
    if not course_record:
        return []

    # OpenGolf / selected course details may be nested differently depending
    # on whether this came from live API, local dataset, or active round.
    candidates = []

    if isinstance(
        course_record,
        dict
    ):
        candidates.extend([
            course_record.get(
                "holes"
            ),
            course_record.get(
                "hole_data"
            ),
            course_record.get(
                "course_holes"
            ),
        ])

        details = course_record.get(
            "details"
        )

        if isinstance(
            details,
            dict
        ):
            candidates.extend([
                details.get(
                    "holes"
                ),
                details.get(
                    "hole_data"
                ),
            ])

        search_result = course_record.get(
            "search_result"
        )

        if isinstance(
            search_result,
            dict
        ):
            candidates.extend([
                search_result.get(
                    "holes"
                ),
                search_result.get(
                    "hole_data"
                ),
            ])

    for candidate in candidates:
        if isinstance(
            candidate,
            list
        ) and candidate:
            return candidate

    return []


def _hole_number_from_record(
    hole
):
    if not isinstance(
        hole,
        dict
    ):
        return None

    for key in [
        "hole",
        "hole_number",
        "number",
        "holeNumber",
        "hole_no",
    ]:
        value = hole.get(
            key
        )

        try:
            number = int(
                value
            )

            if 1 <= number <= 18:
                return number
        except Exception:
            pass

    return None


def _numeric_yardage(
    value
):
    try:
        number = float(
            value
        )

        if 40 <= number <= 800:
            return round(
                number
            )
    except Exception:
        pass

    return None


def hole_tee_yardage(
    course_record,
    hole_number,
    tee_name
):
    """
    Best-effort lookup across the course structures already used by My Play.
    Returns None instead of inventing yardage.
    """
    holes = extract_course_holes(
        course_record
    )

    target = None

    for hole in holes:
        if _hole_number_from_record(
            hole
        ) == int(
            hole_number
        ):
            target = hole
            break

    if not isinstance(
        target,
        dict
    ):
        return None, None

    tee_norm = normalize_tee_name(
        tee_name
    )

    # Common shapes: {"White": 164}, {"white_yards": 164}, nested tees, etc.
    direct_keys = [
        tee_name,
        tee_norm,
        f"{tee_norm}_yards",
        f"{tee_norm}Yards",
        f"{tee_norm}_yardage",
        f"{tee_norm}Yardage",
    ]

    for key in direct_keys:
        if not key:
            continue

        if key in target:
            yardage = _numeric_yardage(
                target.get(
                    key
                )
            )

            if yardage is not None:
                return yardage, target

    for nested_key in [
        "tees",
        "tee_boxes",
        "yardages",
        "tee_yardages",
    ]:
        nested = target.get(
            nested_key
        )

        if isinstance(
            nested,
            dict
        ):
            for key, value in nested.items():
                if normalize_tee_name(
                    key
                ) == tee_norm:
                    yardage = _numeric_yardage(
                        value
                    )

                    if yardage is not None:
                        return yardage, target

                if isinstance(
                    value,
                    dict
                ):
                    name = (
                        value.get(
                            "name"
                        )
                        or value.get(
                            "tee"
                        )
                        or value.get(
                            "tee_name"
                        )
                    )

                    if normalize_tee_name(
                        name
                    ) == tee_norm:
                        for yard_key in [
                            "yards",
                            "yardage",
                            "distance",
                            "length",
                        ]:
                            yardage = _numeric_yardage(
                                value.get(
                                    yard_key
                                )
                            )

                            if yardage is not None:
                                return yardage, target

        elif isinstance(
            nested,
            list
        ):
            for item in nested:
                if not isinstance(
                    item,
                    dict
                ):
                    continue

                name = (
                    item.get(
                        "name"
                    )
                    or item.get(
                        "tee"
                    )
                    or item.get(
                        "tee_name"
                    )
                    or item.get(
                        "color"
                    )
                )

                if normalize_tee_name(
                    name
                ) == tee_norm:
                    for yard_key in [
                        "yards",
                        "yardage",
                        "distance",
                        "length",
                    ]:
                        yardage = _numeric_yardage(
                            item.get(
                                yard_key
                            )
                        )

                        if yardage is not None:
                            return yardage, target

    return None, target


def apply_voice_hole_context(
    parsed
):
    """
    Voice establishes course/hole/tee context, but the actual recommendation
    still runs through the normal My Play caddie and therefore keeps using
    the unified player model (range + simulator + on-course evidence).
    """
    hole_number = parsed.get(
        "hole_number"
    )
    tee_name = parsed.get(
        "tee_name"
    )
    spoken_par = parsed.get(
        "par"
    )

    result = {
        "course_found": False,
        "hole_found": False,
        "yardage_found": False,
        "yardage": None,
        "hole_number": hole_number,
        "tee_name": tee_name,
        "par": spoken_par,
        "message": "",
    }

    if hole_number is None:
        result[
            "message"
        ] = "No hole number was detected."
        return result

    course_record = current_course_record()

    if not course_record:
        result[
            "message"
        ] = (
            "Select or start a course first. Once a course is active, "
            "voice can jump directly to a hole and tee."
        )
        return result

    result[
        "course_found"
    ] = True

    if tee_name:
        st.session_state[
            "voice_selected_tee"
        ] = tee_name

        # Common round/tee session keys used by the app.
        for key in [
            "selected_tee",
            "round_tee",
            "tee_name",
        ]:
            if key in st.session_state:
                st.session_state[
                    key
                ] = tee_name

    # Common hole navigation session keys.
    for key in [
        "current_hole",
        "hole_number",
        "live_hole_number",
        "selected_hole",
    ]:
        if key in st.session_state:
            st.session_state[
                key
            ] = hole_number

    st.session_state[
        "voice_hole_number"
    ] = hole_number

    yardage, hole_record = hole_tee_yardage(
        course_record,
        hole_number,
        tee_name,
    )

    if hole_record is not None:
        result[
            "hole_found"
        ] = True

        record_par = None

        for par_key in [
            "par",
            "Par",
            "hole_par",
        ]:
            try:
                maybe_par = int(
                    hole_record.get(
                        par_key
                    )
                )

                if maybe_par in [
                    3,
                    4,
                    5,
                ]:
                    record_par = maybe_par
                    break
            except Exception:
                pass

        if record_par is not None:
            result[
                "par"
            ] = record_par

            st.session_state[
                "voice_hole_par"
            ] = record_par

    elif spoken_par is not None:
        st.session_state[
            "voice_hole_par"
        ] = spoken_par

    if yardage is not None:
        result[
            "yardage_found"
        ] = True
        result[
            "yardage"
        ] = yardage

        # Prefill normal Caddie distance. This does not choose a club here;
        # the regular caddie engine chooses using the unified player evidence.
        st.session_state[
            "caddie_distance"
        ] = int(
            yardage
        )

        result[
            "message"
        ] = (
            f"Hole {hole_number}, {tee_name or 'selected'} tees: "
            f"{yardage} yards loaded into the caddie."
        )
    else:
        result[
            "message"
        ] = (
            f"Hole {hole_number} context was set, but My Play could not find "
            f"a verified {tee_name or 'selected tee'} yardage for that hole."
        )

    return result



def normalize_club_spoken_name(text):
    value = str(
        text or ""
    ).strip().lower()

    # Normalize punctuation / separators.
    value = value.replace(
        "-",
        " "
    )

    value = re.sub(
        r"\s+",
        " ",
        value
    ).strip()

    word_nums = {
        "two": "2",
        "three": "3",
        "four": "4",
        "five": "5",
        "six": "6",
        "seven": "7",
        "eight": "8",
        "nine": "9",
        "ten": "10",
    }

    for word, number in word_nums.items():
        value = re.sub(
            rf"\b{word}\b",
            number,
            value
        )

    # Remove common ownership / filler words.
    value = re.sub(
        r"\b(my|the|a|an|club|golf club)\b",
        " ",
        value
    )

    value = re.sub(
        r"\s+",
        " ",
        value
    ).strip()

    if "driver" in value:
        return "Driver"

    if "putter" in value:
        return "Putter"

    if "pitching wedge" in value or value == "pw":
        return "Pitching Wedge"

    wood_match = re.search(
        r"\b([2-9])\s*wood\b",
        value
    )
    if wood_match:
        return f"{wood_match.group(1)} Wood"

    hybrid_match = re.search(
        r"\b([2-6])\s*hybrid\b",
        value
    )
    if hybrid_match:
        return f"{hybrid_match.group(1)} Hybrid"

    iron_match = re.search(
        r"\b([2-9])\s*iron\b",
        value
    )
    if iron_match:
        return f"{iron_match.group(1)} Iron"

    wedge_match = re.search(
        r"\b(4[6-9]|5[0-9]|60)\s*(?:degree|degrees|°)?(?:\s*wedge)?\b",
        value
    )
    if wedge_match:
        return f"{wedge_match.group(1)}° Wedge"

    return str(
        text or ""
    ).strip().title()



def detect_spoken_club_from_bag(text):
    spoken = str(
        text or ""
    ).strip().lower()

    spoken = spoken.replace(
        "-",
        " "
    )

    spoken = re.sub(
        r"\s+",
        " ",
        spoken
    )

    word_nums = {
        "two": "2",
        "three": "3",
        "four": "4",
        "five": "5",
        "six": "6",
        "seven": "7",
        "eight": "8",
        "nine": "9",
        "ten": "10",
    }

    for word, number in word_nums.items():
        spoken = re.sub(
            rf"\b{word}\b",
            number,
            spoken
        )

    spoken_flat = re.sub(
        r"[^a-z0-9]+",
        " ",
        spoken
    ).strip()

    candidates = []

    for club in bag:
        club_name = str(
            club.get(
                "Club",
                ""
            )
        ).strip()

        if not club_name:
            continue

        normalized = club_name.lower().replace(
            "°",
            " degree "
        )

        normalized = re.sub(
            r"[^a-z0-9]+",
            " ",
            normalized
        ).strip()

        aliases = {
            normalized,
            normalized.replace(
                " degree wedge",
                " wedge"
            ),
            normalized.replace(
                " degree wedge",
                " degree"
            ),
        }

        for alias in aliases:
            if alias and alias in spoken_flat:
                candidates.append(
                    (
                        len(alias),
                        club_name
                    )
                )

    if candidates:
        candidates.sort(
            reverse=True
        )
        return candidates[0][1]

    # Generic fallback.
    generic_patterns = [
        (r"\bdriver\b", "Driver"),
        (r"\bputter\b", "Putter"),
        (r"\bpitching wedge\b", "Pitching Wedge"),
        (r"\b([2-9])\s*wood\b", "{} Wood"),
        (r"\b([2-6])\s*hybrid\b", "{} Hybrid"),
        (r"\b([2-9])\s*iron\b", "{} Iron"),
        (r"\b(4[6-9]|5[0-9]|60)\s*(?:degree|degrees)?\s*(?:wedge)?\b", "{}° Wedge"),
    ]

    for pattern, template in generic_patterns:
        match = re.search(
            pattern,
            spoken_flat
        )

        if match:
            if "{}" in template:
                return template.format(
                    match.group(
                        1
                    )
                )

            return template

    return None


def find_bag_club_index(club_name):
    target = normalize_club_spoken_name(club_name).lower()

    for idx, club in enumerate(bag):
        if str(club.get("Club", "")).strip().lower() == target:
            return idx

    return None


def parse_voice_bag_command(text):
    raw = str(
        text or ""
    ).strip()

    lower = raw.lower().replace(
        "-",
        " "
    )

    lower = re.sub(
        r"\s+",
        " ",
        lower
    ).strip()

    parsed = {
        "raw": raw,
        "action": None,
        "club": None,
        "brand_model": None,
        "loft": None,
        "stock_carry": None,
        "typical_miss": None,
    }

    # Action
    if any(
        phrase in lower
        for phrase in [
            "delete",
            "remove",
            "take out",
        ]
    ):
        parsed[
            "action"
        ] = "delete"

    elif any(
        phrase in lower
        for phrase in [
            "change",
            "update",
            "edit",
            "set",
            "make my",
        ]
    ):
        parsed[
            "action"
        ] = "edit"

    elif any(
        phrase in lower
        for phrase in [
            "add",
            "put in",
            "new club",
        ]
    ):
        parsed[
            "action"
        ] = "add"

    # Convert spoken numbers before club detection.
    spoken = lower

    word_nums = {
        "two": "2",
        "three": "3",
        "four": "4",
        "five": "5",
        "six": "6",
        "seven": "7",
        "eight": "8",
        "nine": "9",
        "ten": "10",
    }

    for word, number in word_nums.items():
        spoken = re.sub(
            rf"\b{word}\b",
            number,
            spoken
        )

    # First match against this golfer's actual bag names.
    detected_club = detect_spoken_club_from_bag(
        spoken
    )

    if detected_club:
        parsed[
            "club"
        ] = detected_club

    # Carry / stock distance.
    carry_patterns = [
        r"\b(?:carry|carries|stock carry|distance)\s*(?:is|to|at|of)?\s*(\d{2,3})\b",
        r"\b(?:make|set|change|update)\s+(?:my\s+)?(?:driver|putter|(?:[2-9]\s*(?:wood|hybrid|iron))|(?:4[6-9]|5[0-9]|60)\s*(?:degree|degrees|°)?\s*wedge)\s+(?:carry\s+)?(?:to|at)?\s*(\d{2,3})\b",
        r"\b(\d{2,3})\s*(?:yard|yards|yd|yds)\b",
    ]

    for pattern in carry_patterns:
        match = re.search(
            pattern,
            spoken
        )

        if match:
            value = int(
                match.group(
                    1
                )
            )

            if 20 <= value <= 400:
                parsed[
                    "stock_carry"
                ] = value
                break

    # Loft
    loft_match = re.search(
        r"\b(\d{1,2}(?:\.\d+)?)\s*(?:degree|degrees|°)\b",
        spoken
    )

    if loft_match:
        loft_number = loft_match.group(
            1
        )

        # Don't confuse a wedge's name (e.g. 60 degree wedge)
        # with a separate loft value unless the club isn't already that wedge.
        club_name = parsed.get(
            "club"
        )

        if not (
            club_name
            and club_name.startswith(
                f"{loft_number}°"
            )
        ):
            parsed[
                "loft"
            ] = f"{loft_number}°"

    # Miss
    miss_map = [
        (
            "slight pull",
            "slight pull"
        ),
        (
            "slight fade",
            "slight fade"
        ),
        (
            "fade right",
            "fade right"
        ),
        (
            "pull",
            "pull"
        ),
        (
            "push",
            "push"
        ),
        (
            "hook",
            "hook"
        ),
        (
            "slice",
            "slice"
        ),
        (
            "straight",
            "straight"
        ),
        (
            "short",
            "short"
        ),
        (
            "long",
            "long"
        ),
    ]

    for phrase, value in miss_map:
        if phrase in spoken:
            parsed[
                "typical_miss"
            ] = value
            break

    # Brand / model
    known_brands = [
        "callaway",
        "taylormade",
        "titleist",
        "ping",
        "mizuno",
        "cobra",
        "srixon",
        "cleveland",
        "wilson",
        "pxg",
    ]

    for brand in known_brands:
        if brand in spoken:
            brand_match = re.search(
                rf"\b({re.escape(brand)}[^,.;]*?)(?=\s+(?:carry|carries|distance|stock carry|slight pull|pull|slight fade|fade right|push|hook|slice|straight|short|long)\b|$)",
                spoken
            )

            if brand_match:
                parsed[
                    "brand_model"
                ] = brand_match.group(
                    1
                ).strip().title()
            else:
                parsed[
                    "brand_model"
                ] = brand.title()

            break

    return parsed


def build_voice_bag_preview(parsed):
    action = parsed.get("action")
    club_name = parsed.get("club")

    preview = {
        "action": action,
        "club": club_name,
        "valid": False,
        "message": "",
        "current": None,
        "proposed": None,
    }

    if not action:
        preview["message"] = "I could not tell whether you want to add, edit, or delete a club."
        return preview

    if not club_name:
        preview["message"] = "I could not identify the club."
        return preview

    existing_index = find_bag_club_index(club_name)

    if action == "delete":
        if existing_index is None:
            preview["message"] = f"{club_name} is not currently in the bag."
            return preview

        preview["current"] = dict(bag[existing_index])
        preview["valid"] = True
        preview["message"] = f"Remove {club_name} from the bag."
        return preview

    if action == "edit":
        if existing_index is None:
            preview["message"] = f"{club_name} is not currently in the bag."
            return preview

        current = dict(bag[existing_index])
        proposed = dict(current)

        if parsed.get("brand_model"):
            proposed["Brand / Model"] = parsed["brand_model"]

        if parsed.get("loft"):
            proposed["Loft"] = parsed["loft"]

        if parsed.get("stock_carry") is not None:
            proposed["Stock Carry"] = parsed["stock_carry"]

        if parsed.get("typical_miss"):
            proposed["Typical Miss"] = parsed["typical_miss"]

        if proposed == current:
            preview["message"] = "I identified the club, but not what to change."
            return preview

        preview["current"] = current
        preview["proposed"] = proposed
        preview["valid"] = True
        preview["message"] = f"Update {club_name}."
        return preview

    if action == "add":
        if existing_index is not None:
            preview["message"] = f"{club_name} is already in the bag. Say change or update instead."
            return preview

        preview["proposed"] = {
            "Club": club_name,
            "Brand / Model": parsed.get("brand_model") or "",
            "Loft": parsed.get("loft") or "",
            "Stock Carry": parsed.get("stock_carry") or 0,
            "Typical Miss": parsed.get("typical_miss") or "unknown",
        }
        preview["valid"] = True
        preview["message"] = f"Add {club_name} to the bag."
        return preview

    return preview


def commit_voice_bag_change(preview):
    if not preview.get("valid"):
        return False, preview.get("message", "Invalid bag change.")

    action = preview.get("action")
    club_name = preview.get("club")
    updated_bag = [dict(club) for club in bag]

    if action == "delete":
        idx = find_bag_club_index(club_name)
        if idx is None:
            return False, f"{club_name} was not found."
        updated_bag.pop(idx)

    elif action == "edit":
        idx = find_bag_club_index(club_name)
        if idx is None:
            return False, f"{club_name} was not found."
        updated_bag[idx] = dict(preview["proposed"])

    elif action == "add":
        updated_bag.append(dict(preview["proposed"]))

    else:
        return False, "Unsupported bag action."

    save_json(
        BAG_FILE,
        updated_bag
    )

    return True, f"{club_name} updated successfully."




def parse_voice_shot_text(text):
    raw = str(text or "").strip()
    lower = raw.lower()

    parsed = {
        "raw": raw,
        "distance": None,
        "temperature": None,
        "wind_direction": None,
        "wind_speed": None,
        "surface": None,
        "lie_type": None,
        "stance": None,
        "slope_severity": None,
        "trouble_type": None,
        "trouble_location": None,
        "safe_side": None,
        "elevation": None,
        "hole_number": None,
        "par": None,
        "tee_name": None,
    }

    # Hole / par / tee
    hole_match = re.search(
        r"\bhole\s*(?:number\s*)?(\d{1,2})\b",
        lower,
    )
    if hole_match:
        value = int(hole_match.group(1))
        if 1 <= value <= 18:
            parsed["hole_number"] = value

    par_match = re.search(
        r"\bpar\s*([345])\b",
        lower,
    )
    if par_match:
        parsed["par"] = int(par_match.group(1))

    tee_match = re.search(
        r"\b(black|blue|white|gold|yellow|green|red|silver|orange|purple|championship|ladies|senior)\s+tees?\b",
        lower,
    )

    if tee_match:
        tee_word = tee_match.group(
            1
        ).lower()

        tee_aliases = {
            "championship": "Blue",
            "ladies": "Red",
            "senior": "Gold",
        }

        parsed[
            "tee_name"
        ] = tee_aliases.get(
            tee_word,
            tee_word.title()
        )

    elif re.search(
        r"\b(?:the\s+)?blues\b",
        lower
    ):
        parsed[
            "tee_name"
        ] = "Blue"

    elif re.search(
        r"\b(?:the\s+)?whites\b",
        lower
    ):
        parsed[
            "tee_name"
        ] = "White"

    elif re.search(
        r"\b(?:the\s+)?reds\b",
        lower
    ):
        parsed[
            "tee_name"
        ] = "Red"

    elif re.search(
        r"\b(?:the\s+)?golds\b",
        lower
    ):
        parsed[
            "tee_name"
        ] = "Gold"

    # Distance
    for pattern in [
        r"\b(\d{2,3})\s*(?:yards?|yds?)\b",
        r"\b(?:got|have|playing|from|to the pin|pin is|distance is)\s+(\d{2,3})\b",
        r"\b(\d{2,3})\s+to\s+(?:the\s+)?(?:pin|green)\b",
    ]:
        match = re.search(pattern, lower)
        if match:
            value = int(match.group(1))
            if 20 <= value <= 400:
                parsed["distance"] = value
                break

    if parsed["distance"] is None:
        for token in re.findall(r"\b\d{2,3}\b", lower):
            value = int(token)
            if 40 <= value <= 350:
                parsed["distance"] = value
                break

    # Temperature
    temp_match = re.search(
        r"\b(\d{2,3})\s*(?:degrees?|°)\b",
        lower,
    )
    if temp_match:
        value = int(temp_match.group(1))
        if 20 <= value <= 120:
            parsed["temperature"] = value

    # Wind direction
    if any(p in lower for p in [
        "into the wind", "wind into me", "wind in my face",
        "headwind", "wind against me"
    ]):
        parsed["wind_direction"] = "Into"
    elif any(p in lower for p in [
        "downwind", "wind behind me", "wind at my back",
        "tailwind", "helping wind"
    ]):
        parsed["wind_direction"] = "Helping"
    elif any(p in lower for p in [
        "left to right wind", "wind left to right"
    ]):
        parsed["wind_direction"] = "Left to Right"
    elif any(p in lower for p in [
        "right to left wind", "wind right to left"
    ]):
        parsed["wind_direction"] = "Right to Left"

    # Wind speed
    wind_speed_match = re.search(
        r"\b(\d{1,2})\s*(?:mph|miles per hour)\b",
        lower,
    )
    if wind_speed_match:
        value = int(wind_speed_match.group(1))
        if 0 <= value <= 50:
            parsed["wind_speed"] = value
    elif "strong wind" in lower or "really windy" in lower:
        parsed["wind_speed"] = 18
    elif "moderate wind" in lower or "steady wind" in lower:
        parsed["wind_speed"] = 10
    elif "light wind" in lower or "slight wind" in lower or "breeze" in lower:
        parsed["wind_speed"] = 5

    # Surface
    surface_map = [
        (["fairway bunker"], "Fairway Bunker"),
        (["greenside bunker", "green side bunker"], "Greenside Bunker"),
        (["heavy rough", "deep rough", "thick rough"], "Heavy Rough"),
        (["light rough", "first cut"], "Light Rough"),
        (["hardpan", "hard pan"], "Hardpan"),
        (["wet turf", "soft turf", "wet lie", "soft lie"], "Wet / Soft Turf"),
        (["recovery lie", "trouble lie"], "Recovery"),
        (["fairway"], "Fairway"),
    ]
    for phrases, value in surface_map:
        if any(p in lower for p in phrases):
            parsed["surface"] = value
            break

    # Ball sitting
    if any(p in lower for p in ["sitting up", "ball sitting up"]):
        parsed["lie_type"] = "Sitting Up"
    elif "flyer" in lower:
        parsed["lie_type"] = "Flyer"
    elif any(p in lower for p in ["buried", "plugged", "sitting down"]):
        parsed["lie_type"] = "Buried"

    # Slope / stance
    if "ball above my feet" in lower or "ball above feet" in lower:
        parsed["stance"] = "Ball Above Feet"
    elif "ball below my feet" in lower or "ball below feet" in lower:
        parsed["stance"] = "Ball Below Feet"
    elif "uphill lie" in lower:
        parsed["stance"] = "Uphill Lie"
    elif "downhill lie" in lower:
        parsed["stance"] = "Downhill Lie"
    elif "level lie" in lower:
        parsed["stance"] = "Level"

    if "severe" in lower or "extreme" in lower:
        parsed["slope_severity"] = "Severe"
    elif "moderate" in lower or "medium" in lower:
        parsed["slope_severity"] = "Moderate"
    elif "slight" in lower or "little" in lower:
        parsed["slope_severity"] = "Slight"

    # Trouble type
    if "out of bounds" in lower or re.search(r"\bob\b", lower):
        parsed["trouble_type"] = "OB"
    elif any(p in lower for p in ["water", "pond", "lake", "creek"]):
        parsed["trouble_type"] = "Water"
    elif any(p in lower for p in ["penalty area", "red stakes", "yellow stakes"]):
        parsed["trouble_type"] = "Penalty Area"
    elif any(p in lower for p in ["trees", "tree line"]):
        parsed["trouble_type"] = "Trees"
    elif "bunker" in lower or "sand trap" in lower:
        parsed["trouble_type"] = "Bunker"

    # Trouble location
    if "left" in lower:
        parsed["trouble_location"] = "Left"
    elif "right" in lower:
        parsed["trouble_location"] = "Right"
    elif "short" in lower:
        parsed["trouble_location"] = "Short"
    elif "long" in lower:
        parsed["trouble_location"] = "Long"

    # Safe side
    if any(p in lower for p in ["safe left", "favor left", "favour left", "miss left"]):
        parsed["safe_side"] = "Left"
    elif any(p in lower for p in ["safe right", "favor right", "favour right", "miss right"]):
        parsed["safe_side"] = "Right"
    elif any(p in lower for p in ["safe center", "safe middle"]):
        parsed["safe_side"] = "Center"

    # Elevation
    elevation_match = re.search(
        r"\b(\d{1,2})\s*(?:feet|foot|ft)\s*(uphill|up|downhill|down)\b",
        lower,
    )
    if elevation_match:
        feet = int(elevation_match.group(1))
        direction = elevation_match.group(2)
        parsed["elevation"] = feet if direction in ("uphill", "up") else -feet

    return parsed


def apply_voice_shot_to_caddie(parsed):
    mapping = {
        "distance": "caddie_distance",
        "temperature": "caddie_temperature",
        "wind_direction": "caddie_wind_direction",
        "wind_speed": "caddie_wind_speed",
        "surface": "caddie_surface",
        "lie_type": "caddie_lie_type",
        "stance": "caddie_stance",
        "slope_severity": "caddie_slope_severity",
        "trouble_type": "caddie_trouble_type",
        "trouble_location": "caddie_trouble_location",
        "safe_side": "caddie_safe_side",
        "elevation": "caddie_elevation",
    }

    applied = []

    for source_key, state_key in mapping.items():
        value = parsed.get(source_key)

        if value is not None:
            st.session_state[state_key] = value
            applied.append(source_key)

    return applied



def extract_voice_course_name(text):
    raw = str(
        text or ""
    ).strip()

    patterns = [
        r"\b(?:start|starting|begin|beginning|playing|play)\s+(?:a\s+)?round\s+(?:at|on|from)\s+([^,.!?]+)",
        r"\b(?:playing|play)\s+(?:at|on)\s+([^,.!?]+)",
        r"\b(?:at|on)\s+([^,.!?]+?)\s+(?:golf\s+course|country\s+club|golf\s+club)\b",
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            raw,
            flags=re.IGNORECASE
        )

        if not match:
            continue

        course = match.group(
            1
        ).strip(
            " ,.-"
        )

        # Remove trailing tee language if speech recognition included it.
        course = re.sub(
            r"\s+(?:from|off|on)\s+(?:the\s+)?(?:black|blue|white|gold|yellow|green|red|silver|orange|purple|championship|ladies|senior)\s+tees?.*$",
            "",
            course,
            flags=re.IGNORECASE
        ).strip()

        # Remove common filler.
        course = re.sub(
            r"\s+(?:today|right now|this morning|this afternoon|this evening)$",
            "",
            course,
            flags=re.IGNORECASE
        ).strip()

        if course:
            return course

    return None



def load_course_result_for_voice(
    selected_result
):
    source = result_source(
        selected_result
    )

    if source == "My Play Course Library":
        return selected_result

    if source == "My Play Manual Course":
        return selected_result

    if source == "My Play Local Catalog":
        cid = str(
            selected_result.get(
                "id",
                ""
            )
        )

        local_scorecard = local_scorecard_from_row(
            selected_result
        )

        detail = selected_result
        holes_payload = {
            "holes": local_scorecard
        }
        tees_payload = {
            "tees": []
        }
        climate_payload = {}
        osm_features = {
            "holes": [],
            "greens": [],
            "bunkers": [],
            "tees": []
        }

        if cid:
            try:
                detail = fetch_course_detail(
                    cid
                )
            except Exception:
                pass

            try:
                live_holes = fetch_course_holes(
                    cid
                )

                if payload_list(
                    live_holes
                ):
                    holes_payload = live_holes
            except Exception:
                pass

            try:
                live_tees = fetch_course_tees(
                    cid
                )

                if payload_list(
                    live_tees
                ):
                    tees_payload = live_tees
            except Exception:
                pass

            try:
                climate_payload = fetch_course_climate(
                    cid
                )
            except Exception:
                pass

        lat = selected_result.get(
            "latitude"
        )
        lon = selected_result.get(
            "longitude"
        )

        if lat and lon:
            try:
                feature_payload = fetch_osm_golf_features(
                    float(
                        lat
                    ),
                    float(
                        lon
                    )
                )

                osm_features = normalize_osm_features(
                    feature_payload
                )
            except Exception:
                pass

        return {
            "id": cid,
            "source": source,
            "search_result": selected_result,
            "detail": detail,
            "holes": holes_payload,
            "tees": tees_payload,
            "climate": climate_payload,
            "osm_features": osm_features,
            "loaded_at": datetime.now().isoformat()
        }

    if source in (
        "OpenGolfAPI",
        "OpenGolfAPI Live"
    ):
        cid = course_id(
            selected_result
        )

        if not cid:
            raise ValueError(
                "The matched course did not include a usable course ID."
            )

        detail = fetch_course_detail(
            cid
        )

        holes_payload = fetch_course_holes(
            cid
        )

        tees_payload = fetch_course_tees(
            cid
        )

        try:
            climate_payload = fetch_course_climate(
                cid
            )
        except Exception:
            climate_payload = {}

        return {
            "id": cid,
            "source": source,
            "search_result": selected_result,
            "detail": detail,
            "holes": holes_payload,
            "tees": tees_payload,
            "climate": climate_payload,
            "osm_features": {},
            "loaded_at": datetime.now().isoformat()
        }

    # OSM fallback.
    lat = selected_result.get(
        "latitude"
    )
    lon = selected_result.get(
        "longitude"
    )

    osm_features = {
        "holes": [],
        "greens": [],
        "bunkers": [],
        "tees": []
    }

    if lat and lon:
        try:
            feature_payload = fetch_osm_golf_features(
                float(
                    lat
                ),
                float(
                    lon
                )
            )

            osm_features = normalize_osm_features(
                feature_payload
            )
        except Exception:
            pass

    return {
        "id": selected_result.get(
            "id",
            ""
        ),
        "source": source,
        "search_result": selected_result,
        "detail": selected_result,
        "holes": {
            "holes": osm_features.get(
                "holes",
                []
            )
        },
        "tees": {
            "tees": osm_features.get(
                "tees",
                []
            )
        },
        "climate": {},
        "osm_features": osm_features,
        "loaded_at": datetime.now().isoformat()
    }


def best_voice_course_match(
    spoken_course_name
):
    query = str(
        spoken_course_name or ""
    ).strip()

    if not query:
        return None, [], {
            "strong": False,
            "reason": "No course name was detected.",
            "candidates": [],
        }

    state = str(
        profile.get(
            "default_state",
            ""
        )
        or ""
    ).strip()

    results, errors = search_all_free_sources(
        query,
        state
    )

    if not results and state:
        results, second_errors = search_all_free_sources(
            query,
            ""
        )
        errors.extend(
            second_errors
        )

    if not results:
        return None, errors, {
            "strong": False,
            "reason": f'No course matched "{query}".',
            "candidates": [],
        }

    def cleaned_name(value):
        value = normalize_name(
            value
        )
        value = re.sub(
            r"\b(golf course|golf club|country club|club|course)\b",
            " ",
            value
        )
        value = re.sub(
            r"\s+",
            " ",
            value
        ).strip()
        return value

    query_norm = cleaned_name(
        query
    )

    query_terms = [
        term
        for term in query_norm.split()
        if len(
            term
        ) >= 3
    ]

    scored = []

    for item in results:
        display_name = result_name(
            item
        )

        name_norm = cleaned_name(
            display_name
        )

        exact = (
            name_norm == query_norm
        )

        contains = (
            bool(
                query_norm
            )
            and (
                query_norm in name_norm
                or name_norm in query_norm
            )
        )

        term_hits = sum(
            1
            for term in query_terms
            if term in name_norm
        )

        term_ratio = (
            term_hits
            / max(
                1,
                len(
                    query_terms
                )
            )
        )

        score = 0.0

        if exact:
            score += 100.0

        if contains:
            score += 55.0

        score += (
            term_ratio
            * 30.0
        )

        # Prefer same-state results if state metadata is present.
        item_state = str(
            item.get(
                "state",
                ""
            )
            or item.get(
                "region",
                ""
            )
            or ""
        ).strip().lower()

        if (
            state
            and item_state
            and state.lower() in item_state
        ):
            score += 10.0

        scored.append(
            (
                score,
                term_ratio,
                exact,
                contains,
                item
            )
        )

    scored.sort(
        key=lambda row: row[
            0
        ],
        reverse=True
    )

    top_score, top_ratio, top_exact, top_contains, top_item = scored[
        0
    ]

    second_score = (
        scored[
            1
        ][
            0
        ]
        if len(
            scored
        ) > 1
        else -999.0
    )

    margin = (
        top_score
        - second_score
    )

    # Strong match rules:
    # - exact normalized match, OR
    # - high score + most query terms + a meaningful margin
    strong = bool(
        top_exact
        or (
            top_score >= 70.0
            and top_ratio >= 0.75
            and margin >= 12.0
        )
    )

    candidates = [
        {
            "name": result_name(
                row[
                    4
                ]
            ),
            "score": round(
                row[
                    0
                ],
                1
            ),
            "source": result_source(
                row[
                    4
                ]
            ),
        }
        for row in scored[
            :3
        ]
    ]

    if not strong:
        return None, errors, {
            "strong": False,
            "reason": (
                f'I could not verify "{query}" strongly enough to start a round automatically.'
            ),
            "candidates": candidates,
        }

    return top_item, errors, {
        "strong": True,
        "reason": "Strong course match.",
        "candidates": candidates,
    }



def choose_voice_tee(
    loaded_course,
    spoken_tee
):
    tee_rows = normalize_tees(
        loaded_course.get(
            "tees",
            {}
        )
    )

    tee_choices = [
        str(
            tee.get(
                "Tee",
                ""
            )
        ).strip()
        for tee in tee_rows
        if str(
            tee.get(
                "Tee",
                ""
            )
        ).strip()
    ]

    spoken = str(
        spoken_tee or ""
    ).strip()

    if spoken:
        spoken_norm = normalize_name(
            spoken
        )

        for choice in tee_choices:
            choice_norm = normalize_name(
                choice
            )

            if (
                choice_norm == spoken_norm
                or choice_norm.startswith(
                    spoken_norm
                )
                or spoken_norm in choice_norm
            ):
                return choice

        # If the course feed has no tee names but the golfer explicitly
        # stated one, retain the spoken tee instead of dropping it.
        return spoken

    if tee_choices:
        return tee_choices[
            0
        ]

    return "Default / Unknown"


def start_round_from_voice(
    command
):
    payload = command.get(
        "payload",
        {}
    )

    raw = command.get(
        "raw",
        ""
    )

    course_name = (
        payload.get(
            "course_name"
        )
        or extract_voice_course_name(
            raw
        )
    )

    tee_name = payload.get(
        "tee_name"
    )

    if not course_name:
        # If a course is already selected, starting a round can reuse it.
        existing = st.session_state.get(
            "selected_course"
        )

        if not existing:
            return False, (
                "I heard that you want to start a round, but I could not identify the course."
            )

        loaded = existing

    else:
        matched, errors, match_info = best_voice_course_match(
            course_name
        )

        if not matched:
            # Re-run the search so we retain the full candidate records,
            # not only their display names/scores.
            candidate_results, candidate_errors = search_all_free_sources(
                course_name,
                str(
                    profile.get(
                        "default_state",
                        ""
                    )
                    or ""
                ).strip()
            )

            if not candidate_results:
                candidate_results, more_errors = search_all_free_sources(
                    course_name,
                    ""
                )
                candidate_errors.extend(
                    more_errors
                )

            # Keep only the most plausible few choices.
            query_norm = normalize_name(
                course_name
            )

            def candidate_score(item):
                name_norm = normalize_name(
                    result_name(
                        item
                    )
                )

                score = 0

                if query_norm == name_norm:
                    score += 100

                if query_norm and query_norm in name_norm:
                    score += 60

                terms = [
                    t
                    for t in query_norm.split()
                    if len(t) >= 3
                ]

                score += sum(
                    10
                    for term in terms
                    if term in name_norm
                )

                return score

            candidate_results = sorted(
                candidate_results,
                key=candidate_score,
                reverse=True
            )[:5]

            if candidate_results:
                st.session_state[
                    "voice_pending_course_candidates"
                ] = candidate_results

                st.session_state[
                    "voice_pending_course_name"
                ] = course_name

                st.session_state[
                    "voice_pending_course_tee"
                ] = tee_name

                st.session_state[
                    "voice_pending_course_hole"
                ] = payload.get(
                    "hole_number"
                )

                return False, (
                    f'I found multiple possible locations for "{course_name}". '
                    "Choose the correct course below and confirm it. "
                    "I did not start the round yet."
                )

            return False, (
                match_info.get(
                    "reason",
                    f'I could not verify a course matching "{course_name}".'
                )
                + " I did not start the round."
            )

        try:
            loaded = load_course_result_for_voice(
                matched
            )
        except Exception as exc:
            return False, (
                f"I found {result_name(matched)}, but could not load its course data: {exc}"
            )

        st.session_state[
            "selected_course"
        ] = loaded

        cache_selected_course(
            loaded
        )

    selected_result = loaded.get(
        "search_result",
        {}
    )

    resolved_course_name = result_name(
        selected_result
    )

    selected_tee = choose_voice_tee(
        loaded,
        tee_name
    )

    active = new_round(
        resolved_course_name,
        loaded.get(
            "id",
            ""
        ),
        selected_tee
    )

    # If the same voice command also specified a hole, start there.
    hole_number = payload.get(
        "hole_number"
    )

    if hole_number is not None:
        try:
            hole_number = int(
                hole_number
            )

            if 1 <= hole_number <= 18:
                active[
                    "current_hole"
                ] = hole_number
        except Exception:
            pass

    save_active_round(
        active
    )

    st.session_state[
        "voice_pending_round_start_tee"
    ] = selected_tee

    return True, (
        f"Round started at {resolved_course_name}, {selected_tee} tees"
        + (
            f", hole {active.get('current_hole', 1)}."
            if active.get(
                "current_hole",
                1
            ) != 1
            else "."
        )
    )



def voice_course_candidate_label(item):
    name = result_name(
        item
    )

    city = str(
        item.get(
            "city",
            ""
        )
        or item.get(
            "locality",
            ""
        )
        or ""
    ).strip()

    state = str(
        item.get(
            "state",
            ""
        )
        or item.get(
            "region",
            ""
        )
        or ""
    ).strip()

    location_parts = [
        part
        for part in [
            city,
            state
        ]
        if part
    ]

    if location_parts:
        return (
            name
            + " — "
            + ", ".join(
                location_parts
            )
        )

    return name


def start_round_from_confirmed_course(
    selected_result,
    spoken_tee=None,
    hole_number=None
):
    try:
        loaded = load_course_result_for_voice(
            selected_result
        )
    except Exception as exc:
        return False, (
            f"I found {result_name(selected_result)}, but could not load its course data: {exc}"
        )

    st.session_state[
        "selected_course"
    ] = loaded

    cache_selected_course(
        loaded
    )

    resolved_course_name = result_name(
        loaded.get(
            "search_result",
            {}
        )
    )

    selected_tee = choose_voice_tee(
        loaded,
        spoken_tee
    )

    active = new_round(
        resolved_course_name,
        loaded.get(
            "id",
            ""
        ),
        selected_tee
    )

    if hole_number is not None:
        try:
            hole_number = int(
                hole_number
            )

            if 1 <= hole_number <= 18:
                active[
                    "current_hole"
                ] = hole_number
        except Exception:
            pass

    save_active_round(
        active
    )

    st.session_state[
        "voice_pending_round_start_tee"
    ] = selected_tee

    return True, (
        f"Round started at {resolved_course_name}, {selected_tee} tees"
        + (
            f", hole {active.get('current_hole', 1)}."
            if active.get(
                "current_hole",
                1
            ) != 1
            else "."
        )
    )



def extract_conversational_course_context(
    text
):
    raw = str(
        text or ""
    ).strip()

    # Example:
    # "I'm playing at Pinelands in Hamilton, New Jersey..."
    match = re.search(
        r"\b(?:i(?:'m| am)\s+)?(?:playing|play)\s+at\s+(.+?)(?=\s+in\s+[A-Za-z]|,|\.|;|\band\b|\bbecause\b|$)",
        raw,
        flags=re.IGNORECASE
    )

    if match:
        course = match.group(
            1
        ).strip(
            " ,.-"
        )

        if course:
            return course

    match = re.search(
        r"\bat\s+(.+?)(?=\s+in\s+[A-Za-z]|,|\.|;|\band\b|\bbecause\b|$)",
        raw,
        flags=re.IGNORECASE
    )

    if match:
        course = match.group(
            1
        ).strip(
            " ,.-"
        )

        if course:
            return course

    return None


def extract_conversational_hole_number(
    text
):
    lower = str(
        text or ""
    ).lower()

    ordinal_map = {
        "first": 1,
        "second": 2,
        "third": 3,
        "fourth": 4,
        "fifth": 5,
        "sixth": 6,
        "seventh": 7,
        "eighth": 8,
        "ninth": 9,
        "tenth": 10,
        "eleventh": 11,
        "twelfth": 12,
        "thirteenth": 13,
        "fourteenth": 14,
        "fifteenth": 15,
        "sixteenth": 16,
        "seventeenth": 17,
        "eighteenth": 18,
    }

    digit_match = re.search(
        r"\bhole\s+(\d{1,2})\b",
        lower
    )

    if digit_match:
        number = int(
            digit_match.group(
                1
            )
        )

        if 1 <= number <= 18:
            return number

    ordinal_match = re.search(
        r"\b(first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|eleventh|twelfth|thirteenth|fourteenth|fifteenth|sixteenth|seventeenth|eighteenth)\s+hole\b",
        lower
    )

    if ordinal_match:
        return ordinal_map.get(
            ordinal_match.group(
                1
            )
        )

    return None


def voice_course_display_name(
    course_record
):
    try:
        return result_name(
            course_record.get(
                "search_result",
                course_record
            )
        )
    except Exception:
        return "Selected course"


def resolve_course_for_voice_question(
    course_name,
    hole_number=None,
    tee_name=None
):
    selected = st.session_state.get(
        "selected_course"
    )

    if course_name:
        selected_name = voice_course_display_name(
            selected
        ) if selected else ""

        requested_norm = normalize_name(
            course_name
        )

        selected_norm = normalize_name(
            selected_name
        )

        if (
            selected
            and requested_norm
            and (
                requested_norm in selected_norm
                or selected_norm in requested_norm
            )
        ):
            return selected, None

        matched, errors, match_info = best_voice_course_match(
            course_name
        )

        if matched:
            try:
                loaded = load_course_result_for_voice(
                    matched
                )

                st.session_state[
                    "selected_course"
                ] = loaded

                cache_selected_course(
                    loaded
                )

                return loaded, None
            except Exception as exc:
                return None, (
                    f"I found {result_name(matched)}, but I could not load its course data: {exc}"
                )

        # Do not dead-end on an uncertain course name.
        # Persist actual candidate records so the user can choose one.
        state = str(
            profile.get(
                "default_state",
                ""
            )
            or ""
        ).strip()

        candidate_results, candidate_errors = search_all_free_sources(
            course_name,
            state
        )

        if not candidate_results and state:
            candidate_results, more_errors = search_all_free_sources(
                course_name,
                ""
            )
            candidate_errors.extend(
                more_errors
            )

        # Preserve up to five distinct, plausible course records.
        unique_candidates = []
        seen_names = set()

        for item in candidate_results:
            name = result_name(
                item
            )

            normalized = normalize_name(
                name
            )

            if not normalized or normalized in seen_names:
                continue

            seen_names.add(
                normalized
            )

            unique_candidates.append(
                item
            )

            if len(
                unique_candidates
            ) >= 5:
                break

        if unique_candidates:
            st.session_state[
                "voice_pending_course_candidates"
            ] = unique_candidates

            st.session_state[
                "voice_pending_course_name"
            ] = course_name

            st.session_state[
                "voice_pending_course_hole"
            ] = hole_number

            st.session_state[
                "voice_pending_course_tee"
            ] = tee_name

            st.session_state[
                "voice_pending_course_action"
            ] = "hole_plan"

            return None, (
                f'I found more than one possible location for "{course_name}". '
                "Tap the correct course below and I’ll continue with your hole plan."
            )

        return None, (
            match_info.get(
                "reason",
                f'I could not verify "{course_name}".'
            )
            + " I could not find a reliable course option to select."
        )

    if selected:
        return selected, None

    return None, (
        "I understand the golf question, but I still need the course."
    )



def voice_hole_plan_result(
    course_record,
    hole_number,
    tee_name
):
    hole_number = int(
        hole_number
        or 1
    )

    yardage, hole_record = hole_tee_yardage(
        course_record,
        hole_number,
        tee_name
    )

    course_name = voice_course_display_name(
        course_record
    )

    if hole_record is None:
        return {
            "ok": False,
            "message": (
                f"I found {course_name}, but I do not have verified hole data for Hole {hole_number}."
            ),
        }

    par = None

    for par_key in [
        "par",
        "Par",
        "hole_par",
    ]:
        try:
            maybe_par = int(
                hole_record.get(
                    par_key
                )
            )

            if maybe_par in [
                3,
                4,
                5,
            ]:
                par = maybe_par
                break
        except Exception:
            pass

    if yardage is None:
        return {
            "ok": False,
            "message": (
                f"I found {course_name}, Hole {hole_number}"
                + (
                    f", Par {par}"
                    if par
                    else ""
                )
                + f", but I do not have verified yardage for the {tee_name} tees."
            ),
        }

    yardage = round(
        float(
            yardage
        )
    )

    st.session_state[
        "voice_hole_number"
    ] = hole_number

    st.session_state[
        "voice_selected_tee"
    ] = tee_name

    st.session_state[
        "caddie_distance"
    ] = yardage

    if par is not None:
        st.session_state[
            "voice_hole_par"
        ] = par

    # Par 4 / 5: use My Play's existing route engine.
    if par in [
        4,
        5,
    ]:
        try:
            plan = build_hole_plan(
                par,
                yardage,
                bag,
                shots,
                "None",
                "None",
                "Center"
            )

            if plan:
                # build_hole_plan can return route bundles or a route.
                route = None

                if isinstance(
                    plan,
                    dict
                ):
                    route = (
                        plan.get(
                            "recommended"
                        )
                        or plan.get(
                            "recommended_route"
                        )
                        or plan.get(
                            "conservative"
                        )
                        or plan
                    )

                if isinstance(
                    route,
                    dict
                ):
                    tee_club = route.get(
                        "tee_club"
                    )

                    tee_carry = route.get(
                        "tee_carry"
                    )

                    leave = route.get(
                        "leave"
                    )

                    second_club = route.get(
                        "second_club"
                    )

                    parts = [
                        f"{course_name}, Hole {hole_number}",
                        f"{yardage} yards from the {tee_name} tees",
                    ]

                    if par:
                        parts[
                            0
                        ] += f", Par {par}"

                    strategy = ""

                    if tee_club:
                        strategy = (
                            f"My Play likes {tee_club} off the tee"
                            + (
                                f" for about {tee_carry} yards"
                                if tee_carry is not None
                                else ""
                            )
                        )

                    if second_club:
                        strategy += (
                            f", then {second_club}"
                        )

                    if leave is not None:
                        strategy += (
                            f", leaving about {leave} yards"
                        )

                    if strategy:
                        parts.append(
                            strategy + "."
                        )

                    parts.append(
                        "That recommendation uses your learned club data, including range, simulator, and on-course evidence."
                    )

                    return {
                        "ok": True,
                        "message": " ".join(
                            parts
                        ),
                    }
        except Exception:
            pass

    # Par 3 or fallback: select closest learned carry.
    try:
        options = club_options_with_learning(
            bag,
            shots
        )

        if options:
            best = min(
                options,
                key=lambda item: abs(
                    float(
                        item.get(
                            "carry",
                            0
                        )
                    )
                    - float(
                        yardage
                    )
                )
            )

            club_name = best[
                "club"
            ][
                "Club"
            ]

            carry = round(
                float(
                    best.get(
                        "carry",
                        yardage
                    )
                )
            )

            dispersion = best.get(
                "dispersion",
                {}
            )

            normal_miss = dispersion.get(
                "dominant_miss"
            )

            message = (
                f"{course_name}, Hole {hole_number}"
                + (
                    f", Par {par}"
                    if par
                    else ""
                )
                + f": {yardage} yards from the {tee_name} tees. "
                + f"Your best starting club is {club_name}, playing about {carry}. "
            )

            if normal_miss:
                message += (
                    f"Your learned miss is {normal_miss}. "
                )

            message += (
                "This is based on your unified My Play data, including range, simulator, and on-course shots."
            )

            return {
                "ok": True,
                "message": message,
            }
    except Exception:
        pass

    return {
        "ok": True,
        "message": (
            f"{course_name}, Hole {hole_number}"
            + (
                f", Par {par}"
                if par
                else ""
            )
            + f": {yardage} yards from the {tee_name} tees. "
            "I loaded the hole into the caddie, but I could not build a club plan from the available bag data."
        ),
    }


def tee_choices_for_voice_course(
    course_record
):
    rows = normalize_tees(
        course_record.get(
            "tees",
            {}
        )
    )

    choices = []

    for row in rows:
        name = str(
            row.get(
                "Tee",
                ""
            )
        ).strip()

        if name and name not in choices:
            choices.append(
                name
            )

    return choices



def prepare_start_round_course_choices(
    parsed_command
):
    payload = parsed_command.get(
        "payload",
        {}
    )

    raw = str(
        payload.get(
            "raw",
            ""
        )
        or ""
    )

    location_context = extract_course_location_context(
        raw
    )

    course_name = str(
        location_context.get(
            "course_name"
        )
        or payload.get(
            "course_name",
            ""
        )
        or ""
    ).strip()

    city = location_context.get(
        "city"
    )

    state = location_context.get(
        "state"
    )

    if not course_name:
        return False, (
            "Tell me the course name and I’ll show you the matching locations."
        )

    ranked, errors = search_courses_for_voice_location(
        course_name,
        city,
        state
    )

    if not ranked:
        return False, (
            f'I could not find a course matching "{course_name}".'
        )

    # Keep only genuinely relevant options. Do not fall back to random
    # alphabetical courses just because the search backend returned them.
    relevant = [
        (
            score,
            item
        )
        for score, item in ranked
        if score >= 60.0
    ]

    if not relevant:
        top_score, top_item = ranked[
            0
        ]

        return False, (
            f'I could not find a reliable match for "{course_name}"'
            + (
                f" in {city}, {state}"
                if city and state
                else ""
            )
            + ". I will not show unrelated courses."
        )

    # If the top result is an exact/near-exact name plus matching city,
    # it is safe to present it first and usually as the only choice.
    top_score = relevant[
        0
    ][
        0
    ]

    if top_score >= 220.0:
        relevant = relevant[
            :1
        ]
    else:
        relevant = relevant[
            :5
        ]

    unique = []
    seen = set()

    for score, item in relevant:
        key = (
            normalized_course_core(
                result_name(
                    item
                )
            ),
            normalize_name(
                str(
                    item.get(
                        "city",
                        ""
                    )
                    or item.get(
                        "locality",
                        ""
                    )
                    or ""
                )
            ),
        )

        if key in seen:
            continue

        seen.add(
            key
        )

        unique.append(
            item
        )

    st.session_state[
        "voice_pending_course_candidates"
    ] = unique

    st.session_state[
        "voice_pending_course_name"
    ] = course_name

    st.session_state[
        "voice_pending_course_city"
    ] = city

    st.session_state[
        "voice_pending_course_state"
    ] = state

    st.session_state[
        "voice_pending_course_tee"
    ] = payload.get(
        "tee_name"
    )

    st.session_state[
        "voice_pending_course_hole"
    ] = (
        payload.get(
            "hole_number"
        )
        or 1
    )

    st.session_state[
        "voice_pending_course_action"
    ] = "start_round"

    return True, (
        f'I found matching location'
        + (
            "s"
            if len(
                unique
            ) != 1
            else ""
        )
        + f' for "{course_name}". Tap the correct course to continue.'
    )



def build_started_round_summary(
    course_record,
    tee_name,
    hole_number
):
    course_name = voice_course_display_name(
        course_record
    )

    try:
        hole_number = int(
            hole_number
            or 1
        )
    except Exception:
        hole_number = 1

    yardage = None
    hole_record = None

    try:
        yardage, hole_record = hole_tee_yardage(
            course_record,
            hole_number,
            tee_name
        )
    except Exception:
        pass

    par = None

    if isinstance(
        hole_record,
        dict
    ):
        try:
            par = int(
                hole_record.get(
                    "par",
                    hole_record.get(
                        "Par"
                    )
                )
            )
        except Exception:
            par = None

    parts = [
        f"Round started at {course_name}.",
        f"Hole {hole_number}"
        + (
            f" • Par {par}"
            if par
            else ""
        )
        + (
            f" • {round(float(yardage))} yards"
            if yardage is not None
            else ""
        )
        + (
            f" • {tee_name} tees"
            if tee_name
            else ""
        )
        + "."
    ]

    parts.append(
        "My Play is ready to give you the recommended play using your learned club data and available course information."
    )

    return " ".join(
        parts
    )



def extract_course_location_context(
    text
):
    raw = str(
        text or ""
    ).strip()

    cleaned = re.sub(
        r"^\s*(?:no[, ]+)?(?:i\s+said|i\s+meant|what\s+i\s+said\s+was)\s+",
        "",
        raw,
        flags=re.IGNORECASE
    ).strip()

    # "Pinelands Golf Club in Hammonton, New Jersey"
    match = re.search(
        r"^(.*?)(?:\s+in\s+)([A-Za-z .'-]+),\s*([A-Za-z .'-]+)(?:[.!?]|$)",
        cleaned,
        flags=re.IGNORECASE
    )

    if match:
        return {
            "course_name": match.group(
                1
            ).strip(
                " ,.-"
            ),
            "city": match.group(
                2
            ).strip(
                " ,.-"
            ),
            "state": match.group(
                3
            ).strip(
                " ,.-"
            ),
        }

    # "Pinelands Golf Club, Hammonton, New Jersey"
    match = re.search(
        r"^(.*?),\s*([A-Za-z .'-]+),\s*([A-Za-z .'-]+)(?:[.!?]|$)",
        cleaned,
        flags=re.IGNORECASE
    )

    if match:
        return {
            "course_name": match.group(
                1
            ).strip(
                " ,.-"
            ),
            "city": match.group(
                2
            ).strip(
                " ,.-"
            ),
            "state": match.group(
                3
            ).strip(
                " ,.-"
            ),
        }

    return {
        "course_name": extract_conversational_course_context(
            cleaned
        )
        or extract_voice_course_name(
            cleaned
        ),
        "city": None,
        "state": None,
    }


def normalized_course_core(
    value
):
    value = normalize_name(
        value
    )

    value = re.sub(
        r"\b(country club|golf club|golf course)\b",
        " ",
        value
    )

    value = re.sub(
        r"\b(golf|club|course|gc|cc)\b",
        " ",
        value
    )

    value = re.sub(
        r"\s+",
        " ",
        value
    ).strip()

    return value


def rank_course_results_with_location(
    results,
    course_name,
    city=None,
    state=None
):
    query_core = normalized_course_core(
        course_name
    )

    city_norm = normalize_name(
        city or ""
    )

    state_norm = normalize_name(
        state or ""
    )

    scored = []

    for item in results:
        name = result_name(
            item
        )

        name_core = normalized_course_core(
            name
        )

        item_city = normalize_name(
            str(
                item.get(
                    "city",
                    ""
                )
                or item.get(
                    "locality",
                    ""
                )
                or ""
            )
        )

        item_state = normalize_name(
            str(
                item.get(
                    "state",
                    ""
                )
                or item.get(
                    "region",
                    ""
                )
                or ""
            )
        )

        score = 0.0

        if query_core and name_core == query_core:
            score += 150.0
        elif query_core and (
            query_core in name_core
            or name_core in query_core
        ):
            score += 90.0

        query_terms = [
            term
            for term in query_core.split()
            if len(
                term
            ) >= 3
        ]

        if query_terms:
            hit_count = sum(
                1
                for term in query_terms
                if term in name_core
            )

            score += (
                hit_count
                / len(
                    query_terms
                )
            ) * 50.0

        if city_norm:
            if item_city == city_norm:
                score += 80.0
            elif (
                city_norm in item_city
                or item_city in city_norm
            ):
                score += 45.0

        if state_norm:
            # Accept common NJ / New Jersey equivalence.
            state_aliases = {
                "new jersey": "nj",
                "nj": "nj",
            }

            requested_state = state_aliases.get(
                state_norm,
                state_norm
            )

            result_state = state_aliases.get(
                item_state,
                item_state
            )

            if requested_state and result_state == requested_state:
                score += 35.0

        scored.append(
            (
                score,
                item
            )
        )

    scored.sort(
        key=lambda pair: pair[
            0
        ],
        reverse=True
    )

    return scored


def search_courses_for_voice_location(
    course_name,
    city=None,
    state=None
):
    search_state = str(
        state
        or profile.get(
            "default_state",
            ""
        )
        or ""
    ).strip()

    results, errors = search_all_free_sources(
        course_name,
        search_state
    )

    if not results and search_state:
        results, more_errors = search_all_free_sources(
            course_name,
            ""
        )
        errors.extend(
            more_errors
        )

    ranked = rank_course_results_with_location(
        results,
        course_name,
        city,
        state
    )

    return ranked, errors


# ============================================================
# VOICE COMMAND CENTER
# ============================================================

def parse_voice_command_center(text):
    raw = str(text or "").strip()
    lower = raw.lower().replace("-", " ")

    lower = re.sub(
        r"\s+",
        " ",
        lower
    ).strip()

    result = {
        "raw": raw,
        "intent": "unknown",
        "confidence": "low",
        "requires_confirmation": False,
        "payload": {},
    }

    # Parse common structures up front so routing can use them.
    shot_payload = parse_voice_shot_text(
        raw
    )

    bag_payload = parse_voice_bag_command(
        raw
    )

    detected_club = (
        bag_payload.get(
            "club"
        )
        or detect_spoken_club_from_bag(
            raw
        )
    )

    if detected_club:
        bag_payload[
            "club"
        ] = detected_club

    # --------------------------------------------------------
    # Explicit round control
    # --------------------------------------------------------
    if any(
        phrase in lower
        for phrase in [
            "start a round",
            "start round",
            "starting a round",
            "starting round",
            "begin a round",
            "begin round",
            "beginning a round",
            "new round",
            "playing a round",
        ]
    ):
        shot_payload[
            "course_name"
        ] = extract_voice_course_name(
            raw
        )

        shot_payload[
            "raw"
        ] = raw

        result[
            "intent"
        ] = "start_round"
        result[
            "confidence"
        ] = "high"
        result[
            "requires_confirmation"
        ] = True
        result[
            "payload"
        ] = shot_payload
        return result

    if any(
        phrase in lower
        for phrase in [
            "end the round",
            "finish the round",
            "end round",
            "finish round",
            "close the round",
        ]
    ):
        result[
            "intent"
        ] = "end_round"
        result[
            "confidence"
        ] = "high"
        result[
            "requires_confirmation"
        ] = True
        return result

    # --------------------------------------------------------
    # Bag writes: if a club is detected and the sentence sounds
    # like a change, prioritize this before general club queries.
    # --------------------------------------------------------
    bag_write_words = [
        "add",
        "change",
        "update",
        "edit",
        "set",
        "delete",
        "remove",
        "take out",
        "make my",
    ]

    if (
        detected_club
        and any(
            phrase in lower
            for phrase in bag_write_words
        )
    ):
        # Infer action if parser missed it.
        if not bag_payload.get(
            "action"
        ):
            if any(
                phrase in lower
                for phrase in [
                    "delete",
                    "remove",
                    "take out",
                ]
            ):
                bag_payload[
                    "action"
                ] = "delete"

            elif any(
                phrase in lower
                for phrase in [
                    "add",
                    "put in",
                    "new",
                ]
            ):
                bag_payload[
                    "action"
                ] = "add"

            else:
                bag_payload[
                    "action"
                ] = "edit"

        result[
            "intent"
        ] = "bag_change"
        result[
            "confidence"
        ] = "high"
        result[
            "requires_confirmation"
        ] = True
        result[
            "payload"
        ] = bag_payload
        return result

    # --------------------------------------------------------
    # Voice correction for course/location
    # --------------------------------------------------------
    if re.search(
        r"^\s*(?:no[, ]+)?(?:i\s+said|i\s+meant|what\s+i\s+said\s+was)\b",
        raw,
        flags=re.IGNORECASE
    ):
        correction_context = extract_course_location_context(
            raw
        )

        corrected_course = correction_context.get(
            "course_name"
        )

        if corrected_course:
            return {
                "intent": "start_round",
                "confidence": "high",
                "payload": {
                    "raw": raw,
                    "course_name": corrected_course,
                    "city": correction_context.get(
                        "city"
                    ),
                    "state": correction_context.get(
                        "state"
                    ),
                    "tee_name": shot_payload.get(
                        "tee_name"
                    ),
                    "hole_number": shot_payload.get(
                        "hole_number"
                    )
                    or 1,
                },
                "requires_confirmation": True,
            }

    # --------------------------------------------------------
    # Conversational course / hole strategy question
    # --------------------------------------------------------
    conversational_plan_phrases = [
        "how to play",
        "how do i play",
        "how should i play",
        "don't know how to play",
        "do not know how to play",
        "never played here",
        "never played this course",
        "recommendations for this hole",
        "recommendation for this hole",
        "what's the play on",
        "what is the play on",
    ]

    if any(
        phrase in lower
        for phrase in conversational_plan_phrases
    ):
        conversational_course = (
            extract_conversational_course_context(
                raw
            )
            or extract_voice_course_name(
                raw
            )
        )

        conversational_hole = (
            extract_conversational_hole_number(
                raw
            )
            or shot_payload.get(
                "hole_number"
            )
            or 1
        )

        result[
            "intent"
        ] = "hole_plan_query"

        result[
            "confidence"
        ] = "high"

        result[
            "payload"
        ] = {
            **shot_payload,
            "course_name": conversational_course,
            "hole_number": conversational_hole,
            "raw": raw,
        }

        return result

    # --------------------------------------------------------
    # Hole / tee context
    # --------------------------------------------------------
    if (
        shot_payload.get(
            "hole_number"
        ) is not None
        or shot_payload.get(
            "tee_name"
        ) is not None
    ):
        # If they also gave a shot distance / wind / lie, treat it as
        # full caddie input rather than only navigation.
        if any(
            shot_payload.get(
                key
            ) is not None
            for key in [
                "distance",
                "wind_direction",
                "wind_speed",
                "surface",
                "trouble_type",
                "elevation",
            ]
        ):
            result[
                "intent"
            ] = "caddie_input"
            result[
                "confidence"
            ] = "high"
            result[
                "payload"
            ] = shot_payload
            return result

        result[
            "intent"
        ] = "set_hole_context"
        result[
            "confidence"
        ] = "high"
        result[
            "payload"
        ] = shot_payload
        return result

    # --------------------------------------------------------
    # Reminder writes
    # --------------------------------------------------------
    if any(
        phrase in lower
        for phrase in [
            "remind me",
            "save a reminder",
            "add a reminder",
            "remember this",
            "remember that",
        ]
    ):
        reminder_text = raw

        prefixes = [
            "remind me to ",
            "remind me ",
            "save a reminder to ",
            "save a reminder ",
            "add a reminder to ",
            "add a reminder ",
            "remember this ",
            "remember that ",
        ]

        for prefix in prefixes:
            if reminder_text.lower().startswith(
                prefix
            ):
                reminder_text = reminder_text[
                    len(
                        prefix
                    ):
                ].strip()
                break

        result[
            "intent"
        ] = "add_reminder"
        result[
            "confidence"
        ] = "high"
        result[
            "requires_confirmation"
        ] = True
        result[
            "payload"
        ] = {
            "text": reminder_text
        }
        return result

    # --------------------------------------------------------
    # Save current shot
    # --------------------------------------------------------
    if any(
        phrase in lower
        for phrase in [
            "save that shot",
            "save this shot",
            "log that shot",
            "log this shot",
            "record that shot",
            "record this shot",
            "save shot",
            "log shot",
        ]
    ):
        result[
            "intent"
        ] = "save_shot"
        result[
            "confidence"
        ] = "high"
        result[
            "requires_confirmation"
        ] = True
        return result

    # --------------------------------------------------------
    # Club analytics/history questions
    # --------------------------------------------------------
    if detected_club:
        analytics_phrases = [
            "how has my",
            "how is my",
            "how am i hitting",
            "show me",
            "lately",
            "recently",
            "dispersion",
            "miss pattern",
            "consistency",
        ]

        if any(
            phrase in lower
            for phrase in analytics_phrases
        ):
            result[
                "intent"
            ] = "club_analytics_query"
            result[
                "confidence"
            ] = "high"
            result[
                "payload"
            ] = {
                "club": detected_club
            }
            return result

        # Any question about a known club + distance/carry should be a
        # club query even if wording is unusual.
        club_question_words = [
            "what",
            "how far",
            "carry",
            "distance",
            "yardage",
            "yards",
            "hit my",
            "hit the",
        ]

        if (
            "?" in raw
            or any(
                phrase in lower
                for phrase in club_question_words
            )
        ):
            result[
                "intent"
            ] = "club_query"
            result[
                "confidence"
            ] = "high"
            result[
                "payload"
            ] = {
                "club": detected_club
            }
            return result

    # --------------------------------------------------------
    # Hole history
    # --------------------------------------------------------
    if any(
        phrase in lower
        for phrase in [
            "what did i do on this hole",
            "what did i do here last time",
            "last time on this hole",
            "previously on this hole",
            "history on this hole",
            "this hole last time",
        ]
    ):
        result[
            "intent"
        ] = "hole_history"
        result[
            "confidence"
        ] = "high"
        return result

    # --------------------------------------------------------
    # Explicit caddie request
    # --------------------------------------------------------
    if any(
        phrase in lower
        for phrase in [
            "what's the play",
            "what is the play",
            "what club",
            "what should i hit",
            "what do i hit",
            "what should i play",
            "recommend",
            "give me the shot",
            "give me a club",
            "caddie",
        ]
    ):
        result[
            "intent"
        ] = "caddie_query"
        result[
            "confidence"
        ] = "high"
        result[
            "payload"
        ] = shot_payload
        return result

    # --------------------------------------------------------
    # Generic shot description fallback.
    # If the transcription contains any real shot information,
    # accept it instead of calling it unknown.
    # --------------------------------------------------------
    shot_signal_keys = [
        "distance",
        "temperature",
        "wind_direction",
        "wind_speed",
        "surface",
        "lie_type",
        "stance",
        "slope_severity",
        "trouble_type",
        "trouble_location",
        "safe_side",
        "elevation",
        "hole_number",
        "par",
        "tee_name",
    ]

    if any(
        shot_payload.get(
            key
        ) is not None
        for key in shot_signal_keys
    ):
        result[
            "intent"
        ] = "caddie_input"
        result[
            "confidence"
        ] = "medium"
        result[
            "payload"
        ] = shot_payload
        return result

    # --------------------------------------------------------
    # Final fallback: if we recognized a real bag club at all,
    # treat a short ambiguous utterance as a club query rather
    # than rejecting it.
    # --------------------------------------------------------
    if detected_club:
        result[
            "intent"
        ] = "club_query"
        result[
            "confidence"
        ] = "medium"
        result[
            "payload"
        ] = {
            "club": detected_club
        }
        return result

    return result

def voice_command_summary(command):
    intent = command.get("intent", "unknown")
    payload = command.get("payload", {})

    labels = {
        "start_round": "Start Round",
        "end_round": "End Round",
        "set_hole_context": "Set Hole / Tee Context",
        "bag_change": "Change Golf Bag",
        "add_reminder": "Add Reminder",
        "save_shot": "Save Shot",
        "club_query": "Club Distance Query",
        "hole_history": "Hole History",
        "club_analytics_query": "Club Analytics Query",
        "caddie_query": "Caddie Recommendation",
        "caddie_input": "Caddie Input",
        "hole_plan_query": "Hole Strategy",
        "unknown": "Unknown Command",
    }

    return {
        "Intent": labels.get(intent, intent),
        "Confidence": command.get("confidence", "low"),
        "Needs Confirmation": "Yes" if command.get("requires_confirmation") else "No",
        "Payload": json.dumps(payload, default=str),
    }


def execute_read_only_voice_command(command):
    intent = command.get("intent")
    payload = command.get("payload", {})

    if intent == "hole_plan_query":
        course_name = payload.get(
            "course_name"
        )

        hole_number = payload.get(
            "hole_number"
        ) or 1

        tee_name = payload.get(
            "tee_name"
        )

        course_record, course_error = resolve_course_for_voice_question(
            course_name,
            hole_number,
            tee_name
        )

        if course_record is None:
            return {
                "ok": False,
                "message": course_error,
                "talk_back": course_error,
            }

        resolved_name = voice_course_display_name(
            course_record
        )

        if not tee_name:
            tee_choices = tee_choices_for_voice_course(
                course_record
            )

            if tee_choices:
                st.session_state[
                    "voice_pending_hole_plan_course"
                ] = course_record

                st.session_state[
                    "voice_pending_hole_plan_hole"
                ] = hole_number

                st.session_state[
                    "voice_pending_hole_plan_tees"
                ] = tee_choices

                message = (
                    f"Got it — {resolved_name}, Hole {hole_number}. "
                    "Which tees are you playing? Tap one below and I’ll give you the plan."
                )

                return {
                    "ok": True,
                    "message": message,
                    "talk_back": message,
                }

            return {
                "ok": False,
                "message": (
                    f"Got it — {resolved_name}, Hole {hole_number}. "
                    "I need your tee color or tee name before I can give you an accurate plan."
                ),
                "talk_back": (
                    f"I found {resolved_name}, hole {hole_number}. Tell me which tees you are playing."
                ),
            }

        result = voice_hole_plan_result(
            course_record,
            hole_number,
            tee_name
        )

        return {
            "ok": result.get(
                "ok",
                False
            ),
            "message": result.get(
                "message",
                ""
            ),
            "talk_back": result.get(
                "message",
                ""
            ),
        }

    if intent == "set_hole_context":
        result = apply_voice_hole_context(payload)
        return {
            "ok": True,
            "message": result.get(
                "message",
                "Hole context updated."
            ),
            "talk_back": result.get(
                "message",
                "Hole context updated."
            ),
        }

    if intent in ["caddie_query", "caddie_input"]:
        applied = apply_voice_shot_to_caddie(
            payload
        )

        hole_message = None

        if payload.get("hole_number") is not None:
            hole_result = apply_voice_hole_context(
                payload
            )
            hole_message = hole_result.get(
                "message"
            )

        message_parts = []

        if hole_message:
            message_parts.append(
                hole_message
            )

        if applied:
            message_parts.append(
                f"Filled {len(applied)} caddie input(s)."
            )

        if not message_parts:
            message_parts.append(
                "Caddie context updated."
            )

        message_parts.append(
            "My Play loaded the shot into the Caddie. Open Caddie to review or get the recommendation."
        )

        return {
            "ok": True,
            "message": " ".join(message_parts),
            "talk_back": "Caddie inputs are ready. Open the Caddie tab for the recommendation.",
        }

    if intent == "club_query":
        club_name = payload.get("club")

        if not club_name:
            return {
                "ok": False,
                "message": "I could not identify the club.",
                "talk_back": "I could not identify the club.",
            }

        idx = find_bag_club_index(
            club_name
        )

        if idx is None:
            return {
                "ok": False,
                "message": f"{club_name} is not in this golfer's bag.",
                "talk_back": f"{club_name} is not in your bag.",
            }

        club = bag[idx]

        try:
            analytics = comprehensive_club_analytics(
                club,
                shots
            )

            playing = analytics.get(
                "playing_carry"
            )
            reliable = analytics.get(
                "reliable_carry"
            )
            miss = analytics.get(
                "dominant_miss"
            ) or club.get(
                "Typical Miss",
                "unknown"
            )

            message = (
                f"{club_name}: playing carry about {round(float(playing)) if playing is not None else club.get('Stock Carry', 'unknown')} yards"
            )

            if reliable is not None:
                message += (
                    f", reliable carry about {round(float(reliable))} yards"
                )

            message += (
                f", normal miss {miss}."
            )

            return {
                "ok": True,
                "message": message,
                "talk_back": message,
            }

        except Exception:
            stock = club.get(
                "Stock Carry",
                "unknown"
            )
            miss = club.get(
                "Typical Miss",
                "unknown"
            )

            message = (
                f"{club_name}: stock carry {stock} yards, normal miss {miss}."
            )

            return {
                "ok": True,
                "message": message,
                "talk_back": message,
            }

    if intent == "club_analytics_query":
        club_name = payload.get("club")

        if not club_name:
            return {
                "ok": False,
                "message": "I could not identify the club.",
                "talk_back": "I could not identify the club.",
            }

        idx = find_bag_club_index(
            club_name
        )

        if idx is None:
            return {
                "ok": False,
                "message": f"{club_name} is not in this golfer's bag.",
                "talk_back": f"{club_name} is not in your bag.",
            }

        club = bag[idx]

        try:
            analytics = comprehensive_club_analytics(
                club,
                shots
            )

            message = (
                f"{club_name}: playing carry {round(float(analytics.get('playing_carry')))} yards, "
                f"reliable carry {round(float(analytics.get('reliable_carry')))} yards, "
                f"dominant miss {analytics.get('dominant_miss')}, "
                f"confidence {analytics.get('confidence')}."
            )

            return {
                "ok": True,
                "message": message,
                "talk_back": message,
            }

        except Exception as exc:
            return {
                "ok": False,
                "message": f"Could not summarize {club_name}: {exc}",
                "talk_back": f"I could not summarize {club_name}.",
            }

    if intent == "hole_history":
        return {
            "ok": True,
            "message": (
                "Hole-history voice routing is connected, but this command still needs the active-hole history lookup wired into the round data."
            ),
            "talk_back": (
                "Hole history is connected, but I still need to wire the active hole lookup."
            ),
        }

    if intent == "unknown":
        transcript = str(
            command.get(
                "raw",
                ""
            )
        ).strip()

        return {
            "ok": False,
            "message": (
                "My Play heard you, but that request is outside the current voice controls. Use voice for live caddie questions, shot context, or club-data changes. "
                + (
                    f'Transcript: "{transcript}"'
                    if transcript
                    else ""
                )
            ),
            "talk_back": (
                "I heard you, but I could not route that command yet."
            ),
        }

    return {
        "ok": False,
        "message": f"Voice command '{intent}' is not a read-only command.",
        "talk_back": "That command needs confirmation.",
    }


def build_voice_write_preview(command):
    intent = command.get("intent")
    payload = command.get("payload", {})

    preview = {
        "valid": False,
        "intent": intent,
        "message": "",
        "payload": payload,
        "details": None,
    }

    if intent == "bag_change":
        bag_preview = build_voice_bag_preview(
            payload
        )

        preview["valid"] = bag_preview.get(
            "valid",
            False
        )
        preview["message"] = bag_preview.get(
            "message",
            ""
        )
        preview["details"] = bag_preview
        return preview

    if intent == "add_reminder":
        text = str(
            payload.get(
                "text",
                ""
            )
        ).strip()

        if not text:
            preview["message"] = "No reminder text was detected."
            return preview

        preview["valid"] = True
        preview["message"] = f'Add reminder: "{text}"'
        return preview

    if intent == "start_round":
        course_name = (
            payload.get(
                "course_name"
            )
        )

        tee_name = payload.get(
            "tee_name"
        )

        preview[
            "valid"
        ] = bool(
            course_name
            or st.session_state.get(
                "selected_course"
            )
        )

        if course_name:
            preview[
                "message"
            ] = (
                f"Start a round at {course_name}"
                + (
                    f", {tee_name} tees."
                    if tee_name
                    else "."
                )
            )
        else:
            preview[
                "message"
            ] = (
                "Start a round at the currently selected course"
                + (
                    f", {tee_name} tees."
                    if tee_name
                    else "."
                )
            )

        return preview

    if intent == "end_round":
        preview["valid"] = True
        preview["message"] = "End the current round."
        return preview

    if intent == "save_shot":
        preview["valid"] = True
        preview["message"] = (
            "Save the current shot using the active caddie / live-round inputs."
        )
        return preview

    preview["message"] = "Unsupported write command."
    return preview


def commit_voice_write_command(preview):
    intent = preview.get(
        "intent"
    )
    payload = preview.get(
        "payload",
        {}
    )

    if not preview.get(
        "valid"
    ):
        return False, preview.get(
            "message",
            "Invalid command."
        )

    if intent == "bag_change":
        return commit_voice_bag_change(
            preview.get(
                "details",
                {}
            )
        )

    if intent == "add_reminder":
        reminder_text = str(
            payload.get(
                "text",
                ""
            )
        ).strip()

        try:
            reminders = read_swing_reminders()
        except Exception:
            reminders = []

        if reminder_text not in reminders:
            reminders.append(
                reminder_text
            )

        try:
            save_swing_reminders(
                reminders
            )
        except Exception:
            # Fallback to existing writer patterns if function name differs.
            try:
                with open(
                    REMINDER_FILE,
                    "w",
                    encoding="utf-8"
                ) as f:
                    f.write(
                        "\n".join(
                            reminders
                        )
                    )
            except Exception as exc:
                return False, f"Could not save reminder: {exc}"

        return True, "Reminder saved."

    if intent == "start_round":
        return False, (
            "Round setup is click-first now. Choose your course and tees from Courses / Live Round, "
            "then use voice once the round is active for caddie questions and shot context."
        )

    if intent == "end_round":
        st.session_state[
            "voice_requested_end_round"
        ] = True

        return True, (
            "Round end command captured. Open Live Round to review and finish the round."
        )

    if intent == "save_shot":
        st.session_state[
            "voice_requested_save_shot"
        ] = True

        return True, (
            "Save-shot command captured. Open Live Round to review the current shot before saving."
        )

    return False, "Unsupported command."




def render_live_round_caddie_panel(
    bag,
    shots
):
    st.subheader(
        "🏌️ Live Caddie"
    )

    st.caption(
        "Uses the same unified My Play player model: range + simulator + on-course + prior-round evidence."
    )

    if not bag:
        st.info(
            "Add clubs in My Bag before using the Live Caddie."
        )
        return

    current_distance = int(
        st.session_state.get(
            "caddie_distance",
            150
        )
        or 150
    )

    distance = st.number_input(
        "Distance to Pin (yards)",
        min_value=1,
        max_value=400,
        value=current_distance,
        step=1,
        key="live_round_caddie_distance"
    )

    st.session_state[
        "caddie_distance"
    ] = distance

    if st.button(
        "Get Live Recommendation",
        use_container_width=True,
        type="primary",
        key="live_round_get_recommendation"
    ):
        try:
            recommendation = recommend_club(
                bag,
                distance,
                shots=shots
            )

            if isinstance(
                recommendation,
                dict
            ):
                club_name = (
                    recommendation.get(
                        "club"
                    )
                    or recommendation.get(
                        "Club"
                    )
                    or recommendation.get(
                        "recommended_club"
                    )
                    or "Recommended club"
                )

                play_yards = (
                    recommendation.get(
                        "play_yards"
                    )
                    or recommendation.get(
                        "playing_distance"
                    )
                    or distance
                )

                aim = (
                    recommendation.get(
                        "aim"
                    )
                    or recommendation.get(
                        "target"
                    )
                    or "center"
                )

                message = (
                    f"{club_name}. Playing about {round(float(play_yards))} yards. "
                    f"Favor {aim}."
                )

                st.success(
                    message
                )

                st.session_state[
                    "last_spoken_recommendation"
                ] = message

                if st.session_state.get(
                    "caddie_talk_back_enabled",
                    True
                ):
                    speak_in_browser(
                        message,
                        key="live_round_talk_back"
                    )

            else:
                st.success(
                    str(
                        recommendation
                    )
                )

        except Exception:
            # Fall back to the detailed Caddie tab if the compact helper cannot
            # use the current recommend_club signature.
            st.info(
                "Live Caddie context is ready. Use the Caddie tab for the full recommendation controls."
            )



def current_active_hole_number():
    try:
        active = load_active_round()
    except Exception:
        active = None

    if active:
        try:
            return int(
                active.get(
                    "current_hole",
                    1
                )
                or 1
            )
        except Exception:
            return 1

    try:
        return int(
            st.session_state.get(
                "voice_hole_number",
                1
            )
            or 1
        )
    except Exception:
        return 1


def render_voice_quick_actions():
    try:
        active_round = load_active_round()
    except Exception:
        active_round = None

    hole_number = current_active_hole_number()

    if active_round:
        course_name = active_round.get(
            "course_name",
            ""
        )

        st.markdown(
            f"### Hole {hole_number}"
        )

        if course_name:
            st.caption(
                f"{course_name} • Quick actions"
            )

        row1_col1, row1_col2 = st.columns(
            2
        )

        with row1_col1:
            if st.button(
                f"🏌️ How to Play Hole {hole_number}",
                use_container_width=True,
                key="quick_hole_plan"
            ):
                st.session_state[
                    "voice_quick_action"
                ] = "hole_plan"

        with row1_col2:
            if st.button(
                "🎯 Club Recommendation",
                use_container_width=True,
                key="quick_club_recommendation"
            ):
                st.session_state[
                    "voice_quick_action"
                ] = "club_recommendation"

        row2_col1, row2_col2 = st.columns(
            2
        )

        with row2_col1:
            if st.button(
                "🛡️ Safe Play",
                use_container_width=True,
                key="quick_safe_play"
            ):
                st.session_state[
                    "voice_quick_action"
                ] = "safe_play"

        with row2_col2:
            if st.button(
                "🔥 Aggressive Play",
                use_container_width=True,
                key="quick_aggressive_play"
            ):
                st.session_state[
                    "voice_quick_action"
                ] = "aggressive_play"

        row3_col1, row3_col2 = st.columns(
            2
        )

        with row3_col1:
            if st.button(
                "📍 Hole Yardage",
                use_container_width=True,
                key="quick_hole_yardage"
            ):
                st.session_state[
                    "voice_quick_action"
                ] = "hole_yardage"

        with row3_col2:
            if st.button(
                "⚠️ Hazards",
                use_container_width=True,
                key="quick_hazards"
            ):
                st.session_state[
                    "voice_quick_action"
                ] = "hazards"

        row4_col1, row4_col2 = st.columns(
            2
        )

        with row4_col1:
            if st.button(
                "🕘 What Did I Do Here?",
                use_container_width=True,
                key="quick_hole_history"
            ):
                st.session_state[
                    "voice_quick_action"
                ] = "hole_history"

        with row4_col2:
            if st.button(
                "💾 Log Shot",
                use_container_width=True,
                key="quick_log_shot"
            ):
                st.session_state[
                    "voice_quick_action"
                ] = "log_shot"

    else:
        st.markdown(
            "### What do you want to do?"
        )

        row1_col1, row1_col2 = st.columns(
            2
        )

        with row1_col1:
            if st.button(
                "⛳ Start a Round",
                use_container_width=True,
                key="quick_start_round"
            ):
                st.session_state[
                    "voice_quick_action"
                ] = "start_round"

        with row1_col2:
            if st.button(
                "🌐 Choose a Course",
                use_container_width=True,
                key="quick_choose_course"
            ):
                st.session_state[
                    "voice_quick_action"
                ] = "choose_course"

        row2_col1, row2_col2 = st.columns(
            2
        )

        with row2_col1:
            if st.button(
                "🎒 Manage My Bag",
                use_container_width=True,
                key="quick_manage_bag"
            ):
                st.session_state[
                    "voice_quick_action"
                ] = "manage_bag"

        with row2_col2:
            if st.button(
                "📈 Check Club Distances",
                use_container_width=True,
                key="quick_club_distances"
            ):
                st.session_state[
                    "voice_quick_action"
                ] = "club_distances"

    action = st.session_state.pop(
        "voice_quick_action",
        None
    )

    if not action:
        return

    if action == "start_round":
        st.info(
            "Use the Courses tab to select the exact course and location, then choose your tees in Live Round. "
            "Once the round is active, voice becomes your on-course caddie."
        )

    elif action == "choose_course":
        st.info(
            "Use Live Round and tap the exact course/location you want. "
            "This avoids voice guessing on course names."
        )

    elif action == "manage_bag":
        st.info(
            "Open My Bag to add, edit, or remove clubs. Voice bag commands are available there too."
        )

    elif action == "club_distances":
        st.info(
            "Open Club Analytics to see learned carries, reliable carry, dispersion, and misses."
        )

    elif action == "hole_plan":
        st.session_state[
            "caddie_strategy_mode"
        ] = "Recommended"

        st.info(
            f"Hole {hole_number} is ready in Live Round. Use Get Live Recommendation for the full plan."
        )

    elif action == "club_recommendation":
        st.info(
            "Use the Live Caddie panel to confirm the current distance, then tap Get Live Recommendation."
        )

    elif action == "safe_play":
        st.session_state[
            "caddie_strategy_mode"
        ] = "Conservative"

        st.info(
            "Conservative route selected. Open Live Round for the safer caddie plan."
        )

    elif action == "aggressive_play":
        st.session_state[
            "caddie_strategy_mode"
        ] = "Aggressive"

        st.info(
            "Aggressive route selected. Open Live Round for the aggressive caddie plan."
        )

    elif action == "hole_yardage":
        selected_course = st.session_state.get(
            "selected_course"
        )

        tee_name = st.session_state.get(
            "round_start_tee"
        ) or st.session_state.get(
            "voice_pending_round_start_tee"
        )

        if selected_course and tee_name:
            yardage, _ = hole_tee_yardage(
                selected_course,
                hole_number,
                tee_name
            )

            if yardage is not None:
                message = (
                    f"Hole {hole_number} from the {tee_name} tees is {yardage} yards."
                )

                st.success(
                    message
                )

                if st.session_state.get(
                    "caddie_talk_back_enabled",
                    True
                ):
                    speak_in_browser(
                        message,
                        key="quick_hole_yardage_talkback"
                    )
            else:
                st.warning(
                    "I could not verify the yardage for this hole and tee."
                )
        else:
            st.warning(
                "Select a course and tee first."
            )

    elif action == "hazards":
        selected_course = st.session_state.get(
            "selected_course"
        )

        if not selected_course:
            st.warning(
                "Select a course first."
            )
        else:
            osm_features = selected_course.get(
                "osm_features",
                {}
            )

            bunkers = osm_features.get(
                "bunkers",
                []
            )

            st.info(
                f"My Play currently has {len(bunkers)} mapped bunker feature"
                + (
                    "s"
                    if len(bunkers) != 1
                    else ""
                )
                + " available for this course. Live Round uses mapped trouble when available."
            )

    elif action == "hole_history":
        st.info(
            "Hole-history routing is ready; the next refinement is to surface the exact prior shots and scores for this active hole."
        )

    elif action == "log_shot":
        st.session_state[
            "voice_requested_save_shot"
        ] = True

        st.info(
            "Shot logging is ready in Live Round. Review the current shot and save it."
        )



def build_live_caddie_player_context(
    bag,
    shots
):
    rows = []

    for club in bag:
        club_name = str(
            club.get(
                "Club",
                ""
            )
            or ""
        ).strip()

        if not club_name:
            continue

        stock_carry = float(
            club.get(
                "Stock Carry",
                0
            )
            or 0
        )

        try:
            learned = unified_club_profile(
                club_name,
                stock_carry,
                shots
            )
        except Exception:
            learned = {
                "carry": stock_carry,
                "sample_count": 0,
                "dominant_miss": club.get(
                    "Miss",
                    ""
                ),
            }

        carry = round(
            float(
                learned.get(
                    "carry",
                    stock_carry
                )
                or stock_carry
            )
        )

        miss = str(
            learned.get(
                "dominant_miss",
                ""
            )
            or club.get(
                "Miss",
                ""
            )
            or ""
        ).strip()

        sample_count = int(
            learned.get(
                "sample_count",
                0
            )
            or 0
        )

        rows.append(
            {
                "club": club_name,
                "carry": carry,
                "miss": miss,
                "samples": sample_count,
            }
        )

    return rows


def current_live_caddie_round_context(
    active_round,
    selected_course
):
    current_hole = int(
        active_round.get(
            "current_hole",
            1
        )
        or 1
    )

    course_name = str(
        active_round.get(
            "course_name",
            ""
        )
        or ""
    ).strip()

    tee_name = str(
        active_round.get(
            "tee",
            ""
        )
        or st.session_state.get(
            "round_start_tee",
            ""
        )
        or ""
    ).strip()

    hole_yardage = None
    hole_record = None

    if selected_course and tee_name:
        try:
            hole_yardage, hole_record = hole_tee_yardage(
                selected_course,
                current_hole,
                tee_name
            )
        except Exception:
            pass

    par = None

    if isinstance(
        hole_record,
        dict
    ):
        try:
            par = int(
                hole_record.get(
                    "par",
                    hole_record.get(
                        "Par"
                    )
                )
            )
        except Exception:
            par = None

    return {
        "course": course_name,
        "hole": current_hole,
        "tee": tee_name,
        "hole_yardage": hole_yardage,
        "par": par,
    }


def hidden_live_shot_context():
    mapping = {
        "distance_yards": "caddie_distance",
        "temperature_f": "caddie_temperature",
        "wind_direction": "caddie_wind_direction",
        "wind_mph": "caddie_wind_strength",
        "surface": "caddie_lie_surface",
        "ball_sitting": "caddie_ball_sitting",
        "slope": "caddie_slope",
        "slope_severity": "caddie_slope_severity",
        "elevation_change_ft": "caddie_elevation",
        "green_firmness": "caddie_green_firmness",
        "pin_position": "caddie_pin_position",
        "main_trouble": "caddie_main_trouble",
        "trouble_location": "caddie_trouble_location",
        "safe_side": "caddie_safe_side",
        "acceptable_miss": "caddie_acceptable_miss",
        "dead_miss": "caddie_dead_miss",
        "hazard_start": "caddie_hazard_start",
        "hazard_clear": "caddie_hazard_clear",
    }

    context = {}

    for output_key, state_key in mapping.items():
        value = st.session_state.get(
            state_key
        )

        if value not in [
            None,
            "",
            "None",
        ]:
            context[
                output_key
            ] = value

    return context


def update_hidden_live_shot_context(
    transcript
):
    parsed = parse_voice_shot_text(
        transcript
    )

    state_map = {
        "distance": "caddie_distance",
        "temperature": "caddie_temperature",
        "wind_direction": "caddie_wind_direction",
        "wind_strength": "caddie_wind_strength",
        "lie_surface": "caddie_lie_surface",
        "ball_sitting": "caddie_ball_sitting",
        "slope": "caddie_slope",
        "slope_severity": "caddie_slope_severity",
        "elevation": "caddie_elevation",
        "green_firmness": "caddie_green_firmness",
        "pin_position": "caddie_pin_position",
        "main_trouble": "caddie_main_trouble",
        "trouble_location": "caddie_trouble_location",
        "safe_side": "caddie_safe_side",
        "acceptable_miss": "caddie_acceptable_miss",
        "dead_miss": "caddie_dead_miss",
        "hazard_start": "caddie_hazard_start",
        "hazard_clear": "caddie_hazard_clear",
    }

    for parsed_key, state_key in state_map.items():
        value = parsed.get(
            parsed_key
        )

        if value not in [
            None,
            "",
        ]:
            st.session_state[
                state_key
            ] = value

    return parsed


def live_caddie_history_text():
    history = st.session_state.get(
        "live_caddie_chat_history",
        []
    )

    lines = []

    for item in history[
        -8:
    ]:
        role = str(
            item.get(
                "role",
                ""
            )
        )

        text = str(
            item.get(
                "text",
                ""
            )
            or ""
        ).strip()

        if text:
            lines.append(
                f"{role}: {text}"
            )

    return "\n".join(
        lines
    )


def ask_openai_live_caddie(
    user_text,
    photo_file,
    round_context,
    player_context,
    shot_context
):
    client, client_error = get_openai_voice_client()

    if client_error:
        return None, client_error

    import base64
    import json

    round_json = json.dumps(
        round_context,
        ensure_ascii=False
    )

    player_json = json.dumps(
        player_context,
        ensure_ascii=False
    )

    shot_json = json.dumps(
        shot_context,
        ensure_ascii=False
    )

    history_text = live_caddie_history_text()

    system_text = (
        "You are My Play, a personal on-course golf caddie. "
        "Act like a concise, conversational caddie, not a form and not a swing instructor. "
        "Use ALL available player evidence supplied to you, including learned club carries, misses, "
        "range/simulator evidence already reflected in the player model, on-course evidence, "
        "round context, current shot context, and any attached photo. "
        "If a photo is attached, use only visible facts such as lie quality, grass depth, slope/stance, "
        "obstructions, bunker/tree/water visibility, and target window. Never invent exact distance, "
        "wind, elevation, hidden hazards, or pin location from the image. "
        "Honor the ongoing conversation: a follow-up such as 'what if I play safe?' modifies the same shot. "
        "When enough information exists, answer directly with: recommended club or shot, adjusted playing distance "
        "when supportable, target/aim, expected miss or risk, and confidence. "
        "If one essential fact is truly missing, ask ONE short follow-up question instead of listing fields. "
        "Do not tell the golfer to open another tab or fill out manual inputs. "
        "Keep normal responses short enough to hear while playing, usually 2-5 sentences."
    )

    user_context = (
        f"ROUND CONTEXT:\n{round_json}\n\n"
        f"PLAYER MODEL:\n{player_json}\n\n"
        f"CURRENT SHOT MEMORY:\n{shot_json}\n\n"
        f"RECENT CADDIE CONVERSATION:\n{history_text or 'None yet.'}\n\n"
        f"GOLFER SAYS:\n{user_text}"
    )

    content = [
        {
            "type": "input_text",
            "text": (
                system_text
                + "\n\n"
                + user_context
            ),
        }
    ]

    if photo_file is not None:
        image_bytes = photo_file.getvalue()

        mime_type = (
            getattr(
                photo_file,
                "type",
                None
            )
            or "image/jpeg"
        )

        encoded = base64.b64encode(
            image_bytes
        ).decode(
            "utf-8"
        )

        content.append(
            {
                "type": "input_image",
                "image_url": (
                    f"data:{mime_type};base64,{encoded}"
                ),
            }
        )

    try:
        response = client.responses.create(
            model="gpt-5.6-luna",
            reasoning={
                "effort": "low"
            },
            input=[
                {
                    "role": "user",
                    "content": content,
                }
            ],
        )

        answer = str(
            response.output_text
            or ""
        ).strip()

        if not answer:
            return None, (
                "My Play did not return a caddie response."
            )

        return answer, None

    except Exception as exc:
        return None, (
            f"Live Caddie could not respond: {exc}"
        )


def render_voice_first_live_caddie():
    try:
        active_round = load_active_round()
    except Exception:
        active_round = None

    if not active_round:
        st.info(
            "Start the round manually first. Once the course, tees, and hole are set, the Caddie takes over."
        )
        return

    selected_course = st.session_state.get(
        "selected_course"
    )

    round_context = current_live_caddie_round_context(
        active_round,
        selected_course
    )

    context_bits = []

    if round_context.get(
        "course"
    ):
        context_bits.append(
            str(
                round_context[
                    "course"
                ]
            )
        )

    context_bits.append(
        f"Hole {round_context['hole']}"
    )

    if round_context.get(
        "par"
    ):
        context_bits.append(
            f"Par {round_context['par']}"
        )

    if round_context.get(
        "tee"
    ):
        context_bits.append(
            f"{round_context['tee']} tees"
        )

    if round_context.get(
        "hole_yardage"
    ) is not None:
        try:
            context_bits.append(
                f"{round(float(round_context['hole_yardage']))} yds"
            )
        except Exception:
            pass

    st.subheader(
        "🎙️ Caddie"
    )

    st.caption(
        " • ".join(
            context_bits
        )
    )

    st.caption(
        "Talk to My Play like a real caddie. You can also take a picture of the lie or target. "
        "It remembers the current shot and your follow-up questions."
    )

    history = st.session_state.get(
        "live_caddie_chat_history",
        []
    )

    for index, item in enumerate(
        history[
            -6:
        ]
    ):
        role = item.get(
            "role"
        )

        text = item.get(
            "text",
            ""
        )

        if role == "Golfer":
            st.markdown(
                f"**You:** {text}"
            )
        else:
            st.markdown(
                f"**Caddie:** {text}"
            )

    photo_file = None

    with st.expander(
        "📷 Add a photo (optional)",
        expanded=False
    ):
        st.caption(
            "Use a photo only when visual context will help your caddie."
        )

        photo_file = st.camera_input(
            "Take a picture of your lie or target",
            key="live_caddie_photo"
        )

        if photo_file is not None:
            st.caption(
                "Photo attached to the next Caddie message."
            )

    live_audio = st.audio_input(
        "Talk to Caddie",
        key="live_caddie_voice_audio"
    )

    if live_audio is not None:
        duration = audio_duration_seconds(
            live_audio
        )

        if duration >= 0:
            st.caption(
                f"Voice: {duration:.1f}s / {int(VOICE_MAX_SECONDS)}s"
            )

        signature = hashlib.sha256(
            live_audio.getvalue()
        ).hexdigest()

        if st.session_state.get(
            "last_live_caddie_signature"
        ) != signature:
            with st.spinner(
                "Listening..."
            ):
                transcript, transcript_error = transcribe_protected_openai_voice(
                    live_audio
                )

            if transcript_error:
                st.error(
                    transcript_error
                )

            elif transcript:
                st.session_state[
                    "last_live_caddie_signature"
                ] = signature

                st.session_state[
                    "live_caddie_pending_text"
                ] = transcript

                st.rerun()

    pending_text = str(
        st.session_state.get(
            "live_caddie_pending_text",
            ""
        )
        or ""
    ).strip()

    if pending_text:
        st.markdown(
            f"**You:** {pending_text}"
        )

        update_hidden_live_shot_context(
            pending_text
        )

        # If distance was not spoken, use verified hole yardage only as
        # broad hole context — never pretend it is current distance to pin.
        player_context = build_live_caddie_player_context(
            bag,
            shots
        )

        shot_context = hidden_live_shot_context()

        with st.spinner(
            "Caddie is thinking..."
        ):
            answer, answer_error = ask_openai_live_caddie(
                pending_text,
                photo_file,
                round_context,
                player_context,
                shot_context
            )

        if answer_error:
            st.error(
                answer_error
            )

        elif answer:
            history = st.session_state.get(
                "live_caddie_chat_history",
                []
            )

            history.append(
                {
                    "role": "Golfer",
                    "text": pending_text,
                }
            )

            history.append(
                {
                    "role": "Caddie",
                    "text": answer,
                }
            )

            st.session_state[
                "live_caddie_chat_history"
            ] = history[
                -12:
            ]

            st.session_state[
                "last_live_caddie_response"
            ] = answer

            st.session_state.pop(
                "live_caddie_pending_text",
                None
            )

            st.success(
                answer
            )

            if st.session_state.get(
                "caddie_talk_back_enabled",
                True
            ):
                speak_in_browser(
                    answer,
                    key="live_caddie_chat_talkback"
                )

            st.rerun()

    control_col1, control_col2 = st.columns(
        2
    )

    with control_col1:
        if st.button(
            "New Shot",
            use_container_width=True,
            key="live_caddie_new_shot"
        ):
            for state_key in [
                "last_live_caddie_signature",
                "live_caddie_pending_text",
                "last_live_caddie_response",
                "live_caddie_photo",
            ]:
                st.session_state.pop(
                    state_key,
                    None
                )

            # Clear shot-specific context but keep conversation available.
            for state_key in [
                "caddie_distance",
                "caddie_wind_direction",
                "caddie_wind_strength",
                "caddie_lie_surface",
                "caddie_ball_sitting",
                "caddie_slope",
                "caddie_slope_severity",
                "caddie_elevation",
                "caddie_green_firmness",
                "caddie_pin_position",
                "caddie_main_trouble",
                "caddie_trouble_location",
                "caddie_safe_side",
                "caddie_acceptable_miss",
                "caddie_dead_miss",
                "caddie_hazard_start",
                "caddie_hazard_clear",
            ]:
                st.session_state.pop(
                    state_key,
                    None
                )

            st.rerun()

    with control_col2:
        if st.button(
            "Clear Caddie Chat",
            use_container_width=True,
            key="live_caddie_clear_chat"
        ):
            for state_key in [
                "live_caddie_chat_history",
                "last_live_caddie_signature",
                "live_caddie_pending_text",
                "last_live_caddie_response",
                "live_caddie_photo",
            ]:
                st.session_state.pop(
                    state_key,
                    None
                )

            st.rerun()




def normalize_imported_club_name(
    value
):
    value = str(
        value or ""
    ).strip()

    if not value:
        return None

    for club in bag:
        club_name = str(
            club.get(
                "Club",
                ""
            )
            or ""
        ).strip()

        if not club_name:
            continue

        if normalize_name(
            club_name
        ) == normalize_name(
            value
        ):
            return club_name

    return value


def append_club_evidence_record(
    club_name,
    carry,
    source,
    total_distance=None,
    offline=None,
    ball_speed=None,
    club_speed=None,
    launch_angle=None,
    spin_rate=None,
    apex=None,
    contact="Solid",
    shot_shape=None,
    note=None
):
    club_name = normalize_imported_club_name(
        club_name
    )

    if not club_name:
        return False, "Club name is required."

    try:
        carry = float(
            carry
        )
    except Exception:
        return False, "Carry must be a number."

    record = {
        "Club": club_name,
        "Carry": carry,
        "Source": source,
        "Contact": contact,
    }

    optional_fields = {
        "Total Distance": total_distance,
        "Offline": offline,
        "Ball Speed": ball_speed,
        "Club Speed": club_speed,
        "Launch Angle": launch_angle,
        "Spin Rate": spin_rate,
        "Apex": apex,
        "Shot Shape": shot_shape,
        "Note": note,
    }

    for key, value in optional_fields.items():
        if value not in [
            None,
            "",
        ]:
            record[
                key
            ] = value

    existing = load_player_evidence()

    existing.append(
        record
    )

    save_player_evidence(
        existing
    )

    return True, (
        f"Added {club_name} evidence: {round(carry)} carry from {source}."
    )


def import_club_evidence_dataframe(
    df,
    source_label
):
    import pandas as pd

    if df is None or df.empty:
        return 0, [
            "No rows were found."
        ]

    normalized_columns = {
        normalize_name(
            column
        ): column
        for column in df.columns
    }

    def find_column(
        aliases
    ):
        for alias in aliases:
            key = normalize_name(
                alias
            )

            if key in normalized_columns:
                return normalized_columns[
                    key
                ]

        return None

    club_col = find_column(
        [
            "club",
            "club name",
            "club type",
            "selected club",
            "equipment",
        ]
    )

    carry_col = find_column(
        [
            "carry",
            "carry distance",
            "carry yards",
            "carry distance yards",
            "carry yd",
            "carry yds",
            "carry (yds)",
            "carry (yards)",
            "distance",
        ]
    )

    if not club_col or not carry_col:
        return 0, [
            "The file needs at least Club and Carry columns."
        ]

    mappings = {
        "total_distance": find_column(
            [
                "total distance",
                "total",
                "total yards",
                "total (yds)",
            ]
        ),
        "offline": find_column(
            [
                "offline",
                "lateral",
                "side",
                "side distance",
                "distance offline",
                "offline (yds)",
            ]
        ),
        "ball_speed": find_column(
            [
                "ball speed",
                "ball speed mph",
                "ball velocity",
            ]
        ),
        "club_speed": find_column(
            [
                "club speed",
                "swing speed",
                "club head speed",
                "clubhead speed",
            ]
        ),
        "launch_angle": find_column(
            [
                "launch angle",
                "launch",
                "vertical launch",
            ]
        ),
        "spin_rate": find_column(
            [
                "spin rate",
                "spin",
                "back spin",
                "backspin",
                "rpm",
            ]
        ),
        "apex": find_column(
            [
                "apex",
                "peak height",
                "max height",
            ]
        ),
        "contact": find_column(
            [
                "contact",
            ]
        ),
        "shot_shape": find_column(
            [
                "shot shape",
                "shape",
            ]
        ),
        "note": find_column(
            [
                "note",
                "notes",
            ]
        ),
    }

    imported = 0
    errors = []

    for row_index, row in df.iterrows():
        club_name = row.get(
            club_col
        )

        carry = row.get(
            carry_col
        )

        if pd.isna(
            club_name
        ) or pd.isna(
            carry
        ):
            continue

        kwargs = {}

        for output_key, column_name in mappings.items():
            if not column_name:
                continue

            value = row.get(
                column_name
            )

            if pd.isna(
                value
            ):
                continue

            kwargs[
                output_key
            ] = value

        success, message = append_club_evidence_record(
            club_name,
            carry,
            source_label,
            **kwargs
        )

        if success:
            imported += 1
        else:
            errors.append(
                f"Row {row_index + 1}: {message}"
            )

    return imported, errors


def extract_club_data_from_photo(
    photo_file
):
    if photo_file is None:
        return None, "Add a photo first."

    import base64
    import json

    client, client_error = get_openai_voice_client()

    if client_error:
        return None, client_error

    mime_type = (
        getattr(
            photo_file,
            "type",
            None
        )
        or "image/jpeg"
    )

    encoded = base64.b64encode(
        photo_file.getvalue()
    ).decode(
        "utf-8"
    )

    prompt = (
        "Extract golf launch-monitor or range club data visible in this image. "
        "Return ONLY valid JSON with a top-level key named rows. "
        "Each row may contain: club, carry, total_distance, offline, ball_speed, "
        "club_speed, launch_angle, spin_rate, apex, shot_shape, contact, note. "
        "Do not invent values. Omit fields that are not visible."
    )

    try:
        response = client.responses.create(
            model="gpt-5.6-luna",
            reasoning={
                "effort": "low"
            },
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": prompt,
                        },
                        {
                            "type": "input_image",
                            "image_url": (
                                f"data:{mime_type};base64,{encoded}"
                            ),
                        },
                    ],
                }
            ],
        )

        raw = str(
            response.output_text
            or ""
        ).strip()

        raw = raw.removeprefix(
            "```json"
        ).removesuffix(
            "```"
        ).strip()

        data = json.loads(
            raw
        )

        rows = data.get(
            "rows",
            []
        )

        if not isinstance(
            rows,
            list
        ):
            return None, "No structured rows were found."

        return rows, None

    except Exception as exc:
        return None, (
            f"Could not extract club data from the photo: {exc}"
        )


def clear_live_round_session_state(
    clear_course=True
):
    """
    Clear UI/session state that can make Live Round appear stuck.
    The persisted active round itself must be cleared separately with
    clear_active_round().
    """
    state_keys = [
        "voice_requested_start_round",
        "voice_requested_end_round",
        "voice_requested_save_shot",
        "round_start_tee",
        "voice_pending_round_start_tee",
        "current_hole",
        "hole_number",
        "live_hole_number",
        "selected_hole",
        "voice_hole_number",
        "voice_hole_par",
        "voice_selected_tee",
        "round_hole_jump",
        "live_last_recommendation",
        "last_spoken_recommendation",
        "live_round_course_results",
        "live_round_course_errors",
        "live_round_course_choice",
        "caddie_running_pending_text",
        "last_caddie_running_voice_signature",
        "last_live_caddie_signature",
        "live_caddie_pending_text",
        "last_live_caddie_response",
        "live_round_cancel_requested",
    ]

    if clear_course:
        # Do not remove selected_course entirely, because startup logic
        # restores COURSE_CACHE_FILE whenever the key is absent.
        st.session_state[
            "selected_course"
        ] = None

        cache_selected_course(
            {}
        )

        state_keys.extend(
            [
                "live_round_course_query",
                "live_round_course_state",
            ]
        )

    for state_key in state_keys:
        st.session_state.pop(
            state_key,
            None
        )



# ============================================================
# CUSTOM COURSE LIBRARY + SCORECARD IMPORT
# ============================================================


COURSE_EVIDENCE_DIR = "course_evidence"


def _image_bytes_and_type(image_file):
    if image_file is None:
        return None, None

    try:
        data = image_file.getvalue()
    except Exception:
        return None, None

    mime_type = (
        getattr(
            image_file,
            "type",
            None
        )
        or "image/jpeg"
    )

    return data, mime_type


def extract_course_from_multiple_scorecard_images(
    image_files,
    course_name="",
    city="",
    state="",
    address="",
    zip_code=""
):
    image_files = [
        image_file
        for image_file in (
            image_files
            or []
        )
        if image_file is not None
    ]

    if len(
        image_files
    ) < 2:
        return None, (
            "At least 2 scorecard images are required for validation."
        )

    client, client_error = get_openai_voice_client()

    if client_error:
        return None, client_error

    import base64

    content = [
        {
            "type": "input_text",
            "text": (
                "You are validating a batch of photographs for one golf course. "
                "The batch should normally include a course identity/cover image plus scorecard images. "
                "Automatically classify each image as identity_cover, front_nine, back_nine, "
                "full_scorecard, or other. Cross-check all images before returning data. "
                "Verify that the course name and address/location shown are consistent with the expected course details. "
                "Do not guess missing values. If the images appear to show different courses, different scorecards, "
                "an inconsistent address/location, or materially conflicting hole/tee data, return JSON with "
                '"valid": false and explain the conflicts in "validation_notes". '
                "If they are consistent, return JSON ONLY using this schema: "
                '{"valid":true,"validation_notes":"","course_name":"","address":"","city":"","state":"","zip":"",'
                '"image_roles":[{"index":1,"role":"identity_cover","confidence":0.95}],'
                '"hole_count":18,"tee_names":["White"],'
                '"holes":[{"hole":1,"par":4,"handicap":12,"yardages":{"White":350}}]}. '
                "The identity/cover image should support the course identity when possible. "
                "Include every tee row that can be confirmed across the images. "
                "Only include yardages/par/handicap values that are clearly visible or cross-confirmed. "
                f"Expected course if visible: {course_name!r}, address={address!r}, "
                f"city={city!r}, state={state!r}, zip={zip_code!r}."
            ),
        }
    ]

    for image_file in image_files:
        data, mime_type = _image_bytes_and_type(
            image_file
        )

        if not data:
            continue

        encoded = base64.b64encode(
            data
        ).decode(
            "utf-8"
        )

        content.append({
            "type": "input_image",
            "image_url": f"data:{mime_type};base64,{encoded}",
        })

    if len(
        content
    ) < 3:
        return None, (
            "My Play could not read enough of the attached images."
        )

    try:
        response = client.responses.create(
            model="gpt-5.6-luna",
            reasoning={
                "effort": "low"
            },
            input=[
                {
                    "role": "user",
                    "content": content,
                }
            ],
        )

        raw = str(
            response.output_text
            or ""
        ).strip()

        raw = raw.removeprefix(
            "```json"
        ).removesuffix(
            "```"
        ).strip()

        payload = json.loads(
            raw
        )

        if not isinstance(
            payload,
            dict
        ):
            return None, (
                "The scorecard validation response was not structured data."
            )

        if payload.get(
            "valid"
        ) is False:
            return None, (
                "My Play could not verify these images as one consistent scorecard. "
                + str(
                    payload.get(
                        "validation_notes",
                        ""
                    )
                    or ""
                )
            )

        payload[
            "course_name"
        ] = str(
            payload.get(
                "course_name",
                course_name
            )
            or course_name
            or ""
        ).strip()

        payload[
            "city"
        ] = str(
            payload.get(
                "city",
                city
            )
            or city
            or ""
        ).strip()

        payload[
            "state"
        ] = str(
            payload.get(
                "state",
                state
            )
            or state
            or ""
        ).strip()

        payload[
            "address"
        ] = str(
            payload.get(
                "address",
                address
            )
            or address
            or ""
        ).strip()

        payload[
            "zip"
        ] = str(
            payload.get(
                "zip",
                zip_code
            )
            or zip_code
            or ""
        ).strip()

        payload[
            "verification_status"
        ] = "Provisional"

        payload[
            "evidence_image_count"
        ] = len(
            image_files
        )

        return payload, None

    except Exception as exc:
        return None, (
            f"Could not validate the scorecard images: {exc}"
        )


def save_course_validation_submission(
    course_record,
    image_files,
    status="Provisional"
):
    os.makedirs(
        COURSE_EVIDENCE_DIR,
        exist_ok=True
    )

    submission_id = str(
        uuid.uuid4()
    )

    saved_images = []

    for index, image_file in enumerate(
        image_files
        or [],
        start=1
    ):
        data, mime_type = _image_bytes_and_type(
            image_file
        )

        if not data:
            continue

        extension = ".jpg"

        if "png" in str(
            mime_type
        ).lower():
            extension = ".png"

        elif "webp" in str(
            mime_type
        ).lower():
            extension = ".webp"

        filename = (
            submission_id
            + "_"
            + str(
                index
            )
            + extension
        )

        path = Path(
            COURSE_EVIDENCE_DIR
        ) / filename

        path.write_bytes(
            data
        )

        saved_images.append(
            str(
                path
            )
        )

    submissions = load_course_submissions()

    submissions.append({
        "submission_id": submission_id,
        "saved_at": datetime.now().isoformat(),
        "user_id": st.session_state.get(
            "supabase_user_id",
            ""
        ),
        "user_email": st.session_state.get(
            "supabase_user_email",
            ""
        ),
        "course_id": course_record.get(
            "id",
            ""
        ),
        "course_name": result_name(
            course_record.get(
                "search_result",
                course_record
            )
        ),
        "status": status,
        "verification_method": "multi_image_scorecard",
        "image_count": len(
            saved_images
        ),
        "image_paths": saved_images,
    })

    save_course_submissions(
        submissions
    )



def clear_course_builder_state():
    for state_key in [
        "course_builder_method",
        "course_builder_par_rows",
        "course_builder_yard_rows",
        "course_builder_par_editor",
        "course_builder_yard_editor",
        "course_builder_course_name",
        "course_builder_city",
        "course_builder_state",
        "course_builder_tee_names",
        "course_builder_hole_count",
        "course_builder_manual_hole_count",
        "course_builder_manual_tees",
        "course_builder_scorecard_camera",
        "course_builder_scorecard_upload",
    ]:
        st.session_state.pop(
            state_key,
            None
        )



def load_custom_course_library():
    data = load_json(
        CUSTOM_COURSE_LIBRARY_FILE,
        []
    )

    return data if isinstance(data, list) else []


def save_custom_course_library(rows):
    save_json(
        CUSTOM_COURSE_LIBRARY_FILE,
        rows
    )


def load_course_submissions():
    data = load_json(
        COURSE_SUBMISSION_FILE,
        []
    )

    return data if isinstance(data, list) else []


def save_course_submissions(rows):
    save_json(
        COURSE_SUBMISSION_FILE,
        rows
    )


def course_search_key(name, city="", state=""):
    return "|".join(
        [
            normalize_name(name),
            normalize_name(city),
            normalize_name(state),
        ]
    )


def build_blank_course_payload(
    course_name="",
    city="",
    state="",
    hole_count=18,
    tee_names=None
):
    tee_names = tee_names or [
        "Blue",
        "White",
    ]

    tee_names = [
        str(name).strip()
        for name in tee_names
        if str(name).strip()
    ]

    if not tee_names:
        tee_names = [
            "Default",
        ]

    holes = []

    for hole_number in range(
        1,
        int(hole_count) + 1
    ):
        yardages = {}

        for tee_name in tee_names:
            yardages[
                tee_name
            ] = None

        holes.append({
            "hole": hole_number,
            "par": 4,
            "handicap": None,
            "yardages": yardages,
        })

    return {
        "course_name": str(course_name or "").strip(),
        "city": str(city or "").strip(),
        "state": str(state or "").strip(),
        "hole_count": int(hole_count),
        "tee_names": tee_names,
        "holes": holes,
    }


def initialize_course_builder_state(payload):
    payload = payload or {}

    course_name = str(
        payload.get(
            "course_name",
            ""
        )
        or ""
    ).strip()

    city = str(
        payload.get(
            "city",
            ""
        )
        or ""
    ).strip()

    state = str(
        payload.get(
            "state",
            ""
        )
        or ""
    ).strip()

    holes = payload.get(
        "holes",
        []
    ) or []

    tee_names = payload.get(
        "tee_names",
        []
    ) or []

    if not tee_names and holes:
        discovered = []

        for hole in holes:
            for tee_name in (
                hole.get(
                    "yardages",
                    {}
                )
                or {}
            ).keys():
                tee_name = str(
                    tee_name or ""
                ).strip()

                if tee_name and tee_name not in discovered:
                    discovered.append(
                        tee_name
                    )

        tee_names = discovered

    if not tee_names:
        tee_names = [
            "Default",
        ]

    if not holes:
        holes = build_blank_course_payload(
            course_name,
            city,
            state,
            int(
                payload.get(
                    "hole_count",
                    18
                )
                or 18
            ),
            tee_names
        ).get(
            "holes",
            []
        )

    st.session_state[
        "course_builder_course_name"
    ] = course_name
    st.session_state[
        "course_builder_city"
    ] = city
    st.session_state[
        "course_builder_state"
    ] = state
    st.session_state[
        "course_builder_hole_count"
    ] = int(
        payload.get(
            "hole_count",
            len(holes) or 18
        )
        or 18
    )
    st.session_state[
        "course_builder_tee_names"
    ] = ", ".join(
        tee_names
    )

    par_rows = []
    yard_rows = []

    for hole in holes:
        hole_number = int(
            hole.get(
                "hole",
                len(par_rows) + 1
            )
            or len(par_rows) + 1
        )

        par_rows.append({
            "Hole": hole_number,
            "Par": hole.get(
                "par",
                4
            ),
            "Handicap": hole.get(
                "handicap",
                None
            ),
        })

        yard_row = {
            "Hole": hole_number,
        }

        yardages = hole.get(
            "yardages",
            {}
        ) or {}

        for tee_name in tee_names:
            yard_row[
                tee_name
            ] = yardages.get(
                tee_name,
                None
            )

        yard_rows.append(
            yard_row
        )

    st.session_state[
        "course_builder_par_rows"
    ] = par_rows
    st.session_state[
        "course_builder_yard_rows"
    ] = yard_rows


def build_course_payload_from_builder_state():
    course_name = str(
        st.session_state.get(
            "course_builder_course_name",
            ""
        )
        or ""
    ).strip()

    city = str(
        st.session_state.get(
            "course_builder_city",
            ""
        )
        or ""
    ).strip()

    state = str(
        st.session_state.get(
            "course_builder_state",
            ""
        )
        or ""
    ).strip()

    hole_count = int(
        st.session_state.get(
            "course_builder_hole_count",
            18
        )
        or 18
    )

    tee_names = [
        str(name).strip()
        for name in str(
            st.session_state.get(
                "course_builder_tee_names",
                ""
            )
            or ""
        ).split(",")
        if str(name).strip()
    ]

    if not tee_names:
        tee_names = [
            "Default",
        ]

    par_rows = st.session_state.get(
        "course_builder_par_rows",
        []
    )

    yard_rows = st.session_state.get(
        "course_builder_yard_rows",
        []
    )

    holes = []

    for idx in range(
        hole_count
    ):
        par_row = (
            par_rows[idx]
            if idx < len(par_rows)
            else {}
        )

        yard_row = (
            yard_rows[idx]
            if idx < len(yard_rows)
            else {}
        )

        hole_number = int(
            par_row.get(
                "Hole",
                idx + 1
            )
            or idx + 1
        )

        hole = {
            "hole": hole_number,
            "number": hole_number,
            "par": par_row.get(
                "Par",
                4
            ),
            "handicap": par_row.get(
                "Handicap",
                None
            ),
            "yardages": {},
            "tees": {},
        }

        for tee_name in tee_names:
            value = yard_row.get(
                tee_name,
                None
            )

            if value in [
                "",
                None,
            ]:
                yardage = None
            else:
                try:
                    yardage = int(
                        float(value)
                    )
                except Exception:
                    yardage = None

            hole[
                "yardages"
            ][
                tee_name
            ] = yardage
            hole[
                "tees"
            ][
                tee_name
            ] = yardage

        holes.append(
            hole
        )

    return {
        "course_name": course_name,
        "city": city,
        "state": state,
        "hole_count": hole_count,
        "tee_names": tee_names,
        "holes": holes,
    }


def course_payload_to_record(
    payload,
    source_label="My Play Course Library"
):
    course_name = str(
        payload.get(
            "course_name",
            ""
        )
        or ""
    ).strip()

    city = str(
        payload.get(
            "city",
            ""
        )
        or ""
    ).strip()

    state = str(
        payload.get(
            "state",
            ""
        )
        or ""
    ).strip()

    holes = payload.get(
        "holes",
        []
    ) or []

    tee_names = payload.get(
        "tee_names",
        []
    ) or []

    tee_rows = []

    for tee_name in tee_names:
        total = 0
        has_any = False
        tee_holes = []

        for hole in holes:
            hole_number = int(
                hole.get(
                    "hole",
                    hole.get(
                        "number",
                        0
                    )
                    or 0
                )
                or 0
            )

            yardage = (
                (hole.get("yardages") or {}).get(tee_name)
                if isinstance(hole, dict)
                else None
            )

            try:
                yardage_num = int(
                    float(yardage)
                )
            except Exception:
                yardage_num = None

            if yardage_num is not None:
                total += yardage_num
                has_any = True

            tee_holes.append({
                "hole": hole_number,
                "yardage": yardage_num,
            })

        tee_rows.append({
            "name": tee_name,
            "tee_name": tee_name,
            "yardage": total if has_any else None,
            "holes": tee_holes,
        })

    record_id = (
        "custom:"
        + course_search_key(
            course_name,
            city,
            state
        )
    )

    search_result = {
        "id": record_id,
        "name": course_name,
        "course_name": course_name,
        "city": city,
        "state": state,
        "source": source_label,
    }

    return {
        "id": record_id,
        "source": source_label,
        "search_result": search_result,
        "detail": {
            "name": course_name,
            "city": city,
            "state": state,
            "source": source_label,
        },
        "holes": {
            "holes": holes,
        },
        "tees": {
            "tees": tee_rows,
        },
        "climate": {},
        "osm_features": {},
        "loaded_at": datetime.now().isoformat(),
    }


def course_has_playable_data(course_record):
    try:
        tee_rows = normalize_tees(
            course_record.get(
                "tees",
                {}
            )
        )
    except Exception:
        tee_rows = []

    try:
        holes = extract_course_holes(
            course_record
        )
    except Exception:
        holes = []

    return bool(tee_rows) and bool(holes)


def search_custom_courses(
    query,
    state=""
):
    rows = load_custom_course_library()
    results = []
    query_norm = normalize_name(query)
    state_norm = normalize_name(state)
    zip_query = str(query or "").strip()

    for item in rows:
        if not isinstance(item, dict):
            continue

        name = result_name(item)
        city = str(
            item.get(
                "search_result",
                {}
            ).get(
                "city",
                ""
            )
            or item.get(
                "city",
                ""
            )
            or ""
        ).strip()
        item_state = str(
            item.get(
                "search_result",
                {}
            ).get(
                "state",
                ""
            )
            or item.get(
                "state",
                ""
            )
            or ""
        ).strip()
        postal = str(
            item.get(
                "search_result",
                {}
            ).get(
                "zip",
                ""
            )
            or item.get(
                "zip",
                ""
            )
            or ""
        ).strip()

        haystack = " ".join(
            [
                normalize_name(name),
                normalize_name(city),
                normalize_name(item_state),
                normalize_name(postal),
            ]
        ).strip()

        if state_norm and normalize_name(item_state) != state_norm:
            continue

        if query_norm:
            if query_norm not in haystack:
                continue
        elif zip_query:
            if zip_query != postal:
                continue

        results.append(
            item
        )

    return results


def save_course_record_to_library(
    course_record,
    contributor_email=""
):
    library = load_custom_course_library()
    submissions = load_course_submissions()

    key = course_search_key(
        result_name(
            course_record.get(
                "search_result",
                course_record
            )
        ),
        str(
            course_record.get(
                "search_result",
                {}
            ).get(
                "city",
                ""
            )
            or ""
        ),
        str(
            course_record.get(
                "search_result",
                {}
            ).get(
                "state",
                ""
            )
            or ""
        ),
    )

    updated = False

    for idx, existing in enumerate(
        library
    ):
        existing_key = course_search_key(
            result_name(
                existing.get(
                    "search_result",
                    existing
                )
            ),
            str(
                existing.get(
                    "search_result",
                    {}
                ).get(
                    "city",
                    ""
                )
                or ""
            ),
            str(
                existing.get(
                    "search_result",
                    {}
                ).get(
                    "state",
                    ""
                )
                or ""
            ),
        )

        if existing_key == key:
            library[idx] = course_record
            updated = True
            break

    if not updated:
        library.append(
            course_record
        )

    submissions.append({
        "saved_at": datetime.now().isoformat(),
        "contributor_email": contributor_email,
        "course_id": course_record.get(
            "id",
            ""
        ),
        "course_name": result_name(
            course_record.get(
                "search_result",
                course_record
            )
        ),
        "city": str(
            course_record.get(
                "search_result",
                {}
            ).get(
                "city",
                ""
            )
            or ""
        ),
        "state": str(
            course_record.get(
                "search_result",
                {}
            ).get(
                "state",
                ""
            )
            or ""
        ),
    })

    save_custom_course_library(
        library
    )
    save_course_submissions(
        submissions
    )


def extract_course_from_scorecard_image(
    image_file,
    course_name="",
    city="",
    state=""
):
    if image_file is None:
        return None, "Add a scorecard photo first."

    client, client_error = get_openai_voice_client()

    if client_error:
        return None, client_error

    import base64

    mime_type = (
        getattr(
            image_file,
            "type",
            None
        )
        or "image/jpeg"
    )

    encoded = base64.b64encode(
        image_file.getvalue()
    ).decode(
        "utf-8"
    )

    prompt = (
        "Read this golf scorecard and return ONLY valid JSON. "
        "Use this schema: "
        '{"course_name":"","city":"","state":"","hole_count":18,'
        '"tee_names":["White"],"holes":[{"hole":1,"par":4,"handicap":12,'
        '"yardages":{"White":350}}]}. '
        "If a field is not visible, leave it blank or null. "
        "Include every visible tee row and each hole's par, handicap, and yardage by tee. "
        f"Prefer these defaults when visible or partially visible: course_name={course_name!r}, city={city!r}, state={state!r}."
    )

    try:
        response = client.responses.create(
            model="gpt-5.6-luna",
            reasoning={
                "effort": "low"
            },
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": prompt,
                        },
                        {
                            "type": "input_image",
                            "image_url": f"data:{mime_type};base64,{encoded}",
                        },
                    ],
                }
            ],
        )

        raw = str(
            response.output_text
            or ""
        ).strip()
        raw = raw.removeprefix(
            "```json"
        ).removesuffix(
            "```"
        ).strip()

        payload = json.loads(
            raw
        )

        if not isinstance(payload, dict):
            return None, "The extracted scorecard was not valid structured data."

        payload["course_name"] = str(
            payload.get(
                "course_name",
                course_name
            )
            or course_name
            or ""
        ).strip()
        payload["city"] = str(
            payload.get(
                "city",
                city
            )
            or city
            or ""
        ).strip()
        payload["state"] = str(
            payload.get(
                "state",
                state
            )
            or state
            or ""
        ).strip()

        tee_names = payload.get(
            "tee_names",
            []
        ) or []

        if not tee_names and isinstance(
            payload.get(
                "holes",
                []
            ),
            list
        ):
            discovered = []
            for hole in payload.get(
                "holes",
                []
            ):
                for tee_name in (hole.get("yardages") or {}).keys():
                    tee_name = str(
                        tee_name or ""
                    ).strip()
                    if tee_name and tee_name not in discovered:
                        discovered.append(
                            tee_name
                        )
            tee_names = discovered

        payload["tee_names"] = tee_names or [
            "Default",
        ]
        payload["hole_count"] = int(
            payload.get(
                "hole_count",
                len(
                    payload.get(
                        "holes",
                        []
                    )
                )
                or 18
            )
            or 18
        )

        return payload, None

    except Exception as exc:
        return None, f"Could not read the scorecard photo: {exc}"


def render_course_builder_for_selected_course(selected_course):
    search_result = selected_course.get(
        "search_result",
        {}
    ) if isinstance(selected_course, dict) else {}

    default_name = result_name(
        search_result or selected_course
    )
    default_city = str(
        search_result.get(
            "city",
            ""
        )
        or selected_course.get(
            "city",
            ""
        )
        or ""
    ).strip() if isinstance(selected_course, dict) else ""
    default_state = str(
        search_result.get(
            "state",
            ""
        )
        or selected_course.get(
            "state",
            ""
        )
        or ""
    ).strip() if isinstance(selected_course, dict) else ""

    st.warning(
        "This course does not have enough tee / hole data yet. Add a scorecard or build the course manually so My Play can use it now and remember it for future rounds."
    )

    method = st.session_state.get(
        "course_builder_method",
        "Manual Entry"
    )

    if method == "Scorecard Image":
        st.caption(
            "Upload a scorecard image, or optionally open the camera if you want to take one now. My Play will extract the holes and tees and let you review everything before saving."
        )

        uploaded_scorecard = st.file_uploader(
            "Upload a scorecard image",
            type=[
                "png",
                "jpg",
                "jpeg",
                "webp",
            ],
            key="course_builder_scorecard_upload"
        )

        scorecard_photo = None

        with st.expander(
            "📷 Use camera instead (optional)",
            expanded=False
        ):
            scorecard_photo = st.camera_input(
                "Take a scorecard picture",
                key="course_builder_scorecard_camera"
            )

        active_image = uploaded_scorecard or scorecard_photo

        if st.button(
            "Read Scorecard",
            type="primary",
            use_container_width=True,
            key="course_builder_read_scorecard"
        ):
            with st.spinner(
                "Reading the scorecard..."
            ):
                payload, error = extract_course_from_scorecard_image(
                    active_image,
                    default_name,
                    default_city,
                    default_state
                )

            if error:
                st.error(
                    error
                )
            else:
                initialize_course_builder_state(
                    payload
                )
                st.success(
                    "Scorecard captured. Review the extracted course data below before saving."
                )
                st.rerun()

    else:
        st.caption(
            "Enter the number of holes and tee names, then confirm. My Play will open the editable hole-by-hole course sheet next."
        )

        manual_col1, manual_col2 = st.columns(
            2
        )

        with manual_col1:
            manual_hole_count = st.selectbox(
                "Number of holes",
                [9, 18],
                index=1,
                key="course_builder_manual_hole_count"
            )

        with manual_col2:
            manual_tee_names = st.text_input(
                "Tee names (comma separated)",
                value="Blue, White",
                key="course_builder_manual_tees"
            )

        if st.button(
            "Confirm Tee Setup & Continue",
            type="primary",
            use_container_width=True,
            key="course_builder_create_manual"
        ):
            initialize_course_builder_state(
                build_blank_course_payload(
                    default_name,
                    default_city,
                    default_state,
                    manual_hole_count,
                    [
                        name.strip()
                        for name in manual_tee_names.split(",")
                        if name.strip()
                    ]
                )
            )
            st.rerun()

    if st.session_state.get(
        "course_builder_par_rows"
    ) and st.session_state.get(
        "course_builder_yard_rows"
    ):
        st.divider()
        st.subheader(
            "Review Course Data"
        )

        meta_col1, meta_col2, meta_col3 = st.columns(
            3
        )

        with meta_col1:
            st.text_input(
                "Course Name",
                key="course_builder_course_name"
            )

        with meta_col2:
            st.text_input(
                "City",
                key="course_builder_city"
            )

        with meta_col3:
            st.text_input(
                "State",
                key="course_builder_state"
            )

        st.text_input(
            "Tee Names (comma separated)",
            key="course_builder_tee_names"
        )

        par_editor_default = pd.DataFrame(
            st.session_state.get(
                "course_builder_par_rows",
                []
            )
        )

        yard_editor_default = pd.DataFrame(
            st.session_state.get(
                "course_builder_yard_rows",
                []
            )
        )

        st.markdown(
            "#### Par / Handicap"
        )
        edited_par_df = st.data_editor(
            par_editor_default,
            use_container_width=True,
            hide_index=True,
            num_rows="fixed",
            key="course_builder_par_editor"
        )

        st.session_state[
            "course_builder_par_rows"
        ] = edited_par_df.to_dict(
            orient="records"
        )

        st.markdown(
            "#### Yardage by Tee"
        )
        edited_yard_df = st.data_editor(
            yard_editor_default,
            use_container_width=True,
            hide_index=True,
            num_rows="fixed",
            key="course_builder_yard_editor"
        )

        st.session_state[
            "course_builder_yard_rows"
        ] = edited_yard_df.to_dict(
            orient="records"
        )

        save_col1, save_col2 = st.columns(
            2
        )

        with save_col1:
            if st.button(
                "Save Course to My Play",
                type="primary",
                use_container_width=True,
                key="course_builder_save_course"
            ):
                payload = build_course_payload_from_builder_state()

                if not payload.get(
                    "course_name"
                ):
                    st.error(
                        "Course name is required before saving."
                    )
                else:
                    record = course_payload_to_record(
                        payload,
                        "My Play Course Library"
                    )

                    save_course_record_to_library(
                        record,
                        st.session_state.get(
                            "supabase_email",
                            ""
                        )
                    )

                    st.session_state[
                        "selected_course"
                    ] = record
                    cache_selected_course(
                        record
                    )

                    st.session_state.pop(
                        "course_builder_par_rows",
                        None
                    )
                    st.session_state.pop(
                        "course_builder_yard_rows",
                        None
                    )

                    st.success(
                        "Course saved. My Play will now use this course data in Live Round and remember it for future searches."
                    )
                    st.rerun()

        with save_col2:
            if st.button(
                "Clear Draft",
                use_container_width=True,
                key="course_builder_clear"
            ):
                clear_course_builder_state()

                st.rerun()

# ============================================================
# NEW GOLFER ONBOARDING
# ============================================================

if not bag:
    st.header(
        "👋 Welcome to My Play"
    )

    st.write(
        "This is a new golfer account. Add your first club to start building "
        "your personal caddie profile."
    )

    st.caption(
        "You can add the rest of the bag immediately afterward in My Bag."
    )

    first_category = st.selectbox(
        "1. Club category",
        list(CLUB_CATALOG.keys()),
        key="onboarding_club_category",
    )
    first_club_name = st.selectbox(
        "2. Exact club",
        CLUB_CATALOG[first_category],
        key="onboarding_club_name",
    )
    first_brand = st.selectbox(
        "3. Brand",
        CLUB_BRANDS,
        index=CLUB_BRANDS.index("Callaway"),
        key="onboarding_club_brand",
    )
    first_model_choices = model_choices_for(first_brand, first_category)
    first_model = st.selectbox(
        "4. Model",
        first_model_choices,
        index=first_model_choices.index("Model unknown"),
        key="onboarding_club_model_choice",
    )
    if first_model == "Other / Model not listed":
        first_model = st.text_input(
            "Enter model",
            placeholder="Type the model only when it is not listed",
            key="onboarding_club_custom_model",
        ).strip()
    detail_col1, detail_col2 = st.columns(2)
    with detail_col1:
        first_loft = st.number_input(
            "Loft (optional)", min_value=0.0, max_value=80.0,
            value=None, step=0.5, key="onboarding_club_loft",
        )
        first_carry = st.number_input(
            "Normal carry (yards)", min_value=1, max_value=400,
            value=200, step=1, key="onboarding_club_carry",
        )
    with detail_col2:
        first_miss = st.selectbox(
            "Typical miss", TYPICAL_MISSES, key="onboarding_club_miss"
        )
        first_confidence = st.selectbox(
            "Confidence", CONFIDENCE_LEVELS, index=1,
            key="onboarding_club_confidence",
        )
    first_shape = st.selectbox(
        "Normal shot shape", SHOT_SHAPES, key="onboarding_club_shape"
    )
    save_first_club = st.button(
        "Add First Club", type="primary", use_container_width=True,
        key="onboarding_save_first_club",
    )

    if save_first_club:
        first_club = build_club_record(
            first_category, first_club_name, first_brand, first_model.strip(),
            first_loft, first_carry, first_miss, first_shape, first_confidence,
        )
        save_json(BAG_FILE, [first_club])
        st.success(f"{first_club_name} added to your My Play account.")
        st.rerun()

    st.info(
        "Once your first club is saved, the full My Play tabs will unlock."
    )

    st.stop()


tab_round, tab_voice_command, tab_player = st.tabs(
    ["Live Round", "Caddie", "My Player"]
)

with tab_player:
    (
        tab_player_home,
        tab_bag,
        tab_game,
        tab_club_analytics,
        tab_history,
        tab_swing_video,
        tab_data,
    ) = st.tabs(
        [
            "Profile", "My Bag", "Preferences", "Club Analytics",
            "Round Biographies", "Swing Video", "Data Uploads",
        ]
    )

with tab_player_home:
    player_name = str(profile.get("display_name", "") or "").strip() or "Golfer"
    safe_player_name = html.escape(player_name)
    player_rounds = load_round_history()
    snapshot = player_snapshot(player_rounds, all_player_evidence)
    learned_insights = learned_profile_insights(all_player_evidence)
    endurance_summary = endurance_phase_table(all_player_evidence)
    training_plan = recommended_training(
        learned_insights, endurance_summary, all_player_evidence
    )
    hand_label = html.escape(str(profile.get("handedness", "Right-handed")))
    experience_label = html.escape(str(profile.get("experience_level", "Developing")))
    st.markdown(
        f"""
        <div class="myplay-profile-banner">
            <div class="myplay-eyebrow">MY PLAYER</div>
            <h2>{safe_player_name}</h2>
            <p>{hand_label} · {experience_label} golfer · Profile confidence: {snapshot['confidence']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    overview_col1, overview_col2, overview_col3, overview_col4 = st.columns(4)
    with overview_col1:
        st.metric("Rounds", snapshot["rounds"])
    with overview_col2:
        st.metric(
            "Average score",
            f"{snapshot['average_score']:.1f}" if snapshot["average_score"] is not None else "Need rounds",
        )
    with overview_col3:
        st.metric(
            "Best score",
            snapshot["best_score"] if snapshot["best_score"] is not None else "Need rounds",
        )
    with overview_col4:
        st.metric("Shots learned", snapshot["shots"])

    with st.expander("Your game right now", expanded=True):
        st.markdown(
            f"""
            <div class="myplay-insight"><strong>Primary learned tendency</strong><span>{html.escape(learned_insights['primary_tendency'])} · {learned_insights['primary_count']} supporting shots</span></div>
            <div class="myplay-insight"><strong>Most repeatable recorded club</strong><span>{html.escape(learned_insights['reliable_club'])} · {learned_insights['reliable_club_count']} comparable shots</span></div>
            <div class="myplay-insight"><strong>Preferred scoring leave</strong><span>{int(profile.get('preferred_scoring_leave', 100) or 100)} yards · used by the caddie for layup decisions</span></div>
            """,
            unsafe_allow_html=True,
        )

    with st.expander(
        f"Recommended Training · {training_plan['title']} · {training_plan['time']}",
        expanded=True,
    ):
        st.write(training_plan["summary"])
        t1, t2, t3 = st.columns(3)
        t1.metric("Time", training_plan["time"])
        t2.metric("Location", training_plan["location"])
        t3.metric("Clubs", training_plan["clubs"])
        st.caption(f"Why My Play selected this: {training_plan['reason']}")
        for step_number, step in enumerate(training_plan["steps"], start=1):
            st.write(f"{step_number}. {step}")
        if training_plan.get("source_url"):
            st.markdown(
                f"[{training_plan['source_label']}]({training_plan['source_url']})"
            )
        else:
            st.caption(training_plan["source_label"])

    with st.expander("Endurance pattern", expanded=False):
        if endurance_summary.empty:
            st.info(
                "Finish rounds with shot data connected to the round. My Play will compare "
                "shots 1–20, 21–40, 41–60 and 61+ without treating club choice as fatigue."
            )
        else:
            st.dataframe(endurance_summary, use_container_width=True, hide_index=True)
            st.caption(
                "Observed performance pattern only—not a medical or physical diagnosis."
            )

    with st.expander("Recent Round Biographies", expanded=False):
        if player_rounds.empty:
            st.info("Complete a round to create your first Round Biography.")
        else:
            for _, biography_round in player_rounds.head(3).iterrows():
                biography = build_round_biography(
                    biography_round, all_player_evidence, player_rounds
                )
                st.markdown(f"**{biography['title']}**")
                st.write(biography["story"])
                st.divider()

    with st.expander("Bag snapshot", expanded=False):
        bag_col1, bag_col2, bag_col3 = st.columns(3)
        bag_col1.metric("Clubs", len(bag))
        bag_col2.metric("Evidence", snapshot["shots"])
        bag_col3.metric("Profile confidence", snapshot["confidence"])
        st.caption("Open My Bag to add or edit a club. Open Club Analytics for detailed numbers.")

    with st.expander("Ask My Caddie", expanded=False):
        st.write(
            f"Welcome back, {player_name}. Ask about your latest pattern, a club, "
            "a completed round, or why My Play selected your recommended training."
        )
        st.caption("The full conversational caddie is available from the main Caddie tab.")



# ============================================================
# STRATEGY ENGINE
# ============================================================

def shot_type_from_context(
    distance_to_target,
    surface,
    trouble_type,
    current_hole_yardage=None,
    shot_number=None
):
    distance_to_target = float(
        distance_to_target
    )

    if surface == "Recovery":
        return "Recovery"

    if surface in (
        "Greenside Bunker",
        "Fairway Bunker"
    ):
        return (
            "Recovery"
            if surface == "Fairway Bunker"
            and distance_to_target > 170
            else "Approach"
        )

    if shot_number == 1:
        return "Tee Shot"

    if (
        current_hole_yardage is not None
        and distance_to_target >= max(
            220,
            float(
                current_hole_yardage
            ) * 0.55
        )
    ):
        return "Tee Shot"

    if distance_to_target <= 60:
        return "Scoring Shot"

    if distance_to_target <= 220:
        return "Approach"

    return "Layup / Position"

def dispersion_aim_offset(
    dispersion
):
    """
    Positive = aim right.
    Negative = aim left.

    A golfer missing left needs a rightward target correction.
    A golfer missing right needs a leftward target correction.
    """
    if dispersion.get(
        "sample_count",
        0
    ) < 5:
        return 0.0

    left_rate = float(
        dispersion.get(
            "left_rate",
            0
        )
    )

    right_rate = float(
        dispersion.get(
            "right_rate",
            0
        )
    )

    diff = left_rate - right_rate

    if diff >= 0.15:
        return min(
            3.0,
            1.0 + diff * 5
        )

    if diff <= -0.15:
        return max(
            -3.0,
            -1.0 + diff * 5
        )

    return 0.0

def stock_miss_aim_offset(
    handedness,
    player_miss
):
    """
    Positive = aim right.
    Negative = aim left.
    This is compensation for a stock miss, not the direction the ball tends to travel.
    """
    miss = str(
        player_miss
    ).lower()

    offset = 0.0

    if handedness == "Right-handed":
        if "pull" in miss or "left" in miss:
            offset += 1.5
        if "fade" in miss or "right" in miss:
            offset -= 1.0
    else:
        if "pull" in miss or "right" in miss:
            offset -= 1.5
        if "fade" in miss or "left" in miss:
            offset += 1.0

    return offset

def sidehill_aim_offset(
    handedness,
    stance,
    severity
):
    sev = {
        "Slight": 1.0,
        "Moderate": 2.0,
        "Severe": 3.0
    }.get(
        severity,
        1.0
    )

    if stance == "Ball Above Feet":
        return (
            1.0 * sev
            if handedness == "Right-handed"
            else -1.0 * sev
        )

    if stance == "Ball Below Feet":
        return (
            -1.0 * sev
            if handedness == "Right-handed"
            else 1.0 * sev
        )

    return 0.0

def wind_aim_offset(
    wind_relation,
    wind_speed
):
    weight = min(
        float(
            wind_speed
        ) / 8.0,
        2.5
    )

    if wind_relation == "Left to Right":
        return -weight

    if wind_relation == "Right to Left":
        return weight

    return 0.0

def hazard_aim_offset(
    trouble_type,
    trouble_location,
    safe_side
):
    catastrophic = trouble_type in (
        "Water",
        "OB",
        "Penalty Area"
    )

    moderate = trouble_type in (
        "Bunker",
        "Trees"
    )

    weight = (
        6.0
        if catastrophic
        else 3.5
        if moderate
        else 0.0
    )

    offset = 0.0

    if trouble_type != "None":
        if trouble_location == "Left":
            offset += weight
        elif trouble_location == "Right":
            offset -= weight

    if safe_side == "Right":
        offset += 1.5
    elif safe_side == "Left":
        offset -= 1.5

    return offset, catastrophic

def aim_label_from_offset(
    offset
):
    if offset >= 6:
        return "right side"
    if offset >= 2.5:
        return "center-right"
    if offset <= -6:
        return "left side"
    if offset <= -2.5:
        return "center-left"
    return "center"

def club_options_with_learning(
    bag,
    shots
):
    rows = []

    for club in bag:
        learned_carry, count = learned_carry_for_club(
            club["Club"],
            float(
                club.get(
                    "Stock Carry",
                    0
                )
            ),
            shots
        )

        dispersion = learned_dispersion_for_club(
            club["Club"],
            shots
        )

        rows.append({
            "club": club,
            "carry": learned_carry,
            "sample_count": count,
            "dispersion": dispersion
        })

    return sorted(
        rows,
        key=lambda x: x["carry"]
    )

def choose_tee_club(
    bag,
    shots,
    target_distance,
    trouble_type,
    trouble_location,
    safe_side
):
    options = club_options_with_learning(
        bag,
        shots
    )

    long_options = [
        x
        for x in options
        if x["club"]["Club"] in (
            "Driver",
            "3 Wood",
            "3 Hybrid"
        )
    ]

    if not long_options:
        return choose_club(
            bag,
            shots,
            target_distance
        )

    catastrophic = trouble_type in (
        "Water",
        "OB",
        "Penalty Area"
    )

    # Default to longest useful club.
    selected = max(
        long_options,
        key=lambda x: x["carry"]
    )

    # With catastrophic lateral trouble, favor control if a shorter club
    # still leaves a playable next shot.
    if (
        catastrophic
        and trouble_location in (
            "Left",
            "Right"
        )
    ):
        sorted_desc = sorted(
            long_options,
            key=lambda x: x["carry"],
            reverse=True
        )

        if len(
            sorted_desc
        ) >= 2:
            longest = sorted_desc[0]
            second = sorted_desc[1]

            long_disp = longest[
                "dispersion"
            ]

            second_disp = second[
                "dispersion"
            ]

            long_risk = max(
                long_disp.get(
                    "left_rate",
                    0
                ),
                long_disp.get(
                    "right_rate",
                    0
                )
            )

            second_risk = max(
                second_disp.get(
                    "left_rate",
                    0
                ),
                second_disp.get(
                    "right_rate",
                    0
                )
            )

            if (
                second["carry"] >= 190
                and (
                    second_risk + 0.08 < long_risk
                    or long_disp.get(
                        "sample_count",
                        0
                    ) < 5
                )
            ):
                selected = second

    return selected, (
        "Tee-ball priority: playable position over maximum distance."
        if catastrophic
        else "Tee-ball priority: maximize useful distance with your normal shape."
    )

def choose_layup_club(
    bag,
    shots,
    preferred_leave=100
):
    options = club_options_with_learning(
        bag,
        shots
    )

    candidates = [
        x
        for x in options
        if 120 <= x["carry"] <= 210
    ]

    if not candidates:
        candidates = options

    selected = min(
        candidates,
        key=lambda x: abs(
            x["carry"] - 170
        )
    )

    return selected, (
        f"Position shot — favor a comfortable leave around {preferred_leave} yards."
    )

def hole_history_bias(
    memory
):
    """
    Positive = aim right.
    Negative = aim left.
    """
    if not memory:
        return 0.0, None

    common = str(
        memory.get(
            "common_result",
            ""
        )
    ).lower()

    if "left" in common:
        return 1.5, (
            "Your saved history on this hole trends left."
        )

    if "right" in common:
        return -1.5, (
            "Your saved history on this hole trends right."
        )

    return 0.0, None

def build_strategy_decision(
    shot_type,
    club_name,
    aim_label,
    trouble_type,
    trouble_location,
    safe_side,
    pin_position,
    play_yards,
    carry,
    history_note=None
):
    lines = []

    if shot_type == "Tee Shot":
        lines.append(
            f"Hit {club_name} to {aim_label}."
        )

        if trouble_type != "None":
            lines.append(
                f"Keep the ball away from {trouble_location.lower()} {trouble_type.lower()}."
            )
        else:
            lines.append(
                "Prioritize a playable second shot and a good angle into the hole."
            )

    elif shot_type == "Layup / Position":
        lines.append(
            f"Hit {club_name} to {aim_label} and play for position."
        )
        lines.append(
            "Do not chase unnecessary distance."
        )

    elif shot_type == "Recovery":
        lines.append(
            f"Use {club_name} only if the window is clear."
        )
        lines.append(
            "Primary goal: advance safely and eliminate the big number."
        )

    elif shot_type == "Scoring Shot":
        lines.append(
            f"Use {club_name} and favor {aim_label}."
        )
        lines.append(
            "Prioritize distance control over speed."
        )

    else:
        lines.append(
            f"Hit {club_name} to {aim_label}."
        )

        if pin_position == "Back":
            lines.append(
                "Do not chase the back edge."
            )
        elif pin_position == "Front":
            lines.append(
                "Use center-green depth as your safety margin."
            )
        else:
            lines.append(
                "Center-green depth is the baseline."
            )

    if (
        shot_type != "Tee Shot"
        and abs(
            carry - play_yards
        ) > 10
    ):
        lines.append(
            "This is an in-between number, so favor control."
        )

    if history_note:
        lines.append(
            history_note
        )

    return " ".join(
        lines
    )

def determine_round_shot_number(
    round_id,
    hole_number,
    shots
):
    if (
        shots.empty
        or "Round ID" not in shots.columns
        or "Hole" not in shots.columns
    ):
        return 1

    subset = shots[
        shots[
            "Round ID"
        ].astype(
            str
        ) == str(
            round_id
        )
    ].copy()

    subset[
        "Hole_num"
    ] = pd.to_numeric(
        subset[
            "Hole"
        ],
        errors="coerce"
    )

    subset = subset[
        subset[
            "Hole_num"
        ] == int(
            hole_number
        )
    ]

    return len(
        subset
    ) + 1



# ============================================================
# HOLE PLANNER
# ============================================================

def preferred_scoring_distances(
    bag,
    shots
):
    options = club_options_with_learning(
        bag,
        shots
    )

    scoring = []

    for item in options:
        club_name = item[
            "club"
        ][
            "Club"
        ]

        if (
            "Wedge" in club_name
            or "°" in club_name
        ):
            scoring.append({
                "club": club_name,
                "carry": round(
                    float(
                        item[
                            "carry"
                        ]
                    )
                ),
                "dispersion": item.get(
                    "dispersion",
                    {}
                )
            })

    return scoring

def scoring_leave_quality(
    option
):
    dispersion = option.get(
        "dispersion",
        {}
    )

    samples = dispersion.get(
        "sample_count",
        0
    )

    carry_std = dispersion.get(
        "carry_std"
    )

    directional = max(
        dispersion.get(
            "left_rate",
            0
        ),
        dispersion.get(
            "right_rate",
            0
        )
    )

    score = 0.0

    if samples >= 5:
        score += 2

    if carry_std is not None:
        score -= min(
            float(
                carry_std
            ) / 8.0,
            2
        )

    score -= directional * 3

    # Slight preference for traditional scoring numbers.
    if 95 <= option[
        "carry"
    ] <= 125:
        score += 1

    return score

def choose_preferred_scoring_leave(
    bag,
    shots
):
    options = preferred_scoring_distances(
        bag,
        shots
    )

    if not options:
        preferred_yards = int(
            profile.get("preferred_scoring_leave", 100) or 100
        )
        return {
            "club": "Scoring Wedge",
            "carry": preferred_yards,
            "dispersion": {}
        }

    preferred_yards = int(profile.get("preferred_scoring_leave", 100) or 100)
    return min(
        options,
        key=lambda option: (
            abs(float(option.get("carry", preferred_yards)) - preferred_yards),
            -scoring_leave_quality(option),
        ),
    )

def plan_candidate_risk(
    club_option,
    trouble_type,
    trouble_location
):
    dispersion = club_option.get(
        "dispersion",
        {}
    )

    risk = 0.0

    if trouble_location == "Left":
        risk += dispersion.get(
            "left_rate",
            0
        ) * 5

    elif trouble_location == "Right":
        risk += dispersion.get(
            "right_rate",
            0
        ) * 5

    if trouble_type in (
        "Water",
        "OB",
        "Penalty Area"
    ):
        risk *= 1.6

    elif trouble_type in (
        "Bunker",
        "Trees"
    ):
        risk *= 1.2

    if dispersion.get(
        "sample_count",
        0
    ) < 5:
        risk += 0.5

    return risk


def best_go_for_two_route(
    hole_distance,
    bag,
    shots,
    trouble_type,
    trouble_location
):
    options = club_options_with_learning(
        bag,
        shots
    )

    tee_options = [
        item
        for item in options
        if item["club"]["Club"] in (
            "Driver",
            "3 Wood",
            "3 Hybrid"
        )
    ]

    second_options = [
        item
        for item in options
        if (
            item["carry"] >= 170
            and item["club"]["Club"] != "Driver"
        )
    ]

    candidates = []

    for tee in tee_options:
        tee_carry = float(
            tee["carry"]
        )

        remaining = float(
            hole_distance
        ) - tee_carry

        for second in second_options:
            second_carry = float(
                second["carry"]
            )

            reach_gap = remaining - second_carry

            # "Reachable" means the club gets to within 15 yards short
            # or can cover the number outright. Positive reach_gap is short.
            if reach_gap <= 15:
                tee_risk = plan_candidate_risk(
                    tee,
                    trouble_type,
                    trouble_location
                )

                second_dispersion = second.get(
                    "dispersion",
                    {}
                )

                second_side_risk = max(
                    second_dispersion.get(
                        "left_rate",
                        0
                    ),
                    second_dispersion.get(
                        "right_rate",
                        0
                    )
                )

                # Prefer routes that actually cover the green, then lower risk.
                # Prefer a club that reaches without being excessive.
                # A 3 Wood that gets to the front/near the green is more realistic
                # than choosing a much longer club just because it has more carry.
                overshoot = max(
                    0,
                    second_carry - remaining
                )

                score = (
                    max(
                        0,
                        reach_gap
                    ) * 2
                    + overshoot * 0.35
                    + tee_risk * 8
                    + second_side_risk * 6
                )

                candidates.append({
                    "tee_club": tee["club"]["Club"],
                    "tee_carry": round(
                        tee_carry
                    ),
                    "after_tee": round(
                        remaining
                    ),
                    "second_club": second["club"]["Club"],
                    "second_carry": round(
                        second_carry
                    ),
                    "leave": max(
                        0,
                        round(
                            remaining - second_carry
                        )
                    ),
                    "scoring_club": None,
                    "preferred_leave": 0,
                    "go_for_two": True,
                    "reach_gap": round(
                        reach_gap
                    ),
                    "score": score
                })

    if not candidates:
        return None

    return min(
        candidates,
        key=lambda x: x["score"]
    )

def build_par5_routes(
    hole_distance,
    bag,
    shots,
    trouble_type,
    trouble_location
):
    options = club_options_with_learning(
        bag,
        shots
    )

    long_game = [
        item
        for item in options
        if item[
            "club"
        ][
            "Club"
        ] in (
            "Driver",
            "3 Wood",
            "3 Hybrid",
            "5 Iron",
            "6 Iron"
        )
    ]

    if not long_game:
        return []

    preferred_leave = choose_preferred_scoring_leave(
        bag,
        shots
    )

    leave_yards = float(
        preferred_leave[
            "carry"
        ]
    )

    tee_options = [
        item
        for item in long_game
        if item[
            "club"
        ][
            "Club"
        ] in (
            "Driver",
            "3 Wood",
            "3 Hybrid"
        )
    ]

    second_options = [
        item
        for item in long_game
        if item[
            "carry"
        ] >= 150
    ]

    routes = []

    for tee in tee_options:
        tee_carry = float(
            tee[
                "carry"
            ]
        )

        remaining_after_tee = (
            float(
                hole_distance
            )
            - tee_carry
        )

        for second in second_options:
            second_carry = float(
                second[
                    "carry"
                ]
            )

            resulting_leave = (
                remaining_after_tee
                - second_carry
            )

            leave_error = abs(
                resulting_leave
                - leave_yards
            )

            if resulting_leave < 40:
                leave_error += 50

            tee_risk = plan_candidate_risk(
                tee,
                trouble_type,
                trouble_location
            )

            second_risk = (
                max(
                    second[
                        "dispersion"
                    ].get(
                        "left_rate",
                        0
                    ),
                    second[
                        "dispersion"
                    ].get(
                        "right_rate",
                        0
                    )
                )
                * 2
            )

            total_score = (
                leave_error
                + tee_risk * 8
                + second_risk * 4
            )

            routes.append({
                "tee_club": tee[
                    "club"
                ][
                    "Club"
                ],
                "tee_carry": round(
                    tee_carry
                ),
                "after_tee": round(
                    remaining_after_tee
                ),
                "second_club": second[
                    "club"
                ][
                    "Club"
                ],
                "second_carry": round(
                    second_carry
                ),
                "leave": round(
                    resulting_leave
                ),
                "scoring_club": preferred_leave[
                    "club"
                ],
                "preferred_leave": round(
                    leave_yards
                ),
                "score": total_score
            })

    return sorted(
        routes,
        key=lambda x: x[
            "score"
        ]
    )

def build_par4_routes(
    hole_distance,
    bag,
    shots,
    trouble_type,
    trouble_location
):
    options = club_options_with_learning(
        bag,
        shots
    )

    preferred_leave = choose_preferred_scoring_leave(
        bag,
        shots
    )

    tee_options = [
        item
        for item in options
        if item[
            "club"
        ][
            "Club"
        ] in (
            "Driver",
            "3 Wood",
            "3 Hybrid"
        )
    ]

    routes = []

    for tee in tee_options:
        tee_carry = float(
            tee[
                "carry"
            ]
        )

        remaining = float(
            hole_distance
        ) - tee_carry

        risk = plan_candidate_risk(
            tee,
            trouble_type,
            trouble_location
        )

        # Prefer leaving a normal full approach over awkward partials.
        approach_quality = min(
            abs(
                remaining - float(
                    item[
                        "carry"
                    ]
                )
            )
            for item in options
        )

        score = (
            risk * 8
            + approach_quality
        )

        routes.append({
            "tee_club": tee[
                "club"
            ][
                "Club"
            ],
            "tee_carry": round(
                tee_carry
            ),
            "after_tee": round(
                remaining
            ),
            "second_club": None,
            "second_carry": None,
            "leave": round(
                remaining
            ),
            "scoring_club": preferred_leave[
                "club"
            ],
            "preferred_leave": round(
                preferred_leave[
                    "carry"
                ]
            ),
            "score": score
        })

    return sorted(
        routes,
        key=lambda x: x[
            "score"
        ]
    )

def build_hole_plan(
    par,
    hole_distance,
    bag,
    shots,
    trouble_type,
    trouble_location,
    safe_side
):
    try:
        par_num = int(
            float(
                par
            )
        )
    except Exception:
        par_num = None

    if par_num == 5:
        routes = build_par5_routes(
            hole_distance,
            bag,
            shots,
            trouble_type,
            trouble_location
        )

        go_for_two_route = best_go_for_two_route(
            hole_distance,
            bag,
            shots,
            trouble_type,
            trouble_location
        )

    elif par_num == 4:
        routes = build_par4_routes(
            hole_distance,
            bag,
            shots,
            trouble_type,
            trouble_location
        )

    else:
        routes = []

    if not routes:
        return None

    best = routes[
        0
    ]

    if trouble_location == "Left":
        aim = (
            "center-right"
            if safe_side in (
                "Center",
                "Right"
            )
            else "center"
        )

    elif trouble_location == "Right":
        aim = (
            "center-left"
            if safe_side in (
                "Center",
                "Left"
            )
            else "center"
        )

    else:
        aim = (
            safe_side.lower()
            if safe_side != "Center"
            else "center"
        )

    best[
        "aim"
    ] = aim
    best[
        "alternatives"
    ] = routes[
        1:3
    ]

    return best

def hole_plan_text(
    plan,
    par
):
    if not plan:
        return (
            "Not enough course or club data to create a full-hole plan yet."
        )

    if int(
        float(
            par
        )
    ) == 5:
        return (
            f"Hit {plan['tee_club']} toward {plan['aim']}. "
            f"Expected landing is about {plan['tee_carry']} yards, "
            f"leaving roughly {plan['after_tee']}. "
            f"Then advance about {plan['second_carry']} with {plan['second_club']} "
            f"to leave approximately {plan['leave']} yards. "
            f"Your preferred scoring leave is {plan['preferred_leave']} yards "
            f"for {plan['scoring_club']}."
        )

    return (
        f"Hit {plan['tee_club']} toward {plan['aim']}. "
        f"Expected landing is about {plan['tee_carry']} yards, "
        f"leaving roughly {plan['after_tee']} for the approach."
    )



# ============================================================
# CONSERVATIVE VS AGGRESSIVE ROUTES
# ============================================================

def center_hazard_route_adjustment(
    route,
    trouble_type,
    trouble_location,
    hazard_start,
    hazard_clear
):
    if trouble_type == "None" or trouble_location != "Center":
        return 0.0, None

    try:
        tee_carry = float(route.get("tee_carry", 0))
        start = float(hazard_start or 0)
        clear = float(hazard_clear or 0)
    except Exception:
        return 0.0, None

    if start <= 0:
        return 0.0, None

    catastrophic = trouble_type in ("Water", "OB", "Penalty Area")

    if clear > start:
        if tee_carry <= start - 10:
            return -1.5, (
                f"lays short of the center {trouble_type.lower()} "
                f"that starts around {round(start)}"
            )

        if tee_carry >= clear + 10:
            return -0.5, (
                f"carries the center {trouble_type.lower()} "
                f"that clears around {round(clear)}"
            )

        return (
            14.0 if catastrophic else 8.0
        ), (
            f"brings the center {trouble_type.lower()} "
            f"window ({round(start)}–{round(clear)}) into play"
        )

    if abs(tee_carry - start) <= 15:
        return (
            10.0 if catastrophic else 6.0
        ), (
            f"lands near the center {trouble_type.lower()} "
            f"at about {round(start)}"
        )

    return 0.0, None


def route_risk_score(route, bag, shots, trouble_type, trouble_location):
    options = {
        item["club"]["Club"]: item
        for item in club_options_with_learning(
            bag,
            shots
        )
    }

    tee = options.get(
        route.get(
            "tee_club"
        )
    )

    if not tee:
        return 5.0

    risk = plan_candidate_risk(
        tee,
        trouble_type,
        trouble_location
    )

    dispersion = tee.get(
        "dispersion",
        {}
    )

    if dispersion.get(
        "sample_count",
        0
    ) < 5:
        risk += 0.5

    return risk

def split_route_styles(
    routes,
    bag,
    shots,
    trouble_type,
    trouble_location
):
    if not routes:
        return None, None, None

    enriched = []

    for route in routes:
        copy = dict(
            route
        )

        copy[
            "risk"
        ] = route_risk_score(
            route,
            bag,
            shots,
            trouble_type,
            trouble_location
        )

        enriched.append(
            copy
        )

    # Aggressive = longest tee shot / shortest expected remaining,
    # with route quality still used as a tiebreaker.
    aggressive = min(
        enriched,
        key=lambda r: (
            -float(
                r.get(
                    "tee_carry",
                    0
                )
            ),
            float(
                r.get(
                    "score",
                    999
                )
            )
        )
    )

    # Conservative = lowest risk first, then shortest tee carry among
    # similarly low-risk routes.
    conservative = min(
        enriched,
        key=lambda r: (
            float(
                r.get(
                    "risk",
                    999
                )
            ),
            float(
                r.get(
                    "tee_carry",
                    999
                )
            ),
            float(
                r.get(
                    "score",
                    999
                )
            )
        )
    )

    # Recommended balances route quality and risk.
    recommended = min(
        enriched,
        key=lambda r: (
            float(
                r.get(
                    "score",
                    999
                )
            )
            + float(
                r.get(
                    "risk",
                    0
                )
            ) * 6
        )
    )

    return conservative, aggressive, recommended

def build_hole_plan_options(
    par,
    hole_distance,
    bag,
    shots,
    trouble_type,
    trouble_location,
    safe_side,
    hazard_start=None,
    hazard_clear=None
):
    go_for_two_route = None

    try:
        par_num = int(
            float(
                par
            )
        )
    except Exception:
        return None

    if par_num == 5:
        routes = build_par5_routes(
            hole_distance,
            bag,
            shots,
            trouble_type,
            trouble_location
        )

        go_for_two_route = best_go_for_two_route(
            hole_distance,
            bag,
            shots,
            trouble_type,
            trouble_location
        )

    elif par_num == 4:
        routes = build_par4_routes(
            hole_distance,
            bag,
            shots,
            trouble_type,
            trouble_location
        )

    else:
        routes = []

    if not routes:
        return None

    for route in routes:
        hazard_penalty, hazard_note = center_hazard_route_adjustment(
            route,
            trouble_type,
            trouble_location,
            hazard_start,
            hazard_clear
        )

        route["score"] = float(route.get("score", 0)) + hazard_penalty

        if hazard_note:
            route["center_hazard_note"] = hazard_note

    conservative, aggressive, recommended = split_route_styles(
        routes,
        bag,
        shots,
        trouble_type,
        trouble_location
    )

    if go_for_two_route is not None:
        aggressive = go_for_two_route

        # If the go-for-two route is reasonably close in route quality,
        # let it compete for the recommendation instead of forcing layup logic.
        go_two_risk = route_risk_score(
            aggressive,
            bag,
            shots,
            trouble_type,
            trouble_location
        )

        aggressive["risk"] = go_two_risk

        if recommended is not None:
            recommended_value = (
                float(
                    recommended.get(
                        "score",
                        999
                    )
                )
                + float(
                    recommended.get(
                        "risk",
                        0
                    )
                ) * 6
            )

            aggressive_value = (
                float(
                    aggressive.get(
                        "score",
                        999
                    )
                )
                + go_two_risk * 6
            )

            # Aggressive must be materially reasonable to become recommended.
            if aggressive_value <= recommended_value + 8:
                recommended = aggressive

    for route in [
        conservative,
        aggressive,
        recommended
    ]:
        if route is None:
            continue

        if trouble_location == "Left":
            route["aim"] = (
                "center-right"
                if safe_side in (
                    "Center",
                    "Right"
                )
                else "center"
            )

        elif trouble_location == "Right":
            route["aim"] = (
                "center-left"
                if safe_side in (
                    "Center",
                    "Left"
                )
                else "center"
            )

        else:
            route["aim"] = (
                safe_side.lower()
                if safe_side != "Center"
                else "center"
            )

    # Avoid showing identical conservative/aggressive plans if the route
    # pool is too narrow.
    if (
        conservative
        and aggressive
        and conservative.get(
            "tee_club"
        ) == aggressive.get(
            "tee_club"
        )
        and conservative.get(
            "second_club"
        ) == aggressive.get(
            "second_club"
        )
    ):
        alternates = [
            route
            for route in routes
            if (
                route.get(
                    "tee_club"
                ) != aggressive.get(
                    "tee_club"
                )
                or route.get(
                    "second_club"
                ) != aggressive.get(
                    "second_club"
                )
            )
        ]

        if alternates:
            conservative = min(
                alternates,
                key=lambda r: (
                    route_risk_score(
                        r,
                        bag,
                        shots,
                        trouble_type,
                        trouble_location
                    ),
                    r.get(
                        "tee_carry",
                        999
                    )
                )
            )

            conservative["aim"] = recommended.get(
                "aim",
                "center"
            )

    return {
        "conservative": conservative,
        "aggressive": aggressive,
        "recommended": recommended
    }

def route_summary_text(route, par_num):
    if not route:
        return "Not enough data for this route."

    if int(par_num) == 5:
        if route.get(
            "go_for_two"
        ):
            reach_gap = route.get(
                "reach_gap",
                0
            )

            if reach_gap <= 0:
                reach_text = (
                    f"covers the remaining {route['after_tee']} yards"
                )
            else:
                reach_text = (
                    f"gets you to within about {reach_gap} yards of the green"
                )

            return (
                f"{route['tee_club']} about {route['tee_carry']} → "
                f"go for the green with {route['second_club']} off the deck, about "
                f"{route['second_carry']} ({reach_text})."
            )

        return (
            f"{route['tee_club']} about {route['tee_carry']} → "
            f"{route['second_club']} about {route['second_carry']} → "
            f"leave about {route['leave']} for {route['scoring_club']}."
        )

    return (
        f"{route['tee_club']} about {route['tee_carry']} → "
        f"leave about {route['after_tee']} for the approach."
    )



# ============================================================
# CONTEXT / EXPLANATION LAYER
# ============================================================

def route_recommendation_reason(
    conservative,
    aggressive,
    recommended,
    trouble_type,
    trouble_location,
    dispersion
):
    if not recommended:
        return "Not enough information yet to explain the route choice."

    is_cons = (
        conservative
        and recommended.get("tee_club") == conservative.get("tee_club")
        and recommended.get("second_club") == conservative.get("second_club")
    )

    is_aggr = (
        aggressive
        and recommended.get("tee_club") == aggressive.get("tee_club")
        and recommended.get("second_club") == aggressive.get("second_club")
    )

    reasons = []

    if is_cons:
        reasons.append(
            "The conservative route gives you a cleaner scoring leave and reduces big-number risk."
        )
    elif is_aggr:
        reasons.append(
            "The aggressive route creates the best scoring opportunity without adding too much risk."
        )
    else:
        reasons.append(
            "The balanced route gives the best mix of position, scoring leave, and risk."
        )

    if trouble_type != "None":
        reasons.append(
            f"The main danger is {trouble_location.lower()} {trouble_type.lower()}."
        )

    if dispersion and dispersion.get("sample_count", 0) >= 5:
        dominant = dispersion.get("dominant_miss")
        if dominant and dominant != "Not enough data":
            reasons.append(
                f"Your learned miss with the tee club trends {dominant.lower()}."
            )

    if aggressive and aggressive.get("go_for_two"):
        gap = aggressive.get("reach_gap", 0)
        if gap > 0:
            reasons.append(
                f"The aggressive route gets you to about {gap} yards short of the green on stock carry."
            )
        else:
            reasons.append(
                "The aggressive route can cover the green-in-two number on stock carry."
            )

    return " ".join(reasons)

def read_swing_reminders():
    if _cloud_ready():
        try:
            response = (
                supabase
                .table("swing_reminders")
                .select(
                    "reminder"
                )
                .eq(
                    "user_id",
                    _cloud_user_id()
                )
                .eq(
                    "active",
                    True
                )
                .order(
                    "created_at"
                )
                .execute()
            )

            return [
                str(
                    row.get(
                        "reminder",
                        ""
                    )
                ).strip()
                for row in (response.data or [])
                if str(
                    row.get(
                        "reminder",
                        ""
                    )
                ).strip()
            ]
        except Exception:
            pass

    if _cloud_ready():
        return []

    if os.path.exists(
        REMINDER_FILE
    ):
        try:
            with open(
                REMINDER_FILE,
                "r",
                encoding="utf-8"
            ) as f:
                text = f.read().strip()

            return [
                line.strip()
                for line in text.splitlines()
                if line.strip()
            ]
        except Exception:
            return []

    return []

def build_caddie_coaching_points(
    shot_type,
    stance,
    severity,
    surface,
    wind_relation,
    wind_speed,
    player_miss,
    dispersion,
    hole_memory,
    trouble_type,
    trouble_location,
    active_plan,
    gps_green_distance=None
):
    points = []

    if active_plan:
        if shot_type == "Tee Shot":
            points.append(
                f"Commit to the landing window around {active_plan.get('tee_carry')} yards."
            )

        if active_plan.get("go_for_two"):
            points.append(
                "Aggressive route is only worth it with a clean lie and committed strike."
            )

    if trouble_type != "None":
        points.append(
            f"Protect against the {trouble_location.lower()} {trouble_type.lower()} — that is the dead side."
        )

    if stance != "Level":
        points.append(
            setup_advice(
                stance,
                profile.get(
                    "handedness",
                    "Right-handed"
                ),
                severity
            )
        )

    if surface in ("Heavy Rough", "Fairway Bunker", "Recovery"):
        points.append(
            "Prioritize contact and position over forcing maximum distance."
        )

    if wind_speed >= 12:
        if wind_relation == "Into":
            points.append(
                "Wind is strong enough that tempo and solid contact matter more than extra effort."
            )
        elif wind_relation in ("Left to Right", "Right to Left"):
            points.append(
                "Start the ball on the planned side and let the crosswind move it."
            )

    if dispersion and dispersion.get("sample_count", 0) >= 5:
        dominant = dispersion.get("dominant_miss")
        if dominant and dominant != "Not enough data":
            points.append(
                f"Your recent pattern with this club is {dominant.lower()}; build the target around that miss."
            )
    elif player_miss and player_miss != "unknown":
        points.append(
            f"Stock tendency: {player_miss}. Use the target to protect against it."
        )

    if hole_memory and hole_memory.get("common_result"):
        points.append(
            f"On this hole, your most common saved result is {str(hole_memory['common_result']).lower()}."
        )

    if gps_green_distance is not None and shot_type != "Tee Shot":
        points.append(
            f"GPS has the green center at about {round(gps_green_distance)} yards."
        )

    reminders = read_swing_reminders()

    # Add at most one personal reminder so the caddie does not overload the golfer.
    if reminders:
        points.append(
            f"Your reminder: {reminders[0]}"
        )

    # Keep it concise on-course.
    return points[:4]

def nearest_mapped_bunker_yards(
    selected_course,
    latitude,
    longitude
):
    if (
        not selected_course
        or latitude is None
        or longitude is None
    ):
        return None

    features = selected_course.get(
        "osm_features",
        {}
    ) or {}

    bunkers = features.get(
        "bunkers",
        []
    )

    distances = []

    for bunker in bunkers:
        lat = bunker.get("latitude")
        lon = bunker.get("longitude")

        if lat is None or lon is None:
            continue

        try:
            yards = gps_distance_yards(
                latitude,
                longitude,
                float(lat),
                float(lon)
            )
            distances.append(
                yards
            )
        except Exception:
            pass

    if not distances:
        return None

    return min(distances)


# ============================================================
# LIVE ROUND
# ============================================================

with tab_round:
    # Apply voice-selected tee before any Live Round widget with this key exists.
    if "voice_pending_round_start_tee" in st.session_state:
        pending_tee = st.session_state.pop(
            "voice_pending_round_start_tee"
        )

        st.session_state[
            "round_start_tee"
        ] = pending_tee

    st.header(
        "⛳ Live Round"
    )


    # --------------------------------------------------------
    # ALWAYS-AVAILABLE TWO-STEP LIVE ROUND CANCEL
    # --------------------------------------------------------
    cancel_requested = st.session_state.get(
        "live_round_cancel_requested",
        False
    )

    if not cancel_requested:
        if st.button(
            "✕ Cancel Live Round",
            use_container_width=True,
            key="request_cancel_live_round"
        ):
            st.session_state[
                "live_round_cancel_requested"
            ] = True

            st.rerun()

    else:
        st.warning(
            "Cancel Live Round? This will discard the current round/setup and return Live Round to a fresh start. A canceled active round will not be saved as a completed round."
        )

        cancel_confirm_col1, cancel_confirm_col2 = st.columns(
            2
        )

        with cancel_confirm_col1:
            if st.button(
                "Yes, Cancel Round",
                type="primary",
                use_container_width=True,
                key="confirm_cancel_live_round"
            ):
                clear_active_round()

                # Clear every setup / round-specific state so the user
                # truly exits the current Live Round workflow.
                for state_key in [
                    "selected_course",
                    "pending_course_selection",
                    "live_round_course_results",
                    "live_round_course_errors",
                    "live_round_course_results_page",
                    "live_round_course_mode",
                    "existing_course_search_type",
                    "live_round_course_query",
                    "live_round_course_city_query",
                    "live_round_course_zip_query",
                    "live_round_course_state",
                    "live_round_search_radius",
                    "last_geo_search",
                    "round_start_tee",
                    "limited_course_data",
                    "voice_pending_round_start_tee",
                    "voice_requested_start_round",
                    "voice_requested_end_round",
                    "voice_requested_save_shot",
                    "current_hole",
                    "hole_number",
                    "live_hole_number",
                    "selected_hole",
                    "voice_hole_number",
                    "voice_hole_par",
                    "voice_selected_tee",
                    "round_hole_jump",
                    "live_last_recommendation",
                    "manual_new_course_name",
                    "manual_new_course_city",
                    "manual_new_course_state",
                    "add_course_method",
                    "new_course_scorecard_upload",
                    "new_course_scorecard_camera",
                    "confirmed_course_data_method",
                    "live_round_caddie_pending_text",
                    "last_live_round_caddie_voice_signature",
                ]:
                    st.session_state.pop(
                        state_key,
                        None
                    )

                clear_course_builder_state()

                # Prevent the last selected course from restoring itself.
                st.session_state[
                    "selected_course"
                ] = None

                cache_selected_course(
                    {}
                )

                st.session_state[
                    "live_round_cancel_requested"
                ] = False

                st.session_state[
                    "round_cancel_message"
                ] = "Live Round canceled."

                st.rerun()

        with cancel_confirm_col2:
            if st.button(
                "No, Keep Round",
                use_container_width=True,
                key="keep_live_round"
            ):
                st.session_state[
                    "live_round_cancel_requested"
                ] = False

                st.rerun()

    if st.session_state.get(
        "round_cancel_message"
    ):
        st.info(
            st.session_state.pop(
                "round_cancel_message"
            )
        )


    selected_course = st.session_state.get(
        "selected_course"
    )

    active_round = load_active_round()

    if active_round:
        if st.button(
            "↻ Reset Round Screen",
            use_container_width=True,
            key="reset_live_round_screen"
        ):
            for state_key in [
                "current_hole",
                "hole_number",
                "live_hole_number",
                "selected_hole",
                "voice_hole_number",
                "voice_hole_par",
                "voice_selected_tee",
            ]:
                st.session_state.pop(
                    state_key,
                    None
                )

            st.rerun()

    if not active_round:
        if st.session_state.get(
            "round_exit_message"
        ):
            st.success(
                st.session_state.pop(
                    "round_exit_message"
                )
            )

        st.subheader(
            "Start a Round"
        )

        selected_course = st.session_state.get(
            "selected_course"
        )

        pending_course = st.session_state.get(
            "pending_course_selection"
        )

        st.markdown(
            "### Step 1 — Course"
        )

        # ====================================================
        # NO COURSE CONFIRMED YET
        # ====================================================
        if not selected_course:
            if pending_course:
                pending_label = voice_course_candidate_label(
                    pending_course
                )

                st.info(
                    "Confirm this course before continuing."
                )

                with st.container(
                    border=True
                ):
                    st.write(
                        f"**{pending_label}**"
                    )

                    confirm_col1, confirm_col2 = st.columns(
                        2
                    )

                    with confirm_col1:
                        if st.button(
                            "Confirm Course",
                            type="primary",
                            use_container_width=True,
                            key="confirm_pending_course"
                        ):
                            loaded_course = load_course_result_for_voice(
                                pending_course
                            )

                            st.session_state[
                                "selected_course"
                            ] = loaded_course

                            cache_selected_course(
                                loaded_course
                            )

                            st.session_state.pop(
                                "pending_course_selection",
                                None
                            )

                            st.session_state.pop(
                                "live_round_course_results",
                                None
                            )

                            st.session_state.pop(
                                "round_start_tee",
                                None
                            )

                            clear_course_builder_state()

                            st.rerun()

                    with confirm_col2:
                        if st.button(
                            "Back to Search",
                            use_container_width=True,
                            key="cancel_pending_course"
                        ):
                            st.session_state.pop(
                                "pending_course_selection",
                                None
                            )

                            st.rerun()

            else:
                st.caption(
                    "Choose one path to continue."
                )

                mode_col1, mode_col2 = st.columns(
                    2
                )

                with mode_col1:
                    if st.button(
                        "🔎 Select Existing Course",
                        type=(
                            "primary"
                            if st.session_state.get(
                                "live_round_course_mode",
                                ""
                            ) == "Find a Course"
                            else "secondary"
                        ),
                        use_container_width=True,
                        key="choose_existing_course_mode"
                    ):
                        st.session_state[
                            "live_round_course_mode"
                        ] = "Find a Course"

                        st.rerun()

                with mode_col2:
                    if st.button(
                        "➕ Add a Course",
                        type=(
                            "primary"
                            if st.session_state.get(
                                "live_round_course_mode",
                                ""
                            ) == "Add a Course"
                            else "secondary"
                        ),
                        use_container_width=True,
                        key="choose_add_course_mode"
                    ):
                        st.session_state[
                            "live_round_course_mode"
                        ] = "Add a Course"

                        st.rerun()

                course_mode = st.session_state.get(
                    "live_round_course_mode"
                )

                if not course_mode:
                    st.info(
                        "Select Existing Course if the course is already in My Play, or Add a Course if it is missing."
                    )

                # ============================================
                # OPTION 1 — FIND EXISTING COURSE
                # ============================================
                if course_mode == "Find a Course":
                    st.caption(
                        "Use the full course finder. Set your search area first, then search by name, city, ZIP, state, or your current location."
                    )

                    finder_top1, finder_top2 = st.columns(
                        [2, 1]
                    )

                    with finder_top1:
                        existing_course_search_type = st.selectbox(
                            "Search By",
                            [
                                "Course Name",
                                "City",
                                "ZIP / Area",
                                "Browse State",
                                "Near Me",
                            ],
                            key="existing_course_search_type"
                        )

                    with finder_top2:
                        live_round_search_radius = st.selectbox(
                            "Search Radius",
                            [
                                5,
                                10,
                                15,
                                25,
                                50,
                                75,
                                100,
                            ],
                            index=3,
                            format_func=lambda miles: f"{miles} miles",
                            key="live_round_search_radius"
                        )

                    finder_state = st.text_input(
                        "State",
                        value=str(
                            profile.get(
                                "default_state",
                                "NJ"
                            )
                            or "NJ"
                        ),
                        key="live_round_course_state"
                    )

                    search_triggered = False
                    search_text = ""

                    if existing_course_search_type == "Course Name":
                        search_text = st.text_input(
                            "Course Name",
                            key="live_round_course_query",
                            placeholder="e.g. Indian Spring Golf Club"
                        )

                        search_triggered = st.button(
                            "Search Courses",
                            type="primary",
                            use_container_width=True,
                            key="live_round_search_courses_name"
                        )

                    elif existing_course_search_type == "City":
                        search_text = st.text_input(
                            "City",
                            key="live_round_course_city_query",
                            placeholder="e.g. Marlton"
                        )

                        search_triggered = st.button(
                            "Search City",
                            type="primary",
                            use_container_width=True,
                            key="live_round_search_courses_city"
                        )

                    elif existing_course_search_type == "ZIP / Area":
                        search_text = st.text_input(
                            "ZIP Code",
                            key="live_round_course_zip_query",
                            placeholder="e.g. 08053",
                            max_chars=5
                        )

                        search_triggered = st.button(
                            "Search This Area",
                            type="primary",
                            use_container_width=True,
                            key="live_round_search_courses_zip"
                        )

                    elif existing_course_search_type == "Browse State":
                        st.caption(
                            "Browse the course catalog for the selected state."
                        )

                        search_triggered = st.button(
                            "Show Courses in State",
                            type="primary",
                            use_container_width=True,
                            key="live_round_search_courses_state"
                        )

                    else:
                        st.caption(
                            "Use your phone/browser location to find courses inside the selected radius."
                        )

                        if GEOLOCATION_AVAILABLE:
                            live_round_existing_geo = streamlit_geolocation(
                                key="live_round_existing_course_geolocation"
                            )

                            if (
                                live_round_existing_geo
                                and live_round_existing_geo.get(
                                    "latitude"
                                ) is not None
                                and live_round_existing_geo.get(
                                    "longitude"
                                ) is not None
                            ):
                                st.caption(
                                    "Location ready."
                                )

                                search_triggered = st.button(
                                    "Find Courses Near Me",
                                    type="primary",
                                    use_container_width=True,
                                    key="live_round_search_courses_near_me"
                                )
                            else:
                                st.info(
                                    "Allow location access in your browser, then try again."
                                )
                        else:
                            live_round_existing_geo = None
                            st.warning(
                                "Browser location helper is not available on this device."
                            )

                    if search_triggered:
                        errors = []
                        results = []

                        try:
                            if existing_course_search_type == "Course Name":
                                if not str(
                                    search_text
                                ).strip():
                                    st.warning(
                                        "Enter a course name."
                                    )
                                else:
                                    results, errors = search_all_free_sources(
                                        str(
                                            search_text
                                        ).strip(),
                                        finder_state
                                    )

                            elif existing_course_search_type == "City":
                                if not str(
                                    search_text
                                ).strip():
                                    st.warning(
                                        "Enter a city."
                                    )
                                else:
                                    city_results = browse_courses_by_city(
                                        str(
                                            search_text
                                        ).strip(),
                                        finder_state,
                                        limit=300
                                    )

                                    # Add wider geographic results around the city too.
                                    try:
                                        city_geo = geocode_location_text(
                                            (
                                                str(
                                                    search_text
                                                ).strip()
                                                + ", "
                                                + str(
                                                    finder_state
                                                ).strip()
                                                + ", USA"
                                            )
                                        )
                                    except Exception as exc:
                                        city_geo = None
                                        errors.append(
                                            f"City location lookup: {exc}"
                                        )

                                    nearby_city_results = []

                                    if city_geo:
                                        nearby_city_results = browse_courses_near_location(
                                            city_geo[
                                                "latitude"
                                            ],
                                            city_geo[
                                                "longitude"
                                            ],
                                            radius_miles=live_round_search_radius,
                                            limit=300
                                        )

                                    results = (
                                        city_results
                                        + nearby_city_results
                                    )

                            elif existing_course_search_type == "ZIP / Area":
                                zip_text = str(
                                    search_text
                                ).strip()

                                if (
                                    not zip_text.isdigit()
                                    or len(
                                        zip_text
                                    ) != 5
                                ):
                                    st.warning(
                                        "Enter a 5-digit ZIP code."
                                    )
                                else:
                                    try:
                                        zip_geo = geocode_location_text(
                                            f"{zip_text}, USA"
                                        )
                                    except Exception as exc:
                                        zip_geo = None
                                        errors.append(
                                            f"ZIP lookup: {exc}"
                                        )

                                    if zip_geo:
                                        results = browse_courses_near_location(
                                            zip_geo[
                                                "latitude"
                                            ],
                                            zip_geo[
                                                "longitude"
                                            ],
                                            radius_miles=live_round_search_radius,
                                            limit=300
                                        )

                                        st.session_state[
                                            "last_geo_search"
                                        ] = zip_geo
                                    else:
                                        results = search_local_courses(
                                            zip_text,
                                            finder_state,
                                            limit=100
                                        )

                            elif existing_course_search_type == "Browse State":
                                if not str(
                                    finder_state
                                ).strip():
                                    st.warning(
                                        "Enter a state."
                                    )
                                else:
                                    results = browse_courses_by_state(
                                        finder_state,
                                        limit=500
                                    )

                            elif existing_course_search_type == "Near Me":
                                if (
                                    live_round_existing_geo
                                    and live_round_existing_geo.get(
                                        "latitude"
                                    ) is not None
                                    and live_round_existing_geo.get(
                                        "longitude"
                                    ) is not None
                                ):
                                    results = browse_courses_near_location(
                                        live_round_existing_geo[
                                            "latitude"
                                        ],
                                        live_round_existing_geo[
                                            "longitude"
                                        ],
                                        radius_miles=live_round_search_radius,
                                        limit=300
                                    )

                        except Exception as exc:
                            errors.append(
                                str(
                                    exc
                                )
                            )

                        # Deduplicate while preserving order.
                        unique_results = []
                        seen_result_keys = set()

                        for item in results:
                            if not isinstance(
                                item,
                                dict
                            ):
                                continue

                            result_key = (
                                normalize_name(
                                    result_name(
                                        item
                                    )
                                ),
                                normalize_name(
                                    str(
                                        item.get(
                                            "city",
                                            ""
                                        )
                                        or item.get(
                                            "locality",
                                            ""
                                        )
                                        or ""
                                    )
                                ),
                                normalize_name(
                                    str(
                                        item.get(
                                            "state",
                                            ""
                                        )
                                        or item.get(
                                            "region",
                                            ""
                                        )
                                        or ""
                                    )
                                ),
                            )

                            if result_key in seen_result_keys:
                                continue

                            seen_result_keys.add(
                                result_key
                            )
                            unique_results.append(
                                item
                            )

                        # Name searches still rank obvious matches first.
                        if (
                            existing_course_search_type
                            == "Course Name"
                        ):
                            query_norm = normalize_name(
                                search_text
                            )

                            def existing_course_score(item):
                                name_norm = normalize_name(
                                    result_name(
                                        item
                                    )
                                )

                                city_norm = normalize_name(
                                    str(
                                        item.get(
                                            "city",
                                            ""
                                        )
                                        or item.get(
                                            "locality",
                                            ""
                                        )
                                        or ""
                                    )
                                )

                                score = 0

                                if query_norm == name_norm:
                                    score += 100

                                if (
                                    query_norm
                                    and query_norm in name_norm
                                ):
                                    score += 60

                                if (
                                    query_norm
                                    and query_norm in city_norm
                                ):
                                    score += 20

                                return score

                            unique_results = sorted(
                                unique_results,
                                key=existing_course_score,
                                reverse=True
                            )

                        st.session_state[
                            "live_round_course_results"
                        ] = unique_results

                        st.session_state[
                            "live_round_course_errors"
                        ] = errors

                        st.session_state[
                            "live_round_course_results_page"
                        ] = 0

                    live_round_results = st.session_state.get(
                        "live_round_course_results",
                        []
                    )

                    if live_round_results:
                        total_results = len(
                            live_round_results
                        )

                        st.success(
                            f"{total_results} potential course"
                            + (
                                "s"
                                if total_results != 1
                                else ""
                            )
                            + " found."
                        )

                        page_size = 20
                        total_pages = max(
                            1,
                            math.ceil(
                                total_results
                                / page_size
                            )
                        )

                        current_page = int(
                            st.session_state.get(
                                "live_round_course_results_page",
                                0
                            )
                            or 0
                        )

                        current_page = min(
                            max(
                                current_page,
                                0
                            ),
                            total_pages - 1
                        )

                        start_result = (
                            current_page
                            * page_size
                        )
                        end_result = min(
                            start_result
                            + page_size,
                            total_results
                        )

                        st.caption(
                            f"Showing {start_result + 1}–{end_result} of {total_results}."
                        )

                        for result_index in range(
                            start_result,
                            end_result
                        ):
                            course_result = live_round_results[
                                result_index
                            ]

                            course_label = voice_course_candidate_label(
                                course_result
                            )

                            with st.container(
                                border=True
                            ):
                                st.write(
                                    f"**{course_label}**"
                                )

                                if course_result.get(
                                    "distance_miles"
                                ) is not None:
                                    st.caption(
                                        f"{course_result.get('distance_miles')} miles away"
                                    )

                                st.caption(
                                    f"Source: {result_source(course_result)}"
                                )

                                if st.button(
                                    "Choose This Course",
                                    use_container_width=True,
                                    key=(
                                        "live_round_choose_course_"
                                        + str(
                                            result_index
                                        )
                                    )
                                ):
                                    st.session_state[
                                        "pending_course_selection"
                                    ] = course_result

                                    st.rerun()

                        if total_pages > 1:
                            page_col1, page_col2, page_col3 = st.columns(
                                [
                                    1,
                                    2,
                                    1,
                                ]
                            )

                            with page_col1:
                                if st.button(
                                    "← Previous",
                                    use_container_width=True,
                                    disabled=(
                                        current_page <= 0
                                    ),
                                    key="course_results_previous"
                                ):
                                    st.session_state[
                                        "live_round_course_results_page"
                                    ] = max(
                                        0,
                                        current_page - 1
                                    )

                                    st.rerun()

                            with page_col2:
                                st.caption(
                                    f"Page {current_page + 1} of {total_pages}"
                                )

                            with page_col3:
                                if st.button(
                                    "Next →",
                                    use_container_width=True,
                                    disabled=(
                                        current_page
                                        >= total_pages - 1
                                    ),
                                    key="course_results_next"
                                ):
                                    st.session_state[
                                        "live_round_course_results_page"
                                    ] = min(
                                        total_pages - 1,
                                        current_page + 1
                                    )

                                    st.rerun()

                    elif st.session_state.get(
                        "live_round_course_results"
                    ) == []:
                        if st.session_state.get(
                            "live_round_course_errors"
                        ):
                            st.caption(
                                "No matching courses were returned. You can widen the radius, change the search type, or use Add a Course."
                            )

                # ============================================
                # OPTION 2 — ADD NEW COURSE
                # ============================================
                elif course_mode == "Add a Course":
                    st.caption(
                        "Add a missing course in one quick batch: enter the course identity, select all course photos at once, then let My Play validate them."
                    )

                    st.markdown("#### 1. Course Identity")

                    add_course_name = st.text_input(
                        "Course Name",
                        key="new_course_name",
                        placeholder="e.g. Indian Spring Golf Club"
                    )

                    add_course_address = st.text_input(
                        "Street Address",
                        key="new_course_address",
                        placeholder="e.g. 115 S Elmwood Rd"
                    )

                    identity_col1, identity_col2, identity_col3 = st.columns(
                        [2, 1, 1]
                    )

                    with identity_col1:
                        add_course_city = st.text_input(
                            "City",
                            key="new_course_city"
                        )

                    with identity_col2:
                        add_course_state = st.text_input(
                            "State",
                            value=str(
                                profile.get("default_state", "NJ")
                                or "NJ"
                            ),
                            key="new_course_state"
                        )

                    with identity_col3:
                        add_course_zip = st.text_input(
                            "ZIP",
                            key="new_course_zip",
                            max_chars=10
                        )

                    st.markdown("#### 2. Upload Course Images")

                    st.caption(
                        "Select all images at once. For an 18-hole course, upload 3 images: course/scorecard cover, front nine, and back nine."
                    )

                    new_course_images = st.file_uploader(
                        "Choose all course images",
                        type=["png", "jpg", "jpeg", "webp"],
                        accept_multiple_files=True,
                        key="new_course_scorecard_images"
                    )

                    with st.expander(
                        "📷 Use camera instead (optional)",
                        expanded=False
                    ):
                        st.caption(
                            "Only use this if the photos are not already saved on your phone."
                        )
                        camera_image_1 = st.camera_input(
                            "Photo 1",
                            key="new_course_camera_1"
                        )
                        camera_image_2 = st.camera_input(
                            "Photo 2",
                            key="new_course_camera_2"
                        )
                        camera_image_3 = st.camera_input(
                            "Photo 3",
                            key="new_course_camera_3"
                        )

                    all_new_course_images = list(new_course_images or [])
                    for camera_image in [
                        camera_image_1,
                        camera_image_2,
                        camera_image_3,
                    ]:
                        if camera_image is not None:
                            all_new_course_images.append(camera_image)

                    image_count = len(all_new_course_images)

                    if image_count:
                        st.success(
                            f"{image_count} image"
                            + ("s" if image_count != 1 else "")
                            + " ready."
                        )

                        preview_cols = st.columns(min(image_count, 3))
                        for preview_index, preview_image in enumerate(
                            all_new_course_images[:3]
                        ):
                            with preview_cols[preview_index]:
                                st.image(
                                    preview_image,
                                    use_container_width=True
                                )

                        if image_count > 3:
                            st.caption(
                                f"+ {image_count - 3} more image(s)"
                            )
                    else:
                        st.info(
                            "Select the identity/cover and scorecard images together."
                        )

                    if image_count < 3:
                        st.warning(
                            "A new 18-hole course requires 3 images: identity/cover, front nine, and back nine."
                        )

                    ready_to_validate = (
                        image_count >= 3
                        and bool(str(add_course_name).strip())
                        and bool(str(add_course_address).strip())
                    )

                    if st.button(
                        "Validate Course Images",
                        type="primary",
                        use_container_width=True,
                        disabled=not ready_to_validate,
                        key="validate_new_course_images"
                    ):
                        with st.spinner(
                            "Identifying the images and cross-checking the course..."
                        ):
                            payload, validation_error = extract_course_from_multiple_scorecard_images(
                                all_new_course_images,
                                add_course_name,
                                add_course_city,
                                add_course_state,
                                add_course_address,
                                add_course_zip
                            )

                        if validation_error:
                            st.error(validation_error)
                        else:
                            st.session_state[
                                "pending_validated_course_payload"
                            ] = payload
                            st.rerun()

                    pending_payload = st.session_state.get(
                        "pending_validated_course_payload"
                    )

                    if pending_payload:
                        st.markdown("#### 3. Validation Results")
                        st.success(
                            "My Play found a consistent course identity and scorecard set."
                        )

                        image_roles = pending_payload.get(
                            "image_roles",
                            []
                        )
                        if image_roles:
                            role_labels = []
                            for role_item in image_roles:
                                role_labels.append(
                                    "Image "
                                    + str(role_item.get("index", "?"))
                                    + ": "
                                    + str(
                                        role_item.get("role", "unknown")
                                    ).replace("_", " ").title()
                                )
                            st.caption(" • ".join(role_labels))

                        identity_bits = []
                        if pending_payload.get("course_name"):
                            identity_bits.append(
                                str(pending_payload.get("course_name"))
                            )
                        if pending_payload.get("address"):
                            identity_bits.append(
                                str(pending_payload.get("address"))
                            )

                        location_text = " ".join(
                            part
                            for part in [
                                str(pending_payload.get("city", "") or "").strip(),
                                str(pending_payload.get("state", "") or "").strip(),
                                str(pending_payload.get("zip", "") or "").strip(),
                            ]
                            if part
                        )
                        if location_text:
                            identity_bits.append(location_text)

                        if identity_bits:
                            st.info(
                                "Verified identity: "
                                + " • ".join(identity_bits)
                            )

                        initialize_course_builder_state(pending_payload)

                        st.markdown(
                            "#### 4. Review Extracted Scorecard"
                        )
                        st.caption(
                            "Correct any extraction mistake before saving. This creates a provisional submission and does not overwrite verified system data."
                        )

                        par_df = pd.DataFrame(
                            st.session_state.get(
                                "course_builder_par_rows",
                                []
                            )
                        )
                        yard_df = pd.DataFrame(
                            st.session_state.get(
                                "course_builder_yard_rows",
                                []
                            )
                        )

                        edited_par_df = st.data_editor(
                            par_df,
                            use_container_width=True,
                            hide_index=True,
                            num_rows="fixed",
                            key="new_course_review_par"
                        )
                        edited_yard_df = st.data_editor(
                            yard_df,
                            use_container_width=True,
                            hide_index=True,
                            num_rows="fixed",
                            key="new_course_review_yard"
                        )

                        st.session_state[
                            "course_builder_par_rows"
                        ] = edited_par_df.to_dict(orient="records")
                        st.session_state[
                            "course_builder_yard_rows"
                        ] = edited_yard_df.to_dict(orient="records")

                        save_col, discard_col = st.columns(2)

                        with save_col:
                            if st.button(
                                "Save Provisional Course",
                                type="primary",
                                use_container_width=True,
                                key="save_provisional_course"
                            ):
                                final_payload = build_course_payload_from_builder_state()
                                final_payload["course_name"] = str(
                                    pending_payload.get(
                                        "course_name",
                                        add_course_name
                                    )
                                    or add_course_name
                                    or ""
                                ).strip()
                                final_payload["address"] = str(
                                    pending_payload.get(
                                        "address",
                                        add_course_address
                                    )
                                    or add_course_address
                                    or ""
                                ).strip()
                                final_payload["city"] = str(
                                    pending_payload.get(
                                        "city",
                                        add_course_city
                                    )
                                    or add_course_city
                                    or ""
                                ).strip()
                                final_payload["state"] = str(
                                    pending_payload.get(
                                        "state",
                                        add_course_state
                                    )
                                    or add_course_state
                                    or ""
                                ).strip()
                                final_payload["zip"] = str(
                                    pending_payload.get(
                                        "zip",
                                        add_course_zip
                                    )
                                    or add_course_zip
                                    or ""
                                ).strip()

                                record = course_payload_to_record(
                                    final_payload,
                                    "My Play Course Library"
                                )
                                record["verification_status"] = "Provisional"
                                record["evidence_image_count"] = image_count
                                record["validation_method"] = (
                                    "Multi-image identity + scorecard cross-check"
                                )
                                record["image_roles"] = pending_payload.get(
                                    "image_roles",
                                    []
                                )

                                save_course_record_to_library(
                                    record,
                                    st.session_state.get(
                                        "supabase_user_email",
                                        ""
                                    )
                                )

                                save_course_validation_submission(
                                    record,
                                    all_new_course_images,
                                    status="Provisional"
                                )

                                st.session_state["selected_course"] = record
                                cache_selected_course(record)
                                st.session_state.pop(
                                    "pending_validated_course_payload",
                                    None
                                )
                                clear_course_builder_state()
                                st.rerun()

                        with discard_col:
                            if st.button(
                                "Discard Submission",
                                use_container_width=True,
                                key="discard_provisional_course"
                            ):
                                st.session_state.pop(
                                    "pending_validated_course_payload",
                                    None
                                )
                                clear_course_builder_state()
                                st.rerun()

        # ====================================================
        # COURSE CONFIRMED
        # ====================================================
        else:
            round_course_name = result_name(
                selected_course.get(
                    "search_result",
                    {}
                )
            )

            st.success(
                f"✓ Course confirmed: {round_course_name}"
            )

            if st.button(
                "Change Course",
                use_container_width=True,
                key="live_round_change_course"
            ):
                st.session_state[
                    "selected_course"
                ] = None

                cache_selected_course(
                    {}
                )

                for state_key in [
                    "pending_course_selection",
                    "live_round_course_results",
                    "live_round_course_errors",
                    "round_start_tee",
                    "manual_new_course_name",
                    "manual_new_course_city",
                    "manual_new_course_state",
                    "live_round_search_radius",
                    "last_geo_search",
                    "live_round_course_mode",
                    "existing_course_search_type",
                    "live_round_course_results_page",
                    "live_round_course_city_query",
                    "live_round_course_zip_query",
                    "add_course_method",
                    "new_course_scorecard_upload",
                    "new_course_scorecard_camera",
                    "new_course_name",
                    "new_course_address",
                    "new_course_city",
                    "new_course_state",
                    "new_course_zip",
                    "new_course_scorecard_images",
                    "new_course_camera_1",
                    "new_course_camera_2",
                    "new_course_camera_3",
                    "existing_course_scorecard_images",
                    "existing_course_camera_1",
                    "existing_course_camera_2",
                    "existing_course_camera_3",
                    "pending_validated_course_payload",
                    "pending_existing_course_payload",
                ]:
                    st.session_state.pop(
                        state_key,
                        None
                    )

                clear_course_builder_state()

                st.rerun()

            # ================================================
            # EXISTING/NEW COURSE MISSING DATA
            # ================================================
            if not course_has_playable_data(
                selected_course
            ):
                st.markdown(
                    "### Step 2 — Course Data"
                )

                st.caption(
                    "Full course data is preferred, but it is not required to use your caddie."
                )

                st.info(
                    "You can add verified scorecard data now, or start a limited-data round and use My Play with GPS, weather, your bag, learned club data, voice context, and any shot details you provide."
                )

                limited_col1, limited_col2 = st.columns(
                    2
                )

                with limited_col1:
                    if st.button(
                        "Start Limited-Data Round",
                        type="primary",
                        use_container_width=True,
                        key="start_limited_data_round"
                    ):
                        round_course_name = result_name(
                            selected_course.get(
                                "search_result",
                                {}
                            )
                        )

                        active_round = new_round(
                            round_course_name,
                            selected_course.get(
                                "id",
                                ""
                            ),
                            "Unknown / Limited Data"
                        )

                        active_round[
                            "limited_course_data"
                        ] = True

                        active_round[
                            "course_data_status"
                        ] = "limited"

                        save_active_round(
                            active_round
                        )

                        st.session_state[
                            "round_start_tee"
                        ] = "Unknown / Limited Data"

                        st.rerun()

                with limited_col2:
                    st.caption(
                        "Recommended: add scorecard images for better hole, tee, and strategy awareness."
                    )

                st.markdown(
                    "#### Or Add Missing Course Data"
                )

                st.markdown(
                    "#### Upload Multiple Scorecard Images"
                )

                st.caption(
                    "At least 2 images are required. For 18 holes, 3 images is preferred so My Play can cross-check the full card, front nine, and back nine."
                )

                existing_course_images = st.file_uploader(
                    "Upload scorecard images",
                    type=[
                        "png",
                        "jpg",
                        "jpeg",
                        "webp",
                    ],
                    accept_multiple_files=True,
                    key="existing_course_scorecard_images"
                )

                with st.expander(
                    "📷 Add camera images (optional)",
                    expanded=False
                ):
                    existing_camera_1 = st.camera_input(
                        "Camera image 1",
                        key="existing_course_camera_1"
                    )

                    existing_camera_2 = st.camera_input(
                        "Camera image 2",
                        key="existing_course_camera_2"
                    )

                    existing_camera_3 = st.camera_input(
                        "Camera image 3",
                        key="existing_course_camera_3"
                    )

                all_existing_course_images = list(
                    existing_course_images
                    or []
                )

                for camera_image in [
                    existing_camera_1,
                    existing_camera_2,
                    existing_camera_3,
                ]:
                    if camera_image is not None:
                        all_existing_course_images.append(
                            camera_image
                        )

                st.caption(
                    f"Images attached: {len(all_existing_course_images)}"
                )

                if len(
                    all_existing_course_images
                ) < 2:
                    st.info(
                        "Add at least 2 images before My Play can validate the missing course data."
                    )

                if st.button(
                    "Validate Missing Course Data",
                    type="primary",
                    use_container_width=True,
                    disabled=(
                        len(
                            all_existing_course_images
                        ) < 2
                    ),
                    key="validate_existing_course_images"
                ):
                    search_result = selected_course.get(
                        "search_result",
                        {}
                    )

                    with st.spinner(
                        "Cross-checking scorecard images..."
                    ):
                        payload, validation_error = extract_course_from_multiple_scorecard_images(
                            all_existing_course_images,
                            result_name(search_result),
                            str(
                                search_result.get("city", "")
                                or ""
                            ),
                            str(
                                search_result.get("state", "")
                                or ""
                            ),
                            str(
                                search_result.get("address", "")
                                or selected_course.get(
                                    "detail",
                                    {}
                                ).get("address", "")
                                or ""
                            ),
                            str(
                                search_result.get("zip", "")
                                or search_result.get("postal_code", "")
                                or ""
                            )
                        )

                    if validation_error:
                        st.error(
                            validation_error
                        )

                    else:
                        st.session_state[
                            "pending_existing_course_payload"
                        ] = payload

                        st.rerun()

                pending_existing_payload = st.session_state.get(
                    "pending_existing_course_payload"
                )

                if pending_existing_payload:
                    initialize_course_builder_state(
                        pending_existing_payload
                    )

                    st.success(
                        "The images were consistent enough to create a provisional update."
                    )

                    st.caption(
                        "Review the extracted data. This submission will not overwrite verified data automatically."
                    )

                    par_df = pd.DataFrame(
                        st.session_state.get(
                            "course_builder_par_rows",
                            []
                        )
                    )

                    yard_df = pd.DataFrame(
                        st.session_state.get(
                            "course_builder_yard_rows",
                            []
                        )
                    )

                    edited_par_df = st.data_editor(
                        par_df,
                        use_container_width=True,
                        hide_index=True,
                        num_rows="fixed",
                        key="existing_course_review_par"
                    )

                    edited_yard_df = st.data_editor(
                        yard_df,
                        use_container_width=True,
                        hide_index=True,
                        num_rows="fixed",
                        key="existing_course_review_yard"
                    )

                    st.session_state[
                        "course_builder_par_rows"
                    ] = edited_par_df.to_dict(
                        orient="records"
                    )

                    st.session_state[
                        "course_builder_yard_rows"
                    ] = edited_yard_df.to_dict(
                        orient="records"
                    )

                    existing_confirm_col1, existing_confirm_col2 = st.columns(
                        2
                    )

                    with existing_confirm_col1:
                        if st.button(
                            "Save Provisional Course Data",
                            type="primary",
                            use_container_width=True,
                            key="save_existing_provisional_data"
                        ):
                            final_payload = build_course_payload_from_builder_state()

                            record = course_payload_to_record(
                                final_payload,
                                "My Play Course Library"
                            )

                            record[
                                "verification_status"
                            ] = "Provisional"

                            record[
                                "evidence_image_count"
                            ] = len(
                                all_existing_course_images
                            )

                            record[
                                "validation_method"
                            ] = "Multi-image scorecard cross-check"

                            save_course_record_to_library(
                                record,
                                st.session_state.get(
                                    "supabase_user_email",
                                    ""
                                )
                            )

                            save_course_validation_submission(
                                record,
                                all_existing_course_images,
                                status="Provisional"
                            )

                            st.session_state[
                                "selected_course"
                            ] = record

                            cache_selected_course(
                                record
                            )

                            st.session_state.pop(
                                "pending_existing_course_payload",
                                None
                            )

                            clear_course_builder_state()

                            st.rerun()

                    with existing_confirm_col2:
                        if st.button(
                            "Discard Update",
                            use_container_width=True,
                            key="discard_existing_provisional_data"
                        ):
                            st.session_state.pop(
                                "pending_existing_course_payload",
                                None
                            )

                            clear_course_builder_state()

                            st.rerun()

            else:
                # =============================================
                # STEP 2 — CHOOSE TEES
                # =============================================
                st.markdown(
                    "### Step 2 — Choose Tees"
                )

                tee_rows = normalize_tees(
                    selected_course.get(
                        "tees",
                        {}
                    )
                )

                tee_choices = [
                    str(
                        tee.get(
                            "Tee",
                            ""
                        )
                    ).strip()
                    for tee in tee_rows
                    if str(
                        tee.get(
                            "Tee",
                            ""
                        )
                    ).strip()
                ]

                if not tee_choices:
                    tee_choices = [
                        "Default / Unknown"
                    ]

                selected_round_tee = st.selectbox(
                    "Tee",
                    tee_choices,
                    key="round_start_tee"
                )

                if selected_round_tee:
                    st.markdown(
                        "### Step 3 — Start Round"
                    )

                    st.caption(
                        f"{round_course_name} • {selected_round_tee} tees"
                    )

                    if st.button(
                        "Start Round",
                        type="primary",
                        use_container_width=True,
                        key="start_live_round_button"
                    ):
                        active_round = new_round(
                            round_course_name,
                            selected_course.get(
                                "id",
                                ""
                            ),
                            selected_round_tee
                        )

                        save_active_round(
                            active_round
                        )

                        st.rerun()

    else:
        if active_round.get(
            "limited_course_data"
        ):
            st.caption(
                "Limited Course Data Mode • Caddie is available. My Play may ask for a missing distance, hole, or hazard detail when needed."
            )

        current_hole = int(
            active_round.get(
                "current_hole",
                1
            )
        )

        st.subheader(
            active_round.get(
                "course_name",
                "Current Round"
            )
        )

        round_info1, round_info2, round_info3 = st.columns(
            3
        )

        with round_info1:
            st.metric(
                "Hole",
                current_hole
            )

        with round_info2:
            st.metric(
                "Tee",
                active_round.get(
                    "tee",
                    "—"
                )
            )

        with round_info3:
            saved_scores = active_round.get(
                "scores",
                {}
            )

            running_score = sum(
                int(v)
                for v in saved_scores.values()
                if str(v).isdigit()
            )

            st.metric(
                "Running Strokes",
                running_score
            )

        with st.expander(
            "💡 Live Round Hint",
            expanded=False
        ):
            st.caption(
                "Keep this screen simple while you play: move between holes, open Caddie when you need advice, and record only the score/details you want My Play to learn from."
            )

        st.divider()

        with st.expander(
            "🗣️ Caddie",
            expanded=False
        ):
            st.caption(
                "Ask naturally: “What’s the play?”, “162 into the wind,” or “bunker right.” Voice, typing, and photos are optional."
            )

            live_round_chat_history = st.session_state.get(
                "caddie_chat_history",
                []
            )

            if not live_round_chat_history:
                with st.chat_message(
                    "assistant"
                ):
                    st.write(
                        "I’m with you. Tell me what you’ve got, or just ask, “What’s the play?”"
                    )

            for message in live_round_chat_history[
                -12:
            ]:
                role = str(
                    message.get(
                        "role",
                        ""
                    )
                    or ""
                )

                text = str(
                    message.get(
                        "text",
                        ""
                    )
                    or ""
                ).strip()

                if not text:
                    continue

                with st.chat_message(
                    "user"
                    if role == "Golfer"
                    else "assistant"
                ):
                    st.write(
                        text
                    )

            live_round_photo = None

            with st.expander(
                "📷 Add photo to next message (optional)",
                expanded=False
            ):
                photo_source = st.radio(
                    "Photo source",
                    [
                        "Upload Image",
                        "Use Camera",
                    ],
                    horizontal=True,
                    key="live_round_caddie_photo_source"
                )

                if photo_source == "Upload Image":
                    live_round_photo = st.file_uploader(
                        "Upload lie / target image",
                        type=[
                            "png",
                            "jpg",
                            "jpeg",
                            "webp",
                        ],
                        key="live_round_caddie_photo_upload"
                    )
                else:
                    live_round_photo = st.camera_input(
                        "Take a picture for your caddie",
                        key="live_round_caddie_photo_camera"
                    )

                if live_round_photo is not None:
                    st.caption(
                        "Photo attached to your next caddie message."
                    )

            live_round_voice_audio = None

            if voice_input_ready():
                live_round_voice_audio = st.audio_input(
                    "🎙️ Voice",
                    sample_rate=16000,
                    key="live_round_caddie_voice"
                )

            live_round_typed_text = st.chat_input(
                "Message your caddie...",
                key="live_round_caddie_text"
            )

            if live_round_voice_audio is not None:
                duration = audio_duration_seconds(
                    live_round_voice_audio
                )

                if duration >= 0:
                    if duration > VOICE_MAX_SECONDS:
                        st.error(
                            f"That recording is {duration:.1f}s. The voice limit is "
                            f"{int(VOICE_MAX_SECONDS)} seconds."
                        )
                    else:
                        st.caption(
                            f"Recording: {duration:.1f}s / {int(VOICE_MAX_SECONDS)}s"
                        )

                voice_signature = hashlib.sha256(
                    live_round_voice_audio.getvalue()
                ).hexdigest()

                if (
                    duration <= VOICE_MAX_SECONDS
                    and st.session_state.get(
                        "last_live_round_caddie_voice_signature"
                    ) != voice_signature
                ):
                    with st.spinner(
                        "Listening..."
                    ):
                        voice_text, voice_error = transcribe_protected_openai_voice(
                            live_round_voice_audio
                        )

                    if voice_error:
                        st.error(
                            voice_error
                        )

                    elif voice_text:
                        st.session_state[
                            "last_live_round_caddie_voice_signature"
                        ] = voice_signature

                        st.session_state[
                            "live_round_caddie_pending_text"
                        ] = voice_text

                        st.rerun()

            if live_round_typed_text:
                st.session_state[
                    "live_round_caddie_pending_text"
                ] = live_round_typed_text

                st.rerun()

            live_round_pending_text = str(
                st.session_state.get(
                    "live_round_caddie_pending_text",
                    ""
                )
                or ""
            ).strip()

            if live_round_pending_text:
                try:
                    update_hidden_live_shot_context(
                        live_round_pending_text
                    )
                except Exception:
                    pass

                player_context = build_live_caddie_player_context(
                    bag,
                    shots
                )

                shot_context = hidden_live_shot_context()

                round_context = current_live_caddie_round_context(
                    active_round,
                    selected_course
                )

                st.session_state[
                    "live_caddie_chat_history"
                ] = live_round_chat_history[
                    -16:
                ]

                with st.chat_message(
                    "user"
                ):
                    st.write(
                        live_round_pending_text
                    )

                with st.chat_message(
                    "assistant"
                ):
                    with st.spinner(
                        "Thinking..."
                    ):
                        answer, answer_error = ask_openai_live_caddie(
                            live_round_pending_text,
                            live_round_photo,
                            round_context,
                            player_context,
                            shot_context
                        )

                    if answer_error:
                        st.error(
                            answer_error
                        )

                    elif answer:
                        st.write(
                            answer
                        )

                        live_round_chat_history.append(
                            {
                                "role": "Golfer",
                                "text": live_round_pending_text,
                            }
                        )

                        live_round_chat_history.append(
                            {
                                "role": "Caddie",
                                "text": answer,
                            }
                        )

                        st.session_state[
                            "caddie_chat_history"
                        ] = live_round_chat_history[
                            -40:
                        ]

                        st.session_state[
                            "live_caddie_chat_history"
                        ] = st.session_state[
                            "caddie_chat_history"
                        ]

                        st.session_state.pop(
                            "live_round_caddie_pending_text",
                            None
                        )

                        if st.session_state.get(
                            "caddie_talk_back_enabled",
                            True
                        ):
                            speak_in_browser(
                                answer,
                                key="live_round_caddie_talkback"
                            )

                        st.rerun()

            caddie_action_col1, caddie_action_col2 = st.columns(
                2
            )

            with caddie_action_col1:
                if st.button(
                    "New Shot",
                    use_container_width=True,
                    key="live_round_caddie_new_shot"
                ):
                    for state_key in [
                        "caddie_distance",
                        "caddie_wind_direction",
                        "caddie_wind_strength",
                        "caddie_lie_surface",
                        "caddie_ball_sitting",
                        "caddie_slope",
                        "caddie_slope_severity",
                        "caddie_elevation",
                        "caddie_green_firmness",
                        "caddie_pin_position",
                        "caddie_main_trouble",
                        "caddie_trouble_location",
                        "caddie_safe_side",
                        "caddie_acceptable_miss",
                        "caddie_dead_miss",
                        "caddie_hazard_start",
                        "caddie_hazard_clear",
                        "live_round_caddie_pending_text",
                        "last_live_round_caddie_voice_signature",
                    ]:
                        st.session_state.pop(
                            state_key,
                            None
                        )

                    history = st.session_state.get(
                        "caddie_chat_history",
                        []
                    )

                    history.append(
                        {
                            "role": "Caddie",
                            "text": "New shot. What are you looking at?",
                        }
                    )

                    st.session_state[
                        "caddie_chat_history"
                    ] = history[
                        -40:
                    ]

                    st.rerun()

            with caddie_action_col2:
                if st.button(
                    "Clear Caddie Chat",
                    use_container_width=True,
                    key="live_round_caddie_clear"
                ):
                    for state_key in [
                        "caddie_chat_history",
                        "live_caddie_chat_history",
                        "live_round_caddie_pending_text",
                        "last_live_round_caddie_voice_signature",
                    ]:
                        st.session_state.pop(
                            state_key,
                            None
                        )

                    st.rerun()

        st.divider()

        nav1, nav2, nav3 = st.columns(
            [
                1,
                2,
                1
            ]
        )

        with nav1:
            if st.button(
                "← Previous",
                use_container_width=True,
                disabled=(
                    current_hole <= 1
                )
            ):
                active_round[
                    "current_hole"
                ] = max(
                    1,
                    current_hole - 1
                )

                save_active_round(
                    active_round
                )

                st.rerun()

        with nav2:
            selected_hole = st.selectbox(
                "Jump to Hole",
                list(
                    range(
                        1,
                        19
                    )
                ),
                index=current_hole - 1,
                key="round_hole_jump"
            )

            if selected_hole != current_hole:
                active_round[
                    "current_hole"
                ] = selected_hole

                save_active_round(
                    active_round
                )

                st.rerun()

        with nav3:
            if st.button(
                "Next →",
                use_container_width=True,
                disabled=(
                    current_hole >= 18
                )
            ):
                active_round[
                    "current_hole"
                ] = min(
                    18,
                    current_hole + 1
                )

                save_active_round(
                    active_round
                )

                st.rerun()

        # Hole metadata from selected course if the cached course is the active-round course.
        hole_info = None
        holes_for_round = []

        if selected_course:
            selected_name = result_name(
                selected_course.get(
                    "search_result",
                    {}
                )
            )

            if selected_name == active_round.get(
                "course_name"
            ):
                holes_for_round = normalize_holes(
                    selected_course.get(
                        "holes",
                        {}
                    )
                )

        for h in holes_for_round:
            if str(
                h.get(
                    "Hole"
                )
            ) == str(
                current_hole
            ):
                hole_info = h
                break

        if hole_info:
            h1, h2, h3 = st.columns(
                3
            )

            with h1:
                st.metric(
                    "Par",
                    hole_info.get(
                        "Par",
                        "—"
                    )
                )

            with h2:
                st.metric(
                    "Hole Handicap",
                    hole_info.get(
                        "Handicap",
                        "—"
                    )
                )

            with h3:
                st.metric(
                    "Catalog Yardage",
                    hole_info.get(
                        "Yardage",
                        "—"
                    )
                )

        st.divider()
        st.subheader(
            "🗺️ Hole Plan"
        )

        planner_par = (
            hole_info.get(
                "Par"
            )
            if hole_info
            else None
        )

        planner_yardage = (
            hole_info.get(
                "Yardage"
            )
            if hole_info
            else None
        )

        planner1, planner2, planner3 = st.columns(
            3
        )

        with planner1:
            manual_plan_par = st.selectbox(
                "Par",
                [
                    3,
                    4,
                    5
                ],
                index=(
                    [3, 4, 5].index(
                        int(
                            float(
                                planner_par
                            )
                        )
                    )
                    if planner_par is not None
                    and int(
                        float(
                            planner_par
                        )
                    ) in [
                        3,
                        4,
                        5
                    ]
                    else 1
                ),
                key=f"planner_par_{current_hole}"
            )

        with planner2:
            default_plan_yardage = 500

            try:
                if planner_yardage is not None:
                    default_plan_yardage = int(
                        float(
                            planner_yardage
                        )
                    )
            except Exception:
                pass

            plan_hole_distance = st.number_input(
                "Hole Yardage",
                min_value=80,
                max_value=800,
                value=max(
                    80,
                    min(
                        800,
                        default_plan_yardage
                    )
                ),
                step=1,
                key=f"planner_yardage_{current_hole}"
            )

        with planner3:
            preferred_leave = choose_preferred_scoring_leave(
                bag,
                shots
            )

            st.metric(
                "Preferred Scoring Leave",
                f"{preferred_leave['carry']} yds"
            )

        st.caption(
            f"Current preferred scoring club: {preferred_leave['club']}"
        )

        planner_h1, planner_h2, planner_h3 = st.columns(
            3
        )

        with planner_h1:
            planner_trouble = st.selectbox(
                "Main Hole Trouble",
                [
                    "None",
                    "Bunker",
                    "Water",
                    "Trees",
                    "OB",
                    "Penalty Area"
                ],
                key=f"planner_trouble_{current_hole}"
            )

        with planner_h2:
            planner_trouble_location = st.selectbox(
                "Trouble Side",
                [
                    "Left",
                    "Right",
                    "Center",
                    "Short",
                    "Long"
                ],
                disabled=(
                    planner_trouble == "None"
                ),
                key=f"planner_trouble_location_{current_hole}"
            )

        with planner_h3:
            planner_safe_side = st.selectbox(
                "Preferred Safe Side",
                [
                    "Center",
                    "Left",
                    "Right"
                ],
                key=f"planner_safe_{current_hole}"
            )

        hazard_distance_start = None
        hazard_distance_clear = None

        if planner_trouble != "None":
            hd1, hd2 = st.columns(2)

            with hd1:
                hazard_distance_start = st.number_input(
                    "Trouble Starts At (yards)",
                    min_value=0,
                    max_value=800,
                    value=0,
                    step=1,
                    key=f"planner_hazard_start_{current_hole}",
                    help="Distance from the current shot/tee to the near edge of the trouble."
                )

            with hd2:
                hazard_distance_clear = st.number_input(
                    "Trouble Clears At (yards)",
                    min_value=0,
                    max_value=800,
                    value=0,
                    step=1,
                    key=f"planner_hazard_clear_{current_hole}",
                    help="Distance needed to fully carry the trouble. Leave 0 if not applicable."
                )

        # Build the hole plan automatically. The golfer should not have
        # to press a separate button before asking the caddie.
        plan_options = build_hole_plan_options(
            manual_plan_par,
            plan_hole_distance,
            bag,
            shots,
            planner_trouble,
            planner_trouble_location,
            planner_safe_side,
            hazard_distance_start,
            hazard_distance_clear
        )

        saved_plan = (
            plan_options.get(
                "recommended"
            )
            if plan_options
            else None
        )

        st.session_state[
            f"hole_plan_options_{current_hole}"
        ] = plan_options

        st.session_state[
            f"hole_plan_{current_hole}"
        ] = saved_plan

        if plan_options:
            conservative_plan = plan_options.get(
                "conservative"
            )

            aggressive_plan = plan_options.get(
                "aggressive"
            )

            recommended_plan = plan_options.get(
                "recommended"
            )

            st.markdown(
                "**Caddie's Hole Plan**"
            )

            if recommended_plan:
                recommended_style = (
                    "Conservative"
                    if conservative_plan
                    and recommended_plan.get(
                        "tee_club"
                    ) == conservative_plan.get(
                        "tee_club"
                    )
                    and recommended_plan.get(
                        "second_club"
                    ) == conservative_plan.get(
                        "second_club"
                    )
                    else "Aggressive"
                    if aggressive_plan
                    and recommended_plan.get(
                        "tee_club"
                    ) == aggressive_plan.get(
                        "tee_club"
                    )
                    and recommended_plan.get(
                        "second_club"
                    ) == aggressive_plan.get(
                        "second_club"
                    )
                    else "Balanced"
                )

                st.success(
                    f"Recommended today: {recommended_style} route."
                )

            option1, option2 = st.columns(
                2
            )

            with option1:
                st.markdown(
                    "### 🛡️ Conservative"
                )

                st.info(
                    route_summary_text(
                        conservative_plan,
                        manual_plan_par
                    )
                )

                if conservative_plan:
                    st.write(
                        f"**Aim:** {conservative_plan.get('aim', 'center')}"
                    )

                    st.write(
                        f"**Expected after tee:** {conservative_plan['after_tee']} yds"
                    )

                    st.write(
                        f"**Preferred scoring leave:** "
                        f"{conservative_plan['preferred_leave']} yds"
                    )

                    if conservative_plan.get("center_hazard_note"):
                        st.write(
                            f"**Hazard plan:** {conservative_plan['center_hazard_note']}."
                        )

            with option2:
                st.markdown(
                    (
                        "### 🔥 Aggressive — Go for Two"
                        if aggressive_plan
                        and aggressive_plan.get(
                            "go_for_two"
                        )
                        else "### 🔥 Aggressive"
                    )
                )

                st.warning(
                    route_summary_text(
                        aggressive_plan,
                        manual_plan_par
                    )
                )

                if aggressive_plan:
                    st.write(
                        f"**Aim:** {aggressive_plan.get('aim', 'center')}"
                    )

                    st.write(
                        f"**Expected after tee:** {aggressive_plan['after_tee']} yds"
                    )

                    st.write(
                        f"**Preferred scoring leave:** "
                        f"{aggressive_plan['preferred_leave']} yds"
                    )

                    if aggressive_plan.get("center_hazard_note"):
                        st.write(
                            f"**Hazard plan:** {aggressive_plan['center_hazard_note']}."
                        )

            route_choice = st.radio(
                "Play This Route",
                [
                    "Recommended",
                    "Conservative",
                    "Aggressive"
                ],
                horizontal=True,
                key=f"route_choice_{current_hole}"
            )

            if route_choice == "Conservative":
                saved_plan = conservative_plan

            elif route_choice == "Aggressive":
                saved_plan = aggressive_plan

            else:
                saved_plan = recommended_plan

            st.session_state[
                f"hole_plan_{current_hole}"
            ] = saved_plan

            if saved_plan:
                st.caption(
                    f"Active plan: {route_choice} — "
                    f"{route_summary_text(saved_plan, manual_plan_par)}"
                )


        st.divider()
        st.subheader(
            "📍 Position"
        )

        if GEOLOCATION_AVAILABLE:
            location = streamlit_geolocation()

            if isinstance(
                location,
                dict
            ):
                try:
                    lat_value = location.get(
                        "latitude"
                    )
                    lon_value = location.get(
                        "longitude"
                    )

                    if (
                        lat_value is not None
                        and lon_value is not None
                    ):
                        st.session_state[
                            "gps_latitude"
                        ] = float(
                            lat_value
                        )

                        st.session_state[
                            "gps_longitude"
                        ] = float(
                            lon_value
                        )
                except Exception:
                    pass

            st.caption(
                "Use the location button above and allow location access in the browser."
            )

        else:
            st.warning(
                "Browser GPS helper is not installed. The rest of Live Round works normally."
            )

            st.code(
                "pip install streamlit-geolocation"
            )

        manual1, manual2 = st.columns(
            2
        )

        with manual1:
            manual_lat = st.number_input(
                "Latitude",
                value=float(
                    st.session_state.get(
                        "gps_latitude"
                    )
                    or 0.0
                ),
                format="%.6f",
                key="manual_round_lat"
            )

        with manual2:
            manual_lon = st.number_input(
                "Longitude",
                value=float(
                    st.session_state.get(
                        "gps_longitude"
                    )
                    or 0.0
                ),
                format="%.6f",
                key="manual_round_lon"
            )

        if st.button(
            "Use These Coordinates",
            use_container_width=True
        ):
            if (
                manual_lat != 0
                and manual_lon != 0
            ):
                st.session_state[
                    "gps_latitude"
                ] = manual_lat

                st.session_state[
                    "gps_longitude"
                ] = manual_lon

                st.success(
                    "Current position saved."
                )

        gps_lat = st.session_state.get(
            "gps_latitude"
        )

        gps_lon = st.session_state.get(
            "gps_longitude"
        )

        course_lat, course_lon = selected_course_coordinates(
            selected_course
        )

        weather_lat = (
            gps_lat
            if gps_lat is not None
            else course_lat
        )

        weather_lon = (
            gps_lon
            if gps_lon is not None
            else course_lon
        )

        st.divider()
        st.subheader(
            "🌤️ Live Conditions"
        )

        current_weather = {}

        if (
            weather_lat is not None
            and weather_lon is not None
        ):
            try:
                current_weather = fetch_current_weather(
                    weather_lat,
                    weather_lon
                )
            except Exception as error:
                st.warning(
                    f"Automatic weather is temporarily unavailable: {error}"
                )

        if current_weather:
            w1, w2, w3, w4 = st.columns(
                4
            )

            with w1:
                st.metric(
                    "Temperature",
                    f"{round(float(current_weather.get('temperature_2m', 70)))}°F"
                )

            with w2:
                st.metric(
                    "Wind",
                    f"{round(float(current_weather.get('wind_speed_10m', 0)))} mph"
                )

            with w3:
                wind_degrees = current_weather.get(
                    "wind_direction_10m",
                    0
                )

                st.metric(
                    "Wind From",
                    degrees_to_cardinal(
                        wind_degrees
                    )
                )

            with w4:
                st.metric(
                    "Conditions",
                    weather_code_text(
                        current_weather.get(
                            "weather_code"
                        )
                    )
                )

        else:
            st.caption(
                "Weather will populate automatically when My Play has a course or GPS coordinate."
            )

        nearest_bunker_distance = nearest_mapped_bunker_yards(
            selected_course,
            gps_lat,
            gps_lon
        )

        if nearest_bunker_distance is not None:
            st.caption(
                f"📍 Nearest mapped bunker from current GPS position: "
                f"about {round(nearest_bunker_distance)} yards."
            )

        st.divider()
        st.subheader(
            "🎯 Shot"
        )

        active_hole_plan = st.session_state.get(
            f"hole_plan_{current_hole}"
        )

        # If the planner exists in the current render, use it immediately.
        if "saved_plan" in locals() and saved_plan:
            active_hole_plan = saved_plan

        if active_hole_plan:
            st.success(
                f"Active hole plan: {active_hole_plan['tee_club']} "
                f"to about {active_hole_plan['tee_carry']} yards, "
                f"leaving roughly {active_hole_plan['after_tee']}."
            )

        live_shot_number = determine_round_shot_number(
            active_round.get(
                "round_id",
                ""
            ),
            current_hole,
            load_shots()
        )

        st.caption(
            f"Shot #{live_shot_number} on hole {current_hole}"
        )

        green = mapped_green_for_hole(
            selected_course,
            current_hole
        )

        gps_green_distance = None

        if (
            green
            and gps_lat is not None
            and gps_lon is not None
        ):
            gps_green_distance = gps_distance_yards(
                gps_lat,
                gps_lon,
                green[
                    "latitude"
                ],
                green[
                    "longitude"
                ]
            )

            st.success(
                f"Mapped green-center distance: {round(gps_green_distance)} yards"
            )

        # Shot #1 uses full hole / remaining distance.
        # Later shots use distance to the current target or green.
        if live_shot_number == 1:
            catalog_hole_yards = None

            if hole_info:
                try:
                    catalog_hole_yards = float(
                        hole_info.get(
                            "Yardage"
                        )
                    )
                except Exception:
                    catalog_hole_yards = None

            planner_hole_yards = None

            try:
                planner_hole_yards = float(
                    st.session_state.get(
                        f"planner_yardage_{current_hole}"
                    )
                )
            except Exception:
                planner_hole_yards = None

            if (
                planner_hole_yards is not None
                and 1 <= planner_hole_yards <= 800
            ):
                default_shot_distance = int(
                    round(
                        planner_hole_yards
                    )
                )

            elif (
                catalog_hole_yards is not None
                and 1 <= catalog_hole_yards <= 800
            ):
                default_shot_distance = int(
                    round(
                        catalog_hole_yards
                    )
                )

            else:
                default_shot_distance = 500

            distance_label = "Hole / Remaining Distance (yards)"
        else:
            default_shot_distance = (
                int(
                    round(
                        gps_green_distance
                    )
                )
                if gps_green_distance is not None
                and 1 <= gps_green_distance <= 800
                else 150
            )
            distance_label = "Distance to Target (yards)"

        # New key intentionally clears the stale value from the older widget.
        distance_key = f"live_distance_v3_{current_hole}_{live_shot_number}"

        shot_col1, shot_col2 = st.columns(
            2
        )

        with shot_col1:
            live_distance = st.number_input(
                distance_label,
                min_value=1,
                max_value=800,
                value=max(
                    1,
                    min(
                        800,
                        default_shot_distance
                    )
                ),
                step=1,
                key=distance_key
            )

            live_surface = st.selectbox(
                "Surface",
                [
                    "Fairway",
                    "Light Rough",
                    "Heavy Rough",
                    "Fairway Bunker",
                    "Greenside Bunker",
                    "Hardpan",
                    "Wet / Soft Turf",
                    "Recovery"
                ],
                key=f"live_surface_{current_hole}"
            )

            live_lie_type = st.selectbox(
                "Ball Sitting",
                [
                    "Normal",
                    "Sitting Up",
                    "Flyer",
                    "Buried"
                ],
                key=f"live_lie_{current_hole}"
            )

        with shot_col2:
            live_stance = st.selectbox(
                "Slope / Stance",
                [
                    "Level",
                    "Uphill Lie",
                    "Downhill Lie",
                    "Ball Above Feet",
                    "Ball Below Feet"
                ],
                key=f"live_stance_{current_hole}"
            )

            live_severity = st.selectbox(
                "Slope Severity",
                [
                    "Slight",
                    "Moderate",
                    "Severe"
                ],
                index=1,
                key=f"live_severity_{current_hole}"
            )

            live_wind_relation = st.selectbox(
                "Wind Effect on This Shot",
                [
                    "None",
                    "Into",
                    "Helping",
                    "Left to Right",
                    "Right to Left"
                ],
                key=f"live_wind_{current_hole}"
            )

        # The live shot inherits the hole-plan hazard strategy by default.
        live_trouble = planner_trouble
        live_trouble_location = planner_trouble_location
        live_safe_side = planner_safe_side

        st.caption(
            f"Hole-plan strategy: trouble = {live_trouble}"
            + (
                f" {live_trouble_location.lower()}"
                if live_trouble != "None"
                else ""
            )
            + f"; safe side = {live_safe_side.lower()}."
        )

        with st.expander(
            "Override Trouble for This Shot"
        ):
            override_h1, override_h2, override_h3 = st.columns(
                3
            )

            with override_h1:
                override_trouble = st.selectbox(
                    "Shot-Specific Trouble",
                    [
                        "Use Hole Plan",
                        "None",
                        "Bunker",
                        "Water",
                        "Trees",
                        "OB",
                        "Penalty Area"
                    ],
                    key=f"override_trouble_{current_hole}_{live_shot_number}"
                )

            if override_trouble != "Use Hole Plan":
                live_trouble = override_trouble

                if live_trouble == "None":
                    live_trouble_location = "Center"
                    live_safe_side = planner_safe_side

                else:
                    with override_h2:
                        live_trouble_location = st.selectbox(
                            "Shot-Specific Trouble Location",
                            [
                                "Left",
                                "Right",
                                "Center",
                                "Short",
                                "Long"
                            ],
                            key=f"override_location_{current_hole}_{live_shot_number}"
                        )

                    with override_h3:
                        live_safe_side = st.selectbox(
                            "Shot-Specific Safe Side",
                            [
                                "Center",
                                "Left",
                                "Right"
                            ],
                            key=f"override_safe_{current_hole}_{live_shot_number}"
                        )

        live_pin = st.selectbox(
            "Pin Position",
            [
                "Front",
                "Middle",
                "Back"
            ],
            index=1,
            key=f"live_pin_{current_hole}"
        )

        if st.button(
            "Get Live Caddie Call",
            type="primary",
            use_container_width=True
        ):
            auto_temp = float(
                current_weather.get(
                    "temperature_2m",
                    70
                )
            )

            auto_wind_speed = float(
                current_weather.get(
                    "wind_speed_10m",
                    0
                )
            )

            lie_yards, lie_penalty, lie_notes = lie_adjustment(
                live_surface,
                live_lie_type,
                live_stance,
                live_severity
            )

            current_hole_yardage = None

            if hole_info:
                try:
                    current_hole_yardage = float(
                        hole_info.get(
                            "Yardage"
                        )
                    )
                except Exception:
                    current_hole_yardage = None

            shot_type = shot_type_from_context(
                live_distance,
                live_surface,
                live_trouble,
                current_hole_yardage,
                live_shot_number
            )

            if shot_type == "Tee Shot":
                # On the tee, live_distance is the hole / remaining distance.
                # Club carry determines the expected landing distance.
                play_yards = float(
                    live_distance
                )
                reasons = [
                    "Tee-shot mode: this number is the remaining hole distance. "
                    "The selected club's carry is the expected landing distance."
                ]
            else:
                play_yards, reasons = playing_distance(
                    live_distance,
                    auto_temp,
                    live_wind_relation,
                    auto_wind_speed,
                    0,
                    "Normal",
                    lie_yards
                )

            if (
                shot_type == "Tee Shot"
                and active_hole_plan
            ):
                planned_club_name = active_hole_plan.get(
                    "tee_club"
                )

                matching_options = [
                    item
                    for item in club_options_with_learning(
                        bag,
                        shots
                    )
                    if item[
                        "club"
                    ][
                        "Club"
                    ] == planned_club_name
                ]

                if matching_options:
                    best = matching_options[
                        0
                    ]
                else:
                    best, _ = choose_tee_club(
                        bag,
                        shots,
                        live_distance,
                        live_trouble,
                        live_trouble_location,
                        live_safe_side
                    )

                swing = (
                    f"Execute the hole plan — land this around "
                    f"{active_hole_plan.get('tee_carry', round(best['carry']))} yards."
                )

            elif shot_type == "Tee Shot":
                best, swing = choose_tee_club(
                    bag,
                    shots,
                    live_distance,
                    live_trouble,
                    live_trouble_location,
                    live_safe_side
                )

            elif shot_type == "Layup / Position":
                best, swing = choose_layup_club(
                    bag,
                    shots,
                    preferred_leave=100
                )

            else:
                best, swing = choose_club(
                    bag,
                    shots,
                    play_yards
                )

            club = best[
                "club"
            ]

            club_name = club[
                "Club"
            ]

            carry = best[
                "carry"
            ]

            player_miss = club.get(
                "Typical Miss",
                "unknown"
            )

            dispersion = learned_dispersion_for_club(
                club_name,
                shots
            )

            handedness = profile.get(
                "handedness",
                "Right-handed"
            )

            total_aim_offset = 0.0

            total_aim_offset += stock_miss_aim_offset(
                handedness,
                player_miss
            )

            total_aim_offset += dispersion_aim_offset(
                dispersion
            )

            total_aim_offset += sidehill_aim_offset(
                handedness,
                live_stance,
                live_severity
            )

            total_aim_offset += wind_aim_offset(
                live_wind_relation,
                auto_wind_speed
            )

            hazard_offset, catastrophic = hazard_aim_offset(
                live_trouble,
                live_trouble_location,
                live_safe_side
            )

            total_aim_offset += hazard_offset

            round_memory = hole_memory_summary(
                shots,
                active_round.get(
                    "course_name",
                    ""
                ),
                current_hole
            )

            history_offset, history_note = hole_history_bias(
                round_memory
            )

            total_aim_offset += history_offset

            aim = aim_label_from_offset(
                total_aim_offset
            )

            if (
                shot_type == "Tee Shot"
                and active_hole_plan
                and active_hole_plan.get(
                    "aim"
                )
            ):
                aim = active_hole_plan[
                    "aim"
                ]

            acceptable, dead = miss_windows(
                live_trouble,
                live_trouble_location,
                live_safe_side,
                live_pin
            )

            confidence_score = 4

            if shot_type != "Tee Shot":
                if abs(
                    carry - play_yards
                ) > 5:
                    confidence_score -= 1

                if abs(
                    carry - play_yards
                ) > 12:
                    confidence_score -= 1

            if auto_wind_speed >= 15:
                confidence_score -= 1

            confidence_score -= lie_penalty

            if catastrophic:
                confidence_score -= 1

            if dispersion.get(
                "sample_count",
                0
            ) >= 5:
                confidence_score += 1

            if shot_type == "Recovery":
                confidence_score -= 1

            confidence = (
                "High"
                if confidence_score >= 4
                else "Medium"
                if confidence_score >= 1
                else "Low"
            )

            strategy = build_strategy_decision(
                shot_type,
                club_name,
                aim,
                live_trouble,
                live_trouble_location,
                live_safe_side,
                live_pin,
                play_yards,
                carry,
                history_note
            )

            if (
                shot_type == "Tee Shot"
                and active_hole_plan
            ):
                plan_parts = [
                    f"Hit {club_name} toward {aim}.",
                    f"Ideal landing window: about "
                    f"{max(1, active_hole_plan['tee_carry'] - 10)}–"
                    f"{active_hole_plan['tee_carry'] + 10} yards.",
                    f"Expected remaining distance: roughly "
                    f"{active_hole_plan['after_tee']} yards."
                ]

                if active_hole_plan.get(
                    "second_club"
                ):
                    if active_hole_plan.get(
                        "go_for_two"
                    ):
                        plan_parts.append(
                            f"Second-shot plan: go for the green with "
                            f"{active_hole_plan['second_club']} for about "
                            f"{active_hole_plan['second_carry']} yards."
                        )

                        if active_hole_plan.get(
                            "reach_gap",
                            0
                        ) > 0:
                            plan_parts.append(
                                f"Expected to finish about "
                                f"{active_hole_plan['reach_gap']} yards short "
                                f"if struck to normal carry."
                            )
                    else:
                        plan_parts.append(
                            f"Next-shot plan: {active_hole_plan['second_club']} "
                            f"for about {active_hole_plan['second_carry']} yards."
                        )

                        plan_parts.append(
                            f"Preferred leave: about "
                            f"{active_hole_plan['preferred_leave']} yards "
                            f"for {active_hole_plan['scoring_club']}."
                        )

                if live_trouble != "None":
                    plan_parts.append(
                        f"Dead side: {live_trouble_location.lower()} "
                        f"{live_trouble.lower()}."
                    )

                strategy = " ".join(
                    plan_parts
                )

            st.session_state[
                "live_last_recommendation"
            ] = {
                "club": club_name,
                "playing_distance": round(
                    play_yards,
                    1
                ),
                "confidence": confidence,
                "distance_to_target": live_distance,
                "shot_type": shot_type,
                "aim": aim
            }

            st.success(
                f"{shot_type}: Take {club_display_name(club)}"
            )

            result1, result2, result3, result4 = st.columns(
                4
            )

            with result1:
                st.metric(
                    "Shot Type",
                    shot_type
                )

            with result2:
                st.metric(
                    (
                        "Hole Remaining"
                        if shot_type == "Tee Shot"
                        else "Plays Like"
                    ),
                    f"{round(play_yards)} yds"
                )

            with result3:
                st.metric(
                    (
                        "Expected Landing"
                        if shot_type == "Tee Shot"
                        else "Expected Carry"
                    ),
                    f"{round(carry)} yds"
                )

            with result4:
                st.metric(
                    "Confidence",
                    confidence
                )

            st.subheader(
                "🧠 Caddie Decision"
            )

            current_plan_options = st.session_state.get(
                f"hole_plan_options_{current_hole}"
            )

            if shot_type == "Tee Shot" and current_plan_options:
                live_cons = current_plan_options.get("conservative")
                live_aggr = current_plan_options.get("aggressive")
                live_reco = current_plan_options.get("recommended")

                rc1, rc2 = st.columns(2)

                with rc1:
                    st.markdown("### 🛡️ Conservative Option")
                    st.info(
                        route_summary_text(
                            live_cons,
                            manual_plan_par
                        )
                    )
                    if live_cons:
                        st.caption(
                            f"Aim {live_cons.get('aim', 'center')} · "
                            f"after tee ~{live_cons.get('after_tee')} yds"
                        )

                with rc2:
                    st.markdown(
                        (
                            "### 🔥 Aggressive Option — Go for Two"
                            if live_aggr
                            and live_aggr.get(
                                "go_for_two"
                            )
                            else "### 🔥 Aggressive Option"
                        )
                    )
                    st.warning(
                        route_summary_text(
                            live_aggr,
                            manual_plan_par
                        )
                    )
                    if live_aggr:
                        st.caption(
                            f"Aim {live_aggr.get('aim', 'center')} · "
                            f"after tee ~{live_aggr.get('after_tee')} yds"
                        )

                if live_reco:
                    reco_name = (
                        "Conservative"
                        if live_cons
                        and live_reco.get("tee_club") == live_cons.get("tee_club")
                        and live_reco.get("second_club") == live_cons.get("second_club")
                        else "Aggressive"
                        if live_aggr
                        and live_reco.get("tee_club") == live_aggr.get("tee_club")
                        and live_reco.get("second_club") == live_aggr.get("second_club")
                        else "Balanced"
                    )
                    st.success(
                        f"My Play recommends the {reco_name} route for this hole."
                    )

            st.markdown("**Why My Play Prefers This Route**")

            tee_dispersion_for_reason = learned_dispersion_for_club(
                club_name,
                shots
            )

            recommendation_reason = route_recommendation_reason(
                live_cons if shot_type == "Tee Shot" and current_plan_options else None,
                live_aggr if shot_type == "Tee Shot" and current_plan_options else None,
                live_reco if shot_type == "Tee Shot" and current_plan_options else active_hole_plan,
                live_trouble,
                live_trouble_location,
                tee_dispersion_for_reason
            )

            st.write(
                recommendation_reason
            )

            st.markdown("**Active Caddie Call**")

            st.info(
                strategy
            )

            coaching_points = build_caddie_coaching_points(
                shot_type,
                live_stance,
                live_severity,
                live_surface,
                live_wind_relation,
                auto_wind_speed,
                player_miss,
                dispersion,
                round_memory,
                live_trouble,
                live_trouble_location,
                active_hole_plan,
                gps_green_distance
            )

            if coaching_points:
                st.markdown(
                    "**Caddie Coaching Points**"
                )

                for point in coaching_points:
                    st.write(
                        f"• {point}"
                    )

            unified_notes = unified_context_summary(
                club_name,
                bag,
                shots,
                round_memory,
                current_weather,
                gps_green_distance
            )

            if unified_notes:
                with st.expander(
                    "What My Play Used for This Decision"
                ):
                    for note in unified_notes:
                        st.write(
                            f"• {note}"
                        )

            if (
                shot_type == "Tee Shot"
                and active_hole_plan
            ):
                hp1, hp2, hp3 = st.columns(
                    3
                )

                with hp1:
                    st.metric(
                        "Ideal Landing Window",
                        f"{max(1, active_hole_plan['tee_carry'] - 10)}–"
                        f"{active_hole_plan['tee_carry'] + 10} yds"
                    )

                with hp2:
                    st.metric(
                        "Expected Remaining",
                        f"{active_hole_plan['after_tee']} yds"
                    )

                with hp3:
                    st.metric(
                        (
                            "Second-Shot Goal"
                            if active_hole_plan.get(
                                "go_for_two"
                            )
                            else "Preferred Leave"
                        ),
                        (
                            "Green"
                            if active_hole_plan.get(
                                "go_for_two"
                            )
                            else f"{active_hole_plan['preferred_leave']} yds"
                        )
                    )

            st.write(
                f"**Swing / Intent:** {swing}"
            )

            miss1, miss2 = st.columns(
                2
            )

            with miss1:
                st.caption(
                    f"Acceptable miss: {acceptable}"
                )

            with miss2:
                if catastrophic:
                    st.error(
                        f"Dead Miss: {dead}"
                    )
                else:
                    st.caption(
                        f"Avoid: {dead}"
                    )

            if round_memory:
                st.write(
                    f"**Hole Memory:** {round_memory.get('count', 0)} saved shot(s) on this hole."
                )

                if round_memory.get(
                    "common_result"
                ):
                    st.write(
                        f"Most common saved result here: {round_memory['common_result']}."
                    )

            if dispersion.get(
                "sample_count",
                0
            ) >= 5:
                st.write(
                    f"**Learned dispersion:** {dispersion['sample_count']} recorded "
                    f"{club_name} shots; dominant miss = {dispersion['dominant_miss']}."
                )

                if dispersion.get(
                    "carry_std"
                ) is not None:
                    st.write(
                        f"**Carry dispersion:** ±{round(dispersion['carry_std'])} yards standard deviation."
                    )

            if reasons:
                with st.expander(
                    "Why it plays this distance"
                ):
                    for reason in reasons:
                        st.write(
                            f"• {reason}"
                        )

        with st.expander(
            "➕ Save Shot (optional)",
            expanded=False
        ):
            st.caption(
                "Optional: save a shot when you want My Play to learn from the result."
            )

            live_bag_names = [
                club[
                    "Club"
                ]
                for club in bag
            ]

            recommended_live_club = st.session_state.get(
                "live_last_recommendation",
                {}
            ).get(
                "club",
                live_bag_names[
                    0
                ]
                if live_bag_names
                else ""
            )

            live_index = (
                live_bag_names.index(
                    recommended_live_club
                )
                if recommended_live_club in live_bag_names
                else 0
            )

            save1, save2 = st.columns(
                2
            )

            with save1:
                live_club_used = st.selectbox(
                    "Club Used",
                    live_bag_names,
                    index=live_index,
                    key=f"live_club_used_{current_hole}"
                )

                live_actual_carry = st.number_input(
                    "Actual Carry",
                    min_value=0,
                    max_value=400,
                    value=150,
                    step=1,
                    key=f"live_actual_carry_{current_hole}"
                )

            with save2:
                live_result = st.selectbox(
                    "Shot Result",
                    [
                        "On Target",
                        "Short",
                        "Long",
                        "Left",
                        "Right",
                        "Short Left",
                        "Short Right",
                        "Long Left",
                        "Long Right"
                    ],
                    key=f"live_result_{current_hole}"
                )

                live_contact = st.selectbox(
                    "Contact",
                    [
                        "Solid",
                        "Slight Mishit",
                        "Poor Contact"
                    ],
                    key=f"live_contact_{current_hole}"
                )

            if st.button(
                "Save Live Shot",
                use_container_width=True
            ):
                live_rec = st.session_state.get(
                    "live_last_recommendation",
                    {}
                )

                save_shot({
                    "Date": datetime.now().strftime(
                        "%Y-%m-%d %H:%M"
                    ),
                    "Round ID": active_round.get(
                        "round_id",
                        ""
                    ),
                    "Course": active_round.get(
                        "course_name",
                        ""
                    ),
                    "Hole": current_hole,
                    "Distance To Pin": live_rec.get(
                        "distance_to_target",
                        live_distance
                    ),
                    "Playing Distance": live_rec.get(
                        "playing_distance",
                        live_distance
                    ),
                    "Recommended Club": live_rec.get(
                        "club",
                        "None"
                    ),
                    "Shot Type": live_rec.get(
                        "shot_type",
                        ""
                    ),
                    "Recommended Aim": live_rec.get(
                        "aim",
                        ""
                    ),
                    "Club Used": live_club_used,
                    "Actual Carry": live_actual_carry,
                    "Result": live_result,
                    "Contact": live_contact,
                    "Shot Shape": "Normal",
                    "Surface": live_surface,
                    "Lie Type": live_lie_type,
                    "Slope / Stance": live_stance,
                    "Slope Severity": live_severity,
                    "Temperature": float(
                        current_weather.get(
                            "temperature_2m",
                            70
                        )
                    ),
                    "Wind Direction": live_wind_relation,
                    "Wind Speed": float(
                        current_weather.get(
                            "wind_speed_10m",
                            0
                        )
                    ),
                    "Elevation": 0,
                    "Green Firmness": "Normal",
                    "Pin Position": live_pin,
                    "Trouble Type": live_trouble,
                    "Trouble Location": (
                        live_trouble_location
                        if live_trouble != "None"
                        else "None"
                    ),
                    "Safe Side": live_safe_side,
                    "Latitude": gps_lat,
                    "Longitude": gps_lon,
                    "Note": "Live Round"
                })

                st.toast(
                    "Live shot saved."
                )

                st.rerun()

        with st.expander(
            "✏️ Score This Hole",
            expanded=True
        ):
            st.caption(
                "Record the hole when you’re ready. Everything else can stay closed while you play."
            )

            score_col1, score_col2, score_col3, score_col4 = st.columns(
                4
            )

            existing_score = active_round.get(
                "scores",
                {}
            ).get(
                str(
                    current_hole
                ),
                4
            )

            existing_putts = active_round.get(
                "putts",
                {}
            ).get(
                str(
                    current_hole
                ),
                2
            )

            with score_col1:
                hole_score = st.number_input(
                    "Strokes",
                    min_value=1,
                    max_value=20,
                    value=int(
                        existing_score
                    ),
                    step=1,
                    key=f"round_score_{current_hole}"
                )

            with score_col2:
                hole_putts = st.number_input(
                    "Putts",
                    min_value=0,
                    max_value=10,
                    value=int(
                        existing_putts
                    ),
                    step=1,
                    key=f"round_putts_{current_hole}"
                )

            with score_col3:
                fairway_status = st.selectbox(
                    "Fairway",
                    [
                        "N/A",
                        "Hit",
                        "Miss Left",
                        "Miss Right",
                        "Miss Short"
                    ],
                    key=f"round_fairway_{current_hole}"
                )

            with score_col4:
                green_status = st.selectbox(
                    "Green",
                    [
                        "Hit",
                        "Miss Left",
                        "Miss Right",
                        "Miss Short",
                        "Miss Long"
                    ],
                    key=f"round_green_{current_hole}"
                )

            if st.button(
                "Save Hole",
                use_container_width=True
            ):
                active_round.setdefault(
                    "scores",
                    {}
                )[
                    str(
                        current_hole
                    )
                ] = int(
                    hole_score
                )

                active_round.setdefault(
                    "putts",
                    {}
                )[
                    str(
                        current_hole
                    )
                ] = int(
                    hole_putts
                )

                active_round.setdefault(
                    "fairways",
                    {}
                )[
                    str(
                        current_hole
                    )
                ] = fairway_status

                active_round.setdefault(
                    "greens",
                    {}
                )[
                    str(
                        current_hole
                    )
                ] = green_status

                save_active_round(
                    active_round
                )

                st.toast(
                    f"Hole {current_hole} saved."
                )

                st.rerun()

            with st.expander(
                "Round Scorecard"
            ):
                score_rows = []

                for hole_num in range(
                    1,
                    19
                ):
                    score_rows.append({
                        "Hole": hole_num,
                        "Score": active_round.get(
                            "scores",
                            {}
                        ).get(
                            str(
                                hole_num
                            ),
                            ""
                        ),
                        "Putts": active_round.get(
                            "putts",
                            {}
                        ).get(
                            str(
                                hole_num
                            ),
                            ""
                        ),
                        "Fairway": active_round.get(
                            "fairways",
                            {}
                        ).get(
                            str(
                                hole_num
                            ),
                            ""
                        ),
                        "Green": active_round.get(
                            "greens",
                            {}
                        ).get(
                            str(
                                hole_num
                            ),
                            ""
                        )
                    })

                st.dataframe(
                    pd.DataFrame(
                        score_rows
                    ),
                    use_container_width=True,
                    hide_index=True
                )

        st.divider()

        if st.button(
            "End Round",
            type="secondary",
            use_container_width=True,
            key="end_round_and_exit"
        ):
            append_round_history(
                active_round
            )

            clear_active_round()

            clear_live_round_session_state(
                clear_course=True
            )

            st.session_state[
                "round_exit_message"
            ] = (
                "Round saved. My Play registered the complete round and built your "
                "Round Biography in My Player → Round Biographies."
            )

            st.rerun()


# ============================================================
# COURSES
# ============================================================


    if st.session_state.get(
        "last_spoken_recommendation"
    ):
        if st.button(
            "🔊 Repeat Last Recommendation",
            use_container_width=True,
            key="repeat_last_caddie_recommendation"
        ):
            speak_in_browser(
                st.session_state[
                    "last_spoken_recommendation"
                ],
                key="repeat_caddie_talk_back"
            )


with tab_voice_command:
    st.header(
        "🗣️ Caddie"
    )

    try:
        active_round = load_active_round()
    except Exception:
        active_round = None

    selected_course = st.session_state.get(
        "selected_course"
    )

    if active_round:
        round_context = current_live_caddie_round_context(
            active_round,
            selected_course
        )

        context_bits = []

        if round_context.get(
            "course"
        ):
            context_bits.append(
                str(
                    round_context[
                        "course"
                    ]
                )
            )

        context_bits.append(
            f"Hole {round_context.get('hole', 1)}"
        )

        if round_context.get(
            "par"
        ):
            context_bits.append(
                f"Par {round_context['par']}"
            )

        if round_context.get(
            "tee"
        ):
            context_bits.append(
                f"{round_context['tee']} tees"
            )

        if round_context.get(
            "hole_yardage"
        ) is not None:
            try:
                context_bits.append(
                    f"{round(float(round_context['hole_yardage']))} yds"
                )
            except Exception:
                pass

        st.caption(
            " • ".join(
                context_bits
            )
        )
    else:
        round_context = {
            "course": None,
            "hole": None,
            "tee": None,
            "hole_yardage": None,
            "par": None,
        }

        st.caption(
            "Off-course mode • Ask about your clubs, strategy, or your game."
        )

    with st.expander(
        "💡 How to use Caddie",
        expanded=False
    ):
        st.caption(
            "Talk or type naturally. During a Live Round, My Play also uses the current hole and shot context automatically."
        )

    chat_history = st.session_state.get(
        "caddie_chat_history",
        []
    )

    if not chat_history:
        with st.chat_message(
            "assistant"
        ):
            st.write(
                "I’m ready. Tell me what you’re looking at, ask about a club, or just ask, “What’s the play?”"
            )

    for message in chat_history:
        role = str(
            message.get(
                "role",
                ""
            )
            or ""
        )

        text = str(
            message.get(
                "text",
                ""
            )
            or ""
        ).strip()

        if not text:
            continue

        with st.chat_message(
            "user"
            if role == "Golfer"
            else "assistant"
        ):
            st.write(
                text
            )

    with st.expander(
        "＋ Voice / Photo",
        expanded=False
    ):
        photo_file = None

        st.caption(
            "Attach a photo only when showing the lie or target is easier than describing it."
        )

        photo_file = st.file_uploader(
            "Photo",
            type=[
                "png",
                "jpg",
                "jpeg",
                "webp",
            ],
            key="caddie_running_chat_photo"
        )

        if photo_file is not None:
            st.caption(
                "Photo attached to your next message."
            )

        voice_status = voice_usage_status()

        if voice_status.get(
            "ok"
        ):
            remaining = int(
                voice_status.get(
                    "remaining",
                    0
                )
            )

            st.caption(
                f"Voice remaining today: {remaining}/{VOICE_DAILY_LIMIT}"
            )

        voice_audio = None

        if voice_input_ready():
            voice_audio = st.audio_input(
                "🎙️ Voice message",
                sample_rate=16000,
                key="caddie_running_chat_voice"
            )

    typed_text = st.chat_input(
        "Message your caddie..."
    )

    if voice_audio is not None:
        duration = audio_duration_seconds(
            voice_audio
        )

        if duration >= 0:
            if duration > VOICE_MAX_SECONDS:
                st.error(
                    f"That recording is {duration:.1f}s. The voice limit is "
                    f"{int(VOICE_MAX_SECONDS)} seconds."
                )
            else:
                st.caption(
                    f"Recording: {duration:.1f}s / {int(VOICE_MAX_SECONDS)}s"
                )

        voice_signature = hashlib.sha256(
            voice_audio.getvalue()
        ).hexdigest()

        if (
            duration <= VOICE_MAX_SECONDS
            and st.session_state.get(
                "last_caddie_running_voice_signature"
            ) != voice_signature
        ):
            with st.spinner(
                "Listening..."
            ):
                voice_text, voice_error = transcribe_protected_openai_voice(
                    voice_audio
                )

            if voice_error:
                st.error(
                    voice_error
                )

            elif voice_text:
                st.session_state[
                    "last_caddie_running_voice_signature"
                ] = voice_signature

                st.session_state[
                    "caddie_running_pending_text"
                ] = voice_text

                st.rerun()

    if typed_text:
        st.session_state[
            "caddie_running_pending_text"
        ] = typed_text

        st.rerun()

    pending_text = str(
        st.session_state.get(
            "caddie_running_pending_text",
            ""
        )
        or ""
    ).strip()

    if pending_text:
        if active_round:
            try:
                update_hidden_live_shot_context(
                    pending_text
                )
            except Exception:
                pass

        player_context = build_live_caddie_player_context(
            bag,
            shots
        )

        shot_context = hidden_live_shot_context()

        # The OpenAI helper reads this shared history.
        st.session_state[
            "live_caddie_chat_history"
        ] = chat_history[
            -16:
        ]

        with st.chat_message(
            "user"
        ):
            st.write(
                pending_text
            )

        with st.chat_message(
            "assistant"
        ):
            with st.spinner(
                "Thinking..."
            ):
                answer, answer_error = ask_openai_live_caddie(
                    pending_text,
                    photo_file,
                    round_context,
                    player_context,
                    shot_context
                )

            if answer_error:
                st.error(
                    answer_error
                )

            elif answer:
                st.write(
                    answer
                )

                chat_history.append(
                    {
                        "role": "Golfer",
                        "text": pending_text,
                    }
                )

                chat_history.append(
                    {
                        "role": "Caddie",
                        "text": answer,
                    }
                )

                st.session_state[
                    "caddie_chat_history"
                ] = chat_history[
                    -40:
                ]

                st.session_state[
                    "live_caddie_chat_history"
                ] = st.session_state[
                    "caddie_chat_history"
                ]

                st.session_state.pop(
                    "caddie_running_pending_text",
                    None
                )

                if st.session_state.get(
                    "caddie_talk_back_enabled",
                    True
                ):
                    speak_in_browser(
                        answer,
                        key="caddie_running_chat_talkback"
                    )

                st.rerun()

    action_col1, action_col2 = st.columns(
        2
    )

    with action_col1:
        if st.button(
            "New Shot",
            use_container_width=True,
            key="caddie_running_new_shot"
        ):
            for state_key in [
                "caddie_distance",
                "caddie_wind_direction",
                "caddie_wind_strength",
                "caddie_lie_surface",
                "caddie_ball_sitting",
                "caddie_slope",
                "caddie_slope_severity",
                "caddie_elevation",
                "caddie_green_firmness",
                "caddie_pin_position",
                "caddie_main_trouble",
                "caddie_trouble_location",
                "caddie_safe_side",
                "caddie_acceptable_miss",
                "caddie_dead_miss",
                "caddie_hazard_start",
                "caddie_hazard_clear",
                "caddie_running_pending_text",
                "last_caddie_running_voice_signature",
            ]:
                st.session_state.pop(
                    state_key,
                    None
                )

            history = st.session_state.get(
                "caddie_chat_history",
                []
            )

            history.append(
                {
                    "role": "Caddie",
                    "text": "New shot. What are you looking at?",
                }
            )

            st.session_state[
                "caddie_chat_history"
            ] = history[
                -40:
            ]

            st.rerun()

    with action_col2:
        if st.button(
            "Clear Chat",
            use_container_width=True,
            key="caddie_running_clear_chat"
        ):
            for state_key in [
                "caddie_chat_history",
                "live_caddie_chat_history",
                "caddie_running_pending_text",
                "last_caddie_running_voice_signature",
            ]:
                st.session_state.pop(
                    state_key,
                    None
                )

            st.rerun()

with tab_bag:
    st.header(
        "My Bag"
    )
    st.caption(
        "Hint: Keep your stock carries and typical misses current. My Play combines these with learned shot data."
    )

    # Voice bag management was intentionally removed from this screen.
    if False:
        st.caption(
            "Speak a bag change, review it, then confirm before My Play saves anything."
        )

        st.write(
            'Examples: "Add a 5 wood, Ping, 235 carry."  '
            '"Change my 8 iron carry to 168."  '
            '"Delete my 60 degree wedge."'
        )

        if not voice_input_ready():
            st.warning(
                "OpenAI voice transcription is not available."
            )
            st.code(
                "pip install openai",
                language="bash"
            )
        else:
            bag_voice_audio = st.audio_input(
                "Bag voice command",
                sample_rate=16000,
                key="my_play_native_voice_bag"
            )

            if bag_voice_audio is not None:
                bag_voice_signature = (
                    hashlib.sha256(
                        bag_voice_audio.getvalue()
                    ).hexdigest(),
                    len(
                        bag_voice_audio.getvalue()
                    )
                )

                if st.session_state.get(
                    "last_native_voice_bag_signature"
                ) != bag_voice_signature:
                    with st.spinner(
                        "Listening..."
                    ):
                        bag_voice_text, bag_voice_error = transcribe_protected_openai_voice(
                            bag_voice_audio
                        )

                    st.session_state[
                        "last_native_voice_bag_signature"
                    ] = bag_voice_signature

                    if bag_voice_error:
                        st.error(
                            bag_voice_error
                        )
                    elif bag_voice_text:
                        st.session_state[
                            "voice_bag_command_text"
                        ] = str(
                            bag_voice_text
                        ).strip()

            current_command = st.session_state.get(
                "voice_bag_command_text",
                ""
            )

            if current_command:
                edited_command = st.text_area(
                    "What My Play heard",
                    value=current_command,
                    height=90,
                    key="voice_bag_command_edit"
                )

                parsed_command = parse_voice_bag_command(
                    edited_command
                )
                preview = build_voice_bag_preview(
                    parsed_command
                )

                rows = []
                for label, field in [
                    ("Action", "action"),
                    ("Club", "club"),
                    ("Brand / Model", "brand_model"),
                    ("Loft", "loft"),
                    ("Stock Carry", "stock_carry"),
                    ("Typical Miss", "typical_miss"),
                ]:
                    value = parsed_command.get(field)
                    if value is not None:
                        rows.append(
                            {
                                "Field": label,
                                "Detected": value,
                            }
                        )

                if rows:
                    st.dataframe(
                        pd.DataFrame(rows),
                        hide_index=True,
                        use_container_width=True
                    )

                st.info(
                    preview.get(
                        "message",
                        ""
                    )
                )

                if preview.get("current"):
                    st.markdown("**Current club**")
                    st.json(preview["current"])

                if preview.get("proposed"):
                    st.markdown("**Proposed club**")
                    st.json(preview["proposed"])

                confirm_col, clear_col = st.columns(2)

                with confirm_col:
                    if st.button(
                        "Confirm Bag Update",
                        type="primary",
                        use_container_width=True,
                        disabled=not preview.get("valid", False),
                        key="confirm_voice_bag_update"
                    ):
                        success, message = commit_voice_bag_change(
                            preview
                        )

                        if success:
                            st.success(message)
                            st.session_state.pop(
                                "voice_bag_command_text",
                                None
                            )
                            st.rerun()
                        else:
                            st.error(message)

                with clear_col:
                    if st.button(
                        "Clear Bag Command",
                        use_container_width=True,
                        key="clear_voice_bag_command"
                    ):
                        st.session_state.pop(
                            "voice_bag_command_text",
                            None
                        )
                        st.rerun()


    bag_mode = st.session_state.get("bag_manage_mode", "view")

    if bag_mode == "view":
        heading_col, add_col = st.columns([3, 1])
        with heading_col:
            st.subheader(f"{len(bag)} clubs")
            st.caption("Select any club card to view or edit its details.")
        with add_col:
            if st.button(
                "＋ Add Club", type="primary", use_container_width=True,
                key="bag_add_mode",
            ):
                st.session_state["bag_manage_mode"] = "add"
                st.session_state.pop("bag_delete_pending", None)
                st.rerun()

        for row_start in range(0, len(bag), 3):
            card_columns = st.columns(3)
            for offset, column in enumerate(card_columns):
                bag_index = row_start + offset
                if bag_index >= len(bag):
                    continue
                club = bag[bag_index]
                club_name = str(club.get("Club", "Club") or "Club")
                brand, model = split_brand_model(club)
                brand_model = " • ".join(value for value in [brand, model] if value)
                loft = str(club.get("Loft", "") or "Loft not set")
                carry = round(float(club.get("Stock Carry", 0) or 0))
                miss = str(club.get("Typical Miss", "unknown") or "unknown").title()
                confidence = str(club.get("Confidence", "Developing") or "Developing")
                card_label = (
                    f"**{club_name}**\n\n"
                    f"{brand_model or 'Brand/model not set'}\n\n"
                    f"**{carry} yd** carry  •  {loft}\n\n"
                    f"{miss}  •  {confidence}"
                )
                with column:
                    with st.container(key=f"club_card_{bag_index}"):
                        if st.button(
                            card_label,
                            use_container_width=True,
                            key=f"open_club_{bag_index}",
                        ):
                            st.session_state["bag_edit_choice"] = club_name
                            st.session_state["bag_manage_mode"] = "edit"
                            st.session_state.pop("bag_delete_pending", None)
                            st.rerun()

    elif bag_mode == "add":
        if st.button("← Back to My Bag", key="bag_add_back"):
            st.session_state["bag_manage_mode"] = "view"
            st.rerun()
        st.header("Add a club")
        st.caption("Choose one step at a time. My Play standardizes the club automatically.")
        new_club = render_club_builder("bag_add")
        save_col, cancel_col = st.columns(2)
        with save_col:
            if st.button("Save Club", type="primary", use_container_width=True, key="bag_add_save"):
                if not new_club.get("Club"):
                    st.warning("Enter the club name before saving.")
                elif any(
                    canonical_club_id(item.get("Club")) == new_club["Canonical ID"]
                    for item in bag
                ):
                    st.warning("That club is already in your bag. Choose Edit Club instead.")
                else:
                    save_json(BAG_FILE, list(bag) + [new_club])
                    st.session_state["bag_manage_mode"] = "view"
                    st.success(f"{new_club['Club']} added.")
                    st.rerun()
        with cancel_col:
            if st.button("Cancel", use_container_width=True, key="bag_add_cancel"):
                st.session_state["bag_manage_mode"] = "view"
                st.rerun()

    elif bag_mode == "edit" and bag:
        edit_names = [str(item.get("Club", "")) for item in bag]
        edit_name = st.session_state.get("bag_edit_choice", edit_names[0])
        if edit_name not in edit_names:
            edit_name = edit_names[0]
        edit_index = edit_names.index(edit_name)
        if st.button("← Back to My Bag", key="bag_edit_back"):
            st.session_state["bag_manage_mode"] = "view"
            st.session_state.pop("bag_delete_pending", None)
            st.rerun()
        st.header(f"Edit {edit_name}")
        st.caption("Update the club and save. Changes are used by analytics and the caddie.")
        edit_club = render_club_builder(
            f"bag_edit_{canonical_club_id(edit_name)}", bag[edit_index]
        )
        save_col, cancel_col, delete_col = st.columns([2, 1, 1])
        with save_col:
            if st.button("Save Changes", type="primary", use_container_width=True, key="bag_edit_save"):
                updated_bag = list(bag)
                updated_bag[edit_index] = edit_club
                save_json(BAG_FILE, updated_bag)
                st.session_state["bag_manage_mode"] = "view"
                st.session_state.pop("bag_delete_pending", None)
                st.success(f"{edit_club['Club']} updated.")
                st.rerun()
        with cancel_col:
            if st.button("Cancel", use_container_width=True, key="bag_edit_cancel"):
                st.session_state["bag_manage_mode"] = "view"
                st.session_state.pop("bag_delete_pending", None)
                st.rerun()
        with delete_col:
            if st.button("Delete Club", use_container_width=True, key="bag_edit_delete"):
                st.session_state["bag_delete_pending"] = edit_name
                st.rerun()

        if st.session_state.get("bag_delete_pending") == edit_name:
            st.warning(
                f"Delete {edit_name} from My Bag? Recorded shot history will remain intact."
            )
            confirm_col, keep_col = st.columns(2)
            with confirm_col:
                if st.button(
                    "Yes, Delete Club", type="primary", use_container_width=True,
                    key="bag_delete_confirm",
                ):
                    updated_bag = [
                        item for item in bag
                        if str(item.get("Club", "")) != edit_name
                    ]
                    save_json(BAG_FILE, updated_bag)
                    st.session_state["bag_manage_mode"] = "view"
                    st.session_state.pop("bag_delete_pending", None)
                    st.rerun()
            with keep_col:
                if st.button(
                    "Keep Club", use_container_width=True, key="bag_delete_cancel"
                ):
                    st.session_state.pop("bag_delete_pending", None)
                    st.rerun()

if False:  # Retained legacy analytics block; replaced by the clean view below.
    st.divider()
    st.subheader(
        "Learned Club Distances"
    )

    learned_rows = []

    for club in bag:
        stock = float(
            club.get(
                "Stock Carry",
                0
            )
        )

        learned, count = learned_carry_for_club(
            club["Club"],
            stock,
            shots
        )

        learned_rows.append({
            "Club": club["Club"],
            "Stock Carry": round(
                stock,
                1
            ),
            "My Play Carry": round(
                learned,
                1
            ),
            "Solid Shots": count,
            "Learning Status": (
                "Learned"
                if count >= 3
                else f"Need {3 - count} more"
            )
        })

    st.dataframe(
        pd.DataFrame(
            learned_rows
        ),
        use_container_width=True,
        hide_index=True
    )

    st.divider()
    st.subheader(
        "Unified Player Model"
    )

    unified_rows = []

    for club in bag:
        profile_row = unified_club_profile(
            club["Club"],
            float(
                club.get(
                    "Stock Carry",
                    0
                )
            ),
            shots
        )

        unified_rows.append({
            "Club": club["Club"],
            "Unified Carry": round(
                profile_row["carry"],
                1
            ),
            "Evidence": profile_row[
                "sample_count"
            ],
            "Effective Weight": profile_row[
                "effective_weight"
            ],
            "Dominant Miss": profile_row[
                "dominant_miss"
            ],
            "Carry SD": (
                round(
                    profile_row[
                        "carry_std"
                    ],
                    1
                )
                if profile_row[
                    "carry_std"
                ] is not None
                else ""
            ),
            "Sources": ", ".join(
                f"{key}:{value}"
                for key, value in profile_row[
                    "source_breakdown"
                ].items()
            )
        })

    st.dataframe(
        pd.DataFrame(
            unified_rows
        ),
        use_container_width=True,
        hide_index=True
    )

with tab_data:
    st.header("Data Uploads")
    st.caption(
        "Import simulator, launch-monitor, range, and previous-round data. "
        "My Play preserves every original column before mapping recognized metrics."
    )
    st.subheader("Quick CSV Import")

    import_source = st.radio(
        "Session Type",
        [
            "Simulator",
            "Launch Monitor",
            "Driving Range"
        ],
        horizontal=True,
        key="evidence_import_source"
    )

    uploaded_csv = st.file_uploader(
        "Upload session CSV",
        type=[
            "csv"
        ]
    )

    if uploaded_csv is not None:
        try:
            sim = pd.read_csv(
                uploaded_csv
            )

            st.dataframe(
                sim.head(
                    10
                ),
                use_container_width=True,
                hide_index=True
            )

            columns = list(
                sim.columns
            )

            if columns:
                club_col = st.selectbox(
                    "Club Column",
                    columns
                )

                carry_col = st.selectbox(
                    "Carry Distance Column",
                    columns,
                    index=(
                        1
                        if len(
                            columns
                        ) > 1
                        else 0
                    )
                )

                optional_columns = [
                    "None"
                ] + columns

                result_col_choice = st.selectbox(
                    "Result / Direction Column (optional)",
                    optional_columns,
                    key="import_result_col"
                )

                contact_col_choice = st.selectbox(
                    "Contact Quality Column (optional)",
                    optional_columns,
                    key="import_contact_col"
                )

                with st.expander(
                    "Advanced Launch Monitor Fields (optional)"
                ):
                    total_col_choice = st.selectbox(
                        "Total Distance",
                        optional_columns,
                        key="import_total_col"
                    )

                    offline_col_choice = st.selectbox(
                        "Offline / Lateral",
                        optional_columns,
                        key="import_offline_col"
                    )

                    ball_speed_col_choice = st.selectbox(
                        "Ball Speed",
                        optional_columns,
                        key="import_ball_speed_col"
                    )

                    club_speed_col_choice = st.selectbox(
                        "Club Speed",
                        optional_columns,
                        key="import_club_speed_col"
                    )

                    launch_col_choice = st.selectbox(
                        "Launch Angle",
                        optional_columns,
                        key="import_launch_col"
                    )

                    spin_col_choice = st.selectbox(
                        "Spin Rate",
                        optional_columns,
                        key="import_spin_col"
                    )

                    apex_col_choice = st.selectbox(
                        "Apex / Peak Height",
                        optional_columns,
                        key="import_apex_col"
                    )

                temp = sim[
                    [
                        club_col,
                        carry_col
                    ]
                ].copy()

                temp[
                    carry_col
                ] = pd.to_numeric(
                    temp[
                        carry_col
                    ],
                    errors="coerce"
                )

                temp = temp.dropna()

                averages = (
                    temp
                    .groupby(
                        club_col
                    )[
                        carry_col
                    ]
                    .agg(
                        [
                            "mean",
                            "count"
                        ]
                    )
                    .reset_index()
                )

                averages[
                    "mean"
                ] = averages[
                    "mean"
                ].round(
                    1
                )

                st.dataframe(
                    averages,
                    use_container_width=True,
                    hide_index=True
                )

                if st.button(
                    f"Import {import_source} Session Into My Play",
                    type="primary",
                    use_container_width=True
                ):
                    raw_saved, raw_message = preserve_raw_import(
                        sim,
                        getattr(uploaded_csv, "name", "session.csv"),
                        import_source,
                    )
                    if not raw_saved:
                        st.warning(raw_message)
                        st.stop()

                    evidence_rows = imported_session_to_evidence(
                        sim,
                        club_col,
                        carry_col,
                        import_source,
                        (
                            None
                            if result_col_choice == "None"
                            else result_col_choice
                        ),
                        (
                            None
                            if contact_col_choice == "None"
                            else contact_col_choice
                        ),
                        {
                            "Total": total_col_choice,
                            "Offline": offline_col_choice,
                            "Ball Speed": ball_speed_col_choice,
                            "Club Speed": club_speed_col_choice,
                            "Launch": launch_col_choice,
                            "Spin": spin_col_choice,
                            "Apex": apex_col_choice
                        }
                    )

                    append_player_evidence(
                        evidence_rows
                    )

                    st.success(
                        f"Imported {len(evidence_rows)} {import_source.lower()} shot(s) into the Unified Player Model."
                    )

                    st.rerun()

        except Exception as error:
            st.error(
                f"Could not read that CSV: {error}"
            )

# ============================================================
# SHOT HISTORY
# ============================================================



    st.divider()

    st.header(
        "📥 Update Club Data"
    )

    st.caption(
        "Range, simulator, imported files, and extracted photo data all become player evidence used by My Play."
    )

    update_mode = st.radio(
        "How do you want to add data?",
        [
            "Manual Range Entry",
            "Upload File",
            "Upload / Photo Import",
        ],
        horizontal=True,
        key="club_data_update_mode"
    )

    if update_mode == "Manual Range Entry":
        available_clubs = [
            str(
                club.get(
                    "Club",
                    ""
                )
            ).strip()
            for club in bag
            if str(
                club.get(
                    "Club",
                    ""
                )
            ).strip()
        ]

        manual_col1, manual_col2 = st.columns(
            2
        )

        with manual_col1:
            manual_club = st.selectbox(
                "Club",
                available_clubs,
                key="manual_range_club"
            )

            manual_carry = st.number_input(
                "Carry (yards)",
                min_value=1.0,
                max_value=400.0,
                step=1.0,
                key="manual_range_carry"
            )

            manual_total = st.number_input(
                "Total Distance",
                min_value=0.0,
                max_value=450.0,
                step=1.0,
                key="manual_range_total"
            )

            manual_offline = st.number_input(
                "Offline / Lateral",
                min_value=-100.0,
                max_value=100.0,
                step=1.0,
                key="manual_range_offline"
            )

        with manual_col2:
            manual_ball_speed = st.number_input(
                "Ball Speed",
                min_value=0.0,
                max_value=250.0,
                step=1.0,
                key="manual_range_ball_speed"
            )

            manual_club_speed = st.number_input(
                "Club Speed",
                min_value=0.0,
                max_value=180.0,
                step=1.0,
                key="manual_range_club_speed"
            )

            manual_launch = st.number_input(
                "Launch Angle",
                min_value=-10.0,
                max_value=60.0,
                step=0.1,
                key="manual_range_launch"
            )

            manual_spin = st.number_input(
                "Spin Rate",
                min_value=0.0,
                max_value=15000.0,
                step=50.0,
                key="manual_range_spin"
            )

        manual_contact = st.selectbox(
            "Contact",
            [
                "Solid",
                "Average",
                "Poor",
                "Mishit",
            ],
            key="manual_range_contact"
        )

        manual_note = st.text_input(
            "Optional note",
            key="manual_range_note"
        )

        if st.button(
            "Add Range Shot",
            type="primary",
            use_container_width=True,
            key="manual_range_add"
        ):
            success, message = append_club_evidence_record(
                manual_club,
                manual_carry,
                "Driving Range",
                total_distance=manual_total or None,
                offline=manual_offline,
                ball_speed=manual_ball_speed or None,
                club_speed=manual_club_speed or None,
                launch_angle=manual_launch or None,
                spin_rate=manual_spin or None,
                contact=manual_contact,
                note=manual_note or None
            )

            if success:
                st.success(
                    message
                )

                st.rerun()
            else:
                st.error(
                    message
                )

    elif update_mode == "Upload File":
        uploaded_club_file = st.file_uploader(
            "Upload simulator / range data",
            type=[
                "csv",
                "xlsx",
                "xls",
            ],
            key="club_data_file_upload"
        )

        st.caption(
            "Best columns: Club, Carry. Optional: Total Distance, Offline, Ball Speed, "
            "Club Speed, Launch Angle, Spin Rate, Apex, Contact, Shot Shape, Note."
        )

        import_source = st.selectbox(
            "Data source",
            [
                "Simulator",
                "Launch Monitor",
                "Driving Range",
                "Previous Round",
                "Manual",
            ],
            key="club_data_file_source"
        )

        if uploaded_club_file is not None:
            try:
                import pandas as pd

                if uploaded_club_file.name.lower().endswith(
                    ".csv"
                ):
                    import_df = pd.read_csv(
                        uploaded_club_file
                    )
                else:
                    import_df = pd.read_excel(
                        uploaded_club_file
                    )

                st.dataframe(
                    import_df.head(
                        20
                    ),
                    use_container_width=True
                )

                if st.button(
                    "Import Club Data",
                    type="primary",
                    use_container_width=True,
                    key="import_club_data_file"
                ):
                    raw_saved, raw_message = preserve_raw_import(
                        import_df,
                        getattr(uploaded_club_file, "name", "uploaded_data"),
                        import_source,
                    )
                    if not raw_saved:
                        st.warning(raw_message)
                        st.stop()

                    imported, errors = import_club_evidence_dataframe(
                        import_df,
                        import_source
                    )

                    if imported:
                        st.success(
                            f"Imported {imported} shot record"
                            + (
                                "s."
                                if imported != 1
                                else "."
                            )
                        )

                    for error in errors[
                        :10
                    ]:
                        st.warning(
                            error
                        )

                    if imported:
                        st.rerun()

            except Exception as exc:
                st.error(
                    f"Could not read the file: {exc}"
                )

    else:
        club_data_upload = st.file_uploader(
            "Upload a simulator / range data image",
            type=[
                "png",
                "jpg",
                "jpeg",
                "webp",
            ],
            key="club_data_image_upload"
        )

        club_data_photo = None

        with st.expander(
            "📷 Use camera instead (optional)",
            expanded=False
        ):
            club_data_photo = st.camera_input(
                "Take a picture of simulator / range data",
                key="club_data_photo"
            )

        active_club_data_image = club_data_upload or club_data_photo

        if active_club_data_image is not None:
            if st.button(
                "Extract Club Data",
                type="primary",
                use_container_width=True,
                key="extract_club_data_photo"
            ):
                with st.spinner(
                    "Reading the data..."
                ):
                    extracted_rows, extract_error = extract_club_data_from_photo(
                        active_club_data_image
                    )

                if extract_error:
                    st.error(
                        extract_error
                    )
                else:
                    st.session_state[
                        "pending_extracted_club_rows"
                    ] = extracted_rows

                    st.rerun()

        extracted_rows = st.session_state.get(
            "pending_extracted_club_rows",
            []
        )

        if extracted_rows:
            import pandas as pd

            extracted_df = pd.DataFrame(
                extracted_rows
            )

            st.dataframe(
                extracted_df,
                use_container_width=True
            )

            st.caption(
                "Review the extracted values before saving them as player evidence."
            )

            if st.button(
                "Save Extracted Data",
                type="primary",
                use_container_width=True,
                key="save_extracted_club_data"
            ):
                raw_saved, raw_message = preserve_raw_import(
                    extracted_df,
                    getattr(active_club_data_image, "name", "simulator_photo"),
                    "Simulator Photo",
                )
                if not raw_saved:
                    st.warning(raw_message)
                    st.stop()

                imported = 0
                errors = []

                for row_index, row in enumerate(
                    extracted_rows
                ):
                    success, message = append_club_evidence_record(
                        row.get(
                            "club"
                        ),
                        row.get(
                            "carry"
                        ),
                        "Simulator",
                        total_distance=row.get(
                            "total_distance"
                        ),
                        offline=row.get(
                            "offline"
                        ),
                        ball_speed=row.get(
                            "ball_speed"
                        ),
                        club_speed=row.get(
                            "club_speed"
                        ),
                        launch_angle=row.get(
                            "launch_angle"
                        ),
                        spin_rate=row.get(
                            "spin_rate"
                        ),
                        apex=row.get(
                            "apex"
                        ),
                        contact=row.get(
                            "contact",
                            "Solid"
                        ),
                        shot_shape=row.get(
                            "shot_shape"
                        ),
                        note=row.get(
                            "note"
                        ),
                    )

                    if success:
                        imported += 1
                    else:
                        errors.append(
                            f"Row {row_index + 1}: {message}"
                        )

                if imported:
                    st.success(
                        f"Saved {imported} extracted record"
                        + (
                            "s."
                            if imported != 1
                            else "."
                        )
                    )

                    st.session_state.pop(
                        "pending_extracted_club_rows",
                        None
                    )

                    st.rerun()

                for error in errors:
                    st.warning(
                        error
                    )


with tab_club_analytics:
    st.header("Club Analytics")
    st.caption(
        "A clean view of what My Play has learned. Open only the section you need."
    )

    analytics_snapshot = player_snapshot(load_round_history(), all_player_evidence)
    analytics_endurance = endurance_phase_table(all_player_evidence)

    analytics_col1, analytics_col2, analytics_col3 = st.columns(3)
    analytics_col1.metric("Clubs", len(bag))
    analytics_col2.metric("Shots learned", analytics_snapshot["shots"])
    analytics_col3.metric("Model confidence", analytics_snapshot["confidence"])

    with st.expander("Bag gapping", expanded=True):
        gap_table = bag_gapping_table(bag, shots)
        if gap_table.empty:
            st.info("Add clubs to My Bag to build your yardage book.")
        else:
            st.dataframe(gap_table, use_container_width=True, hide_index=True)
        for note in caddie_essentials_summary(bag, shots):
            st.write(f"• {note}")

    with st.expander("Individual club", expanded=True):
        club_names = [club.get("Club", "") for club in bag if club.get("Club")]
        if not club_names:
            st.info("Add a club to My Bag before opening individual analytics.")
        else:
            selected_club_analytics = st.selectbox(
                "Choose club", club_names, key="clean_club_analytics_selector"
            )
            selected_club_record = next(
                (club for club in bag if club.get("Club") == selected_club_analytics), None
            )
            club_stats = comprehensive_club_analytics(selected_club_record, shots)
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Reliable carry", f"{club_stats['reliable_carry']:.0f} yd")
            c2.metric("Playing carry", f"{club_stats['playing_carry']:.0f} yd")
            c3.metric("Evidence", club_stats["sample_count"])
            c4.metric("Confidence", club_stats["confidence"])

            d1, d2, d3 = st.columns(3)
            d1.metric(
                "Carry dispersion",
                f"{club_stats['carry_std']:.1f} yd"
                if club_stats["carry_std"] is not None else "Need data",
            )
            d2.metric("Dominant miss", club_stats["dominant_miss"])
            solid_rate = club_stats["solid_contact_rate"]
            d3.metric(
                "Solid contact",
                f"{solid_rate * 100:.0f}%" if solid_rate is not None else "Need data",
            )

            st.markdown("**How My Play should caddie this club**")
            for point in caddie_number_guidance(club_stats):
                st.write(f"• {point}")

            with st.expander("Advanced evidence", expanded=False):
                dispersion_df = pd.DataFrame([
                    {"Miss": "Left", "Rate": round(club_stats["left_rate"] * 100, 1)},
                    {"Miss": "Right", "Rate": round(club_stats["right_rate"] * 100, 1)},
                    {"Miss": "Short", "Rate": round(club_stats["short_rate"] * 100, 1)},
                    {"Miss": "Long", "Rate": round(club_stats["long_rate"] * 100, 1)},
                ])
                st.dataframe(dispersion_df, use_container_width=True, hide_index=True)
                if club_stats["source_performance"]:
                    source_rows = [
                        {
                            "Source": source_name,
                            "Shots": source_stats["count"],
                            "Average carry": source_stats["carry"],
                        }
                        for source_name, source_stats in club_stats["source_performance"].items()
                    ]
                    st.dataframe(pd.DataFrame(source_rows), use_container_width=True, hide_index=True)

    with st.expander("Endurance and fatigue pattern", expanded=False):
        if analytics_endurance.empty:
            st.info(
                "My Play needs shot sequences attached to completed rounds before it can "
                "compare opening, middle, late and extended performance."
            )
        else:
            st.dataframe(analytics_endurance, use_container_width=True, hide_index=True)
            st.caption(
                "My Play compares carry relative to each club's own baseline so changing clubs "
                "is not mistaken for fatigue."
            )

    with st.expander("How the player model works", expanded=False):
        st.write(
            "Stock bag values begin the model. On-course, range and launch-monitor evidence "
            "then adjusts carry, dispersion, contact and confidence. Conclusions remain marked "
            "as building until enough comparable evidence exists."
        )


if False:  # Retained legacy analytics block; replaced by the clean view above.
    st.header(
        "📈 Club Analytics"
    )

    st.caption(
        "My Play turns all available range, simulator, and on-course evidence into caddie-ready numbers."
    )

    gap_table = bag_gapping_table(
        bag,
        shots
    )

    st.subheader(
        "Caddie Yardage Book"
    )

    st.dataframe(
        gap_table,
        use_container_width=True,
        hide_index=True
    )

    essential_notes = caddie_essentials_summary(
        bag,
        shots
    )

    if essential_notes:
        st.markdown(
            "**Bag / Data Alerts**"
        )

        for note in essential_notes:
            st.write(
                f"• {note}"
            )

    st.divider()

    selected_club_analytics = st.selectbox(
        "Club",
        [
            club[
                "Club"
            ]
            for club in bag
        ],
        key="club_analytics_selector"
    )

    selected_club_record = next(
        (
            club
            for club in bag
            if isinstance(
                club,
                dict
            )
            and str(
                club.get(
                    "Club",
                    ""
                )
            ) == str(
                selected_club_analytics
            )
        ),
        None
    )

    club_stats = comprehensive_club_analytics(
        selected_club_record,
        shots
    )

    a1, a2, a3, a4 = st.columns(
        4
    )

    with a1:
        st.metric(
            "Reliable Carry",
            f"{club_stats['reliable_carry']:.0f} yds"
        )

    with a2:
        st.metric(
            "Playing Carry",
            f"{club_stats['playing_carry']:.0f} yds"
        )

    with a3:
        st.metric(
            "Upper Carry",
            f"{club_stats['upper_carry']:.0f} yds"
        )

    with a4:
        st.metric(
            "Confidence",
            club_stats[
                "confidence"
            ]
        )

    b1, b2, b3, b4 = st.columns(
        4
    )

    with b1:
        st.metric(
            "Evidence",
            club_stats[
                "sample_count"
            ]
        )

    with b2:
        st.metric(
            "Carry SD",
            (
                f"{club_stats['carry_std']:.1f} yds"
                if club_stats[
                    "carry_std"
                ] is not None
                else "Need data"
            )
        )

    with b3:
        st.metric(
            "Dominant Miss",
            club_stats[
                "dominant_miss"
            ]
        )

    with b4:
        solid_rate = club_stats[
            "solid_contact_rate"
        ]

        st.metric(
            "Solid Contact",
            (
                f"{solid_rate * 100:.0f}%"
                if solid_rate is not None
                else "Need data"
            )
        )

    if club_stats[
        "recent_carry"
    ] is not None:
        st.markdown(
            "**Current Form**"
        )

        recent_delta = club_stats[
            "recent_vs_baseline"
        ]

        st.write(
            f"Recent weighted carry: **{club_stats['recent_carry']:.1f} yards** "
            f"({recent_delta:+.1f} vs unified baseline)."
        )

    st.markdown(
        "**Dispersion Profile**"
    )

    dispersion_df = pd.DataFrame(
        [
            {
                "Miss": "Left",
                "Rate": round(
                    club_stats[
                        "left_rate"
                    ] * 100,
                    1
                )
            },
            {
                "Miss": "Right",
                "Rate": round(
                    club_stats[
                        "right_rate"
                    ] * 100,
                    1
                )
            },
            {
                "Miss": "Short",
                "Rate": round(
                    club_stats[
                        "short_rate"
                    ] * 100,
                    1
                )
            },
            {
                "Miss": "Long",
                "Rate": round(
                    club_stats[
                        "long_rate"
                    ] * 100,
                    1
                )
            }
        ]
    )

    st.dataframe(
        dispersion_df,
        use_container_width=True,
        hide_index=True
    )

    if club_stats[
        "source_performance"
    ]:
        st.markdown(
            "**Performance by Data Source**"
        )

        source_rows = []

        for source_name, source_stats in club_stats[
            "source_performance"
        ].items():
            source_rows.append({
                "Source": source_name,
                "Shots": source_stats[
                    "count"
                ],
                "Average Carry": source_stats[
                    "carry"
                ]
            })

        st.dataframe(
            pd.DataFrame(
                source_rows
            ),
            use_container_width=True,
            hide_index=True
        )

    if club_stats[
        "optional_metrics"
    ]:
        st.markdown(
            "**Launch Monitor Profile**"
        )

        metric_rows = [
            {
                "Metric": key,
                "Average": value
            }
            for key, value in club_stats[
                "optional_metrics"
            ].items()
        ]

        st.dataframe(
            pd.DataFrame(
                metric_rows
            ),
            use_container_width=True,
            hide_index=True
        )

    st.markdown(
        "**How My Play Should Caddie This Club**"
    )

    for point in caddie_number_guidance(
        club_stats
    ):
        st.write(
            f"• {point}"
        )

    st.info(
        "As you add simulator, range, and real-round shots, these numbers will tighten automatically. "
        "The reliable carry is intentionally more conservative than the normal playing carry."
    )



with tab_swing_video:
    st.header(
        "🎥 Swing Video Beta"
    )

    st.caption(
        "Save swings by club, create a personal baseline, and compare future swings to your own normal pattern."
    )


    if st.session_state.get(
        "last_video_save_message"
    ):
        st.success(
            st.session_state.pop(
                "last_video_save_message"
            )
        )

    if st.session_state.get(
        "last_video_cloud_upload"
    ):
        st.success(
            st.session_state.pop(
                "last_video_cloud_upload"
            )
        )

    if st.session_state.get(
        "last_video_cloud_error"
    ):
        st.warning(
            "The swing was saved locally, but the private cloud upload failed: "
            + st.session_state[
                "last_video_cloud_error"
            ]
        )

    st.info(
        "On a phone, the video picker can usually let you record a new video or choose one already on the device. "
        "New videos are stored privately in your My Play cloud account. Automated AI vision analysis will plug into this same history later."
    )

    video_club = st.selectbox(
        "Club",
        [
            club[
                "Club"
            ]
            for club in bag
        ],
        key="swing_video_club"
    )

    session_type = st.selectbox(
        "Session",
        [
            "Driving Range",
            "Simulator",
            "Practice",
            "Warm-Up",
            "On Course",
            "Lesson"
        ],
        key="swing_video_session"
    )

    swing_label = st.text_input(
        "Swing Label",
        placeholder="Example: Normal 7 Iron, Driver warm-up, Best swing",
        key="swing_video_label"
    )

    if "swing_video_uploader_version" not in st.session_state:
        st.session_state[
            "swing_video_uploader_version"
        ] = 0

    uploaded_swing = st.file_uploader(
        "Record or upload swing video",
        type=[
            "mp4",
            "mov",
            "m4v",
            "avi",
            "webm"
        ],
        key=(
            "swing_video_upload_"
            + str(
                st.session_state[
                    "swing_video_uploader_version"
                ]
            )
        )
    )

    baseline_now = st.checkbox(
        "Use this as my baseline for this club",
        key="swing_video_baseline_now"
    )

    if uploaded_swing is not None:
        uploaded_mime = (
            uploaded_swing.type
            or swing_video_mime_type(
                uploaded_swing.name
            )
        )

        try:
            st.video(
                uploaded_swing.getvalue(),
                format=uploaded_mime
            )
        except Exception as exc:
            st.warning(
                f"Video selected, but the browser could not preview it: {exc}"
            )

        st.caption(
            f"Selected file: {uploaded_swing.name} · "
            f"Detected type: {uploaded_mime}"
        )

        if st.button(
            "Save Swing Video",
            type="primary",
            use_container_width=True,
            key="save_swing_video_button"
        ):
            saved_id = save_uploaded_swing_video(
                uploaded_swing,
                video_club,
                session_type,
                swing_label.strip()
                or f"{video_club} swing",
                baseline_now
            )

            st.session_state[
                "last_video_save_message"
            ] = (
                "Swing video saved. My Play created a browser-safe "
                "H.264 MP4 when conversion support was available."
            )

            st.session_state[
                "swing_video_uploader_version"
            ] += 1

            st.rerun()

    st.divider()

    video_history = load_swing_video_history()

    if video_history.empty:
        st.warning(
            "No swing videos saved yet."
        )
    else:
        st.subheader(
            "Swing Library"
        )

        st.caption(
            "Choose one saved swing to open. Only the selected swing is shown below."
        )

        video_options = {}

        for _, row in video_history.iloc[
            ::-1
        ].iterrows():
            baseline_badge = (
                " ★ BASELINE"
                if str(
                    row.get(
                        "Baseline",
                        False
                    )
                ).lower() in (
                    "true",
                    "1",
                    "yes"
                )
                else ""
            )

            option_label = (
                f"{row.get('Date', '')} · "
                f"{row.get('Club', '')} · "
                f"{row.get('Session Type', '')} · "
                f"{row.get('Label', '')}"
                f"{baseline_badge}"
            )

            video_options[
                option_label
            ] = str(
                row.get(
                    "Video ID",
                    ""
                )
            )

        selected_label = st.selectbox(
            "Saved Swing",
            list(
                video_options.keys()
            ),
            key="review_swing_video"
        )

        selected_id = video_options[
            selected_label
        ]

        selected_rows = video_history[
            video_history[
                "Video ID"
            ].astype(
                str
            ) == selected_id
        ]

        if not selected_rows.empty:
            selected_row = selected_rows.iloc[-1]

            selected_path = str(
                selected_row.get(
                    "Path",
                    ""
                )
            ).strip()

            if (
                not selected_path
                or (
                    not os.path.exists(
                        selected_path
                    )
                    and "/" not in selected_path
                )
            ):
                local_fallback_path = local_swing_video_path_for_id(
                    selected_id
                )

                if local_fallback_path:
                    selected_path = local_fallback_path

            with st.expander(
                "Video Storage Check",
                expanded=True
            ):
                st.write(
                    f"Stored path: `{selected_path or 'missing'}`"
                )

                st.write(
                    "Local fallback exists: "
                    + (
                        "Yes"
                        if (
                            selected_path
                            and os.path.exists(
                                selected_path
                            )
                        )
                        else "No"
                    )
                )

                st.write(
                    f"Detected video type: `{swing_video_mime_type(selected_path)}`"
                )

                if _cloud_ready():
                    try:
                        cloud_files = (
                            supabase
                            .storage
                            .from_(
                                SWING_VIDEO_BUCKET
                            )
                            .list(
                                _cloud_user_id(),
                                {
                                    "limit": 100,
                                    "offset": 0
                                }
                            )
                        )

                        cloud_names = [
                            str(
                                item.get(
                                    "name",
                                    ""
                                )
                            )
                            for item in (
                                cloud_files
                                or []
                            )
                        ]

                        st.write(
                            f"Private cloud folder contains {len(cloud_names)} file(s)."
                        )

                        if selected_path:
                            selected_name = selected_path.split(
                                "/"
                            )[-1]

                            st.write(
                                "Selected file found in cloud folder: "
                                + (
                                    "Yes"
                                    if selected_name in cloud_names
                                    else "No"
                                )
                            )

                    except Exception as exc:
                        st.write(
                            f"Could not list private cloud folder: {exc}"
                        )

                st.caption(
                    "For a newly saved cloud video, the private folder count should be "
                    "at least 1. If it is 0, My Play is playing the local safety copy."
                )

            selected_video_source, selected_video_mime = resolve_swing_video_source(
                selected_path
            )

            if selected_video_source:
                file_size_mb = None

                if os.path.exists(
                    selected_video_source
                ):
                    try:
                        file_size_mb = (
                            os.path.getsize(
                                selected_video_source
                            )
                            / 1024
                            / 1024
                        )
                    except Exception:
                        file_size_mb = None

                st.video(
                    selected_video_source,
                    format=selected_video_mime
                )

                st.caption(
                    f"Playback file: {selected_video_source} · "
                    f"{selected_video_mime}"
                    + (
                        f" · {file_size_mb:.2f} MB"
                        if file_size_mb is not None
                        else ""
                    )
                )
            else:
                st.warning(
                    "The swing video file could not be opened."
                )

            selected_club = str(
                selected_row.get(
                    "Club",
                    ""
                )
            )

            baseline_row = baseline_for_club(
                selected_club,
                video_history
            )

            baseline_text = (
                "Yes"
                if (
                    baseline_row is not None
                    and str(
                        baseline_row.get(
                            "Video ID",
                            ""
                        )
                    ) == selected_id
                )
                else "No"
            )

            info1, info2, info3 = st.columns(
                3
            )

            with info1:
                st.metric(
                    "Club",
                    selected_club
                )

            with info2:
                st.metric(
                    "Session",
                    str(
                        selected_row.get(
                            "Session Type",
                            ""
                        )
                    )
                    or "—"
                )

            with info3:
                st.metric(
                    "Baseline",
                    baseline_text
                )

            action1, action2 = st.columns(
                2
            )

            with action1:
                if st.button(
                    "★ Set as Baseline",
                    use_container_width=True,
                    key=f"set_video_baseline_{selected_id}"
                ):
                    set_swing_video_baseline(
                        selected_id
                    )

                    st.success(
                        f"Baseline updated for {selected_club}."
                    )

                    st.rerun()

            with action2:
                if st.button(
                    "Delete Swing",
                    use_container_width=True,
                    key=f"delete_video_{selected_id}"
                ):
                    delete_saved_swing_video(
                        selected_id,
                        selected_path
                    )

                    st.session_state[
                        "last_video_save_message"
                    ] = "Swing deleted."

                    st.rerun()

            st.markdown(
                "**Swing Observations**"
            )

            st.caption(
                "For now these are structured observations you can save while reviewing the swing. "
                "The AI vision version will populate the same fields automatically."
            )

            observation_choices = {
                "Tempo": [
                    "",
                    "Smooth",
                    "Quick",
                    "Slow",
                    "Rushed transition",
                    "Even"
                ],
                "Setup": [
                    "",
                    "Normal",
                    "More upright",
                    "More bent",
                    "Open",
                    "Closed"
                ],
                "Balance": [
                    "",
                    "Balanced",
                    "Falling forward",
                    "Falling back",
                    "Toward toes",
                    "Toward heels"
                ],
                "Backswing": [
                    "",
                    "Normal",
                    "Short",
                    "Long",
                    "Inside",
                    "Outside"
                ],
                "Transition": [
                    "",
                    "Smooth",
                    "Quick",
                    "Paused",
                    "Steep",
                    "Shallow"
                ],
                "Finish": [
                    "",
                    "Balanced",
                    "Held",
                    "Cut off",
                    "Falling back",
                    "Stepped through"
                ]
            }

            saved_observations = {}

            for field_name, choices in observation_choices.items():
                current_value = str(
                    selected_row.get(
                        field_name,
                        ""
                    )
                ).strip()

                if current_value not in choices:
                    choices = choices + [
                        current_value
                    ]

                saved_observations[
                    field_name
                ] = st.selectbox(
                    field_name,
                    choices,
                    index=(
                        choices.index(
                            current_value
                        )
                        if current_value in choices
                        else 0
                    ),
                    key=f"swing_obs_{field_name}_{selected_id}"
                )

            observation_notes = st.text_area(
                "Review Notes",
                value=str(
                    selected_row.get(
                        "Observation Notes",
                        ""
                    )
                ),
                placeholder=(
                    "Visible change, feel, shot result, or something you want My Play to remember."
                ),
                key=f"swing_obs_notes_{selected_id}"
            )

            if st.button(
                "Save Swing Observations",
                use_container_width=True,
                key=f"save_swing_obs_{selected_id}"
            ):
                saved_observations[
                    "Observation Notes"
                ] = observation_notes

                save_swing_observations(
                    selected_id,
                    saved_observations
                )

                st.success(
                    "Swing observations saved."
                )

                st.rerun()

            if (
                baseline_row is not None
                and str(
                    baseline_row.get(
                        "Video ID",
                        ""
                    )
                ) != selected_id
            ):
                st.divider()
                st.subheader(
                    "Baseline Comparison"
                )

                baseline_path = str(
                    baseline_row.get(
                        "Path",
                        ""
                    )
                )

                baseline_video_source, baseline_video_mime = resolve_swing_video_source(
                    baseline_path
                )

                left_video, right_video = st.columns(
                    2
                )

                with left_video:
                    st.markdown(
                        "**Baseline**"
                    )

                    if baseline_video_source:
                        st.video(
                            baseline_video_source,
                            format=baseline_video_mime
                        )

                with right_video:
                    st.markdown(
                        "**Current Swing**"
                    )

                    if selected_video_source:
                        st.video(
                            selected_video_source,
                            format=selected_video_mime
                        )

                comparison = swing_comparison_points(
                    selected_row,
                    baseline_row
                )

                if comparison:
                    st.markdown(
                        "**Visible Changes From Baseline**"
                    )

                    for point in comparison:
                        st.write(
                            f"• {point}"
                        )
                else:
                    st.caption(
                        "Save observations for both swings to build the baseline comparison."
                    )

            st.divider()
            st.markdown(
                "**Future AI Analysis Layer**"
            )

            st.write(
                "My Play will use these stored videos to evaluate visible changes in tempo, setup, "
                "balance, backswing length, transition and finish against your personal baseline, "
                "then compare those changes with the shot data from that session."
            )


with tab_history:
    st.header("Round Biographies")
    st.caption(
        "Every completed round becomes a permanent story of what happened, what My Play learned, and what to do next."
    )

    round_history = load_round_history()
    history = load_shots()

    if round_history.empty:
        st.info("Complete a Live Round to create your first Round Biography.")
    else:
        biography_options = []
        biography_rows = {}
        for row_index, biography_row in round_history.iterrows():
            score_value = biography_row.get("Total Score", "")
            course_value = biography_row.get("Course", "Unknown course")
            date_value = str(biography_row.get("Date", ""))[:10]
            label = f"{date_value} · {course_value} · {score_value}"
            if label in biography_rows:
                label = f"{label} · {row_index + 1}"
            biography_options.append(label)
            biography_rows[label] = biography_row

        selected_biography_label = st.selectbox(
            "Choose a round", biography_options, key="round_biography_selector"
        )
        selected_round_row = biography_rows[selected_biography_label]
        biography = build_round_biography(
            selected_round_row, all_player_evidence, round_history
        )

        st.markdown(
            f"""
            <div class="myplay-profile-banner">
                <div class="myplay-eyebrow">ROUND BIOGRAPHY</div>
                <h2>{html.escape(biography['title'])}</h2>
                <p>{html.escape(biography['story'])}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        selected_round_id = str(selected_round_row.get("Round ID", "") or "")
        selected_round_evidence = all_player_evidence
        if (
            isinstance(all_player_evidence, pd.DataFrame)
            and not all_player_evidence.empty
            and "Round ID" in all_player_evidence.columns
            and selected_round_id
        ):
            selected_round_evidence = all_player_evidence[
                all_player_evidence["Round ID"].fillna("").astype(str) == selected_round_id
            ].copy()

        round_insights = learned_profile_insights(selected_round_evidence)
        round_endurance = endurance_phase_table(selected_round_evidence)
        round_training = recommended_training(
            round_insights, round_endurance, selected_round_evidence
        )

        with st.expander("The round in one minute", expanded=True):
            r1, r2, r3 = st.columns(3)
            r1.metric(
                "Score",
                biography["score"] if biography["score"] is not None else "Not recorded",
            )
            r2.metric("Shots connected", biography["shots"])
            r3.metric("Main recorded pattern", round_insights["primary_tendency"])
            st.write(biography["story"])

        with st.expander("What went well and what changed", expanded=False):
            if selected_round_evidence.empty:
                st.info("No shot-by-shot evidence is connected to this round yet.")
            else:
                st.write(
                    f"• Most repeatable recorded club: **{round_insights['reliable_club']}**"
                )
                st.write(
                    f"• Primary recorded tendency: **{round_insights['primary_tendency']}**"
                )
                st.caption(
                    "My Play reports only patterns supported by the shots attached to this round."
                )

        with st.expander("Endurance and fatigue", expanded=False):
            if round_endurance.empty:
                st.info(
                    "This biography needs more sequenced shots before opening and late-round performance can be compared."
                )
            else:
                st.dataframe(round_endurance, use_container_width=True, hide_index=True)

        with st.expander("What My Play learned", expanded=True):
            st.write(f"• {round_insights['primary_tendency']}")
            st.write(
                f"• {round_insights['reliable_club']} currently has the most repeatable recorded carry in this round."
            )
            st.caption(
                "One round can strengthen or weaken confidence, but established profile tendencies change only when enough comparable evidence supports them."
            )

        with st.expander(
            f"Recommended Training · {round_training['title']}", expanded=True
        ):
            st.write(round_training["summary"])
            st.caption(f"Why: {round_training['reason']}")
            for step_number, step in enumerate(round_training["steps"], start=1):
                st.write(f"{step_number}. {step}")
            if round_training.get("source_url"):
                st.markdown(
                    f"[{round_training['source_label']}]({round_training['source_url']})"
                )
            else:
                st.caption(round_training["source_label"])

        with st.expander("Complete shot timeline and raw data", expanded=False):
            if selected_round_evidence.empty:
                st.info("No connected shot timeline is available.")
            else:
                st.dataframe(
                    selected_round_evidence, use_container_width=True, hide_index=True
                )
            st.download_button(
                "Download all shot history",
                history.to_csv(index=False).encode("utf-8"),
                file_name="my_play_shot_history.csv",
                mime="text/csv",
            )

        with st.expander("All completed rounds", expanded=False):
            st.dataframe(round_history, use_container_width=True, hide_index=True)


if False:  # Retained legacy history tables; replaced by Round Biographies above.
    st.header(
        "Analytics"
    )

    round_history = load_round_history()

    if not round_history.empty:
        st.subheader(
            "Round History"
        )

        st.dataframe(
            round_history.iloc[
                ::-1
            ],
            use_container_width=True,
            hide_index=True
        )

        st.divider()

    st.subheader(
        "Shot History"
    )

    history = load_shots()

    if history.empty:
        st.info(
            "No shots saved yet."
        )

    else:
        m1, m2, m3 = st.columns(
            3
        )

        with m1:
            st.metric(
                "Total Saved Shots",
                len(
                    history
                )
            )

        with m2:
            solid_count = (
                int(
                    (
                        history[
                            "Contact"
                        ]
                        == "Solid"
                    ).sum()
                )
                if "Contact"
                in history.columns
                else 0
            )

            st.metric(
                "Solid Shots",
                solid_count
            )

        with m3:
            courses = (
                history[
                    "Course"
                ]
                .replace(
                    "Unknown",
                    pd.NA
                )
                .dropna()
                .nunique()
                if "Course"
                in history.columns
                else 0
            )

            st.metric(
                "Courses Remembered",
                courses
            )

        st.dataframe(
            history.iloc[
                ::-1
            ],
            use_container_width=True,
            hide_index=True
        )

        st.divider()
        st.subheader(
            "Club Performance"
        )

        if {
            "Club Used",
            "Actual Carry"
        }.issubset(
            set(
                history.columns
            )
        ):
            perf = history.copy()

            perf[
                "Actual Carry"
            ] = pd.to_numeric(
                perf[
                    "Actual Carry"
                ],
                errors="coerce"
            )

            perf = perf.dropna(
                subset=[
                    "Actual Carry"
                ]
            )

            if "Contact" in perf.columns:
                perf = perf[
                    perf[
                        "Contact"
                    ]
                    == "Solid"
                ]

            if not perf.empty:
                summary = (
                    perf
                    .groupby(
                        "Club Used"
                    )[
                        "Actual Carry"
                    ]
                    .agg(
                        [
                            "count",
                            "mean",
                            "min",
                            "max",
                            "std"
                        ]
                    )
                    .reset_index()
                )

                summary[
                    "mean"
                ] = summary[
                    "mean"
                ].round(
                    1
                )

                summary[
                    "std"
                ] = summary[
                    "std"
                ].round(
                    1
                )

                summary = summary.rename(
                    columns={
                        "count": "Solid Shots",
                        "mean": "Average Carry",
                        "min": "Shortest",
                        "max": "Longest",
                        "std": "Dispersion"
                    }
                )

                st.dataframe(
                    summary,
                    use_container_width=True,
                    hide_index=True
                )

        csv_data = history.to_csv(
            index=False
        ).encode(
            "utf-8"
        )

        st.download_button(
            "Download Shot History CSV",
            csv_data,
            file_name="my_play_shot_history.csv",
            mime="text/csv"
        )


        st.divider()
        st.subheader(
            "Unified Data Sources"
        )

        evidence = combined_player_evidence(
            history
        )

        if not evidence.empty:
            source_summary = (
                evidence[
                    "Source"
                ]
                .fillna(
                    "Unknown"
                )
                .astype(str)
                .value_counts()
                .rename_axis(
                    "Source"
                )
                .reset_index(
                    name="Data Points"
                )
            )

            st.dataframe(
                source_summary,
                use_container_width=True,
                hide_index=True
            )

        st.divider()

        st.subheader(
            "Strategy Tendencies"
        )

        if "Shot Type" in history.columns:
            shot_type_summary = (
                history[
                    "Shot Type"
                ]
                .fillna(
                    "Unknown"
                )
                .value_counts()
                .rename_axis(
                    "Shot Type"
                )
                .reset_index(
                    name="Shots"
                )
            )

            st.dataframe(
                shot_type_summary,
                use_container_width=True,
                hide_index=True
            )

        if {
            "Recommended Aim",
            "Result"
        }.issubset(
            set(
                history.columns
            )
        ):
            strategy_rows = []

            for aim_name, group in history.groupby(
                "Recommended Aim"
            ):
                if not str(
                    aim_name
                ).strip():
                    continue

                total = len(
                    group
                )

                on_target = int(
                    (
                        group[
                            "Result"
                        ] == "On Target"
                    ).sum()
                )

                strategy_rows.append({
                    "Recommended Aim": aim_name,
                    "Shots": total,
                    "On Target %": round(
                        (
                            on_target
                            / total
                            * 100
                        )
                        if total
                        else 0
                    )
                })

            if strategy_rows:
                st.dataframe(
                    pd.DataFrame(
                        strategy_rows
                    ),
                    use_container_width=True,
                    hide_index=True
                )

        st.divider()

        st.subheader(
            "Learned Dispersion"
        )

        dispersion_rows = []

        for club in bag:
            club_name = club[
                "Club"
            ]

            dispersion = learned_dispersion_for_club(
                club_name,
                history
            )

            dispersion_rows.append({
                "Club": club_name,
                "Shots": dispersion.get(
                    "sample_count",
                    0
                ),
                "Dominant Miss": dispersion.get(
                    "dominant_miss",
                    "Not enough data"
                ),
                "Left %": round(
                    dispersion.get(
                        "left_rate",
                        0
                    ) * 100
                ),
                "Right %": round(
                    dispersion.get(
                        "right_rate",
                        0
                    ) * 100
                ),
                "Short %": round(
                    dispersion.get(
                        "short_rate",
                        0
                    ) * 100
                ),
                "Long %": round(
                    dispersion.get(
                        "long_rate",
                        0
                    ) * 100
                ),
                "Carry SD": (
                    round(
                        dispersion[
                            "carry_std"
                        ],
                        1
                    )
                    if dispersion.get(
                        "carry_std"
                    ) is not None
                    else ""
                )
            })

        st.dataframe(
            pd.DataFrame(
                dispersion_rows
            ),
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# MY GAME
# ============================================================

with tab_game:
    st.header("Preferences")
    st.caption(
        "Only open the area you want to change. Your learned performance remains automatic."
    )

    with st.expander("Player Identity", expanded=False):
        with st.form("clean_player_identity_form"):
            identity_col1, identity_col2 = st.columns(2)
            with identity_col1:
                clean_display_name = st.text_input(
                    "Player name",
                    value=str(profile.get("display_name", "") or ""),
                    placeholder="What should My Play call you?",
                )
                clean_hand_options = ["Right-handed", "Left-handed"]
                clean_current_hand = profile.get("handedness", "Right-handed")
                if clean_current_hand not in clean_hand_options:
                    clean_current_hand = "Right-handed"
                clean_handedness = st.selectbox(
                    "Handedness",
                    clean_hand_options,
                    index=clean_hand_options.index(clean_current_hand),
                )
            with identity_col2:
                st.caption(
                    "These are the only identity fields My Play needs. Golf details are kept separately below."
                )
            clean_save_identity = st.form_submit_button(
                "Save Identity", type="primary", use_container_width=True
            )
        if clean_save_identity:
            save_json(PROFILE_FILE, {
                **profile,
                "display_name": clean_display_name.strip(),
                "handedness": clean_handedness,
            })
            st.success("Player identity saved.")
            st.rerun()

    with st.expander("Golf Details", expanded=False):
        with st.form("clean_golf_details_form"):
            golf_detail_col1, golf_detail_col2 = st.columns(2)
            clean_experience_options = [
                "New golfer", "Developing", "Intermediate", "Advanced"
            ]
            clean_experience = profile.get("experience_level", "Developing")
            if clean_experience not in clean_experience_options:
                clean_experience = "Developing"
            with golf_detail_col1:
                clean_handicap = st.text_input(
                    "Handicap", value=str(profile.get("handicap", "") or ""),
                    placeholder="Optional",
                )
                clean_typical_score = st.text_input(
                    "Typical score",
                    value=str(profile.get("typical_score", "") or ""),
                    placeholder="Example: 92",
                )
                clean_experience_level = st.selectbox(
                    "Experience",
                    clean_experience_options,
                    index=clean_experience_options.index(clean_experience),
                )
            with golf_detail_col2:
                clean_default_course = st.text_input(
                    "Home course", value=str(profile.get("default_course", "") or "")
                )
                clean_default_state = st.text_input(
                    "Home state",
                    value=str(profile.get("default_state", "NJ") or "NJ"),
                    max_chars=2,
                )
            clean_save_golf_details = st.form_submit_button(
                "Save Golf Details", use_container_width=True
            )
        if clean_save_golf_details:
            save_json(PROFILE_FILE, {
                **profile,
                "handicap": clean_handicap,
                "typical_score": clean_typical_score,
                "experience_level": clean_experience_level,
                "default_course": clean_default_course,
                "default_state": clean_default_state.upper(),
            })
            st.success("Golf details saved.")
            st.rerun()

    with st.expander("Caddie Preferences", expanded=False):
        with st.form("clean_caddie_preferences_form"):
            caddie_pref_col1, caddie_pref_col2 = st.columns(2)
            clean_priority_options = [
                "Balanced", "Avoid big numbers", "Aggressive when confident",
                "Fairways first", "Greens first"
            ]
            clean_priority = game_profile.get("playing_priority", "Balanced")
            if clean_priority not in clean_priority_options:
                clean_priority = "Balanced"
            with caddie_pref_col1:
                clean_preferred_leave = st.number_input(
                    "Preferred scoring leave (yards)",
                    min_value=30, max_value=180,
                    value=int(profile.get("preferred_scoring_leave", 100) or 100),
                    step=5,
                    help="The caddie uses this target when considering a layup.",
                )
                clean_playing_priority = st.selectbox(
                    "Playing strategy",
                    clean_priority_options,
                    index=clean_priority_options.index(clean_priority),
                )
            with caddie_pref_col2:
                communication_options = ["Brief", "Balanced detail", "Explain every decision"]
                current_communication = game_profile.get("communication_style", "Balanced detail")
                if current_communication not in communication_options:
                    current_communication = "Balanced detail"
                clean_communication = st.selectbox(
                    "Caddie response style",
                    communication_options,
                    index=communication_options.index(current_communication),
                )
            clean_save_caddie = st.form_submit_button(
                "Save Caddie Preferences", type="primary", use_container_width=True
            )
        if clean_save_caddie:
            save_json(PROFILE_FILE, {
                **profile,
                "preferred_scoring_leave": int(clean_preferred_leave),
            })
            saved = save_game_profile({
                **game_profile,
                "playing_priority": clean_playing_priority,
                "communication_style": clean_communication,
            })
            if saved:
                st.success("Caddie preferences saved.")
                st.rerun()
            else:
                st.error("Caddie preferences could not be saved to the cloud.")

    with st.expander("Goals", expanded=False):
        with st.form("clean_player_goals_form"):
            goal_col1, goal_col2 = st.columns(2)
            with goal_col1:
                clean_target_score = st.number_input(
                    "Target 18-hole score",
                    min_value=50, max_value=150,
                    value=int(game_profile.get("target_score", 90) or 90),
                    step=1,
                )
                goal_focus_options = [
                    "Lower scores", "Driving", "Iron play", "Wedges",
                    "Putting", "Course management", "Endurance"
                ]
                current_goal_focus = game_profile.get("goal_focus", "Lower scores")
                if current_goal_focus not in goal_focus_options:
                    current_goal_focus = "Lower scores"
                clean_goal_focus = st.selectbox(
                    "Primary goal",
                    goal_focus_options,
                    index=goal_focus_options.index(current_goal_focus),
                )
            with goal_col2:
                clean_target_handicap = st.text_input(
                    "Target handicap",
                    value=str(game_profile.get("target_handicap", "") or ""),
                    placeholder="Optional",
                )
                practice_time_options = ["15 minutes", "30 minutes", "45 minutes", "60 minutes"]
                current_practice_time = game_profile.get("practice_time", "30 minutes")
                if current_practice_time not in practice_time_options:
                    current_practice_time = "30 minutes"
                clean_practice_time = st.selectbox(
                    "Normal practice time",
                    practice_time_options,
                    index=practice_time_options.index(current_practice_time),
                )
            clean_save_goals = st.form_submit_button(
                "Save Goals", type="primary", use_container_width=True
            )
        if clean_save_goals:
            saved = save_game_profile({
                **game_profile,
                "target_score": int(clean_target_score),
                "target_handicap": clean_target_handicap.strip(),
                "goal_focus": clean_goal_focus,
                "practice_time": clean_practice_time,
            })
            if saved:
                st.success("Goals saved.")
                st.rerun()
            else:
                st.error("Goals could not be saved to the cloud.")

    with st.expander("Manual Tendencies · Optional", expanded=False):
        st.caption(
            "Use these as temporary caddie hints. Automatic learned tendencies take priority when enough evidence exists."
        )
        with st.form("clean_manual_tendencies_form"):
            manual_col1, manual_col2 = st.columns(2)
            with manual_col1:
                clean_driver_miss = st.selectbox(
                    "Driver miss", TYPICAL_MISSES,
                    index=TYPICAL_MISSES.index(game_profile.get("driver_miss", "unknown"))
                    if game_profile.get("driver_miss", "unknown") in TYPICAL_MISSES else 0,
                )
                clean_wood_miss = st.selectbox(
                    "Wood / hybrid miss", TYPICAL_MISSES,
                    index=TYPICAL_MISSES.index(game_profile.get("wood_miss", "unknown"))
                    if game_profile.get("wood_miss", "unknown") in TYPICAL_MISSES else 0,
                )
            with manual_col2:
                clean_iron_miss = st.selectbox(
                    "Iron miss", TYPICAL_MISSES,
                    index=TYPICAL_MISSES.index(game_profile.get("iron_miss", "unknown"))
                    if game_profile.get("iron_miss", "unknown") in TYPICAL_MISSES else 0,
                )
                clean_wedge_miss = st.selectbox(
                    "Wedge miss", TYPICAL_MISSES,
                    index=TYPICAL_MISSES.index(game_profile.get("wedge_miss", "unknown"))
                    if game_profile.get("wedge_miss", "unknown") in TYPICAL_MISSES else 0,
                )
            clean_save_tendencies = st.form_submit_button(
                "Save Manual Tendencies", use_container_width=True
            )
        if clean_save_tendencies:
            saved = save_game_profile({
                **game_profile,
                "driver_miss": clean_driver_miss,
                "wood_miss": clean_wood_miss,
                "iron_miss": clean_iron_miss,
                "wedge_miss": clean_wedge_miss,
            })
            if saved:
                st.success("Manual tendencies saved.")
                st.rerun()
            else:
                st.error("Manual tendencies could not be saved to the cloud.")

    with st.expander("Swing Reminders", expanded=False):
        if _cloud_ready():
            try:
                clean_reminder_response = (
                    supabase.table("swing_reminders").select("reminder")
                    .eq("user_id", _cloud_user_id()).eq("active", True)
                    .order("created_at").execute()
                )
                clean_existing_reminders = "\n".join(
                    row.get("reminder", "")
                    for row in (clean_reminder_response.data or [])
                    if row.get("reminder")
                )
            except Exception:
                clean_existing_reminders = ""
        elif os.path.exists(REMINDER_FILE):
            with open(REMINDER_FILE, "r", encoding="utf-8") as reminder_file:
                clean_existing_reminders = reminder_file.read()
        else:
            clean_existing_reminders = ""

        with st.form("clean_swing_reminders_form"):
            clean_reminders = st.text_area(
                "Personal reminders",
                value=clean_existing_reminders,
                height=120,
                placeholder="Smooth tempo\nFinish the turn\nDon't rush from the top",
            )
            clean_save_reminders = st.form_submit_button(
                "Save Swing Reminders", use_container_width=True
            )
        if clean_save_reminders:
            clean_reminder_lines = [
                line.strip() for line in clean_reminders.splitlines() if line.strip()
            ]
            if _cloud_ready():
                supabase.table("swing_reminders").delete().eq(
                    "user_id", _cloud_user_id()
                ).execute()
                if clean_reminder_lines:
                    supabase.table("swing_reminders").insert([
                        {"user_id": _cloud_user_id(), "reminder": line, "active": True}
                        for line in clean_reminder_lines
                    ]).execute()
            with open(REMINDER_FILE, "w", encoding="utf-8") as reminder_file:
                reminder_file.write(clean_reminders)
            st.success("Swing reminders saved.")

    with st.expander("Account & Technical", expanded=False):
        st.caption(
            f"Signed in as {st.session_state.get('supabase_user_email', 'Golfer')}"
        )
        if not st.session_state.get("my_player_schema_ready", False):
            st.warning(
                "The My Player cloud upgrade is not detected. Some preferences may not persist across devices."
            )
        technical_col1, technical_col2 = st.columns(2)
        with technical_col1:
            if st.button(
                "Copy Local Test Data to Cloud",
                use_container_width=True,
                key="clean_migrate_local_to_cloud",
            ):
                try:
                    migrate_all_local_data_to_cloud(supabase)
                    st.success("Cloud migration completed.")
                except Exception as exc:
                    st.error(f"Migration stopped: {exc}")
        with technical_col2:
            if st.button(
                "Sign Out", use_container_width=True, key="clean_preferences_sign_out"
            ):
                sign_out_cloud(supabase)
                st.rerun()
        clean_course_stats = catalog_stats()
        st.caption(
            f"Course catalog: {clean_course_stats['count']:,} courses available."
            if clean_course_stats["count"] > 0
            else "Course catalog is not currently available."
        )


if False:  # Retained legacy Preferences form; replaced by the clean sections above.
    st.header(
        "Profile & Caddie Preferences"
    )

    st.caption(
        "Edit only identity, goals, and preferences here. Performance conclusions update automatically from saved data."
    )

    if not st.session_state.get("my_player_schema_ready", False):
        st.warning(
            "My Player's new cloud fields need the supplied Supabase upgrade before "
            "scoring preferences and expanded club details can persist across devices."
        )

    with st.expander(
        "⚙️ Account & Beta Tools",
        expanded=False
    ):
        st.caption(
            f"Signed in as {st.session_state.get('supabase_user_email', 'Golfer')}"
        )

        st.caption(
            "Cloud storage is active for your player profile, bag, shots, completed rounds, reminders, and swing-video metadata."
        )

        with st.expander(
            "Cloud Data Migration",
            expanded=False
        ):
            st.caption(
                "Only use this if you need to copy older local test data into this signed-in account."
            )

            current_cloud_status = cloud_data_status(
                supabase
            )

            status_cols = st.columns(
                len(
                    current_cloud_status
                )
            )

            for status_col, (
                label,
                value
            ) in zip(
                status_cols,
                current_cloud_status.items()
            ):
                with status_col:
                    st.metric(
                        label,
                        value
                    )

            if st.button(
                "Copy Local Test Data to Cloud",
                use_container_width=True,
                key="migrate_local_to_cloud_settings"
            ):
                try:
                    migration_results = migrate_all_local_data_to_cloud(
                        supabase
                    )

                    st.toast(
                        "Cloud migration completed."
                    )

                    for label, (
                        count,
                        status
                    ) in migration_results.items():
                        if status == "already_has_cloud_data":
                            st.caption(
                                f"{label}: skipped — cloud data already exists."
                            )
                        elif status == "no_local_data":
                            st.caption(
                                f"{label}: no local data to migrate."
                            )
                        else:
                            st.caption(
                                f"{label}: {count} record(s) copied."
                            )

                except Exception as exc:
                    st.error(
                        f"Migration stopped: {exc}"
                    )

        if st.button(
            "Sign Out",
            use_container_width=True,
            key="cloud_sign_out_settings"
        ):
            sign_out_cloud(
                supabase
            )
            st.rerun()

    st.subheader(
        "Player Profile"
    )

    display_name = st.text_input(
        "Player name",
        value=str(profile.get("display_name", "") or ""),
        placeholder="What should My Play call you?",
    )

    handedness_options = [
        "Right-handed",
        "Left-handed"
    ]

    current_hand = profile.get(
        "handedness",
        "Right-handed"
    )

    if current_hand not in handedness_options:
        current_hand = (
            "Right-handed"
        )

    handedness = st.selectbox(
        "Handedness",
        handedness_options,
        index=handedness_options.index(
            current_hand
        )
    )

    handicap = st.text_input(
        "Handicap",
        value=str(
            profile.get(
                "handicap",
                ""
            )
        ),
        placeholder="Optional"
    )

    profile_col1, profile_col2 = st.columns(2)
    with profile_col1:
        typical_score = st.text_input(
            "Typical 18-hole score",
            value=str(profile.get("typical_score", "") or ""),
            placeholder="Example: 92",
        )
        experience_options = ["New golfer", "Developing", "Intermediate", "Advanced"]
        current_experience = profile.get("experience_level", "Developing")
        if current_experience not in experience_options:
            current_experience = "Developing"
        experience_level = st.selectbox(
            "Experience level", experience_options,
            index=experience_options.index(current_experience),
        )
    with profile_col2:
        preferred_scoring_leave = st.number_input(
            "Preferred scoring leave (yards)",
            min_value=30, max_value=180,
            value=int(profile.get("preferred_scoring_leave", 100) or 100),
            step=5,
            help="The caddie uses this target when considering a layup.",
        )

    default_course = st.text_input(
        "Default Course",
        value=profile.get(
            "default_course",
            ""
        )
    )

    default_state = st.text_input(
        "Default State",
        value=profile.get(
            "default_state",
            "NJ"
        ),
        max_chars=2
    )

    if st.button(
        "Save Player Profile"
    ):
        save_json(
            PROFILE_FILE,
            {
                "display_name": display_name.strip(),
                "handedness": handedness,
                "handicap": handicap,
                "typical_score": typical_score,
                "experience_level": experience_level,
                "preferred_scoring_leave": int(preferred_scoring_leave),
                "default_course": default_course,
                "default_state": default_state.upper()
            }
        )

        st.success(
            "Player profile saved."
        )

        st.rerun()

    st.divider()
    st.subheader("Optional Caddie Overrides")
    st.caption(
        "Use these only when My Play does not have enough evidence yet. Learned tendencies on your Profile take priority as confidence grows."
    )

    tendency_col1, tendency_col2 = st.columns(2)
    with tendency_col1:
        driver_miss = st.selectbox(
            "Driver miss", TYPICAL_MISSES,
            index=TYPICAL_MISSES.index(game_profile.get("driver_miss", "unknown"))
            if game_profile.get("driver_miss", "unknown") in TYPICAL_MISSES else 0,
            key="game_driver_miss",
        )
        wood_miss = st.selectbox(
            "Fairway wood / hybrid miss", TYPICAL_MISSES,
            index=TYPICAL_MISSES.index(game_profile.get("wood_miss", "unknown"))
            if game_profile.get("wood_miss", "unknown") in TYPICAL_MISSES else 0,
            key="game_wood_miss",
        )
        iron_miss = st.selectbox(
            "Iron miss", TYPICAL_MISSES,
            index=TYPICAL_MISSES.index(game_profile.get("iron_miss", "unknown"))
            if game_profile.get("iron_miss", "unknown") in TYPICAL_MISSES else 0,
            key="game_iron_miss",
        )
        wedge_miss = st.selectbox(
            "Wedge miss", TYPICAL_MISSES,
            index=TYPICAL_MISSES.index(game_profile.get("wedge_miss", "unknown"))
            if game_profile.get("wedge_miss", "unknown") in TYPICAL_MISSES else 0,
            key="game_wedge_miss",
        )
    with tendency_col2:
        shape_default = game_profile.get("normal_shot_shape", "Unknown")
        if shape_default not in SHOT_SHAPES:
            shape_default = "Unknown"
        normal_shot_shape = st.selectbox(
            "Normal shot shape", SHOT_SHAPES,
            index=SHOT_SHAPES.index(shape_default), key="game_normal_shape",
        )
        game_areas = [
            "Not selected", "Driving", "Fairway woods / hybrids", "Iron play",
            "Approach play", "Wedges", "Bunkers", "Putting", "Course management",
        ]
        strongest_default = game_profile.get("strongest_area", "Not selected")
        weakest_default = game_profile.get("weakest_area", "Not selected")
        strongest_area = st.selectbox(
            "Strongest part of your game", game_areas,
            index=game_areas.index(strongest_default) if strongest_default in game_areas else 0,
            key="game_strongest_area",
        )
        weakest_area = st.selectbox(
            "Weakest part of your game", game_areas,
            index=game_areas.index(weakest_default) if weakest_default in game_areas else 0,
            key="game_weakest_area",
        )
        preferred_approach_distance = st.number_input(
            "Most comfortable approach distance (yards)", min_value=30, max_value=220,
            value=int(game_profile.get("preferred_approach_distance", 100) or 100), step=5,
            key="game_preferred_approach",
        )

    trouble_options = [
        "Not selected", "Penalty off the tee", "Right-side trouble", "Left-side trouble",
        "Fairway bunkers", "Greenside bunkers", "Water", "Trees / recovery shots",
        "Short-sided misses", "Three-putts",
    ]
    priority_options = ["Balanced", "Avoid big numbers", "Aggressive when confident", "Fairways first", "Greens first"]
    lower_col1, lower_col2 = st.columns(2)
    with lower_col1:
        trouble_default = game_profile.get("trouble_tendency", "Not selected")
        trouble_tendency = st.selectbox(
            "Most common trouble pattern", trouble_options,
            index=trouble_options.index(trouble_default) if trouble_default in trouble_options else 0,
            key="game_trouble_tendency",
        )
    with lower_col2:
        priority_default = game_profile.get("playing_priority", "Balanced")
        playing_priority = st.selectbox(
            "Preferred strategy", priority_options,
            index=priority_options.index(priority_default) if priority_default in priority_options else 0,
            key="game_playing_priority",
        )

    if st.button("Save Game Tendencies", type="primary", key="save_game_tendencies"):
        saved = save_game_profile({
            "driver_miss": driver_miss,
            "wood_miss": wood_miss,
            "iron_miss": iron_miss,
            "wedge_miss": wedge_miss,
            "normal_shot_shape": normal_shot_shape,
            "strongest_area": strongest_area,
            "weakest_area": weakest_area,
            "preferred_approach_distance": int(preferred_approach_distance),
            "trouble_tendency": trouble_tendency,
            "playing_priority": playing_priority,
        })
        if saved:
            st.success("Game tendencies saved.")
            st.rerun()
        else:
            st.error("Run the supplied Supabase My Player upgrade, then save again.")

    st.divider()
    st.subheader(
        "My Swing Reminders"
    )

    if _cloud_ready():
        try:
            response = (
                supabase
                .table("swing_reminders")
                .select(
                    "reminder"
                )
                .eq(
                    "user_id",
                    _cloud_user_id()
                )
                .eq(
                    "active",
                    True
                )
                .order(
                    "created_at"
                )
                .execute()
            )

            existing = "\n".join(
                row.get(
                    "reminder",
                    ""
                )
                for row in (response.data or [])
                if row.get(
                    "reminder"
                )
            )
        except Exception:
            existing = ""
    elif os.path.exists(
        REMINDER_FILE
    ):
        with open(
            REMINDER_FILE,
            "r",
            encoding="utf-8"
        ) as f:
            existing = f.read()
    else:
        existing = ""

    reminders = st.text_area(
        "Reminders",
        value=existing,
        height=160,
        placeholder=(
            "Smooth tempo\n"
            "Finish the turn\n"
            "Don't rush from the top"
        )
    )

    if st.button(
        "Save My Reminders"
    ):
        reminder_lines = [
            line.strip()
            for line in reminders.splitlines()
            if line.strip()
        ]

        if _cloud_ready():
            (
                supabase
                .table("swing_reminders")
                .delete()
                .eq(
                    "user_id",
                    _cloud_user_id()
                )
                .execute()
            )

            if reminder_lines:
                (
                    supabase
                    .table("swing_reminders")
                    .insert(
                        [
                            {
                                "user_id": _cloud_user_id(),
                                "reminder": line,
                                "active": True
                            }
                            for line in reminder_lines
                        ]
                    )
                    .execute()
                )

        with open(
            REMINDER_FILE,
            "w",
            encoding="utf-8"
        ) as f:
            f.write(
                reminders
            )

        st.success(
            "Swing reminders saved."
        )

    st.divider()
    st.subheader(
        "Course Data Status"
    )

    stats = catalog_stats()

    if stats["count"] > 0:
        st.success(
            f"Local U.S. course catalog enabled: {stats['count']:,} courses."
        )
    else:
        st.warning(
            "Local course catalog is not currently available."
        )

    st.info(
        "My Play Beta now includes local course discovery, Live Round mode, optional browser GPS, "
        "automatic Open-Meteo weather, learned club dispersion, hole/round scoring, and round analytics."
    )

    if GEOLOCATION_AVAILABLE:
        st.success(
            "Browser GPS helper installed."
        )
    else:
        st.warning(
            "Optional GPS helper is not installed yet. Run: pip install streamlit-geolocation"
        )

"""
Configuration and metadata for the Google Form:
Production Task Entry Form
URL: https://docs.google.com/forms/d/e/1FAIpQLSfGQNuI7ZWSq1MkLafYsbAtVVBTnuF9P7Bnh6YFFCAQqzYSQA/viewform
"""

import urllib.request
import re
import json
import os
import tempfile
from datetime import datetime

FORM_ID = "1FAIpQLSfGQNuI7ZWSq1MkLafYsbAtVVBTnuF9P7Bnh6YFFCAQqzYSQA"
VIEW_URL = f"https://docs.google.com/forms/d/e/{FORM_ID}/viewform"
RESPONSE_URL = f"https://docs.google.com/forms/d/e/{FORM_ID}/formResponse"

FIELD_MAPPING = {
    "date": "entry.1093955894",
    "shift": "entry.909598259",
    "camera": "entry.1510650394",
    "location": "entry.601338817",
    "recorder": "entry.253587207",
    "scene": "entry.1557748935",
    "task": "entry.1612822529",
    "duration": "entry.1309181485",
}

def _get_safe_config_path():
    base_dir = os.path.dirname(__file__)
    target_path = os.path.join(base_dir, "form_data.json")
    try:
        if os.path.exists(target_path):
            with open(target_path, "a", encoding="utf-8") as f:
                pass
        return target_path
    except (OSError, IOError, PermissionError):
        return os.path.join(tempfile.gettempdir(), "form_data.json")

CONFIG_FILE = _get_safe_config_path()

DEFAULT_OPTIONS = {
    "shifts": ["Morning", "Evening"],
    "cameras": [f"Cam {i}" for i in range(1, 16)],
    "locations": ["Noida", "Gurugram"],
    "recorders": [
        "Anchal Bhagat", "Mayank Chauhan", "Ashish Kumar", "Prashant kumar",
        "Lokesh kumar", "Atul kumar", "Krishna Gupta", "Jatin Rathee",
        "Deepesh Garg", "Aman Bhadouriya", "Roshan Verma", "Vipin Vishwakarma",
        "Ajay Verma", "Diksha", "Sakib Khan", "Siddharth",
        "Monu", "Tanisha Tiwari", "Malik Ansari", "Bhagwati", "Babita"
    ],
    "scenes": [
        "reception", "board room", "sick bay", "training room", "corridor",
        "vending machine", "dining area", "meeting room", "private workspace",
        "hot desking area", "pantry storeroom", "pantry", "refrigerated display",
        "vending machine storeroom", "beverage display area", "test",
        "Liquor Shop", "Printer", "Recreation Room", "Ececutive Cabin",
        "Admin Room", "Reading Room", "Display shelf (apperal)",
        "Folding station (apperal)", "Worktable (Medicos)", "Display shelf (Medicos)",
        "Store Room", "Dish washing area", "Ingredient preparation area",
        "back of house", "Bakery", "self-serve drinks area", "Mailroom",
        "Staff lounge", "Loading bay", "Recycling area", "Paper shredding area",
        "Office Storage", "indoor play area", "Kids Study room", "Archive Room"
    ],
    "tasks": [
        "Arrange Items", "set up meeting table", "Make bed", "set up training room",
        "water the plants", "stock products", "Set Dining Table", "Arrange Pot Plants",
        "arrange chairs", "Organize desk", "stack boxes", "organise pantry items",
        "Restock Products", "stock shelves", "assemble office chair", "prepare snack",
        "restock pantry", "Restock Fridge", "cut vegetables", "R&D TEST",
        "prepare pizza", "change bedsheets", "Load paper in printer", "Setup pool table",
        "Arranging workdesk", "tidy up room", "Restock clothes", "Folding clothes",
        "Organise medicine into boxes", "Restock Product", "Hang keys in key cabinet",
        "wipe down utensils", "chop vegetables", "plate cake slices",
        "restock display cabinet", "scoop ice into cups", "sorting mail by department",
        "insert documents into envelope", "set up tables with refreshments",
        "load empty water dispenser bottle onto trolley", "Segregate recyclables",
        "Shred paper and dispose bin", "Insert folders into drawers", "keep toys",
        "stack chairs", "tidy up study room", "Keeping archive files on shelves"
    ]
}

def sync_live_options():
    """Fetches the latest options dynamically from the live Google Form."""
    try:
        req = urllib.request.Request(VIEW_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8")
        
        match = re.search(r'FB_PUBLIC_LOAD_DATA_\s*=\s*(.*?);\s*</script>', html, re.DOTALL)
        if not match:
            return DEFAULT_OPTIONS
        
        data = json.loads(match.group(1))
        questions = data[1][1]
        
        options = dict(DEFAULT_OPTIONS)
        
        for q in questions:
            title = (q[1] or "").strip().lower()
            if len(q) > 4 and q[4] and len(q[4][0]) > 1 and q[4][0][1]:
                opts = [opt[0] for opt in q[4][0][1]]
                if "shift" in title:
                    options["shifts"] = opts
                elif "camera" in title:
                    options["cameras"] = opts
                elif "location" in title:
                    options["locations"] = opts
                elif "recorder" in title:
                    options["recorders"] = opts
                elif "scene" in title:
                    options["scenes"] = opts
                elif "task" in title:
                    options["tasks"] = opts

        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(options, f, indent=2, ensure_ascii=False)
        except Exception:
            pass
        return options
    except Exception as e:
        print(f"Warning: Failed to sync live options: {e}")
        return get_options()

def get_options():
    """Returns the cached options or default options."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return DEFAULT_OPTIONS

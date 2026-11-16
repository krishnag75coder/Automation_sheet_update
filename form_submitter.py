"""
Form submission engine for Google Form: Production Task Entry Form.
Posts directly to Google Forms formResponse endpoint to update the sheet.
"""

import urllib.request
import urllib.parse
import re
import time
import os
import csv
import tempfile
from collections import deque
from datetime import datetime
from form_config import VIEW_URL, RESPONSE_URL, FIELD_MAPPING

def _get_safe_log_path():
    base_dir = os.path.dirname(__file__)
    target_path = os.path.join(base_dir, "submission_log.csv")
    try:
        with open(target_path, "a", encoding="utf-8") as f:
            pass
        return target_path
    except (OSError, IOError, PermissionError):
        return os.path.join(tempfile.gettempdir(), "submission_log.csv")

LOG_FILE = _get_safe_log_path()
in_memory_history = deque(maxlen=200)

cached_fbzx = None
last_fbzx_fetch = 0

def get_fbzx():
    """Fetches the fbzx token from the Google Form viewform page."""
    global cached_fbzx, last_fbzx_fetch
    now = time.time()
    # Cache fbzx for 10 minutes
    if cached_fbzx and (now - last_fbzx_fetch < 600):
        return cached_fbzx

    try:
        req = urllib.request.Request(
            VIEW_URL,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8")
            match = re.search(r'name="fbzx"\s+value="([^"]+)"', html)
            if match:
                cached_fbzx = match.group(1)
                last_fbzx_fetch = now
                return cached_fbzx
    except Exception as e:
        print(f"Warning: could not fetch fbzx token: {e}")
    
    return cached_fbzx or ""

def normalize_duration(duration_str):
    """
    Normalizes a variety of timing inputs into the required 00:00:00 format.
    Examples:
      - '00:05:30' -> '00:05:30'
      - '5:30'     -> '00:05:30'
      - '05:30'    -> '00:05:30'
      - '1:05:30'  -> '01:05:30'
      - '45'       -> '00:00:45'
      - '45s'      -> '00:00:45'
      - '15m'      -> '00:15:00'
      - '1h'       -> '01:00:00'
    """
    if not duration_str:
        return ""
    
    raw = duration_str.strip().lower()
    
    # Check for unit suffix like 15m, 45s, 1h
    if raw.endswith("s") and raw[:-1].isdigit():
        secs = int(raw[:-1])
        return f"{secs // 3600:02d}:{(secs % 3600) // 60:02d}:{secs % 60:02d}"
    if raw.endswith("m") and raw[:-1].isdigit():
        mins = int(raw[:-1])
        return f"{mins // 60:02d}:{mins % 60:02d}:00"
    if raw.endswith("h") and raw[:-1].isdigit():
        hours = int(raw[:-1])
        return f"{hours:02d}:00:00"

    parts = [p.strip() for p in raw.split(":") if p.strip()]
    if len(parts) == 3:
        h, m, s = int(parts[0]), int(parts[1]), int(parts[2])
        return f"{h:02d}:{m:02d}:{s:02d}"
    elif len(parts) == 2:
        m, s = int(parts[0]), int(parts[1])
        h = m // 60
        m = m % 60
        return f"{h:02d}:{m:02d}:{s:02d}"
    elif len(parts) == 1 and parts[0].isdigit():
        num = parts[0]
        if len(num) == 4:
            m = int(num[:2])
            s = int(num[2:])
            return f"00:{m:02d}:{s:02d}"
        val = int(num)
        if val < 60:
            return f"00:00:{val:02d}"
        else:
            return f"00:{val // 60:02d}:{val % 60:02d}"
            
    return duration_str.strip()

def calculate_duration_from_timestamps(start_str, end_str):
    """Calculates duration (00:00:00) between two timestamps HH:MM:SS or HH:MM."""
    try:
        def parse_to_sec(s):
            parts = [int(p) for p in s.strip().split(":")]
            if len(parts) == 3:
                return parts[0] * 3600 + parts[1] * 60 + parts[2]
            elif len(parts) == 2:
                return parts[0] * 3600 + parts[1] * 60
            return int(s)

        sec1 = parse_to_sec(start_str)
        sec2 = parse_to_sec(end_str)
        diff = max(0, sec2 - sec1)
        h = diff // 3600
        m = (diff % 3600) // 60
        s = diff % 60
        return f"{h:02d}:{m:02d}:{s:02d}"
    except Exception as e:
        raise ValueError(f"Invalid timestamp format: {e}")

def submit_entry(date, shift, camera, location, recorder, scene, task, duration):
    """
    Submits a single entry to the Google Form.
    Updates the Google Sheet connected to this form.
    """
    normalized_duration = normalize_duration(duration)
    if not normalized_duration:
        return {"success": False, "message": "Duration cannot be empty"}

    # Parse date components
    try:
        dt = datetime.strptime(date, "%Y-%m-%d")
        year, month, day = dt.year, dt.month, dt.day
    except Exception:
        dt = datetime.now()
        year, month, day = dt.year, dt.month, dt.day
        date = dt.strftime("%Y-%m-%d")

    fbzx = get_fbzx()

    payload = {
        FIELD_MAPPING["date"]: date,
        f"{FIELD_MAPPING['date']}_year": str(year),
        f"{FIELD_MAPPING['date']}_month": str(month),
        f"{FIELD_MAPPING['date']}_day": str(day),
        FIELD_MAPPING["shift"]: shift,
        FIELD_MAPPING["camera"]: camera,
        FIELD_MAPPING["location"]: location,
        FIELD_MAPPING["recorder"]: recorder,
        FIELD_MAPPING["scene"]: scene,
        FIELD_MAPPING["task"]: task,
        FIELD_MAPPING["duration"]: normalized_duration,
        "fvv": "1",
        "pageHistory": "0",
        "fbzx": fbzx
    }

    data_bytes = urllib.parse.urlencode(payload).encode("utf-8")
    req = urllib.request.Request(
        RESPONSE_URL,
        data=data_bytes,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Referer": VIEW_URL,
            "Content-Type": "application/x-www-form-urlencoded"
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            code = resp.getcode()
            body = resp.read().decode("utf-8")
            if code == 200 and ("response has been recorded" in body.lower() or "production task" in body.lower()):
                result = {
                    "success": True,
                    "message": "Recorded successfully in Google Sheet!",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "date": date,
                    "shift": shift,
                    "camera": camera,
                    "location": location,
                    "recorder": recorder,
                    "scene": scene,
                    "task": task,
                    "duration": normalized_duration
                }
                in_memory_history.appendleft(result)
                log_entry_to_csv(result)
                return result
            else:
                return {
                    "success": False,
                    "message": f"Unexpected response (HTTP {code})",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
    except Exception as e:
        return {
            "success": False,
            "message": f"Network or submission error: {str(e)}",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

def log_entry_to_csv(entry):
    """Appends successful submission to CSV log for audit and backup."""
    try:
        file_exists = os.path.exists(LOG_FILE)
        with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Timestamp", "Date", "Shift", "Camera", "Location", "Recorder", "Scene", "Task", "Duration", "Status"])
            writer.writerow([
                entry.get("timestamp", ""),
                entry.get("date", ""),
                entry.get("shift", ""),
                entry.get("camera", ""),
                entry.get("location", ""),
                entry.get("recorder", ""),
                entry.get("scene", ""),
                entry.get("task", ""),
                entry.get("duration", ""),
                "Success" if entry.get("success") else "Failed"
            ])
    except Exception as e:
        print(f"Notice: CSV write skipped ({e})")

def get_submission_history(limit=50):
    """Reads latest submission history from memory or CSV log."""
    if in_memory_history:
        return list(in_memory_history)[:limit]

    if not os.path.exists(LOG_FILE):
        return []
    rows = []
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)
        return list(reversed(rows))[:limit]
    except Exception:
        return []

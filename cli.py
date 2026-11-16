"""
Interactive CLI for Production Task Google Form Automation.
Allows selecting fixed fields once and entering multiple timings from the terminal.
"""

import sys
import os
from datetime import datetime
from form_config import get_options, sync_live_options
from form_submitter import submit_entry, normalize_duration

def prompt_choice(label, options, default=0):
    print(f"\nSelect {label}:")
    for i, opt in enumerate(options, 1):
        marker = " (Default)" if i - 1 == default else ""
        print(f"  [{i}] {opt}{marker}")
    while True:
        try:
            choice = input(f"Enter choice [1-{len(options)}] (or press Enter for default): ").strip()
            if not choice:
                return options[default]
            idx = int(choice) - 1
            if 0 <= idx < len(options):
                return options[idx]
            print("Invalid choice, please try again.")
        except ValueError:
            print("Please enter a valid number.")

def prompt_search(label, options):
    print(f"\nSelect {label} ({len(options)} options available):")
    query = input(f"Type keyword to search or press Enter to list all: ").strip().lower()
    matches = [o for o in options if query in o.lower()] if query else options
    if not matches:
        print("No matches found, showing full list.")
        matches = options
    return prompt_choice(label, matches, default=0)

def interactive_session():
    print("=" * 60)
    print(" 🚀 Google Form & Sheet Production Task Entry CLI")
    print("=" * 60)
    
    options = get_options()
    
    # 1. Fixed details (select once)
    today = datetime.now().strftime("%Y-%m-%d")
    date_input = input(f"\nEnter Date (YYYY-MM-DD) [Default: {today}]: ").strip()
    date = date_input if date_input else today

    shift = prompt_choice("Shift", options["shifts"], default=0)
    location = prompt_choice("Location", options["locations"], default=0)
    camera = prompt_choice("Camera", options["cameras"], default=0)
    recorder = prompt_search("Recorder Name", options["recorders"])
    scene = prompt_search("Scene", options["scenes"])
    task = prompt_search("Task", options["tasks"])

    print("\n" + "=" * 60)
    print(" ✅ FIXED DETAILS SELECTED FOR THIS SESSION:")
    print(f"  • Date:     {date}")
    print(f"  • Shift:    {shift}")
    print(f"  • Location: {location}")
    print(f"  • Camera:   {camera}")
    print(f"  • Recorder: {recorder}")
    print(f"  • Scene:    {scene}")
    print(f"  • Task:     {task}")
    print("=" * 60)
    print("\n⚡ RAPID TIMINGS ENTRY MODE ACTIVE")
    print("Type timing (e.g. 00:04:15, 4:15, or 45s) and press Enter.")
    print("Type 'exit' or 'q' to end session.")
    print("-" * 60)

    count = 0
    while True:
        try:
            val = input(f"\n[{count + 1}] Enter Timing > ").strip()
            if not val:
                continue
            if val.lower() in ["exit", "q", "quit"]:
                print(f"\nSession ended. Total entries submitted: {count}")
                break

            norm = normalize_duration(val)
            print(f"   Submitting duration '{norm}' to Google Sheet...", end=" ", flush=True)
            res = submit_entry(
                date=date,
                shift=shift,
                camera=camera,
                location=location,
                recorder=recorder,
                scene=scene,
                task=task,
                duration=norm
            )
            if res.get("success"):
                count += 1
                print(f"✅ RECORDED! (Total: {count})")
            else:
                print(f"❌ Failed: {res.get('message')}")
        except KeyboardInterrupt:
            print(f"\nSession interrupted. Total entries submitted: {count}")
            break

def batch_file_mode(filepath):
    """Submits timings from a text or csv file."""
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return

    with open(filepath, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    print(f"Found {len(lines)} timings in {filepath}")
    options = get_options()
    today = datetime.now().strftime("%Y-%m-%d")
    date = input(f"Enter Date [{today}]: ").strip() or today
    shift = prompt_choice("Shift", options["shifts"], default=0)
    location = prompt_choice("Location", options["locations"], default=0)
    camera = prompt_choice("Camera", options["cameras"], default=0)
    recorder = prompt_search("Recorder Name", options["recorders"])
    scene = prompt_search("Scene", options["scenes"])
    task = prompt_search("Task", options["tasks"])

    success = 0
    for idx, line in enumerate(lines, 1):
        norm = normalize_duration(line)
        print(f"[{idx}/{len(lines)}] Submitting {norm}...", end=" ", flush=True)
        res = submit_entry(
            date=date, shift=shift, camera=camera, location=location,
            recorder=recorder, scene=scene, task=task, duration=norm
        )
        if res.get("success"):
            success += 1
            print("✅ OK")
        else:
            print(f"❌ Failed: {res.get('message')}")

    print(f"\nFinished: {success}/{len(lines)} recorded in Google Sheet.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--batch":
        batch_file_mode(sys.argv[2])
    else:
        interactive_session()

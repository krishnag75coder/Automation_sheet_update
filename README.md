# 🚀 Production Task Entry Automation

Automated entry system for Google Form:
**[Production Task Entry Form](https://docs.google.com/forms/d/e/1FAIpQLSfGQNuI7ZWSq1MkLafYsbAtVVBTnuF9P7Bnh6YFFCAQqzYSQA/viewform)**

This tool is designed specifically for your requirement:
> **"Only the timings will type only and rest of the thing will select once and all the entry update in the sheet"**

---

## 🌟 Key Features

1. **Select Fixed Details Once**:
   - Date, Shift (Morning/Evening), Location (Noida/Gurugram), Camera (Cam 1–15), Recorder Name, Scene, and Task are selected once.
   - **Auto-Saved Locally**: Your selections are remembered across sessions so you don't even have to re-select when you reopen.
   - **Lock Switch**: Toggle the lock to prevent accidental mouse clicks while entering timings.

2. **Rapid Timings Entry (Type Only & Press Enter)**:
   - Type your duration (e.g. `00:04:15`, or shortcuts like `4:15` or `45`) and hit **Enter**.
   - Directly posts to the Google Form response endpoint (`formResponse`) without opening multiple browser tabs.
   - Updates your linked Google Sheet immediately in real-time.
   - Keeps cursor focused in the timing box so you can type the next timing immediately without touching the mouse!
   - Synthesizes audio chime and visual checkmark for rapid feedback.

3. **Bulk Multi-Paste Mode**:
   - Paste 10, 50, or 100 timings (from Excel or Notepad) into the textarea.
   - One click submits all entries sequentially with a live progress bar.

4. **Start & End Time Calculator**:
   - Enter Start Time (e.g. `10:00:00`) and End Time (e.g. `10:14:35`).
   - Automatically computes duration (`00:14:35`) and submits it to the sheet.

5. **Live Log & CSV Backup**:
   - View recent submissions and status directly on the dashboard.
   - One-click export to local CSV for your records.

---

## ⚡ How to Run

### Method 1: One-Click Windows Launch (Recommended)
Simply double-click **`start.bat`** in this folder!
It will start the local server and automatically open your browser to `http://127.0.0.1:5000`.

### Method 2: Command Line
Open PowerShell or Command Prompt in this folder and run:
```bash
python app.py
```
Then visit: `http://127.0.0.1:5000`

### Method 3: Terminal CLI Mode
If you prefer entering timings directly from the terminal:
```bash
python cli.py
```
It asks you for the fixed details once, then lets you enter timing after timing continuously.

### Method 4: Browser Userscript (Tampermonkey)
If you prefer working on `docs.google.com/forms` directly:
- Install the Tampermonkey extension in Chrome/Edge.
- Add the `google_form_helper.user.js` script.
- It will automatically prefill your previous selections every time and focus on the Duration input!

---

## 📋 Form Questions & Entry Mapping

| Question | Type | Options / Format | Google Form Entry ID |
|---|---|---|---|
| **Date** | Date | `YYYY-MM-DD` | `entry.1093955894` |
| **Shift** | Radio | `Morning`, `Evening` | `entry.909598259` |
| **Camera** | Dropdown | `Cam 1` to `Cam 15` | `entry.1510650394` |
| **Location** | Radio | `Noida`, `Gurugram` | `entry.601338817` |
| **Recorder Name** | Dropdown | 21 Recorders (Anchal, Mayank, etc.) | `entry.253587207` |
| **Scene** | Dropdown | 41 Scenes (reception, board room, etc.) | `entry.1557748935` |
| **Task** | Dropdown | 47 Tasks (Arrange Items, Restock, etc.) | `entry.1612822529` |
| **Duration** | Text | `00:00:00` | `entry.1309181485` |

---

## 💡 Timing Format Shortcuts Accepted
You do not have to type the full `00:00:00` format manually; the tool automatically formats:
- `4:15` ➔ `00:04:15`
- `05:30` ➔ `00:05:30`
- `1:15:20` ➔ `01:15:20`
- `45` or `45s` ➔ `00:00:45`
- `15m` ➔ `00:15:00`

## Live link 
https://automation-sheet-update.onrender.com/

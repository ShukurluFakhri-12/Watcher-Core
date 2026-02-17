# 🔍 Watcher-Core Engine v1.0

Watcher-Core is a smart automation tool designed to monitor website content changes. It takes snapshots of specific web elements and alerts you when a change is detected, showing a detailed side-by-side comparison.



## ✨ Key Features
- **Smart Scraper:** Uses BeautifulSoup4 to target specific CSS selectors.
- **Diff Detection:** Visual reporting of added/removed content using `difflib`.
- **Persistent Storage:** SQLite database tracks historical data for consistency.
- **Auto-Config:** Automatically generates a `config.json` template on first run.

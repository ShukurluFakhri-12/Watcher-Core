import sqlite3
import requests
from bs4 import BeautifulSoup
import difflib
import time
import json
import os

# Professional UI Header
def print_banner():
    print("-" * 50)
    print("      WATCHER-CORE v1.0 - SMART MONITORING")
    print("-" * 50)
    print("[*] Status: Running")
    print("[*] Control: Press Ctrl+C to Exit")
    print("-" * 50)

def init_db():
    conn = sqlite3.connect('watcher.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS sites 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                      url TEXT UNIQUE, 
                      css_selector TEXT, 
                      last_content TEXT, 
                      status TEXT)''')
    conn.commit()
    conn.close()

# AUTOMATIC CONFIG CREATOR (Customer Friendly)
def load_config(filename='config.json'):
    if not os.path.exists(filename):
        print(f"[!] Config not found. Creating default {filename}...")
        default_config = [
            {"name": "Python News", "url": "https://www.python.org", "selector": "title"}
        ]
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=4)
    
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            sites = json.load(file)
            for site in sites:
                add_site(site['url'], site['selector'])
            print(f"[*] Successfully loaded {len(sites)} target(s) from config.")
    except Exception as e:
        print(f"[!] Critical Config Error: {e}")

def add_site(url, selector):
    conn = sqlite3.connect('watcher.db')
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO sites (url, css_selector, status) VALUES (?, ?, ?)', 
                   (url, selector, 'active'))
    conn.commit()
    conn.close()

def fetch_content(url, selector):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            element = soup.select_one(selector)
            return element.get_text(strip=True) if element else "Element not found"
    except:
        return None

def check_for_updates():
    conn = sqlite3.connect('watcher.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, url, css_selector, last_content FROM sites WHERE status='active'")
    records = cursor.fetchall()
    
    for row in records:
        site_id, url, selector, old_content = row
        current_content = fetch_content(url, selector)
        
        if current_content is None:
            print(f"[Offline] Could not reach: {url}")
            continue
            
        if old_content is None:
            print(f"[System] Initializing data for: {url}")
            cursor.execute("UPDATE sites SET last_content = ? WHERE id = ?", (current_content, site_id))
            conn.commit()
        elif current_content != old_content:
            print(f"\n[!!!] CHANGE DETECTED: {url}")
            diff = difflib.ndiff([old_content], [current_content])
            print("--- Summary of Change ---")
            print('\n'.join(diff))
            cursor.execute("UPDATE sites SET last_content = ? WHERE id = ?", (current_content, site_id))
            conn.commit()
            print("-" * 25)
        else:
            print(f"[Checked] {url}: No changes.")
            
    conn.close()

if __name__ == "__main__":
    init_db()
    print_banner() 
    load_config()  
    
    try:
        while True:
            check_for_updates()
            print("\n[Waiting] Scanning again in 60 seconds...")
            time.sleep(60)
    except KeyboardInterrupt:
        print("\n[!] Shutting down gracefully. Goodbye!")

#!/usr/bin/env python3
"""
Scrape current data from the live General Strike US site.
Appends new data to the fine-grained CSV if it's newer than the latest entry.
"""

import csv
import sys
import re
from datetime import datetime
import requests


def extract_api_url(html):
    """Extract the Google Sheets API URL from the HTML."""
    try:
        if 'sheets.googleapis.com' in html:
            pattern = r'https://sheets\.googleapis\.com/v4/spreadsheets/[^"\s]+'
            match = re.search(pattern, html)
            if match:
                return match.group(0)
        return None
    except Exception as e:
        print(f"Error extracting API URL: {e}", file=sys.stderr)
        return None


def fetch_google_sheets_data(session, api_url):
    """Fetch data from the Google Sheets API."""
    try:
        # Add Referer header to satisfy API key restrictions
        headers = {
            'Referer': 'https://generalstrikeus.com/'
        }
        response = session.get(api_url, headers=headers, timeout=10, allow_redirects=True)

        if response.status_code != 200:
            return None, None

        data = response.json()

        # The API returns data in the format: {"values": [["committed"]]}
        if 'values' in data and len(data['values']) > 0:
            values = data['values'][0]
            if len(values) >= 1:
                committed = values[0].replace(',', '').strip()

                # Validate that we got an actual number
                if committed.isdigit():
                    committed_int = int(committed)
                    needed_int = 11000000 - committed_int
                    return str(committed_int), str(needed_int)

        return None, None

    except Exception as e:
        print(f"Error fetching Sheets API: {e}", file=sys.stderr)
        return None, None


def scrape_live_site():
    """Scrape the current live site."""
    url = "https://generalstrikeus.com"

    print(f"Scraping live site: {url}")

    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    })

    try:
        response = session.get(url, timeout=15)

        if response.status_code != 200:
            print(f"Error: HTTP {response.status_code}")
            return None

        # Extract the Google Sheets API URL from the HTML
        api_url = extract_api_url(response.text)

        if not api_url:
            print("Error: Could not find Google Sheets API URL")
            return None

        print(f"Found API URL, fetching data...")

        # Fetch the actual data from the Google Sheets API
        committed, needed = fetch_google_sheets_data(session, api_url)

        if committed and needed:
            print(f"✓ Committed: {int(committed):,}, Needed: {int(needed):,}")

            # Get current timestamp
            now = datetime.utcnow()
            date_str = now.strftime('%Y-%m-%d')
            timestamp_str = now.strftime('%Y%m%d%H%M%S')

            return {
                'date': date_str,
                'timestamp': timestamp_str,
                'committed': committed,
                'needed': needed,
                'url': ''  # No URL for live scrapes
            }
        else:
            print("Error: Could not extract counts from API")
            return None

    except requests.Timeout:
        print("Error: Request timeout")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def load_existing_data(csv_file):
    """Load existing data from CSV file."""
    existing_data = []
    try:
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            existing_data = list(reader)
    except FileNotFoundError:
        pass
    return existing_data


def get_latest_timestamp(existing_data):
    """Get the latest timestamp from existing data."""
    if not existing_data:
        return None

    timestamps = [row['timestamp'] for row in existing_data if row.get('timestamp')]
    if not timestamps:
        return None

    return max(timestamps)


def main():
    csv_file = 'general_strike_data plus-fine-grained.csv'

    # Scrape live site
    new_data = scrape_live_site()

    if not new_data:
        print("Failed to scrape live site")
        sys.exit(1)

    # Load existing data
    existing_data = load_existing_data(csv_file)
    latest_timestamp = get_latest_timestamp(existing_data)

    # Check if we have newer data
    if latest_timestamp and new_data['timestamp'] <= latest_timestamp:
        print(f"No new data (latest: {latest_timestamp}, current: {new_data['timestamp']})")
        sys.exit(0)

    # Append new data
    print(f"\nAppending new data to {csv_file}...")
    with open(csv_file, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['date', 'timestamp', 'committed', 'needed', 'url'])
        writer.writerow(new_data)

    print(f"✓ Added new entry: {new_data['date']} - {new_data['committed']} committed")

    # Output for GitHub Actions
    print(f"\n::set-output name=new_data::true")
    print(f"::set-output name=committed::{new_data['committed']}")
    print(f"::set-output name=date::{new_data['date']}")


if __name__ == '__main__':
    main()

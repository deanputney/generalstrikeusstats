#!/usr/bin/env python3
"""
Scrape General Strike US signup data from Wayback Machine archives.
This version scrapes ALL available snapshots (no weekly sampling).
Simple version using requests + BeautifulSoup (no browser required).
"""

import json
import csv
import sys
import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup


def extract_api_url(html):
    """Extract the Google Sheets API URL from the HTML."""
    try:
        # Look for the Google Sheets API URL
        if 'sheets.googleapis.com' in html:
            import re
            pattern = r'https://sheets\.googleapis\.com/v4/spreadsheets/[^"\s]+'
            match = re.search(pattern, html)
            if match:
                return match.group(0)
        return None
    except Exception as e:
        print(f"  Error extracting API URL: {e}", file=sys.stderr)
        return None


def fetch_google_sheets_data(session, timestamp, api_url):
    """Fetch data from the Google Sheets API via Wayback Machine."""
    try:
        # Convert the API URL to a Wayback Machine URL
        wayback_api_url = f"https://web.archive.org/web/{timestamp}/{api_url}"

        # Follow redirects automatically
        response = session.get(wayback_api_url, timeout=10, allow_redirects=True)

        if response.status_code != 200:
            return None, None

        data = response.json()

        # The API returns data in the format: {"values": [["committed"]]}
        # The "needed" value is calculated as 11,000,000 - committed
        if 'values' in data and len(data['values']) > 0:
            values = data['values'][0]
            if len(values) >= 1:
                committed = values[0].replace(',', '').strip()

                # Validate that we got an actual number, not a placeholder
                if committed.isdigit():
                    committed_int = int(committed)
                    needed_int = 11000000 - committed_int
                    return str(committed_int), str(needed_int)

        return None, None

    except Exception as e:
        print(f"    Error fetching Sheets API: {e}", file=sys.stderr)
        return None, None


def scrape_snapshot(session, timestamp, url):
    """Scrape a single Wayback Machine snapshot."""
    # Format: YYYYMMDDHHMMSS -> YYYY-MM-DD
    date_str = timestamp[:8]
    formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"

    wayback_url = f"https://web.archive.org/web/{timestamp}/{url}"

    print(f"Scraping {formatted_date} ({timestamp})...")

    try:
        response = session.get(wayback_url, timeout=15)

        if response.status_code != 200:
            print(f"  ✗ HTTP {response.status_code}")
            return None

        # Extract the Google Sheets API URL from the HTML
        api_url = extract_api_url(response.text)

        if not api_url:
            print(f"  ✗ Could not find Google Sheets API URL")
            return None

        print(f"    Found API URL, fetching data...")

        # Fetch the actual data from the Google Sheets API
        committed, needed = fetch_google_sheets_data(session, timestamp, api_url)

        if committed and needed:
            # Format with commas for display
            committed_display = f"{int(committed):,}"
            needed_display = f"{int(needed):,}"
            print(f"  ✓ Committed: {committed_display}, Needed: {needed_display}")
            return {
                'date': formatted_date,
                'timestamp': timestamp,
                'committed': committed,
                'needed': needed,
                'url': wayback_url
            }
        else:
            print(f"  ✗ Could not extract counts from API")
            return None

    except requests.Timeout:
        print(f"  ✗ Request timeout")
        return None
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return None


def is_valid_data(committed, needed):
    """Check if the data is valid (numeric and not placeholders)."""
    if not committed or not needed:
        return False
    # Remove any commas and check if it's a valid number
    committed_clean = str(committed).replace(',', '').strip()
    needed_clean = str(needed).replace(',', '').strip()
    return committed_clean.isdigit() and needed_clean.isdigit() and '#' not in committed and '#' not in needed


def load_existing_data(filename):
    """Load existing data from CSV file."""
    existing = {}
    try:
        with open(filename, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                timestamp = row.get('timestamp', '')
                committed = row.get('committed', '')
                needed = row.get('needed', '')

                # Regenerate date from timestamp to ensure it's always correct
                if timestamp and len(timestamp) >= 8:
                    date_str = timestamp[:8]
                    date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
                else:
                    continue  # Skip rows without valid timestamps

                if is_valid_data(committed, needed):
                    existing[date] = {
                        'date': date,
                        'timestamp': timestamp,
                        'committed': committed,
                        'needed': needed,
                        'url': row.get('url', '')
                    }
    except FileNotFoundError:
        pass  # File doesn't exist yet
    return existing


def sample_weekly_snapshots(snapshots):
    """Sample one snapshot per week from the list."""
    weekly_snapshots = {}

    for timestamp, url in snapshots:
        # Extract date and calculate week number
        date_str = timestamp[:8]  # YYYYMMDD
        date = datetime.strptime(date_str, '%Y%m%d')
        # Use ISO calendar week (year, week_number)
        year_week = (date.year, date.isocalendar()[1])

        # Keep only the first snapshot of each week
        if year_week not in weekly_snapshots:
            weekly_snapshots[year_week] = (timestamp, url)

    # Sort by date
    sorted_snapshots = sorted(weekly_snapshots.values(), key=lambda x: x[0])
    return sorted_snapshots


def fetch_cdx_snapshots(from_date='20241101', to_date='20251231'):
    """Fetch available snapshots from Wayback Machine CDX API."""
    cdx_url = (
        f"http://web.archive.org/cdx/search/cdx"
        f"?url=generalstrikeus.com"
        f"&from={from_date}"
        f"&to={to_date}"
        f"&output=json"
        f"&filter=statuscode:200"
        f"&filter=mimetype:text/html"
        f"&collapse=timestamp:8"
    )

    print("Fetching snapshots from Wayback Machine CDX API...")
    try:
        response = requests.get(cdx_url, timeout=30)
        response.raise_for_status()
        snapshots_data = response.json()

        # Save to local file
        with open('wayback_snapshots.json', 'w') as f:
            json.dump(snapshots_data, f, indent=2)

        print(f"✓ Saved snapshots to wayback_snapshots.json")
        return snapshots_data
    except Exception as e:
        print(f"✗ Error fetching CDX data: {e}")
        # Try to load from existing file
        try:
            with open('wayback_snapshots.json', 'r') as f:
                print("  Using existing wayback_snapshots.json")
                return json.load(f)
        except FileNotFoundError:
            print("  No existing snapshot file found")
            raise


def main():
    # Fetch snapshots from CDX API
    snapshots_data = fetch_cdx_snapshots()

    # Skip header row and extract timestamp and URL
    all_snapshots = []
    for row in snapshots_data[1:]:  # Skip header
        timestamp = row[1]
        url = row[2]
        all_snapshots.append((timestamp, url))

    print(f"Found {len(all_snapshots)} total snapshots")
    print(f"Will scrape ALL available snapshots\n")

    # Use all snapshots (no weekly sampling)
    snapshots = all_snapshots

    # Initialize output file
    output_file = 'general_strike_data.csv'

    # Load existing valid data
    print(f"Loading existing data from {output_file}...")
    existing_data = load_existing_data(output_file)
    print(f"Found {len(existing_data)} dates with valid data\n")

    # Collect all results (existing + new)
    all_results = {}

    # Add existing valid data
    for date, data in existing_data.items():
        all_results[date] = data

    # Create a requests session for connection pooling
    new_count = 0
    skipped_count = 0
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    })

    # Scrape each snapshot
    for i, (timestamp, url) in enumerate(snapshots, 1):
        print(f"\n[{i}/{len(snapshots)}]")

        # Check if we already have valid data for this date
        date_str = timestamp[:8]
        formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"

        if formatted_date in existing_data:
            print(f"Skipping {formatted_date} - already have valid data")
            skipped_count += 1
            continue

        result = scrape_snapshot(session, timestamp, url)

        if result:
            all_results[result['date']] = result
            new_count += 1

        # Be nice to archive.org - small delay between requests
        time.sleep(1)

    # Write all results to CSV (sorted by date)
    print(f"\n\nWriting all results to {output_file}...")
    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['date', 'timestamp', 'committed', 'needed', 'url'])
        writer.writeheader()
        for date in sorted(all_results.keys()):
            writer.writerow(all_results[date])

    total_valid = len(all_results)
    print(f"✓ Done!")
    print(f"  Skipped: {skipped_count} (already had valid data)")
    print(f"  New: {new_count}")
    print(f"  Total valid entries: {total_valid} out of {len(snapshots)} snapshots")
    print(f"\nOutput saved to: {output_file}")


if __name__ == '__main__':
    main()

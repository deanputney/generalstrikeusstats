#!/usr/bin/env python3
"""
Scrape General Strike US signup data from Wayback Machine archives.
"""

import json
import csv
import sys
from datetime import datetime
import requests
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


def extract_counts(page):
    """Extract committed and needed counts from the page."""
    try:
        result = page.evaluate("""() => {
            // Find elements with "COMMITTED" and "NEEDED" text
            const allElements = Array.from(document.querySelectorAll('*'));

            // Find COMMITTED section
            const committedElement = allElements.find(el => el.textContent.trim() === 'COMMITTED');
            const committedNumber = committedElement?.parentElement?.querySelector('h1')?.textContent;

            // Find NEEDED section
            const neededElement = allElements.find(el => el.textContent.trim() === 'NEEDED');
            const neededNumber = neededElement?.parentElement?.querySelector('h1')?.textContent;

            return {
                committed: committedNumber,
                needed: neededNumber
            };
        }""")

        return result.get('committed'), result.get('needed')
    except Exception as e:
        print(f"  Error extracting counts: {e}", file=sys.stderr)
        return None, None


def scrape_snapshot(page, timestamp, url):
    """Scrape a single Wayback Machine snapshot."""
    # Format: YYYYMMDDHHMMSS -> YYYY-MM-DD
    date_str = timestamp[:8]
    formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"

    wayback_url = f"https://web.archive.org/web/{timestamp}/{url}"

    print(f"Scraping {formatted_date} ({timestamp})...")

    try:
        page.goto(wayback_url, timeout=15000, wait_until="domcontentloaded")
        page.wait_for_timeout(1000)  # Give page time to render

        committed, needed = extract_counts(page)

        if committed and needed:
            # Remove commas from numbers for easier processing
            committed_clean = committed.replace(',', '')
            needed_clean = needed.replace(',', '')
            print(f"  ✓ Committed: {committed}, Needed: {needed}")
            return {
                'date': formatted_date,
                'timestamp': timestamp,
                'committed': committed_clean,
                'needed': needed_clean,
                'url': wayback_url
            }
        else:
            print(f"  ✗ Could not extract counts")
            return None

    except PlaywrightTimeoutError:
        print(f"  ✗ Timeout loading page")
        return None
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return None


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

    # Sample one per week
    snapshots = sample_weekly_snapshots(all_snapshots)
    print(f"Sampling {len(snapshots)} snapshots (one per week)\n")

    # Initialize output file
    output_file = 'general_strike_data.csv'

    # Write CSV header
    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['date', 'timestamp', 'committed', 'needed', 'url'])
        writer.writeheader()

    print(f"Writing results to {output_file}\n")

    # Initialize Playwright
    results_count = 0

    with sync_playwright() as p:
        print("Launching browser...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        page = context.new_page()

        # Scrape each snapshot
        for i, (timestamp, url) in enumerate(snapshots, 1):
            print(f"\n[{i}/{len(snapshots)}]")
            result = scrape_snapshot(page, timestamp, url)

            if result:
                # Write result immediately to CSV (append mode)
                with open(output_file, 'a', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=['date', 'timestamp', 'committed', 'needed', 'url'])
                    writer.writerow(result)
                results_count += 1

        browser.close()

    print(f"\n\n✓ Done! Scraped {results_count} out of {len(snapshots)} snapshots")
    print(f"  Success rate: {results_count/len(snapshots)*100:.1f}%")
    print(f"\nOutput saved to: {output_file}")


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Generate a plot of General Strike US growth over time.
"""

import csv
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime


def main():
    # Read the data
    dates = []
    committed = []

    with open('general_strike_data.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            date_str = row.get('date', '')
            timestamp = row.get('timestamp', '')
            committed_str = row.get('committed', '')

            # Skip rows without committed data
            if not committed_str:
                continue

            # Parse date - use timestamp if date field is empty
            if date_str:
                date = datetime.strptime(date_str, '%Y-%m-%d')
            elif timestamp and len(timestamp) >= 8:
                # Parse date from timestamp (YYYYMMDD)
                date_from_ts = timestamp[:8]
                date = datetime.strptime(date_from_ts, '%Y%m%d')
            else:
                continue  # Skip rows without valid date or timestamp

            dates.append(date)
            committed.append(int(committed_str))

    if not dates:
        print("Error: No data found in general_strike_data.csv")
        return

    # Create the plot
    fig, ax = plt.subplots(figsize=(14, 7))

    # Plot the data
    ax.plot(dates, committed, linewidth=2.5, color='#2E86AB', marker='o', markersize=4, markerfacecolor='#A23B72')

    # Format the y-axis to show numbers with commas
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}'))

    # Set Y-axis limit to 500k for better visibility
    ax.set_ylim(0, 500000)

    # Style the plot
    ax.set_xlabel('Date', fontsize=14, fontweight='bold')
    ax.set_ylabel('People Committed', fontsize=14, fontweight='bold')
    ax.set_title('General Strike US - Growth Over Time', fontsize=18, fontweight='bold', pad=20)

    # Format x-axis dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    plt.xticks(rotation=45, ha='right')

    # Add grid
    ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)

    # Add statistics text box with latest date
    start_val = committed[0]
    end_val = committed[-1]
    growth = end_val - start_val
    growth_pct = (growth / start_val) * 100
    latest_date = dates[-1].strftime('%B %d, %Y')

    stats_text = f'Start: {start_val:,}\nCurrent: {end_val:,}\nGrowth: +{growth:,} (+{growth_pct:.1f}%)\nAs of: {latest_date}'
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
    ax.text(0.98, 0.97, stats_text, transform=ax.transAxes, fontsize=11,
            verticalalignment='top', horizontalalignment='right', bbox=props, family='monospace')

    # Tight layout
    plt.tight_layout()

    # Save the plot at 72 DPI
    output_file = 'strike_growth_plot.png'
    plt.savefig(output_file, dpi=72, bbox_inches='tight')

    print(f"✓ Plot saved as: {output_file}")
    print(f"  Date range: {dates[0].strftime('%B %d, %Y')} → {latest_date}")
    print(f"  Data points: {len(dates)}")
    print(f"  Growth: {start_val:,} → {end_val:,} (+{growth:,})")


if __name__ == '__main__':
    main()

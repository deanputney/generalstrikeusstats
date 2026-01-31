#!/usr/bin/env python3
"""
Generate a plot of General Strike US growth over time.
"""

import csv
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import numpy as np


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

    # Plot the actual data
    ax.plot(dates, committed, linewidth=2.5, color='#2E86AB', marker='o', markersize=4,
            markerfacecolor='#A23B72', label='Actual Committed', zorder=3)

    # Goal line
    goal = 11000000
    ax.axhline(y=goal, color='#28A745', linestyle='--', linewidth=2,
               label=f'Goal: {goal:,}', alpha=0.8, zorder=2)

    # Calculate projection based on last 1 month of data
    cutoff_date = dates[-1] - timedelta(days=30)
    recent_dates = [d for d in dates if d >= cutoff_date]
    recent_committed = [committed[i] for i, d in enumerate(dates) if d >= cutoff_date]

    if len(recent_dates) >= 2:
        # Convert dates to days since first date for linear regression
        days_since_start = [(d - recent_dates[0]).days for d in recent_dates]

        # Fit linear regression to recent data
        coeffs = np.polyfit(days_since_start, recent_committed, 1)
        daily_growth = coeffs[0]

        # Project forward: calculate how many days to reach goal
        current_value = committed[-1]
        days_to_goal = (goal - current_value) / daily_growth if daily_growth > 0 else 0

        if days_to_goal > 0 and days_to_goal < 365 * 5:  # Only project if reasonable (< 5 years)
            projection_end_date = dates[-1] + timedelta(days=days_to_goal)
            projection_dates = [dates[-1], projection_end_date]
            projection_values = [current_value, goal]

            ax.plot(projection_dates, projection_values, linewidth=2, color='#FFA500',
                   linestyle=':', label=f'1-Month Projection', alpha=0.8, zorder=2)

            # Add projection info to plot
            proj_text = f'Projected goal date:\n{projection_end_date.strftime("%B %d, %Y")}\n(+{int(days_to_goal)} days)'
            ax.text(projection_end_date, goal, proj_text, fontsize=9,
                   verticalalignment='bottom', horizontalalignment='left',
                   bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7))

    # Format the y-axis to show numbers with commas
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}'))

    # Dynamic Y-axis limit based on data
    max_val = max(max(committed), goal * 1.1)
    ax.set_ylim(0, max_val)

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

    # Add legend
    ax.legend(loc='upper left', fontsize=11, framealpha=0.9)

    # Add statistics text box with latest date
    start_val = committed[0]
    end_val = committed[-1]
    growth = end_val - start_val
    growth_pct = (growth / start_val) * 100
    latest_date = dates[-1].strftime('%B %d, %Y')

    # Calculate 30-day growth
    if len(recent_dates) >= 2:
        recent_growth = recent_committed[-1] - recent_committed[0]
        days_span = (recent_dates[-1] - recent_dates[0]).days
        daily_avg = recent_growth / days_span if days_span > 0 else 0
        stats_text = f'Start: {start_val:,}\nCurrent: {end_val:,}\nTotal Growth: +{growth:,} (+{growth_pct:.1f}%)\n30-Day Growth: +{recent_growth:,}\nDaily Avg (30d): +{daily_avg:.0f}\nAs of: {latest_date}'
    else:
        stats_text = f'Start: {start_val:,}\nCurrent: {end_val:,}\nGrowth: +{growth:,} (+{growth_pct:.1f}%)\nAs of: {latest_date}'

    props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
    ax.text(0.98, 0.97, stats_text, transform=ax.transAxes, fontsize=10,
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

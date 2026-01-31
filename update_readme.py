#!/usr/bin/env python3
"""
Update README.md with the latest statistics from the CSV file.
"""

import csv
import re
from datetime import datetime


def load_data(csv_file):
    """Load data from CSV file."""
    dates = []
    committed = []

    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            date_str = row.get('date', '')
            committed_str = row.get('committed', '')

            if not date_str or not committed_str:
                continue

            date = datetime.strptime(date_str, '%Y-%m-%d')
            dates.append(date)
            committed.append(int(committed_str))

    return dates, committed


def calculate_stats(dates, committed):
    """Calculate key statistics."""
    start_val = committed[0]
    end_val = committed[-1]
    growth = end_val - start_val
    growth_pct = (growth / start_val) * 100
    latest_date = dates[-1]

    # Calculate 30-day growth
    from datetime import timedelta
    cutoff_date = dates[-1] - timedelta(days=30)
    recent_indices = [i for i, d in enumerate(dates) if d >= cutoff_date]

    if len(recent_indices) >= 2:
        recent_growth = committed[recent_indices[-1]] - committed[recent_indices[0]]
        days_span = (dates[recent_indices[-1]] - dates[recent_indices[0]]).days
        daily_avg = recent_growth / days_span if days_span > 0 else 0
    else:
        daily_avg = 0

    goal = 11000000
    progress_pct = (end_val / goal) * 100

    return {
        'committed': end_val,
        'growth_pct': growth_pct,
        'data_points': len(dates),
        'latest_date': latest_date.strftime('%B %d, %Y'),
        'progress_pct': progress_pct,
        'daily_avg': int(daily_avg)
    }


def update_readme(stats):
    """Update README.md with latest statistics."""
    readme_file = 'README.md'

    with open(readme_file, 'r') as f:
        content = f.read()

    # Update the status section
    status_pattern = r'\*\*Current Status \(as of [^)]+\):\*\*\n- \*\*[0-9,]+ people committed\*\*[^\n]+\n- \*\*[0-9]+ data points\*\*[^\n]+\n- \*\*[0-9.]+% progress\*\*[^\n]+\n- \*\*~[0-9,]+ people/day\*\*[^\n]+'

    new_status = f"""**Current Status (as of {stats['latest_date']}):**
- **{stats['committed']:,} people committed** (+{stats['growth_pct']:.1f}% growth since November 2024)
- **{stats['data_points']} data points** collected from November 2024 to {stats['latest_date'].split()[-1]}
- **{stats['progress_pct']:.2f}% progress** toward 11 million goal
- **~{stats['daily_avg']:,} people/day** average growth rate (last 30 days)"""

    updated_content = re.sub(status_pattern, new_status, content)

    # Update the "Last Updated" line
    updated_content = re.sub(
        r'\*Last Updated: [^\*]+\*',
        f"*Last Updated: {datetime.now().strftime('%B %d, %Y')}*",
        updated_content
    )

    with open(readme_file, 'w') as f:
        f.write(updated_content)

    print(f"✓ Updated README.md with latest statistics")
    print(f"  Committed: {stats['committed']:,}")
    print(f"  Data points: {stats['data_points']}")
    print(f"  Latest date: {stats['latest_date']}")


def main():
    csv_file = 'general_strike_data plus-fine-grained.csv'

    print("Loading data from CSV...")
    dates, committed = load_data(csv_file)

    print("Calculating statistics...")
    stats = calculate_stats(dates, committed)

    print("Updating README.md...")
    update_readme(stats)

    print("\n✓ README.md updated successfully!")


if __name__ == '__main__':
    main()

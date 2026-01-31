#!/usr/bin/env python3
"""
Generate multiple plots of General Strike US growth over time.
"""

import csv
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import numpy as np
import argparse
import os


def load_data(csv_file):
    """Load data from CSV file."""
    dates = []
    committed = []

    with open(csv_file, 'r') as f:
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

    return dates, committed


def plot_1_basic(dates, committed, output_dir):
    """Plot 1: Just the count of committed over time."""
    fig, ax = plt.subplots(figsize=(14, 7))

    # Plot the actual data
    ax.plot(dates, committed, linewidth=2.5, color='#2E86AB', marker='o', markersize=4,
            markerfacecolor='#A23B72', zorder=3)

    # Format the y-axis to show numbers with commas
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}'))

    # Style the plot
    ax.set_xlabel('Date', fontsize=14, fontweight='bold')
    ax.set_ylabel('People Committed', fontsize=14, fontweight='bold')
    ax.set_title('General Strike US - Committed Count Over Time', fontsize=18, fontweight='bold', pad=20)

    # Format x-axis dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    plt.xticks(rotation=45, ha='right')

    # Add grid
    ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)

    # Add statistics text box
    start_val = committed[0]
    end_val = committed[-1]
    growth = end_val - start_val
    growth_pct = (growth / start_val) * 100
    latest_date = dates[-1].strftime('%B %d, %Y')

    stats_text = f'Start: {start_val:,}\nCurrent: {end_val:,}\nGrowth: +{growth:,} (+{growth_pct:.1f}%)\nAs of: {latest_date}'
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
    ax.text(0.98, 0.03, stats_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='bottom', horizontalalignment='right', bbox=props, family='monospace')

    # Tight layout
    plt.tight_layout()

    # Save the plot
    output_file = os.path.join(output_dir, 'plot_1_basic.png')
    plt.savefig(output_file, dpi=72, bbox_inches='tight')
    plt.close()

    print(f"✓ Plot 1 saved as: {output_file}")


def plot_2_with_goal(dates, committed, output_dir):
    """Plot 2: Count with goal line."""
    fig, ax = plt.subplots(figsize=(14, 7))

    # Get the last goal value from the data (11,000,000 - last needed value)
    goal = 11000000

    # Plot the actual data
    ax.plot(dates, committed, linewidth=2.5, color='#2E86AB', marker='o', markersize=4,
            markerfacecolor='#A23B72', label='Committed', zorder=3)

    # Goal line
    ax.axhline(y=goal, color='#28A745', linestyle='--', linewidth=2,
               label=f'Goal: {goal:,}', alpha=0.8, zorder=2)

    # Format the y-axis to show numbers with commas
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}'))

    # Dynamic Y-axis limit
    max_val = max(max(committed), goal * 1.1)
    ax.set_ylim(0, max_val)

    # Style the plot
    ax.set_xlabel('Date', fontsize=14, fontweight='bold')
    ax.set_ylabel('People Committed', fontsize=14, fontweight='bold')
    ax.set_title('General Strike US - Progress Toward Goal', fontsize=18, fontweight='bold', pad=20)

    # Format x-axis dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    plt.xticks(rotation=45, ha='right')

    # Add grid and legend
    ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
    ax.legend(loc='upper left', fontsize=11, framealpha=0.9)

    # Add statistics text box
    start_val = committed[0]
    end_val = committed[-1]
    progress_pct = (end_val / goal) * 100
    latest_date = dates[-1].strftime('%B %d, %Y')

    stats_text = f'Current: {end_val:,}\nGoal: {goal:,}\nProgress: {progress_pct:.2f}%\nAs of: {latest_date}'
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
    ax.text(0.98, 0.03, stats_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='bottom', horizontalalignment='right', bbox=props, family='monospace')

    # Tight layout
    plt.tight_layout()

    # Save the plot
    output_file = os.path.join(output_dir, 'plot_2_with_goal.png')
    plt.savefig(output_file, dpi=72, bbox_inches='tight')
    plt.close()

    print(f"✓ Plot 2 saved as: {output_file}")


def plot_3_logarithmic(dates, committed, output_dir):
    """Plot 3: Count with goal line, logarithmic scale."""
    fig, ax = plt.subplots(figsize=(14, 7))

    goal = 11000000

    # Plot the actual data
    ax.plot(dates, committed, linewidth=2.5, color='#2E86AB', marker='o', markersize=4,
            markerfacecolor='#A23B72', label='Committed', zorder=3)

    # Goal line
    ax.axhline(y=goal, color='#28A745', linestyle='--', linewidth=2,
               label=f'Goal: {goal:,}', alpha=0.8, zorder=2)

    # Set logarithmic scale
    ax.set_yscale('log')

    # Format the y-axis to show numbers with commas
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}'))

    # Style the plot
    ax.set_xlabel('Date', fontsize=14, fontweight='bold')
    ax.set_ylabel('People Committed (log scale)', fontsize=14, fontweight='bold')
    ax.set_title('General Strike US - Progress Toward Goal (Logarithmic)', fontsize=18, fontweight='bold', pad=20)

    # Format x-axis dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    plt.xticks(rotation=45, ha='right')

    # Add grid and legend
    ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5, which='both')
    ax.legend(loc='upper left', fontsize=11, framealpha=0.9)

    # Add statistics text box
    start_val = committed[0]
    end_val = committed[-1]
    progress_pct = (end_val / goal) * 100
    latest_date = dates[-1].strftime('%B %d, %Y')

    stats_text = f'Current: {end_val:,}\nGoal: {goal:,}\nProgress: {progress_pct:.2f}%\nAs of: {latest_date}'
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
    ax.text(0.98, 0.03, stats_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='bottom', horizontalalignment='right', bbox=props, family='monospace')

    # Tight layout
    plt.tight_layout()

    # Save the plot
    output_file = os.path.join(output_dir, 'plot_3_logarithmic.png')
    plt.savefig(output_file, dpi=72, bbox_inches='tight')
    plt.close()

    print(f"✓ Plot 3 saved as: {output_file}")


def plot_4_with_projection(dates, committed, output_dir):
    """Plot 4: Logarithmic with projection based on last month."""
    fig, ax = plt.subplots(figsize=(14, 7))

    goal = 11000000

    # Plot the actual data
    ax.plot(dates, committed, linewidth=2.5, color='#2E86AB', marker='o', markersize=4,
            markerfacecolor='#A23B72', label='Committed', zorder=3)

    # Goal line
    ax.axhline(y=goal, color='#28A745', linestyle='--', linewidth=2,
               label=f'Goal: {goal:,}', alpha=0.8, zorder=2)

    # Calculate projection based on last 1 month of data
    cutoff_date = dates[-1] - timedelta(days=30)
    recent_indices = [i for i, d in enumerate(dates) if d >= cutoff_date]
    recent_dates = [dates[i] for i in recent_indices]
    recent_committed = [committed[i] for i in recent_indices]

    if len(recent_dates) >= 2:
        # Convert dates to days since first date for linear regression
        days_since_start = [(d - recent_dates[0]).days for d in recent_dates]

        # Fit linear regression to recent data
        coeffs = np.polyfit(days_since_start, recent_committed, 1)
        daily_growth = coeffs[0]

        # Project forward: calculate how many days to reach goal
        current_value = committed[-1]
        days_to_goal = (goal - current_value) / daily_growth if daily_growth > 0 else 0

        if days_to_goal > 0:
            projection_end_date = dates[-1] + timedelta(days=days_to_goal)
            projection_dates = [dates[-1], projection_end_date]
            projection_values = [current_value, goal]

            ax.plot(projection_dates, projection_values, linewidth=2.5, color='#FFA500',
                   linestyle=':', label=f'Projection (based on 30-day trend)', alpha=0.9, zorder=2)

            # Calculate years to goal
            years_to_goal = days_to_goal / 365.25

    # Set logarithmic scale
    ax.set_yscale('log')

    # Format the y-axis to show numbers with commas
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}'))

    # Style the plot
    ax.set_xlabel('Date', fontsize=14, fontweight='bold')
    ax.set_ylabel('People Committed (log scale)', fontsize=14, fontweight='bold')
    ax.set_title('General Strike US - Projection to Goal (Logarithmic)', fontsize=18, fontweight='bold', pad=20)

    # Format x-axis dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    plt.xticks(rotation=45, ha='right')

    # Add grid and legend
    ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5, which='both')
    ax.legend(loc='upper left', fontsize=11, framealpha=0.9)

    # Add statistics text box with projection info
    start_val = committed[0]
    end_val = committed[-1]
    progress_pct = (end_val / goal) * 100
    latest_date = dates[-1].strftime('%B %d, %Y')

    if len(recent_dates) >= 2 and days_to_goal > 0:
        stats_text = (f'Current: {end_val:,}\nGoal: {goal:,}\nProgress: {progress_pct:.2f}%\n'
                     f'30-Day Growth: +{int(daily_growth * 30):,}\n'
                     f'Projected Goal Date:\n{projection_end_date.strftime("%B %d, %Y")}\n'
                     f'({years_to_goal:.1f} years)\n'
                     f'As of: {latest_date}')
    else:
        stats_text = f'Current: {end_val:,}\nGoal: {goal:,}\nProgress: {progress_pct:.2f}%\nAs of: {latest_date}'

    props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
    ax.text(0.98, 0.03, stats_text, transform=ax.transAxes, fontsize=9,
            verticalalignment='bottom', horizontalalignment='right', bbox=props, family='monospace')

    # Tight layout
    plt.tight_layout()

    # Save the plot
    output_file = os.path.join(output_dir, 'plot_4_with_projection.png')
    plt.savefig(output_file, dpi=72, bbox_inches='tight')
    plt.close()

    print(f"✓ Plot 4 saved as: {output_file}")


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Generate multiple plots of General Strike US growth over time.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use default CSV and output directory
  python generate_all_plots.py

  # Specify CSV file
  python generate_all_plots.py --csv mydata.csv

  # Specify output directory
  python generate_all_plots.py --output images/custom_plots

  # Specify both
  python generate_all_plots.py --csv mydata.csv --output images/custom_plots
        """
    )
    parser.add_argument(
        '--csv',
        default='general_strike_data.csv',
        help='Path to the CSV file (default: general_strike_data.csv)'
    )
    parser.add_argument(
        '--output',
        default='images/plots_waybackonly',
        help='Output directory for plots (default: images/plots_waybackonly)'
    )
    args = parser.parse_args()

    csv_file = args.csv
    output_dir = args.output

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Load data
    print(f"Loading data from {csv_file}...")
    try:
        dates, committed = load_data(csv_file)
    except FileNotFoundError:
        print(f"Error: CSV file not found: {csv_file}")
        return
    except Exception as e:
        print(f"Error loading data: {e}")
        return

    if not dates:
        print(f"Error: No data found in {csv_file}")
        return

    print(f"Loaded {len(dates)} data points from {dates[0].strftime('%B %d, %Y')} to {dates[-1].strftime('%B %d, %Y')}")
    print(f"Output directory: {output_dir}\n")

    # Generate all plots
    print("Generating plots...\n")
    plot_1_basic(dates, committed, output_dir)
    plot_2_with_goal(dates, committed, output_dir)
    plot_3_logarithmic(dates, committed, output_dir)
    plot_4_with_projection(dates, committed, output_dir)

    print("\n✓ All plots generated successfully!")


if __name__ == '__main__':
    main()

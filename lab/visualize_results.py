#!/usr/bin/env python3
"""
Visualize Market Simulation Results
Creates charts for LOVE minting, market indicators, correlations, and predictions
"""

import json
import sys
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np
import seaborn as sns

# Set style
sns.set_style("darkgrid")
plt.rcParams['figure.figsize'] = (14, 8)


def load_simulation_data(report_file: str = "lab/output/market_simulation_report.json"):
    """Load simulation report data"""
    file_path = Path(report_file)
    if not file_path.exists():
        print(f"Error: Report file not found: {report_file}")
        sys.exit(1)
    
    with open(file_path, 'r') as f:
        return json.load(f)


def plot_love_minting_timeline(data):
    """Plot LOVE minting over time by sector"""
    fig, axes = plt.subplots(2, 1, figsize=(14, 10))
    
    # Extract daily LOVE by sector
    daily_history = data['daily_history']
    sectors = list(data['sector_love'].keys())
    
    days = list(range(1, len(daily_history) + 1))
    
    # Plot 1: Daily LOVE minting by sector
    ax1 = axes[0]
    for sector in sectors:
        sector_love_daily = []
        for day_data in daily_history:
            sector_love = 0.0
            for org_id, org_data in day_data.get('organizations', {}).items():
                # Find which sector this org belongs to
                for org_id_check, org_info in data['organizations'].items():
                    if org_id_check == org_id and org_info['sector'] == sector:
                        sector_love += org_data.get('love_minted', 0.0)
            sector_love_daily.append(sector_love)
        
        ax1.plot(days, sector_love_daily, marker='o', label=sector.replace('_', ' ').title(), linewidth=2)
    
    ax1.set_xlabel('Day', fontsize=12)
    ax1.set_ylabel('LOVE Minted', fontsize=12)
    ax1.set_title('Daily LOVE Minting by Sector', fontsize=14, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Cumulative LOVE by sector
    ax2 = axes[1]
    for sector in sectors:
        cumulative_love = []
        running_total = 0.0
        for day_data in daily_history:
            sector_love = 0.0
            for org_id, org_data in day_data.get('organizations', {}).items():
                for org_id_check, org_info in data['organizations'].items():
                    if org_id_check == org_id and org_info['sector'] == sector:
                        sector_love += org_data.get('love_minted', 0.0)
            running_total += sector_love
            cumulative_love.append(running_total)
        
        ax2.plot(days, cumulative_love, marker='s', label=sector.replace('_', ' ').title(), linewidth=2)
    
    ax2.set_xlabel('Day', fontsize=12)
    ax2.set_ylabel('Cumulative LOVE', fontsize=12)
    ax2.set_title('Cumulative LOVE Minting by Sector', fontsize=14, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def plot_market_indicators(data):
    """Plot market health indicators over time"""
    fig, axes = plt.subplots(2, 1, figsize=(14, 10))
    
    daily_history = data['daily_history']
    sectors = list(data['market_indicators'].keys())
    days = list(range(1, len(daily_history) + 1))
    
    # Plot 1: Market health over time
    ax1 = axes[0]
    for sector in sectors:
        market_values = []
        for day_data in daily_history:
            market_data = day_data.get('market_indicators', {}).get(sector, {})
            market_values.append(market_data.get('value', 0))
        
        ax1.plot(days, market_values, marker='o', label=sector.replace('_', ' ').title(), linewidth=2)
    
    ax1.set_xlabel('Day', fontsize=12)
    ax1.set_ylabel('Market Health (0-100)', fontsize=12)
    ax1.set_title('Market Health Indicators Over Time', fontsize=14, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(0, 100)
    
    # Plot 2: Market trend over time
    ax2 = axes[1]
    for sector in sectors:
        trends = []
        for day_data in daily_history:
            market_data = day_data.get('market_indicators', {}).get(sector, {})
            trends.append(market_data.get('trend', 0))
        
        ax2.plot(days, trends, marker='s', label=sector.replace('_', ' ').title(), linewidth=2)
        ax2.axhline(y=0, color='r', linestyle='--', alpha=0.5, label='Neutral')
    
    ax2.set_xlabel('Day', fontsize=12)
    ax2.set_ylabel('Market Trend (points/day)', fontsize=12)
    ax2.set_title('Market Trend Over Time', fontsize=14, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def plot_love_vs_market_correlation(data):
    """Plot LOVE vs Market correlation scatter plots"""
    sectors = list(data['market_indicators'].keys())
    n_sectors = len(sectors)
    
    fig, axes = plt.subplots(1, n_sectors, figsize=(6*n_sectors, 6))
    if n_sectors == 1:
        axes = [axes]
    
    daily_history = data['daily_history']
    
    for idx, sector in enumerate(sectors):
        ax = axes[idx]
        
        # Extract cumulative LOVE and market values
        cumulative_love = []
        market_values = []
        running_total = 0.0
        
        for day_data in daily_history:
            # Get sector LOVE for this day
            sector_love = 0.0
            for org_id, org_data in day_data.get('organizations', {}).items():
                for org_id_check, org_info in data['organizations'].items():
                    if org_id_check == org_id and org_info['sector'] == sector:
                        sector_love += org_data.get('love_minted', 0.0)
            
            running_total += sector_love
            cumulative_love.append(running_total)
            
            # Get market value
            market_data = day_data.get('market_indicators', {}).get(sector, {})
            market_values.append(market_data.get('value', 0))
        
        # Scatter plot
        ax.scatter(cumulative_love, market_values, alpha=0.6, s=100)
        
        # Add trend line (only if there's variation in the data)
        if len(cumulative_love) > 1 and np.std(cumulative_love) > 0 and np.std(market_values) > 0:
            try:
                z = np.polyfit(cumulative_love, market_values, 1)
                p = np.poly1d(z)
                ax.plot(cumulative_love, p(cumulative_love), "r--", alpha=0.8, linewidth=2)
            except (np.linalg.LinAlgError, ValueError):
                # Skip trend line if fit fails
                pass
        
        # Get correlation
        correlation = data['predictions'].get(sector, {}).get('correlation', 0)
        
        ax.set_xlabel('Cumulative LOVE', fontsize=11)
        ax.set_ylabel('Market Health', fontsize=11)
        ax.set_title(f'{sector.replace("_", " ").title()}\nCorrelation: {correlation:.4f}', 
                     fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def plot_sector_comparison(data):
    """Create comparison charts for sectors"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    
    sectors = list(data['sector_love'].keys())
    sector_labels = [s.replace('_', ' ').title() for s in sectors]
    
    # Plot 1: Total LOVE by sector
    ax1 = axes[0, 0]
    love_values = [data['sector_love'][s] for s in sectors]
    colors = plt.cm.Reds(np.linspace(0.4, 0.9, len(sectors)))
    bars = ax1.bar(sector_labels, love_values, color=colors)
    ax1.set_ylabel('Total LOVE Minted', fontsize=12)
    ax1.set_title('Total LOVE Minted by Sector', fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:,.0f}',
                ha='center', va='bottom', fontsize=10)
    
    # Plot 2: Market change by sector
    ax2 = axes[0, 1]
    market_changes = [data['market_indicators'][s]['change'] for s in sectors]
    colors = ['red' if x < 0 else 'green' for x in market_changes]
    bars = ax2.bar(sector_labels, market_changes, color=colors, alpha=0.7)
    ax2.set_ylabel('Market Change (points)', fontsize=12)
    ax2.set_title('Market Health Change by Sector', fontsize=13, fontweight='bold')
    ax2.axhline(y=0, color='black', linestyle='-', linewidth=1)
    ax2.grid(True, alpha=0.3, axis='y')
    
    for bar in bars:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:+.1f}',
                ha='center', va='bottom' if height > 0 else 'top', fontsize=10)
    
    # Plot 3: Correlation by sector
    ax3 = axes[1, 0]
    correlations = [data['predictions'].get(s, {}).get('correlation', 0) for s in sectors]
    colors = ['red' if x < -0.3 else 'orange' if x < 0 else 'green' if x > 0.3 else 'gray' 
              for x in correlations]
    bars = ax3.bar(sector_labels, correlations, color=colors, alpha=0.7)
    ax3.set_ylabel('Correlation Coefficient', fontsize=12)
    ax3.set_title('LOVE-Market Correlation by Sector', fontsize=13, fontweight='bold')
    ax3.axhline(y=0, color='black', linestyle='-', linewidth=1)
    ax3.set_ylim(-1.1, 1.1)
    ax3.grid(True, alpha=0.3, axis='y')
    
    for bar in bars:
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.3f}',
                ha='center', va='bottom' if height > 0 else 'top', fontsize=10)
    
    # Plot 4: LOVE per Market Point
    ax4 = axes[1, 1]
    love_per_point = []
    for s in sectors:
        total_love = data['sector_love'][s]
        market_change = abs(data['market_indicators'][s]['change'])
        if market_change > 0:
            love_per_point.append(total_love / market_change)
        else:
            love_per_point.append(0)
    
    bars = ax4.bar(sector_labels, love_per_point, color=plt.cm.viridis(np.linspace(0.2, 0.8, len(sectors))))
    ax4.set_ylabel('LOVE per Market Point', fontsize=12)
    ax4.set_title('LOVE Efficiency by Sector', fontsize=13, fontweight='bold')
    ax4.grid(True, alpha=0.3, axis='y')
    
    for bar in bars:
        height = bar.get_height()
        if height > 0:
            ax4.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}',
                    ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    return fig


def plot_prediction_accuracy(data):
    """Plot prediction accuracy visualization"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    sectors = list(data['predictions'].keys())
    sector_labels = [s.replace('_', ' ').title() for s in sectors]
    
    # Plot 1: Prediction correctness
    ax1 = axes[0]
    predictions = [data['predictions'][s].get('prediction_correct', False) for s in sectors]
    colors = ['green' if p else 'red' for p in predictions]
    bars = ax1.bar(sector_labels, [1 if p else 0 for p in predictions], color=colors, alpha=0.7)
    ax1.set_ylabel('Prediction Correct', fontsize=12)
    ax1.set_title('Prediction Accuracy by Sector', fontsize=13, fontweight='bold')
    ax1.set_ylim(0, 1.2)
    ax1.set_yticks([0, 1])
    ax1.set_yticklabels(['Incorrect', 'Correct'])
    ax1.grid(True, alpha=0.3, axis='y')
    
    for i, (bar, pred) in enumerate(zip(bars, predictions)):
        ax1.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.05,
                'CORRECT' if pred else 'INCORRECT',
                ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    # Plot 2: LOVE Change vs Market Change
    ax2 = axes[1]
    love_changes = [data['predictions'][s].get('love_change', 0) for s in sectors]
    market_changes = [data['predictions'][s].get('market_change', 0) for s in sectors]
    predictions_correct = [data['predictions'][s].get('prediction_correct', False) for s in sectors]
    
    colors = ['green' if p else 'red' for p in predictions_correct]
    ax2.scatter(love_changes, market_changes, c=colors, s=200, alpha=0.6, edgecolors='black', linewidth=2)
    
    # Add labels
    for i, label in enumerate(sector_labels):
        ax2.annotate(label, (love_changes[i], market_changes[i]), 
                    xytext=(5, 5), textcoords='offset points', fontsize=9)
    
    ax2.set_xlabel('LOVE Change', fontsize=12)
    ax2.set_ylabel('Market Change', fontsize=12)
    ax2.set_title('LOVE Change vs Market Change\n(Green = Correct Prediction)', 
                 fontsize=13, fontweight='bold')
    ax2.axhline(y=0, color='black', linestyle='--', alpha=0.5)
    ax2.axvline(x=0, color='black', linestyle='--', alpha=0.5)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def create_summary_dashboard(data):
    """Create a comprehensive summary dashboard"""
    fig = plt.figure(figsize=(16, 10))
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
    
    sectors = list(data['sector_love'].keys())
    sector_labels = [s.replace('_', ' ').title() for s in sectors]
    
    # 1. Total LOVE (top left)
    ax1 = fig.add_subplot(gs[0, 0])
    love_values = [data['sector_love'][s] for s in sectors]
    ax1.pie(love_values, labels=sector_labels, autopct='%1.1f%%', startangle=90)
    ax1.set_title('LOVE Distribution', fontweight='bold')
    
    # 2. Market Health (top middle)
    ax2 = fig.add_subplot(gs[0, 1])
    market_current = [data['market_indicators'][s]['current'] for s in sectors]
    colors = plt.cm.RdYlGn(np.array(market_current) / 100)
    bars = ax2.barh(sector_labels, market_current, color=colors)
    ax2.set_xlabel('Market Health')
    ax2.set_xlim(0, 100)
    ax2.set_title('Current Market Health', fontweight='bold')
    for i, (bar, val) in enumerate(zip(bars, market_current)):
        ax2.text(val + 2, i, f'{val:.1f}', va='center', fontsize=9)
    
    # 3. Correlation (top right)
    ax3 = fig.add_subplot(gs[0, 2])
    correlations = [data['predictions'].get(s, {}).get('correlation', 0) for s in sectors]
    colors = ['red' if x < -0.3 else 'orange' if x < 0 else 'green' if x > 0.3 else 'gray' 
              for x in correlations]
    bars = ax3.barh(sector_labels, correlations, color=colors, alpha=0.7)
    ax3.set_xlabel('Correlation')
    ax3.set_xlim(-1, 1)
    ax3.axvline(x=0, color='black', linestyle='-', linewidth=1)
    ax3.set_title('LOVE-Market Correlation', fontweight='bold')
    for i, (bar, val) in enumerate(zip(bars, correlations)):
        ax3.text(val + 0.05 if val >= 0 else val - 0.05, i, f'{val:.3f}', 
                va='center', ha='left' if val >= 0 else 'right', fontsize=9)
    
    # 4. LOVE Timeline (middle, spans 2 columns)
    ax4 = fig.add_subplot(gs[1, :2])
    daily_history = data['daily_history']
    days = list(range(1, len(daily_history) + 1))
    for sector in sectors:
        cumulative_love = []
        running_total = 0.0
        for day_data in daily_history:
            sector_love = 0.0
            for org_id, org_data in day_data.get('organizations', {}).items():
                for org_id_check, org_info in data['organizations'].items():
                    if org_id_check == org_id and org_info['sector'] == sector:
                        sector_love += org_data.get('love_minted', 0.0)
            running_total += sector_love
            cumulative_love.append(running_total)
        ax4.plot(days, cumulative_love, marker='o', label=sector.replace('_', ' ').title(), linewidth=2)
    ax4.set_xlabel('Day')
    ax4.set_ylabel('Cumulative LOVE')
    ax4.set_title('Cumulative LOVE Over Time', fontweight='bold')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    # 5. Market Health Timeline (middle right)
    ax5 = fig.add_subplot(gs[1, 2])
    for sector in sectors:
        market_values = []
        for day_data in daily_history:
            market_data = day_data.get('market_indicators', {}).get(sector, {})
            market_values.append(market_data.get('value', 0))
        ax5.plot(days, market_values, marker='s', label=sector.replace('_', ' ').title(), linewidth=2)
    ax5.set_xlabel('Day')
    ax5.set_ylabel('Market Health')
    ax5.set_title('Market Health Over Time', fontweight='bold')
    ax5.legend(fontsize=8)
    ax5.grid(True, alpha=0.3)
    ax5.set_ylim(0, 100)
    
    # 6. Key Metrics (bottom, spans 3 columns)
    ax6 = fig.add_subplot(gs[2, :])
    ax6.axis('off')
    
    # Calculate summary stats
    total_love = data['total_love_minted']
    total_interventions = data['total_interventions']
    avg_correlation = np.mean([data['predictions'].get(s, {}).get('correlation', 0) for s in sectors])
    correct_predictions = sum(1 for s in sectors if data['predictions'].get(s, {}).get('prediction_correct', False))
    prediction_accuracy = (correct_predictions / len(sectors) * 100) if sectors else 0
    
    summary_text = f"""
    SIMULATION SUMMARY
    {'='*60}
    Total Days: {data['total_days']}
    Total LOVE Minted: {total_love:,.2f}
    Total Interventions: {total_interventions}
    Average Correlation: {avg_correlation:.4f}
    Prediction Accuracy: {correct_predictions}/{len(sectors)} ({prediction_accuracy:.1f}%)
    """
    
    ax6.text(0.1, 0.5, summary_text, fontsize=12, family='monospace',
            verticalalignment='center', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    return fig


def main():
    """Main visualization function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Visualize market simulation results')
    parser.add_argument('--report', default='lab/output/market_simulation_report.json',
                       help='Path to simulation report JSON file')
    parser.add_argument('--output-dir', default='lab/output/visualizations',
                       help='Output directory for visualization files')
    parser.add_argument('--all', action='store_true',
                       help='Generate all visualizations')
    parser.add_argument('--timeline', action='store_true',
                       help='Generate LOVE timeline charts')
    parser.add_argument('--market', action='store_true',
                       help='Generate market indicator charts')
    parser.add_argument('--correlation', action='store_true',
                       help='Generate correlation scatter plots')
    parser.add_argument('--comparison', action='store_true',
                       help='Generate sector comparison charts')
    parser.add_argument('--prediction', action='store_true',
                       help='Generate prediction accuracy charts')
    parser.add_argument('--dashboard', action='store_true',
                       help='Generate summary dashboard')
    
    args = parser.parse_args()
    
    # Load data
    print(f"Loading simulation data from {args.report}...")
    data = load_simulation_data(args.report)
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate visualizations
    if args.all or args.timeline:
        print("Generating LOVE timeline charts...")
        fig = plot_love_minting_timeline(data)
        fig.savefig(output_dir / 'love_timeline.png', dpi=300, bbox_inches='tight')
        plt.close(fig)
        print(f"  Saved: {output_dir / 'love_timeline.png'}")
    
    if args.all or args.market:
        print("Generating market indicator charts...")
        fig = plot_market_indicators(data)
        fig.savefig(output_dir / 'market_indicators.png', dpi=300, bbox_inches='tight')
        plt.close(fig)
        print(f"  Saved: {output_dir / 'market_indicators.png'}")
    
    if args.all or args.correlation:
        print("Generating correlation scatter plots...")
        fig = plot_love_vs_market_correlation(data)
        fig.savefig(output_dir / 'correlation.png', dpi=300, bbox_inches='tight')
        plt.close(fig)
        print(f"  Saved: {output_dir / 'correlation.png'}")
    
    if args.all or args.comparison:
        print("Generating sector comparison charts...")
        fig = plot_sector_comparison(data)
        fig.savefig(output_dir / 'sector_comparison.png', dpi=300, bbox_inches='tight')
        plt.close(fig)
        print(f"  Saved: {output_dir / 'sector_comparison.png'}")
    
    if args.all or args.prediction:
        print("Generating prediction accuracy charts...")
        fig = plot_prediction_accuracy(data)
        fig.savefig(output_dir / 'prediction_accuracy.png', dpi=300, bbox_inches='tight')
        plt.close(fig)
        print(f"  Saved: {output_dir / 'prediction_accuracy.png'}")
    
    if args.all or args.dashboard:
        print("Generating summary dashboard...")
        fig = create_summary_dashboard(data)
        fig.savefig(output_dir / 'summary_dashboard.png', dpi=300, bbox_inches='tight')
        plt.close(fig)
        print(f"  Saved: {output_dir / 'summary_dashboard.png'}")
    
    # Default: generate all if no specific option
    if not any([args.all, args.timeline, args.market, args.correlation, 
                args.comparison, args.prediction, args.dashboard]):
        print("Generating all visualizations...")
        fig = plot_love_minting_timeline(data)
        fig.savefig(output_dir / 'love_timeline.png', dpi=300, bbox_inches='tight')
        plt.close(fig)
        
        fig = plot_market_indicators(data)
        fig.savefig(output_dir / 'market_indicators.png', dpi=300, bbox_inches='tight')
        plt.close(fig)
        
        fig = plot_love_vs_market_correlation(data)
        fig.savefig(output_dir / 'correlation.png', dpi=300, bbox_inches='tight')
        plt.close(fig)
        
        fig = plot_sector_comparison(data)
        fig.savefig(output_dir / 'sector_comparison.png', dpi=300, bbox_inches='tight')
        plt.close(fig)
        
        fig = plot_prediction_accuracy(data)
        fig.savefig(output_dir / 'prediction_accuracy.png', dpi=300, bbox_inches='tight')
        plt.close(fig)
        
        fig = create_summary_dashboard(data)
        fig.savefig(output_dir / 'summary_dashboard.png', dpi=300, bbox_inches='tight')
        plt.close(fig)
        
        print(f"\n✓ All visualizations saved to {output_dir}/")
    
    print("\nVisualization complete!")


if __name__ == "__main__":
    main()


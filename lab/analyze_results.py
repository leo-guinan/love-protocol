#!/usr/bin/env python3
"""
Analyze market simulation results
"""

import json
import sys
from pathlib import Path

def analyze_results():
    """Analyze market simulation results"""
    
    report_file = Path("lab/output/market_simulation_report.json")
    if not report_file.exists():
        print("No market simulation report found. Run simulation first.")
        return
    
    data = json.load(open(report_file))
    
    print("="*60)
    print("MARKET SIMULATION ANALYSIS")
    print("="*60)
    
    # Overall stats
    print(f"\n📊 OVERALL STATISTICS")
    print(f"  Total Days: {data['total_days']}")
    print(f"  Total LOVE Minted: {data['total_love_minted']:,.2f}")
    print(f"  Total Interventions: {data['total_interventions']}")
    print(f"  Avg LOVE per Intervention: {data['total_love_minted'] / data['total_interventions']:.2f}")
    print(f"  Interventions per Day: {data['total_interventions'] / data['total_days']:.2f}")
    
    # Sector analysis
    print(f"\n🏢 SECTOR ANALYSIS")
    print("-" * 60)
    
    for sector, love in sorted(data['sector_love'].items(), key=lambda x: x[1], reverse=True):
        indicator = data['market_indicators'][sector]
        prediction = data['predictions'].get(sector, {})
        
        print(f"\n{sector.upper().replace('_', ' ')}")
        print(f"  💰 LOVE Minted: {love:,.2f}")
        print(f"  📈 Market Health: {indicator['current']:.2f} (started at {indicator['initial']:.2f})")
        print(f"  📉 Market Change: {indicator['change']:+.2f}")
        print(f"  📊 Trend: {indicator['trend']:+.4f} per day")
        
        # LOVE efficiency
        if indicator['change'] != 0:
            love_per_point = love / abs(indicator['change'])
            print(f"  ⚡ LOVE per Market Point: {love_per_point:.2f}")
        
        # Prediction analysis
        if prediction:
            print(f"\n  🔮 PREDICTION ANALYSIS:")
            print(f"    Early LOVE (days 1-7): {prediction['early_love']:,.2f}")
            print(f"    Late LOVE (days 24-30): {prediction['late_love']:,.2f}")
            print(f"    LOVE Change: {prediction['love_change']:+.2f}")
            print(f"    Market Change: {prediction['market_change']:+.2f}")
            print(f"    Prediction Correct: {'✅ YES' if prediction['prediction_correct'] else '❌ NO'}")
            print(f"    Correlation: {prediction['correlation']:+.4f}")
            
            # Interpretation
            if prediction['correlation'] < -0.3:
                print(f"    💡 Strong negative correlation (as expected)")
            elif prediction['correlation'] < 0:
                print(f"    💡 Weak negative correlation")
            elif prediction['correlation'] > 0.3:
                print(f"    ⚠️  Positive correlation (unexpected - should be negative)")
            else:
                print(f"    ⚠️  Weak/no correlation")
    
    # Key insights
    print(f"\n🔍 KEY INSIGHTS")
    print("-" * 60)
    
    # Find sectors with most LOVE
    max_love_sector = max(data['sector_love'].items(), key=lambda x: x[1])
    print(f"  Highest LOVE: {max_love_sector[0]} ({max_love_sector[1]:,.2f} LOVE)")
    
    # Find sectors with worst market decline
    worst_market = min(data['market_indicators'].items(), key=lambda x: x[1]['change'])
    print(f"  Worst Market Decline: {worst_market[0]} ({worst_market[1]['change']:+.2f})")
    
    # Check hypothesis
    print(f"\n  📋 HYPOTHESIS TEST:")
    print(f"    Expected: More LOVE → Market Decline (negative correlation)")
    
    correlations = [p.get('correlation', 0) for p in data['predictions'].values()]
    avg_correlation = sum(correlations) / len(correlations) if correlations else 0
    
    if avg_correlation < -0.2:
        print(f"    Result: ✅ STRONG SUPPORT (avg correlation: {avg_correlation:+.4f})")
    elif avg_correlation < 0:
        print(f"    Result: ⚠️  WEAK SUPPORT (avg correlation: {avg_correlation:+.4f})")
    else:
        print(f"    Result: ❌ NOT SUPPORTED (avg correlation: {avg_correlation:+.4f})")
        print(f"    Note: Positive correlation suggests LOVE increases with market health")
        print(f"          This contradicts the hypothesis. Check simulation logic.")
    
    # Prediction accuracy
    correct_predictions = sum(1 for p in data['predictions'].values() if p.get('prediction_correct', False))
    total_predictions = len(data['predictions'])
    accuracy = (correct_predictions / total_predictions * 100) if total_predictions > 0 else 0
    
    print(f"\n  🎯 PREDICTION ACCURACY:")
    print(f"    Correct: {correct_predictions}/{total_predictions} ({accuracy:.1f}%)")
    print(f"    Baseline (random): 50%")
    if accuracy > 60:
        print(f"    Result: ✅ Better than random!")
    elif accuracy > 50:
        print(f"    Result: ⚠️  Slightly better than random")
    else:
        print(f"    Result: ❌ Worse than random")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    analyze_results()


#!/usr/bin/env python3
"""
Market Simulation Runner
Tests if LOVE minting patterns predict market movements
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from lab.protocol import LOVEProtocol
from lab.market import MarketSimulation, MarketConfig, MarketSector


def main():
    """Run market simulation"""
    
    load_dotenv()
    
    # Configuration
    config = MarketConfig(
        num_organizations=5,
        min_org_size=10,
        max_org_size=30,
        sectors=[
            MarketSector.DATING_APPS,
            MarketSector.SOCIAL_NETWORKS,
            MarketSector.COMMUNITY_PLATFORMS
        ],
        simulation_days=30,
        interventions_per_day=2.0,
        communication_density_range=(0.3, 0.8),
        stress_range=(0.2, 0.6),
        indicator_volatility=2.0,
        indicator_trend_range=(-1.0, 1.0),
        love_to_market_correlation=-0.3,
        love_prediction_lag_days=7
    )
    
    # Initialize protocol
    protocol = LOVEProtocol(
        k=1.0,
        alpha=1.2,
        beta=1.1,
        gamma=1.0,
        delta=1.1,
        epsilon=1.0,
        zeta=1.0
    )
    
    # Create market simulation
    market = MarketSimulation(config=config, protocol=protocol)
    
    # Run simulation
    summary = market.run_simulation(verbose=True)
    
    # Save results
    output_dir = Path("lab/output")
    output_dir.mkdir(exist_ok=True)
    
    report_file = output_dir / "market_simulation_report.json"
    with open(report_file, "w") as f:
        json.dump(summary, f, indent=2, default=str)
    
    print("\n" + "="*60)
    print("MARKET SIMULATION RESULTS")
    print("="*60)
    
    print(f"\nTotal LOVE Minted: {summary['total_love_minted']:.2f}")
    print(f"Total Interventions: {summary['total_interventions']}")
    
    print("\n--- Sector LOVE Distribution ---")
    for sector, love in summary['sector_love'].items():
        print(f"  {sector}: {love:.2f} LOVE")
    
    print("\n--- Market Indicators ---")
    for sector, data in summary['market_indicators'].items():
        print(f"\n  {sector}:")
        print(f"    Current: {data['current']:.2f}")
        print(f"    Change: {data['change']:+.2f}")
        print(f"    Trend: {data['trend']:+.4f}")
    
    print("\n--- Predictions ---")
    for sector, pred in summary['predictions'].items():
        print(f"\n  {sector}:")
        print(f"    LOVE Change: {pred['love_change']:+.2f}")
        print(f"    Market Change: {pred['market_change']:+.2f}")
        print(f"    Prediction Correct: {pred['prediction_correct']}")
        print(f"    Correlation: {pred['correlation']:.4f}")
    
    print(f"\n✓ Report saved to: {report_file}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())


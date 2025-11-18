#!/usr/bin/env python3
"""
Example Market Configuration
Shows how to configure market simulations
"""

from lab.market import MarketConfig, MarketSector

# Example 1: Small test simulation
small_config = MarketConfig(
    num_organizations=3,
    min_org_size=5,
    max_org_size=10,
    sectors=[MarketSector.DATING_APPS],
    simulation_days=7,
    interventions_per_day=1.0
)

# Example 2: Full market simulation
full_config = MarketConfig(
    num_organizations=10,
    min_org_size=20,
    max_org_size=50,
    sectors=[
        MarketSector.DATING_APPS,
        MarketSector.SOCIAL_NETWORKS,
        MarketSector.COMMUNITY_PLATFORMS,
        MarketSector.MENTAL_HEALTH
    ],
    simulation_days=60,
    interventions_per_day=3.0,
    communication_density_range=(0.4, 0.9),
    stress_range=(0.3, 0.7),
    indicator_volatility=3.0,
    love_to_market_correlation=-0.5,  # Stronger correlation
    love_prediction_lag_days=14  # 2 week prediction window
)

# Example 3: High-stress scenario
high_stress_config = MarketConfig(
    num_organizations=5,
    min_org_size=15,
    max_org_size=30,
    sectors=[MarketSector.SOCIAL_NETWORKS, MarketSector.COMMUNITY_PLATFORMS],
    simulation_days=30,
    interventions_per_day=5.0,  # High intervention rate
    stress_range=(0.6, 0.9),  # High stress
    communication_density_range=(0.2, 0.5),  # Low communication
    love_to_market_correlation=-0.4
)

# Example 4: Testing prediction accuracy
prediction_test_config = MarketConfig(
    num_organizations=8,
    min_org_size=10,
    max_org_size=25,
    sectors=[
        MarketSector.DATING_APPS,
        MarketSector.SOCIAL_NETWORKS
    ],
    simulation_days=90,  # Longer simulation
    interventions_per_day=2.0,
    love_prediction_lag_days=7,  # 1 week lag
    indicator_trend_range=(-2.0, 0.0),  # Declining markets
    love_to_market_correlation=-0.3
)


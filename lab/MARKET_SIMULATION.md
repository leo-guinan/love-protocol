# Market Simulation Layer

## Overview

The market simulation layer tests the core hypothesis: **Can LOVE minting patterns predict market movements?**

This simulates organizations (firms) with agents that communicate and generate interventions, then tracks whether LOVE minting patterns correlate with market health indicators.

## Architecture

### Components

1. **Organizations** (`Organization`)
   - Groups of agents (10-50 agents each)
   - Belong to market sectors (dating apps, social networks, etc.)
   - Have internal stress levels and communication density
   - Generate interventions based on stress and interaction

2. **Market Indicators** (`MarketIndicator`)
   - Track health of market sectors (0-100 scale)
   - Update based on trends and volatility
   - Affected by LOVE minting patterns (negative correlation)

3. **Market Simulation** (`MarketSimulation`)
   - Orchestrates daily market activity
   - Generates interventions within organizations
   - Tracks LOVE minting patterns
   - Calculates predictions and correlations

### Market Sectors

- `DATING_APPS` - Dating platform health
- `SOCIAL_NETWORKS` - Social network engagement
- `COMMUNITY_PLATFORMS` - Community platform health
- `MENTAL_HEALTH` - Mental health service demand
- `WORKPLACE` - Workplace satisfaction
- `EDUCATION` - Educational platform engagement

## Configuration

### MarketConfig Parameters

```python
MarketConfig(
    num_organizations=5,           # Number of firms
    min_org_size=10,               # Minimum agents per org
    max_org_size=50,               # Maximum agents per org
    sectors=[...],                 # Sectors to simulate
    simulation_days=30,            # Days to simulate
    interventions_per_day=2.0,     # Avg interventions per org per day
    communication_density_range=(0.3, 0.8),  # Agent interaction level
    stress_range=(0.2, 0.6),      # Organization stress levels
    indicator_volatility=2.0,      # Market volatility
    indicator_trend_range=(-1.0, 1.0),  # Market trend range
    love_to_market_correlation=-0.3,  # LOVE impact on markets
    love_prediction_lag_days=7     # Prediction window
)
```

## How It Works

### Daily Simulation Cycle

1. **Intervention Generation**
   - Each organization generates interventions based on:
     - Intervention rate
     - Organization size
     - Stress level (more stress = more interventions)
   - Agents are paired randomly for interventions

2. **LOVE Minting**
   - Interventions go through HTC validation
   - Validated interventions mint LOVE
   - LOVE is tracked per organization and sector

3. **Market Indicator Updates**
   - Market indicators update based on:
     - Base trend
     - Random volatility
     - LOVE minting impact (negative correlation)
   - More LOVE = declining market health

4. **Prediction Calculation**
   - Compare early LOVE patterns to later market movements
   - Calculate correlation between LOVE and market health
   - Test if LOVE predicts market decline

## Usage

### Basic Simulation

```bash
python lab/run_market_simulation.py
```

### Custom Configuration

```python
from lab.market import MarketSimulation, MarketConfig, MarketSector
from lab.protocol import LOVEProtocol

config = MarketConfig(
    num_organizations=10,
    simulation_days=60,
    sectors=[MarketSector.DATING_APPS, MarketSector.SOCIAL_NETWORKS]
)

protocol = LOVEProtocol()
market = MarketSimulation(config=config, protocol=protocol)
summary = market.run_simulation()
```

## Output

### Simulation Summary

```json
{
  "total_days": 30,
  "total_love_minted": 1234.56,
  "total_interventions": 150,
  "organizations": {...},
  "sector_love": {
    "dating_apps": 456.78,
    "social_networks": 777.78
  },
  "market_indicators": {
    "dating_apps": {
      "current": 65.5,
      "change": -12.3,
      "trend": -0.5
    }
  },
  "predictions": {
    "dating_apps": {
      "love_change": +234.56,
      "market_change": -12.3,
      "prediction_correct": true,
      "correlation": -0.45
    }
  }
}
```

### Key Metrics

- **Total LOVE Minted**: Aggregate LOVE across all organizations
- **Sector LOVE Distribution**: LOVE by market sector
- **Market Indicator Changes**: How market health changed
- **Prediction Accuracy**: Did LOVE predict market movements?
- **Correlation**: Statistical correlation between LOVE and markets

## Hypothesis Testing

The simulation tests:

1. **Leading Indicator**: Does LOVE minting increase before market decline?
2. **Correlation**: Is there negative correlation between LOVE and market health?
3. **Prediction Accuracy**: Can LOVE patterns predict market movements N days ahead?

### Success Criteria

- Negative correlation between LOVE and market health
- LOVE increases predict market decline
- Prediction accuracy > 60% (better than random)

## Example Scenarios

### High-Stress Market

```python
high_stress_config = MarketConfig(
    num_organizations=5,
    stress_range=(0.6, 0.9),  # High stress
    interventions_per_day=5.0,  # High intervention rate
    love_to_market_correlation=-0.5  # Strong correlation
)
```

### Testing Prediction Window

```python
prediction_config = MarketConfig(
    simulation_days=90,  # Longer simulation
    love_prediction_lag_days=14,  # 2 week prediction window
    indicator_trend_range=(-2.0, 0.0)  # Declining markets
)
```

## Next Steps

1. Run simulations with different configurations
2. Analyze correlation patterns
3. Test prediction accuracy
4. Identify optimal prediction windows
5. Build visualization tools for results


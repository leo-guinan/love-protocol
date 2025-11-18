# Visualization Guide

## Overview

The visualization script generates comprehensive charts from market simulation results, showing LOVE minting patterns, market indicators, correlations, and prediction accuracy.

## Usage

### Generate All Visualizations

```bash
python lab/visualize_results.py --all
```

### Generate Specific Visualizations

```bash
# LOVE timeline charts
python lab/visualize_results.py --timeline

# Market indicator charts
python lab/visualize_results.py --market

# Correlation scatter plots
python lab/visualize_results.py --correlation

# Sector comparison charts
python lab/visualize_results.py --comparison

# Prediction accuracy charts
python lab/visualize_results.py --prediction

# Summary dashboard
python lab/visualize_results.py --dashboard
```

### Custom Output Directory

```bash
python lab/visualize_results.py --all --output-dir custom/path
```

## Generated Visualizations

### 1. LOVE Timeline (`love_timeline.png`)

**Two-panel chart showing:**
- **Top**: Daily LOVE minting by sector over time
- **Bottom**: Cumulative LOVE minting by sector

**Use Case**: Track LOVE generation patterns and identify sectors with high intervention activity.

### 2. Market Indicators (`market_indicators.png`)

**Two-panel chart showing:**
- **Top**: Market health (0-100) over time by sector
- **Bottom**: Market trend (points/day) over time

**Use Case**: Monitor market health and identify declining sectors.

### 3. Correlation (`correlation.png`)

**Scatter plots showing:**
- Cumulative LOVE vs Market Health for each sector
- Trend lines showing correlation direction
- Correlation coefficient displayed

**Use Case**: Verify negative correlation hypothesis (more LOVE = lower market health).

### 4. Sector Comparison (`sector_comparison.png`)

**Four-panel comparison:**
- **Top Left**: Total LOVE minted by sector (pie chart)
- **Top Right**: Market health change by sector (bar chart)
- **Bottom Left**: LOVE-Market correlation by sector
- **Bottom Right**: LOVE efficiency (LOVE per market point)

**Use Case**: Compare sectors side-by-side to identify patterns.

### 5. Prediction Accuracy (`prediction_accuracy.png`)

**Two-panel chart showing:**
- **Left**: Prediction correctness by sector
- **Right**: LOVE change vs Market change scatter plot (colored by prediction accuracy)

**Use Case**: Evaluate how well LOVE patterns predict market movements.

### 6. Summary Dashboard (`summary_dashboard.png`)

**Comprehensive dashboard with:**
- LOVE distribution pie chart
- Current market health by sector
- Correlation coefficients
- LOVE timeline
- Market health timeline
- Key summary statistics

**Use Case**: High-level overview of simulation results.

## Output Location

All visualizations are saved to:
```
lab/output/visualizations/
```

## Requirements

- matplotlib
- seaborn
- numpy

## Example Output

After running a simulation:

```bash
# Run simulation
python lab/run_market_simulation.py

# Generate visualizations
python lab/visualize_results.py --all

# View results
open lab/output/visualizations/summary_dashboard.png
```

## Interpreting Results

### Negative Correlation (Expected)
- Correlation < -0.3: Strong support for hypothesis
- Correlation < 0: Weak support
- More LOVE → Lower market health

### Prediction Accuracy
- > 60%: Better than random (good)
- > 50%: Slightly better than random
- < 50%: Worse than random (needs investigation)

### Market Health
- 80-100: Healthy
- 50-80: Moderate
- 0-50: Declining
- 0: Collapsed

## Tips

1. **Compare multiple runs**: Run simulations with different parameters and compare visualizations
2. **Focus on correlation plots**: These show if the hypothesis is supported
3. **Check prediction accuracy**: Should be > 50% for hypothesis validation
4. **Monitor trends**: Market trend charts show if markets are declining


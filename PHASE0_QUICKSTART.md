# Phase 0 Lab Environment - Quick Start

## Overview

Phase 0 is a lab environment using AI agents (via local Ollama) to simulate the LOVE Protocol before real community deployment. This allows us to test mechanics, establish baselines, and identify issues.

## Prerequisites

1. **Python 3.12+**
2. **Ollama installed** (optional - simulation works in fallback mode without it)
   ```bash
   # Install from https://ollama.ai
   # Pull a model
   ollama pull llama3.2
   ```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Test Protocol Logic (No AI Required)

```bash
python lab/quick_test.py
```

This tests core LOVE minting and scoring logic without AI agents.

### 3. Test Ollama Connection (Optional)

```bash
python lab/test_ollama.py
```

If Ollama is working, you'll see a confirmation. If not, the simulation will use deterministic fallback mode.

### 4. Run Full Simulation

```bash
python lab/run_simulation.py
```

This will:
- Create 9 AI agents (3 interveners, 3 beneficiaries, 3 validators)
- Run 7 baseline scenarios through HTC validation
- Calculate LOVE mints and IMI metrics
- Generate a report in `lab/output/simulation_report.json`

## What Gets Tested

### Baseline Scenarios

1. **Emotional Support** - Panic attack prevention
2. **Conflict Resolution** - Roommate mediation
3. **Preventive Action** - Dating mismatch warning
4. **Clarification** - Communication misunderstanding
5. **Timely Intervention** - Decision prevention
6. **Edge Case** - Minimal impact intervention
7. **Community Impact** - Large-scale conflict prevention

### Protocol Mechanics

- ✅ Human Triangulation Consensus (HTC)
- ✅ LOVE minting calculation
- ✅ Score distribution (H, T, R, S, E, W)
- ✅ IMI metric computation
- ✅ Participant statistics

### Measurements

- LOVE mint amounts and distributions
- Score patterns and inflation detection
- Validation success rates
- IMI metrics (mint intensity, temporal acceleration)
- Agent behavior patterns

## Output

Results are saved to `lab/output/simulation_report.json`:

```json
{
  "simulation_history": [...],
  "imi_metrics": {
    "total_love": 1234.56,
    "intervention_count": 7,
    "mint_intensity": 41.15,
    "temporal_acceleration": 0.0234,
    "average_scores": {...}
  },
  "protocol_stats": {...},
  "agent_stats": {...}
}
```

## Next Steps

After running simulations:

1. **Analyze Results**: Review score distributions, LOVE patterns
2. **Identify Issues**: Look for collusion patterns, score inflation
3. **Iterate**: Adjust protocol parameters and re-run
4. **Prepare Phase 1**: Use insights for real community pilots

## Customization

### Modify Protocol Parameters

Edit `lab/run_simulation.py`:

```python
protocol = LOVEProtocol(
    k=1.0,        # Global issuance coefficient
    alpha=1.2,    # H (harm) weight
    beta=1.1,     # T (timing) weight
    # Adjust weights to test different configurations
)
```

### Add Custom Scenarios

Add to `lab/scenarios.py`:

```python
my_scenario = InterventionScenario(
    id="custom_001",
    category=InterventionCategory.EMOTIONAL_SUPPORT,
    intervener="Intervener_1",
    beneficiary="Beneficiary_1",
    description="...",
    predicted_harm="...",
    context={...},
    expected_scores={"H": 7.0, "T": 8.0, ...},
    difficulty="medium"
)
```

## Troubleshooting

### Ollama Not Running

The simulation will use deterministic fallback responses based on agent personas. This allows testing protocol logic without AI.

### Import Errors

Make sure you're running from the project root:
```bash
cd /path/to/love-protocol
python lab/run_simulation.py
```

### Model Not Found

Pull the model:
```bash
ollama pull llama3.2
# or
ollama pull mistral
```

## Success Criteria

Phase 0 is successful if:

- ✅ Protocol logic works correctly
- ✅ HTC validation process completes
- ✅ LOVE minting follows expected patterns
- ✅ IMI metrics are calculable
- ✅ No critical bugs discovered
- ✅ Baseline measurements established

Ready to proceed to Phase 1 (real community pilots) when these are met.


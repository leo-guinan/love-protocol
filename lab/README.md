# LOVE Protocol Phase 0 Lab Environment

AI simulation framework for testing LOVE Protocol mechanics before real community deployment.

## Overview

This lab environment uses local Ollama AI agents to simulate the Human Triangulation Consensus (HTC) process, allowing us to:

- Test protocol mechanics in controlled conditions
- Establish baseline measurements
- Identify potential issues before real deployment
- Experiment with different parameter configurations

## Setup

### Prerequisites

1. **Python 3.12+**
2. **Ollama installed and running locally**
   ```bash
   # Install Ollama from https://ollama.ai
   # Pull a model (e.g., llama3.2)
   ollama pull llama3.2
   ```

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env if needed (defaults should work)
```

## Usage

### Run Baseline Simulation

```bash
python lab/run_simulation.py
```

This will:
1. Create a pool of 9 AI agents (3 interveners, 3 beneficiaries, 3 validators)
2. Run 7 baseline scenarios through the HTC process
3. Calculate LOVE mints and IMI metrics
4. Generate a simulation report

### Output

Results are saved to `lab/output/simulation_report.json` containing:
- All intervention records
- Validation results
- LOVE mint distributions
- IMI metrics
- Score comparisons

## Components

### `agents.py`
AI agent system that simulates HTC witnesses using Ollama:
- Primary witnesses (interveners) submit interventions
- Secondary witnesses (beneficiaries) confirm interventions
- Tertiary witnesses (validators) score and validate

### `scenarios.py`
Predefined intervention scenarios for testing:
- Emotional support
- Conflict resolution
- Preventive action
- Clarification
- Timely intervention

### `protocol.py`
Core LOVE Protocol logic:
- LOVE minting calculation
- Score aggregation
- IMI metric computation
- Participant statistics

### `simulator.py`
Main simulation engine that orchestrates:
- Scenario execution
- HTC workflow
- Result collection
- Report generation

## Customization

### Modify Protocol Parameters

Edit `lab/run_simulation.py`:

```python
protocol = LOVEProtocol(
    k=1.0,        # Global issuance coefficient
    alpha=1.2,    # H (harm) weight
    beta=1.1,     # T (timing) weight
    # ... etc
)
```

### Add Custom Scenarios

Add to `lab/scenarios.py`:

```python
custom_scenario = InterventionScenario(
    id="custom_001",
    category=InterventionCategory.EMOTIONAL_SUPPORT,
    # ... define scenario
)
```

### Adjust Agent Behavior

Modify `create_agent_pool()` in `agents.py` to change:
- Agent personas
- Trust levels
- Bias factors
- Social connections

## Next Steps

After running baseline simulations:

1. **Analyze Results**: Review score distributions and LOVE mint patterns
2. **Identify Issues**: Look for collusion patterns, score inflation, etc.
3. **Iterate**: Adjust parameters and re-run
4. **Prepare for Phase 1**: Use insights to design real community pilots

## Troubleshooting

### Ollama Connection Issues

If Ollama isn't running:
```bash
# Start Ollama service
ollama serve
```

### Model Not Found

Pull the model:
```bash
ollama pull llama3.2
# or
ollama pull mistral
```

### Fallback Mode

If Ollama is unavailable, agents will use deterministic fallback responses based on their personas. This allows testing protocol logic without AI.


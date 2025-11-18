#!/usr/bin/env python3
"""
Phase 0 Lab Simulation Runner
Main entry point for running LOVE Protocol simulations with AI agents
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from lab.agents import create_agent_pool
from lab.protocol import LOVEProtocol
from lab.scenarios import BASELINE_SCENARIOS
from lab.simulator import SimulationEngine


def main():
    """Run Phase 0 baseline simulation"""
    
    # Load environment variables
    load_dotenv()
    
    ollama_model = os.getenv("OLLAMA_MODEL", "llama3.2")
    ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    print("="*60)
    print("LOVE PROTOCOL - PHASE 0 LAB ENVIRONMENT")
    print("="*60)
    print(f"Ollama Model: {ollama_model}")
    print(f"Ollama URL: {ollama_base_url}")
    print(f"Baseline Scenarios: {len(BASELINE_SCENARIOS)}")
    print("="*60)
    
    # Initialize protocol
    protocol = LOVEProtocol(
        k=1.0,
        alpha=1.2,  # H weight
        beta=1.1,   # T weight
        gamma=1.0,  # R weight
        delta=1.1,  # S weight
        epsilon=1.0, # E weight
        zeta=1.0    # W weight
    )
    
    # Create agent pool
    print("\nCreating AI agent pool...")
    agents = create_agent_pool(num_agents=9)
    print(f"  ✓ Created {len(agents)} agents")
    print(f"    - Primary witnesses (interveners): 3")
    print(f"    - Secondary witnesses (beneficiaries): 3")
    print(f"    - Tertiary witnesses (validators): 3")
    
    # Initialize simulation engine
    simulator = SimulationEngine(
        protocol=protocol,
        agents=agents,
        ollama_model=ollama_model
    )
    
    # Run baseline simulation suite
    print("\nRunning baseline simulation suite...")
    summary = simulator.run_baseline_suite(verbose=True)
    
    # Generate report
    report = simulator.get_simulation_report()
    
    # Save results
    output_dir = Path("lab/output")
    output_dir.mkdir(exist_ok=True)
    
    report_file = output_dir / "simulation_report.json"
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\n✓ Simulation complete!")
    print(f"✓ Report saved to: {report_file}")
    
    # Print IMI metrics
    print("\n" + "="*60)
    print("INVERSE MARKET INDEX (IMI) METRICS")
    print("="*60)
    imi = report["imi_metrics"]
    print(f"Total LOVE Minted: {imi['total_love']}")
    print(f"Intervention Count: {imi['intervention_count']}")
    print(f"Mint Intensity (LOVE/day): {imi['mint_intensity']}")
    print(f"Temporal Acceleration: {imi['temporal_acceleration']:.4f}")
    print("\nAverage Scores:")
    for key, value in imi['average_scores'].items():
        print(f"  {key}: {value:.2f}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())


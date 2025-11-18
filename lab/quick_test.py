#!/usr/bin/env python3
"""
Quick test of core protocol logic without AI agents
Tests LOVE minting calculation and basic mechanics
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from lab.protocol import LOVEProtocol, Intervention, ValidationResult
from lab.scenarios import BASELINE_SCENARIOS
from datetime import datetime
import uuid


def test_protocol_logic():
    """Test protocol logic with manual scores"""
    
    print("="*60)
    print("LOVE PROTOCOL - QUICK LOGIC TEST")
    print("="*60)
    
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
    
    # Test LOVE calculation with example scores
    test_scores = {
        "H": 7.0,
        "T": 9.0,
        "R": 3.0,
        "S": 6.0,
        "E": 8.0,
        "W": 8.0
    }
    
    love_amount = protocol.calculate_love(test_scores)
    distribution = protocol.distribute_love(love_amount)
    
    print(f"\nTest Scores: {test_scores}")
    print(f"LOVE Minted: {love_amount:.2f}")
    print(f"Distribution:")
    for role, amount in distribution.items():
        print(f"  {role}: {amount:.2f}")
    
    # Test with a scenario
    scenario = BASELINE_SCENARIOS[0]
    
    print(f"\n{'='*60}")
    print(f"Testing Scenario: {scenario.id}")
    print(f"{'='*60}")
    
    # Create intervention
    intervention = Intervention(
        id=str(uuid.uuid4()),
        intervener=scenario.intervener,
        beneficiary=scenario.beneficiary,
        description=scenario.description,
        predicted_harm=scenario.predicted_harm,
        timestamp=datetime.now().timestamp(),
        submission_data={"test": True}
    )
    
    protocol.interventions[intervention.id] = intervention
    
    # Create validation with expected scores
    validation = ValidationResult(
        intervention_id=intervention.id,
        confirmed=True,
        confirmed_by=scenario.beneficiary,
        confirmation_explanation="Test confirmation",
        improvement_score=0.8,
        validated=True,
        validated_by="Test_Validator",
        scores=scenario.expected_scores.copy(),
        validation_reasoning="Test validation"
    )
    
    # Process validation
    mint = protocol.process_validation(intervention.id, validation)
    
    if mint:
        print(f"\n✓ Validation successful!")
        print(f"  LOVE Minted: {mint.amount:.2f}")
        print(f"  Expected vs Actual:")
        for key in ["H", "T", "R", "S", "E", "W"]:
            expected = scenario.expected_scores.get(key, 0)
            actual = mint.scores.get(key, 0)
            diff = actual - expected
            print(f"    {key}: Expected {expected:.1f}, Got {actual:.1f} (diff: {diff:+.1f})")
    else:
        print("\n✗ Validation failed")
    
    # Test IMI calculation
    print(f"\n{'='*60}")
    print("IMI Metrics")
    print("="*60)
    imi = protocol.get_imi_metrics()
    print(f"Total LOVE: {imi['total_love']}")
    print(f"Interventions: {imi['intervention_count']}")
    print(f"Mint Intensity: {imi['mint_intensity']:.2f} LOVE/day")
    
    print("\n✓ Protocol logic test complete!")
    return True


if __name__ == "__main__":
    test_protocol_logic()


"""
Main Simulation Engine
Orchestrates AI agents, scenarios, and protocol execution
"""

import json
import time
from typing import Dict, List, Optional
from datetime import datetime
import uuid

from lab.agents import AIAgent, AgentPersona, WitnessRole, create_agent_pool
from lab.scenarios import InterventionScenario, BASELINE_SCENARIOS
from lab.protocol import LOVEProtocol, Intervention, ValidationResult, LOVEMint


class SimulationEngine:
    """Main simulation engine for Phase 0 lab environment"""
    
    def __init__(
        self,
        protocol: LOVEProtocol,
        agents: List[AIAgent],
        ollama_model: str = "llama3.2"
    ):
        self.protocol = protocol
        self.agents = agents
        self.ollama_model = ollama_model
        
        # Index agents by role and name
        self.primary_agents = {a.persona.name: a for a in agents if a.persona.role == WitnessRole.PRIMARY}
        self.secondary_agents = {a.persona.name: a for a in agents if a.persona.role == WitnessRole.SECONDARY}
        self.tertiary_agents = {a.persona.name: a for a in agents if a.persona.role == WitnessRole.TERTIARY}
        
        self.simulation_history: List[Dict] = []
    
    def run_scenario(
        self,
        scenario: InterventionScenario,
        verbose: bool = True
    ) -> Dict:
        """Run a single intervention scenario through HTC"""
        
        if verbose:
            print(f"\n{'='*60}")
            print(f"Running Scenario: {scenario.id}")
            print(f"Category: {scenario.category.value}")
            print(f"{'='*60}")
        
        # Step 1: Primary witness submits intervention
        primary_agent = self.primary_agents.get(scenario.intervener)
        if not primary_agent:
            raise ValueError(f"Primary agent {scenario.intervener} not found")
        
        if verbose:
            print(f"\n[STEP 1] Primary Witness ({scenario.intervener}) submitting intervention...")
        
        intervention_data = primary_agent.submit_intervention(
            beneficiary=scenario.beneficiary,
            description=scenario.description,
            predicted_harm=scenario.predicted_harm,
            context={
                **scenario.context,
                "timestamp": datetime.now().timestamp()
            }
        )
        
        # Create intervention record
        intervention = Intervention(
            id=str(uuid.uuid4()),
            intervener=scenario.intervener,
            beneficiary=scenario.beneficiary,
            description=scenario.description,
            predicted_harm=scenario.predicted_harm,
            timestamp=datetime.now().timestamp(),
            submission_data=intervention_data
        )
        
        self.protocol.interventions[intervention.id] = intervention
        
        if verbose:
            print(f"  ✓ Intervention submitted: {intervention.id}")
            print(f"  Description: {scenario.description[:100]}...")
        
        # Step 2: Secondary witness confirms
        secondary_agent = self.secondary_agents.get(scenario.beneficiary)
        if not secondary_agent:
            raise ValueError(f"Secondary agent {scenario.beneficiary} not found")
        
        if verbose:
            print(f"\n[STEP 2] Secondary Witness ({scenario.beneficiary}) confirming...")
        
        confirmed, explanation, improvement = secondary_agent.confirm_intervention(
            intervention=intervention_data,
            intervener=scenario.intervener
        )
        
        if verbose:
            print(f"  {'✓' if confirmed else '✗'} Confirmed: {confirmed}")
            print(f"  Explanation: {explanation[:100]}...")
            print(f"  Improvement Score: {improvement:.2f}")
        
        if not confirmed:
            intervention.status = "rejected"
            result = {
                "scenario_id": scenario.id,
                "intervention_id": intervention.id,
                "status": "rejected_at_confirmation",
                "confirmed": False,
                "validated": False,
                "love_minted": 0.0
            }
            self.simulation_history.append(result)
            return result
        
        # Step 3: Tertiary witness validates
        # Select validator (could be random or based on trust)
        validator_name = list(self.tertiary_agents.keys())[0]  # Simple: first validator
        tertiary_agent = self.tertiary_agents[validator_name]
        
        if verbose:
            print(f"\n[STEP 3] Tertiary Witness ({validator_name}) validating...")
        
        validated, scores, reasoning = tertiary_agent.validate_intervention(
            intervention=intervention_data,
            confirmation=(confirmed, explanation, improvement),
            intervener=scenario.intervener,
            beneficiary=scenario.beneficiary
        )
        
        if verbose:
            print(f"  {'✓' if validated else '✗'} Validated: {validated}")
            print(f"  Scores: {json.dumps(scores, indent=2)}")
            print(f"  Reasoning: {reasoning[:100]}...")
        
        # Create validation result
        validation_result = ValidationResult(
            intervention_id=intervention.id,
            confirmed=confirmed,
            confirmed_by=scenario.beneficiary,
            confirmation_explanation=explanation,
            improvement_score=improvement,
            validated=validated,
            validated_by=validator_name,
            scores=scores,
            validation_reasoning=reasoning
        )
        
        # Step 4: Process validation and mint LOVE
        mint = self.protocol.process_validation(intervention.id, validation_result)
        
        if verbose:
            if mint:
                print(f"\n[STEP 4] LOVE Minted!")
                print(f"  Total LOVE: {mint.amount:.2f}")
                print(f"  Distribution:")
                for role, amount in mint.distribution.items():
                    print(f"    {role}: {amount:.2f}")
            else:
                print(f"\n[STEP 4] No LOVE minted (validation failed)")
        
        # Compare with expected scores
        score_comparison = {}
        if scenario.expected_scores:
            for key in ["H", "T", "R", "S", "E", "W"]:
                expected = scenario.expected_scores.get(key, 0)
                actual = scores.get(key, 0)
                score_comparison[key] = {
                    "expected": expected,
                    "actual": actual,
                    "difference": actual - expected
                }
        
        result = {
            "scenario_id": scenario.id,
            "intervention_id": intervention.id,
            "status": "validated" if mint else "rejected",
            "confirmed": confirmed,
            "validated": validated,
            "love_minted": mint.amount if mint else 0.0,
            "scores": scores,
            "score_comparison": score_comparison,
            "distribution": mint.distribution if mint else {},
            "timestamp": datetime.now().timestamp()
        }
        
        self.simulation_history.append(result)
        return result
    
    def run_baseline_suite(self, verbose: bool = True) -> Dict:
        """Run all baseline scenarios"""
        print("\n" + "="*60)
        print("LOVE PROTOCOL PHASE 0 LAB - BASELINE SIMULATION")
        print("="*60)
        
        results = []
        for scenario in BASELINE_SCENARIOS:
            result = self.run_scenario(scenario, verbose=verbose)
            results.append(result)
            time.sleep(0.5)  # Small delay between scenarios
        
        # Calculate summary statistics
        total_love = sum(r["love_minted"] for r in results)
        validated_count = sum(1 for r in results if r["validated"])
        confirmed_count = sum(1 for r in results if r["confirmed"])
        
        summary = {
            "total_scenarios": len(BASELINE_SCENARIOS),
            "confirmed": confirmed_count,
            "validated": validated_count,
            "rejected": len(results) - validated_count,
            "total_love_minted": round(total_love, 2),
            "average_love_per_intervention": round(total_love / validated_count if validated_count > 0 else 0, 2),
            "results": results
        }
        
        if verbose:
            print("\n" + "="*60)
            print("SIMULATION SUMMARY")
            print("="*60)
            print(f"Total Scenarios: {summary['total_scenarios']}")
            print(f"Confirmed: {summary['confirmed']}")
            print(f"Validated: {summary['validated']}")
            print(f"Rejected: {summary['rejected']}")
            print(f"Total LOVE Minted: {summary['total_love_minted']}")
            print(f"Average LOVE per Intervention: {summary['average_love_per_intervention']}")
        
        return summary
    
    def get_simulation_report(self) -> Dict:
        """Generate comprehensive simulation report"""
        imi_metrics = self.protocol.get_imi_metrics()
        
        return {
            "simulation_history": self.simulation_history,
            "imi_metrics": imi_metrics,
            "protocol_stats": {
                "total_interventions": len(self.protocol.interventions),
                "total_validations": len(self.protocol.validations),
                "total_mints": len(self.protocol.mints)
            },
            "agent_stats": {
                "total_agents": len(self.agents),
                "primary_agents": len(self.primary_agents),
                "secondary_agents": len(self.secondary_agents),
                "tertiary_agents": len(self.tertiary_agents)
            }
        }


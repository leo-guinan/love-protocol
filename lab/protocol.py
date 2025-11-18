"""
LOVE Protocol Core Logic
Minting, Scoring, and IMI Calculation
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json
import numpy as np


@dataclass
class Intervention:
    """Represents a submitted intervention"""
    id: str
    intervener: str
    beneficiary: str
    description: str
    predicted_harm: str
    timestamp: float
    submission_data: Dict
    status: str = "submitted"  # submitted, confirmed, validated, rejected


@dataclass
class ValidationResult:
    """Result of HTC validation"""
    intervention_id: str
    confirmed: bool
    confirmed_by: str
    confirmation_explanation: str
    improvement_score: float
    
    validated: bool
    validated_by: str
    scores: Dict[str, float]  # H, T, R, S, E, W
    validation_reasoning: str
    
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())


@dataclass
class LOVEMint:
    """Represents a LOVE token mint"""
    intervention_id: str
    amount: float
    scores: Dict[str, float]
    timestamp: float
    distribution: Dict[str, float]  # intervener, beneficiary, validator, treasury


class LOVEProtocol:
    """Core protocol logic for LOVE minting"""
    
    def __init__(
        self,
        k: float = 1.0,  # Global issuance coefficient
        alpha: float = 1.2,  # H weight
        beta: float = 1.1,   # T weight
        gamma: float = 1.0, # R weight
        delta: float = 1.1, # S weight
        epsilon: float = 1.0, # E weight
        zeta: float = 1.0   # W weight
    ):
        self.k = k
        self.weights = {
            "H": alpha,
            "T": beta,
            "R": gamma,
            "S": delta,
            "E": epsilon,
            "W": zeta
        }
        self.interventions: Dict[str, Intervention] = {}
        self.validations: Dict[str, ValidationResult] = {}
        self.mints: List[LOVEMint] = []
    
    def calculate_love(
        self,
        scores: Dict[str, float],
        confirmed: bool = True
    ) -> float:
        """
        Calculate LOVE mint amount using formula:
        LOVE = k · (H^α · T^β · R^γ · S^δ · E^ε · W^ζ)
        """
        if not confirmed:
            return 0.0
        
        # Ensure all scores are present
        required_scores = ["H", "T", "R", "S", "E", "W"]
        for score_key in required_scores:
            if score_key not in scores:
                scores[score_key] = 1.0  # Minimum score
        
        # Apply formula
        product = 1.0
        for key, weight in self.weights.items():
            score = max(1.0, min(10.0, scores.get(key, 1.0)))  # Clamp 1-10
            product *= (score ** weight)
        
        love_amount = self.k * product
        
        # Normalize to reasonable range (0-1000 LOVE per intervention)
        # This prevents extreme values from high scores
        love_amount = min(1000.0, love_amount)
        
        return round(love_amount, 2)
    
    def distribute_love(
        self,
        total_love: float
    ) -> Dict[str, float]:
        """Distribute LOVE according to protocol rules"""
        return {
            "intervener": round(total_love * 0.60, 2),
            "beneficiary": round(total_love * 0.25, 2),
            "validator": round(total_love * 0.10, 2),
            "treasury": round(total_love * 0.05, 2)
        }
    
    def process_validation(
        self,
        intervention_id: str,
        validation_result: ValidationResult
    ) -> Optional[LOVEMint]:
        """Process a validation and mint LOVE if valid"""
        if intervention_id not in self.interventions:
            raise ValueError(f"Intervention {intervention_id} not found")
        
        intervention = self.interventions[intervention_id]
        
        # Store validation
        self.validations[intervention_id] = validation_result
        
        # Check if validation passed
        if not validation_result.confirmed or not validation_result.validated:
            intervention.status = "rejected"
            return None
        
        # Calculate LOVE
        love_amount = self.calculate_love(validation_result.scores)
        
        # Distribute LOVE
        distribution = self.distribute_love(love_amount)
        
        # Create mint record
        mint = LOVEMint(
            intervention_id=intervention_id,
            amount=love_amount,
            scores=validation_result.scores.copy(),
            timestamp=validation_result.timestamp,
            distribution=distribution
        )
        
        self.mints.append(mint)
        intervention.status = "validated"
        
        return mint
    
    def get_imi_metrics(
        self,
        time_window_days: int = 30
    ) -> Dict:
        """Calculate Inverse Market Index metrics"""
        if not self.mints:
            return {
                "total_love": 0.0,
                "intervention_count": 0,
                "average_scores": {},
                "mint_intensity": 0.0,
                "temporal_acceleration": 0.0
            }
        
        # Filter by time window
        cutoff_time = datetime.now().timestamp() - (time_window_days * 24 * 60 * 60)
        recent_mints = [m for m in self.mints if m.timestamp >= cutoff_time]
        
        if not recent_mints:
            return {
                "total_love": 0.0,
                "intervention_count": 0,
                "average_scores": {},
                "mint_intensity": 0.0,
                "temporal_acceleration": 0.0
            }
        
        # Calculate metrics
        total_love = sum(m.amount for m in recent_mints)
        
        # Average scores
        avg_scores = {}
        for key in ["H", "T", "R", "S", "E", "W"]:
            scores = [m.scores.get(key, 0) for m in recent_mints]
            avg_scores[key] = np.mean(scores) if scores else 0.0
        
        # Mint intensity (LOVE per day)
        mint_intensity = total_love / time_window_days
        
        # Temporal acceleration (rate of change in minting)
        if len(self.mints) > 1:
            sorted_mints = sorted(self.mints, key=lambda x: x.timestamp)
            first_half = sorted_mints[:len(sorted_mints)//2]
            second_half = sorted_mints[len(sorted_mints)//2:]
            
            first_half_love = sum(m.amount for m in first_half)
            second_half_love = sum(m.amount for m in second_half)
            
            time_span = sorted_mints[-1].timestamp - sorted_mints[0].timestamp
            if time_span > 0:
                first_rate = first_half_love / (time_span / 2)
                second_rate = second_half_love / (time_span / 2)
                temporal_acceleration = (second_rate - first_rate) / first_rate if first_rate > 0 else 0.0
            else:
                temporal_acceleration = 0.0
        else:
            temporal_acceleration = 0.0
        
        return {
            "total_love": round(total_love, 2),
            "intervention_count": len(recent_mints),
            "average_scores": {k: round(v, 2) for k, v in avg_scores.items()},
            "mint_intensity": round(mint_intensity, 2),
            "temporal_acceleration": round(temporal_acceleration, 4),
            "time_window_days": time_window_days
        }
    
    def get_participant_stats(self, participant_id: str) -> Dict:
        """Get statistics for a specific participant"""
        participant_interventions = [
            i for i in self.interventions.values()
            if i.intervener == participant_id or i.beneficiary == participant_id
        ]
        
        participant_mints = [
            m for m in self.mints
            if self.interventions[m.intervention_id].intervener == participant_id
        ]
        
        total_love_earned = sum(m.distribution.get("intervener", 0) for m in participant_mints)
        
        return {
            "participant_id": participant_id,
            "interventions_submitted": len([i for i in participant_interventions if i.intervener == participant_id]),
            "interventions_received": len([i for i in participant_interventions if i.beneficiary == participant_id]),
            "total_love_earned": round(total_love_earned, 2),
            "validated_interventions": len(participant_mints)
        }


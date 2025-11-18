"""
Sample Intervention Scenarios for Lab Testing
"""

from typing import Dict, List
from dataclasses import dataclass
from enum import Enum


class InterventionCategory(Enum):
    EMOTIONAL_SUPPORT = "emotional_support"
    CONFLICT_RESOLUTION = "conflict_resolution"
    PREVENTIVE_ACTION = "preventive_action"
    CLARIFICATION = "clarification"
    TIMELY_INTERVENTION = "timely_intervention"


@dataclass
class InterventionScenario:
    """Predefined scenario for testing"""
    id: str
    category: InterventionCategory
    intervener: str
    beneficiary: str
    description: str
    predicted_harm: str
    context: Dict
    expected_scores: Dict[str, float]  # Expected H, T, R, S, E, W
    difficulty: str  # "easy", "medium", "hard" (for validation)


# Baseline Scenarios for Testing

BASELINE_SCENARIOS = [
    InterventionScenario(
        id="scenario_001",
        category=InterventionCategory.EMOTIONAL_SUPPORT,
        intervener="Intervener_1",
        beneficiary="Beneficiary_1",
        description="I noticed my friend was showing signs of a panic attack and helped them through breathing exercises and grounding techniques.",
        predicted_harm="Full panic attack leading to public embarrassment and increased anxiety",
        context={
            "location": "coffee_shop",
            "time_of_day": "afternoon",
            "relationship": "close_friend",
            "before_state": "visible anxiety, rapid breathing, looking overwhelmed",
            "after_state": "calmer, breathing normalized, able to continue conversation"
        },
        expected_scores={
            "H": 7.0,  # Moderate-high harm prevented
            "T": 9.0,  # Very time-sensitive
            "R": 3.0,  # Individual impact
            "S": 6.0,  # Some downstream stability
            "E": 8.0,  # High emotional coherence improvement
            "W": 8.0   # High confidence
        },
        difficulty="easy"
    ),
    InterventionScenario(
        id="scenario_002",
        category=InterventionCategory.CONFLICT_RESOLUTION,
        intervener="Intervener_2",
        beneficiary="Beneficiary_2",
        description="I mediated a misunderstanding between two roommates about shared responsibilities that was escalating into a major conflict.",
        predicted_harm="Living situation breakdown, one person moving out, loss of friendship",
        context={
            "location": "shared_apartment",
            "time_of_day": "evening",
            "relationship": "mutual_friend",
            "before_state": "Tense conversation, raised voices, accusations",
            "after_state": "Agreement reached, clear boundaries set, both parties satisfied"
        },
        expected_scores={
            "H": 8.0,  # High harm prevented
            "T": 7.0,  # Time-sensitive before escalation
            "R": 7.0,  # Multiple people affected
            "S": 9.0,  # High stability improvement
            "E": 7.0,  # Good emotional coherence
            "W": 7.0   # Good confidence
        },
        difficulty="medium"
    ),
    InterventionScenario(
        id="scenario_003",
        category=InterventionCategory.PREVENTIVE_ACTION,
        intervener="Intervener_3",
        beneficiary="Beneficiary_3",
        description="I warned a friend about a potential mismatch with someone they were about to go on a first date with, based on shared values.",
        predicted_harm="Bad first date, emotional disappointment, wasted time and energy",
        context={
            "location": "phone_call",
            "time_of_day": "morning",
            "relationship": "close_friend",
            "before_state": "Excited about date, unaware of potential mismatch",
            "after_state": "More realistic expectations, decided to proceed with caution"
        },
        expected_scores={
            "H": 4.0,  # Moderate harm prevented
            "T": 8.0,  # Very time-sensitive (before date)
            "R": 2.0,  # Individual impact
            "S": 5.0,  # Moderate stability
            "E": 6.0,  # Moderate emotional coherence
            "W": 6.0   # Moderate confidence
        },
        difficulty="hard"  # Harder to validate counterfactual
    ),
    InterventionScenario(
        id="scenario_004",
        category=InterventionCategory.CLARIFICATION,
        intervener="Intervener_1",
        beneficiary="Beneficiary_1",
        description="I clarified a misunderstanding between two partners about communication preferences that was causing ongoing friction.",
        predicted_harm="Continued miscommunication, relationship strain, potential breakup",
        context={
            "location": "group_setting",
            "time_of_day": "afternoon",
            "relationship": "mutual_friend",
            "before_state": "Both partners frustrated, repeating same arguments",
            "after_state": "Understanding reached, new communication approach agreed"
        },
        expected_scores={
            "H": 6.0,  # Moderate-high harm
            "T": 6.0,  # Moderate timing sensitivity
            "R": 6.0,  # Two people affected
            "S": 8.0,  # High stability improvement
            "E": 9.0,  # Very high emotional coherence
            "W": 7.0   # Good confidence
        },
        difficulty="medium"
    ),
    InterventionScenario(
        id="scenario_005",
        category=InterventionCategory.TIMELY_INTERVENTION,
        intervener="Intervener_2",
        beneficiary="Beneficiary_2",
        description="I checked in with a friend at exactly the right moment when they were about to make a decision they would regret.",
        predicted_harm="Poor decision with long-term consequences, regret, relationship damage",
        context={
            "location": "text_message",
            "time_of_day": "late_night",
            "relationship": "close_friend",
            "before_state": "About to send angry message, emotional state",
            "after_state": "Decided to wait, calmer perspective gained"
        },
        expected_scores={
            "H": 7.0,  # Moderate-high harm
            "T": 10.0, # Extremely time-sensitive
            "R": 4.0,  # Moderate relational impact
            "S": 7.0,  # High stability
            "E": 7.0,  # Good emotional coherence
            "W": 7.0   # Good confidence
        },
        difficulty="easy"
    ),
    # Edge cases for testing
    InterventionScenario(
        id="scenario_006",
        category=InterventionCategory.EMOTIONAL_SUPPORT,
        intervener="Intervener_3",
        beneficiary="Beneficiary_3",
        description="I listened to someone vent about work stress for 10 minutes.",
        predicted_harm="Continued stress buildup",
        context={
            "location": "workplace",
            "time_of_day": "afternoon",
            "relationship": "colleague",
            "before_state": "Stressed about work",
            "after_state": "Slightly less stressed"
        },
        expected_scores={
            "H": 2.0,  # Low harm prevented
            "T": 3.0,  # Low timing sensitivity
            "R": 1.0,  # Minimal impact
            "S": 2.0,  # Low stability
            "E": 3.0,  # Low emotional coherence
            "W": 4.0   # Low confidence
        },
        difficulty="hard"  # Hard to validate minimal impact
    ),
    InterventionScenario(
        id="scenario_007",
        category=InterventionCategory.CONFLICT_RESOLUTION,
        intervener="Intervener_1",
        beneficiary="Beneficiary_1",
        description="I prevented a community-wide conflict by addressing a misunderstanding before it spread.",
        predicted_harm="Community split, loss of trust, multiple relationships damaged",
        context={
            "location": "community_space",
            "time_of_day": "evening",
            "relationship": "community_member",
            "before_state": "Rumors spreading, tension building",
            "after_state": "Misunderstanding clarified, community cohesion maintained"
        },
        expected_scores={
            "H": 9.0,  # Very high harm prevented
            "T": 8.0,  # High timing sensitivity
            "R": 10.0, # Very high relational impact
            "S": 9.0,  # Very high stability
            "E": 8.0,  # High emotional coherence
            "W": 8.0   # High confidence
        },
        difficulty="medium"
    ),
]


def get_scenario_by_id(scenario_id: str) -> InterventionScenario:
    """Get a specific scenario by ID"""
    for scenario in BASELINE_SCENARIOS:
        if scenario.id == scenario_id:
            return scenario
    raise ValueError(f"Scenario {scenario_id} not found")


def get_scenarios_by_category(category: InterventionCategory) -> List[InterventionScenario]:
    """Get all scenarios of a specific category"""
    return [s for s in BASELINE_SCENARIOS if s.category == category]


def get_scenarios_by_difficulty(difficulty: str) -> List[InterventionScenario]:
    """Get scenarios by validation difficulty"""
    return [s for s in BASELINE_SCENARIOS if s.difficulty == difficulty]


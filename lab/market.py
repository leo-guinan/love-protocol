"""
Market Simulation Layer
Tests if LOVE minting patterns can predict market movements
"""

import json
import random
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import numpy as np

from lab.agents import AIAgent, AgentPersona, WitnessRole, create_agent_pool
from lab.protocol import LOVEProtocol, Intervention, ValidationResult
from lab.scenarios import InterventionScenario


class MarketSector(Enum):
    """Market sectors to track"""
    DATING_APPS = "dating_apps"
    SOCIAL_NETWORKS = "social_networks"
    COMMUNITY_PLATFORMS = "community_platforms"
    MENTAL_HEALTH = "mental_health"
    WORKPLACE = "workplace"
    EDUCATION = "education"


@dataclass
class MarketIndicator:
    """Tracks a market health indicator"""
    sector: MarketSector
    name: str
    value: float  # Current value (0-100)
    trend: float  # Rate of change per day
    volatility: float  # Random volatility factor
    history: List[Tuple[float, float]] = field(default_factory=list)  # (timestamp, value)
    
    def update(self, delta_days: float = 1.0):
        """Update indicator value based on trend and volatility"""
        # Add trend
        self.value += self.trend * delta_days
        
        # Add random volatility
        self.value += random.gauss(0, self.volatility)
        
        # Clamp to 0-100
        self.value = max(0.0, min(100.0, self.value))
        
        # Record history
        timestamp = datetime.now().timestamp()
        self.history.append((timestamp, self.value))
        
        # Keep only last 1000 points
        if len(self.history) > 1000:
            self.history.pop(0)


@dataclass
class Organization:
    """An organization/firm with agents"""
    id: str
    name: str
    sector: MarketSector
    size: int  # Number of agents
    agents: List[AIAgent]
    communication_density: float  # 0-1, how much agents interact
    internal_stress: float  # 0-1, baseline stress level
    love_mints: List[Dict] = field(default_factory=list)
    intervention_rate: float = 0.1  # Interventions per agent per day
    
    def get_agents_by_role(self, role: WitnessRole) -> List[AIAgent]:
        """Get agents with specific role"""
        return [a for a in self.agents if a.persona.role == role]
    
    def get_random_agent_pair(self) -> Tuple[AIAgent, AIAgent]:
        """Get two random agents for intervention"""
        if len(self.agents) < 2:
            return None, None
        
        intervener, beneficiary = random.sample(self.agents, 2)
        return intervener, beneficiary


@dataclass
class MarketConfig:
    """Configuration for market simulation"""
    num_organizations: int = 5
    min_org_size: int = 10
    max_org_size: int = 50
    sectors: List[MarketSector] = field(default_factory=lambda: [
        MarketSector.DATING_APPS,
        MarketSector.SOCIAL_NETWORKS,
        MarketSector.COMMUNITY_PLATFORMS
    ])
    simulation_days: int = 30
    interventions_per_day: float = 2.0  # Average interventions per organization per day
    communication_density_range: Tuple[float, float] = (0.3, 0.8)
    stress_range: Tuple[float, float] = (0.2, 0.6)
    
    # Market indicator configs
    indicator_volatility: float = 2.0
    indicator_trend_range: Tuple[float, float] = (-1.0, 1.0)  # Per day
    
    # LOVE impact on markets
    love_to_market_correlation: float = -0.3  # Negative: more LOVE = declining market
    love_prediction_lag_days: int = 7  # LOVE predicts market movements N days ahead


class MarketSimulation:
    """Simulates market with organizations and tracks LOVE patterns"""
    
    def __init__(
        self,
        config: MarketConfig,
        protocol: LOVEProtocol
    ):
        self.config = config
        self.protocol = protocol
        self.organizations: List[Organization] = []
        self.market_indicators: Dict[MarketSector, MarketIndicator] = {}
        self.simulation_history: List[Dict] = []
        self.current_day = 0
        
        self._initialize_organizations()
        self._initialize_market_indicators()
    
    def _initialize_organizations(self):
        """Create organizations with agents"""
        # Ensure at least one organization per sector
        sectors_to_assign = list(self.config.sectors) * (self.config.num_organizations // len(self.config.sectors) + 1)
        sectors_to_assign = sectors_to_assign[:self.config.num_organizations]
        
        # Shuffle to randomize order
        random.shuffle(sectors_to_assign)
        
        for i in range(self.config.num_organizations):
            org_size = random.randint(
                self.config.min_org_size,
                self.config.max_org_size
            )
            
            # Create agent pool for this organization
            agents = create_agent_pool(num_agents=org_size)
            
            # Assign sector (ensuring distribution)
            sector = sectors_to_assign[i] if i < len(sectors_to_assign) else random.choice(self.config.sectors)
            
            org = Organization(
                id=f"org_{i+1}",
                name=f"{sector.value.title()} Organization {i+1}",
                sector=sector,
                size=org_size,
                agents=agents,
                communication_density=random.uniform(*self.config.communication_density_range),
                internal_stress=random.uniform(*self.config.stress_range),
                intervention_rate=self.config.interventions_per_day / org_size
            )
            
            self.organizations.append(org)
    
    def _initialize_market_indicators(self):
        """Initialize market health indicators for each sector"""
        # Only create indicators for sectors that have organizations
        sectors_with_orgs = set(org.sector for org in self.organizations)
        
        for sector in self.config.sectors:
            # Only create indicator if sector has organizations
            if sector in sectors_with_orgs:
                indicator = MarketIndicator(
                    sector=sector,
                    name=f"{sector.value.replace('_', ' ').title()} Health",
                    value=random.uniform(60, 90),  # Start healthy
                    trend=random.uniform(*self.config.indicator_trend_range),
                    volatility=self.config.indicator_volatility
                )
                self.market_indicators[sector] = indicator
            else:
                # Sector has no organizations - skip indicator
                # (This shouldn't happen with the new assignment logic, but keep as safety)
                pass
    
    def _generate_intervention_scenario(
        self,
        org: Organization,
        intervener: AIAgent,
        beneficiary: AIAgent
    ) -> Dict:
        """Generate a realistic intervention scenario for organization"""
        # Base intervention types based on sector
        sector_scenarios = {
            MarketSector.DATING_APPS: [
                "prevented a misaligned first date",
                "clarified communication misunderstanding",
                "helped avoid relationship conflict"
            ],
            MarketSector.SOCIAL_NETWORKS: [
                "resolved social media conflict",
                "prevented public embarrassment",
                "clarified misunderstanding between users"
            ],
            MarketSector.COMMUNITY_PLATFORMS: [
                "mediated community conflict",
                "prevented group breakdown",
                "resolved member misunderstanding"
            ],
            MarketSector.MENTAL_HEALTH: [
                "prevented panic spiral",
                "provided emotional support",
                "intervened before crisis"
            ],
            MarketSector.WORKPLACE: [
                "resolved workplace conflict",
                "prevented team breakdown",
                "clarified work misunderstanding"
            ],
            MarketSector.EDUCATION: [
                "prevented student conflict",
                "resolved classroom misunderstanding",
                "provided timely support"
            ]
        }
        
        scenarios = sector_scenarios.get(org.sector, ["provided support"])
        description = random.choice(scenarios)
        
        # Adjust based on organization stress
        harm_severity = org.internal_stress * 10
        
        return {
            "description": f"{intervener.persona.name} {description} for {beneficiary.persona.name}",
            "predicted_harm": f"Potential {org.sector.value} breakdown",
            "context": {
                "organization": org.id,
                "sector": org.sector.value,
                "stress_level": org.internal_stress,
                "before_state": "Tense situation",
                "after_state": "Improved communication"
            }
        }
    
    def simulate_day(self) -> Dict:
        """Simulate one day of market activity"""
        day_results = {
            "day": self.current_day,
            "interventions": [],
            "love_minted": 0.0,
            "market_indicators": {},
            "organizations": {}
        }
        
        # Generate interventions for each organization
        for org in self.organizations:
            # Calculate number of interventions based on rate and stress
            num_interventions = int(
                org.intervention_rate * org.size * 
                (1 + org.internal_stress) *  # More stress = more interventions
                random.uniform(0.5, 1.5)  # Random variation
            )
            
            org_love = 0.0
            
            for _ in range(num_interventions):
                # Get agent pair
                intervener, beneficiary = org.get_random_agent_pair()
                if not intervener or not beneficiary:
                    continue
                
                # Generate scenario
                scenario_data = self._generate_intervention_scenario(
                    org, intervener, beneficiary
                )
                
                # Submit intervention
                try:
                    intervention_data = intervener.submit_intervention(
                        beneficiary=beneficiary.persona.name,
                        description=scenario_data["description"],
                        predicted_harm=scenario_data["predicted_harm"],
                        context=scenario_data["context"]
                    )
                    
                    # Create intervention record
                    intervention = Intervention(
                        id=f"{org.id}_{datetime.now().timestamp()}",
                        intervener=intervener.persona.name,
                        beneficiary=beneficiary.persona.name,
                        description=scenario_data["description"],
                        predicted_harm=scenario_data["predicted_harm"],
                        timestamp=datetime.now().timestamp(),
                        submission_data=intervention_data
                    )
                    
                    self.protocol.interventions[intervention.id] = intervention
                    
                    # Get validator (could be from same org or different)
                    validators = org.get_agents_by_role(WitnessRole.TERTIARY)
                    if not validators:
                        # Get validator from any organization
                        all_validators = [
                            a for org2 in self.organizations 
                            for a in org2.get_agents_by_role(WitnessRole.TERTIARY)
                        ]
                        validators = all_validators
                    
                    if validators:
                        validator = random.choice(validators)
                        
                        # Confirm
                        confirmed, explanation, improvement = beneficiary.confirm_intervention(
                            intervention=intervention_data,
                            intervener=intervener.persona.name
                        )
                        
                        if confirmed:
                            # Validate
                            validated, scores, reasoning = validator.validate_intervention(
                                intervention=intervention_data,
                                confirmation=(confirmed, explanation, improvement),
                                intervener=intervener.persona.name,
                                beneficiary=beneficiary.persona.name
                            )
                            
                            if validated:
                                validation_result = ValidationResult(
                                    intervention_id=intervention.id,
                                    confirmed=confirmed,
                                    confirmed_by=beneficiary.persona.name,
                                    confirmation_explanation=explanation,
                                    improvement_score=improvement,
                                    validated=validated,
                                    validated_by=validator.persona.name,
                                    scores=scores,
                                    validation_reasoning=reasoning
                                )
                                
                                mint = self.protocol.process_validation(
                                    intervention.id,
                                    validation_result
                                )
                                
                                if mint:
                                    org_love += mint.amount
                                    org.love_mints.append({
                                        "intervention_id": intervention.id,
                                        "love": mint.amount,
                                        "scores": scores,
                                        "timestamp": mint.timestamp
                                    })
                                    
                                    day_results["interventions"].append({
                                        "org": org.id,
                                        "intervention_id": intervention.id,
                                        "love": mint.amount
                                    })
                except Exception as e:
                    # Skip failed interventions
                    continue
            
            day_results["organizations"][org.id] = {
                "interventions": num_interventions,
                "love_minted": org_love
            }
            day_results["love_minted"] += org_love
        
        # Update market indicators and track sector-specific LOVE
        # Only update indicators for sectors that have organizations
        for sector, indicator in list(self.market_indicators.items()):
            # Calculate sector-specific LOVE for this day
            orgs_in_sector = [o for o in self.organizations if o.sector == sector]
            sector_love_today = sum(
                day_results["organizations"].get(org.id, {}).get("love_minted", 0.0)
                for org in orgs_in_sector
            )
            
            # Store sector LOVE history for correlation calculation
            if not hasattr(indicator, 'love_history'):
                indicator.love_history = []
            indicator.love_history.append((datetime.now().timestamp(), sector_love_today))
            
            # More LOVE = declining market health (negative correlation)
            # Stronger impact: LOVE directly affects trend
            # Each 1000 LOVE = -0.3 trend change per day (configurable)
            love_impact = sector_love_today * self.config.love_to_market_correlation / 1000.0
            indicator.trend += love_impact  # Direct impact (was 0.1, now 1.0)
            
            # Also apply direct value impact (immediate effect)
            direct_impact = sector_love_today * self.config.love_to_market_correlation / 500.0
            indicator.value += direct_impact
            
            indicator.update(delta_days=1.0)
            day_results["market_indicators"][sector.value] = {
                "value": round(indicator.value, 2),
                "trend": round(indicator.trend, 4),
                "love_today": round(sector_love_today, 2)
            }
        
        self.current_day += 1
        self.simulation_history.append(day_results)
        
        return day_results
    
    def run_simulation(self, verbose: bool = True) -> Dict:
        """Run full market simulation"""
        if verbose:
            print("="*60)
            print("MARKET SIMULATION")
            print("="*60)
            print(f"Organizations: {len(self.organizations)}")
            print(f"Simulation Days: {self.config.simulation_days}")
            print(f"Sectors: {[s.value for s in self.config.sectors]}")
            print("="*60)
        
        for day in range(self.config.simulation_days):
            if verbose and day % 5 == 0:
                print(f"\nDay {day+1}/{self.config.simulation_days}...")
            
            self.simulate_day()
        
        if verbose:
            print("\n" + "="*60)
            print("SIMULATION COMPLETE")
            print("="*60)
        
        return self.get_simulation_summary()
    
    def get_simulation_summary(self) -> Dict:
        """Get summary of simulation results"""
        total_love = sum(day["love_minted"] for day in self.simulation_history)
        total_interventions = sum(len(day["interventions"]) for day in self.simulation_history)
        
        # Calculate LOVE patterns by sector
        sector_love = {}
        for sector in self.config.sectors:
            orgs = [o for o in self.organizations if o.sector == sector]
            sector_total = sum(
                sum(m["love"] for m in org.love_mints)
                for org in orgs
            )
            sector_love[sector.value] = sector_total
        
        # Calculate market predictions
        predictions = self._calculate_predictions()
        
        return {
            "total_days": self.config.simulation_days,
            "total_love_minted": round(total_love, 2),
            "total_interventions": total_interventions,
            "organizations": {
                org.id: {
                    "name": org.name,
                    "sector": org.sector.value,
                    "size": org.size,
                    "total_love": round(sum(m["love"] for m in org.love_mints), 2),
                    "interventions": len(org.love_mints)
                }
                for org in self.organizations
            },
            "sector_love": sector_love,
            "market_indicators": {
                sector.value: {
                    "current": round(indicator.value, 2),
                    "initial": round(indicator.history[0][1] if indicator.history else 0, 2),
                    "change": round(indicator.value - (indicator.history[0][1] if indicator.history else indicator.value), 2),
                    "trend": round(indicator.trend, 4)
                }
                for sector, indicator in self.market_indicators.items()
            },
            "predictions": predictions,
            "daily_history": self.simulation_history
        }
    
    def _calculate_predictions(self) -> Dict:
        """Calculate market predictions based on LOVE patterns"""
        predictions = {}
        
        for sector, indicator in self.market_indicators.items():
            # Get sector-specific LOVE history
            sector_love_history = getattr(indicator, 'love_history', [])
            
            if len(sector_love_history) >= self.config.love_prediction_lag_days and \
               len(indicator.history) >= self.config.love_prediction_lag_days:
                
                # Compare early LOVE to later market movement
                # Early period: first N days
                early_love_days = sector_love_history[:self.config.love_prediction_lag_days]
                early_love = sum(love for _, love in early_love_days)
                
                # Late period: last N days
                late_love_days = sector_love_history[-self.config.love_prediction_lag_days:]
                late_love = sum(love for _, love in late_love_days)
                
                # Get market change over the same period
                early_market = indicator.history[0][1]
                late_market = indicator.history[-1][1]
                market_change = late_market - early_market
                
                # Prediction: More LOVE early should predict market decline later
                # Hypothesis: LOVE increase → Market decline (negative correlation)
                # Compare early LOVE to later market change
                # If early LOVE is high, market should decline later
                
                # Calculate early cumulative LOVE (first N days)
                early_cumulative_love = sum(love for _, love in early_love_days)
                
                # Calculate late cumulative LOVE (last N days)  
                late_cumulative_love = sum(love for _, love in late_love_days)
                
                # For prediction: if early LOVE is high, market should decline
                # We compare early LOVE to market change over the full period
                love_increase = late_cumulative_love > early_cumulative_love
                market_decline = market_change < 0
                
                # Prediction logic: High early LOVE should predict market decline
                # Compare early LOVE period to later market change
                # Simple approach: if early LOVE is above median, predict decline
                if len(sector_love_history) > self.config.love_prediction_lag_days:
                    # Calculate median early LOVE across all sectors for comparison
                    # Or use a simple threshold: if early LOVE > 0, expect decline
                    high_early_love = early_cumulative_love > 0  # Any LOVE means stress
                    prediction_correct = (high_early_love and market_decline) or \
                                      (not high_early_love and not market_decline)
                else:
                    # Fallback: use simple comparison
                    prediction_correct = (love_increase and market_decline) or \
                                      (not love_increase and not market_decline)
                
                # Calculate sector-specific correlation
                # Compare cumulative LOVE to market value over time
                # Hypothesis: As cumulative LOVE increases, market should decrease (negative correlation)
                if len(sector_love_history) == len(indicator.history) and len(sector_love_history) > 1:
                    # Calculate cumulative LOVE over time
                    cumulative_love = []
                    running_total = 0.0
                    for _, love in sector_love_history:
                        running_total += love
                        cumulative_love.append(running_total)
                    
                    market_values = [value for _, value in indicator.history]
                    
                    # Ensure same length
                    min_len = min(len(cumulative_love), len(market_values))
                    cumulative_love = cumulative_love[:min_len]
                    market_values = market_values[:min_len]
                    
                    # Calculate correlation: should be negative (more LOVE = lower market)
                    if len(cumulative_love) > 1 and np.std(cumulative_love) > 0 and np.std(market_values) > 0:
                        correlation = np.corrcoef(cumulative_love, market_values)[0][1]
                    else:
                        correlation = 0.0
                else:
                    correlation = 0.0
                
                predictions[sector.value] = {
                    "early_love": round(early_love, 2),
                    "late_love": round(late_love, 2),
                    "love_change": round(late_love - early_love, 2),
                    "market_change": round(market_change, 2),
                    "prediction_correct": prediction_correct,
                    "correlation": round(correlation, 4)
                }
            else:
                # Not enough data
                predictions[sector.value] = {
                    "early_love": 0.0,
                    "late_love": 0.0,
                    "love_change": 0.0,
                    "market_change": 0.0,
                    "prediction_correct": False,
                    "correlation": 0.0
                }
        
        return predictions


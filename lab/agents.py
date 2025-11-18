"""
AI Agent System for Simulating HTC Witnesses
Uses local Ollama for agent reasoning
"""

import json
import random
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import ollama


class WitnessRole(Enum):
    """Roles in Human Triangulation Consensus"""
    PRIMARY = "intervener"  # Submits intervention
    SECONDARY = "beneficiary"  # Confirms intervention
    TERTIARY = "validator"  # Neutral validation


@dataclass
class AgentPersona:
    """Personality and behavior profile for AI agent"""
    name: str
    role: WitnessRole
    trust_level: float  # 0.0 to 1.0 (affects validation strictness)
    social_connection: Optional[str] = None  # If connected to another agent
    bias_factor: float = 0.0  # -1.0 (skeptical) to 1.0 (generous)
    response_style: str = "balanced"  # "strict", "balanced", "generous"


class AIAgent:
    """AI agent that can act as HTC witness"""
    
    def __init__(
        self,
        persona: AgentPersona,
        ollama_model: str = "llama3.2",
        ollama_base_url: str = "http://localhost:11434"
    ):
        self.persona = persona
        self.ollama_model = ollama_model
        self.ollama_base_url = ollama_base_url
        self.validation_history: List[Dict] = []
        
    def _call_ollama(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Call local Ollama model"""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = ollama.chat(
                model=self.ollama_model,
                messages=messages
            )
            return response['message']['content']
        except Exception as e:
            # Fallback to deterministic response based on persona
            return self._fallback_response(prompt)
    
    def _extract_json(self, text: str) -> Optional[Dict]:
        """Extract JSON from text, handling markdown code blocks"""
        import re
        
        # Try direct JSON parse first
        try:
            return json.loads(text.strip())
        except:
            pass
        
        # Try extracting from markdown code blocks
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except:
                pass
        
        # Try finding JSON object in text
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except:
                pass
        
        return None
    
    def _fallback_response(self, prompt: str) -> str:
        """Fallback deterministic response when Ollama unavailable"""
        # Simple rule-based fallback
        if "validate" in prompt.lower():
            if self.persona.bias_factor > 0.3:
                return "Yes, this intervention seems valid and helpful."
            elif self.persona.bias_factor < -0.3:
                return "I'm skeptical about this claim. Need more evidence."
            else:
                return "This appears plausible, but I'd like more context."
        return "I need to consider this further."
    
    def submit_intervention(
        self,
        beneficiary: str,
        description: str,
        predicted_harm: str,
        context: Dict
    ) -> Dict:
        """Primary witness submits an intervention"""
        if self.persona.role != WitnessRole.PRIMARY:
            raise ValueError("Only PRIMARY witness can submit interventions")
        
        system_prompt = f"""You are {self.persona.name}, a caring person who helps others.
You are submitting an intervention you performed to help {beneficiary}.
Be honest and specific about what you did and what harm you prevented."""
        
        prompt = f"""Describe an intervention you performed:

Beneficiary: {beneficiary}
What you did: {description}
Harm you prevented: {predicted_harm}
Context: {json.dumps(context, indent=2)}

Format your response as JSON with:
- "intervention_description": detailed narrative
- "before_state": what the situation was like
- "after_state": what changed
- "evidence": what proves this helped
"""
        
        response = self._call_ollama(prompt, system_prompt)
        
        # Try to parse JSON, fallback to structured text
        intervention_data = self._extract_json(response)
        if not intervention_data:
            intervention_data = {
                "intervention_description": response,
                "before_state": context.get("before_state", "Unknown"),
                "after_state": context.get("after_state", "Improved"),
                "evidence": "Narrative confirmation"
            }
        
        return {
            "intervener": self.persona.name,
            "beneficiary": beneficiary,
            "submission": intervention_data,
            "timestamp": context.get("timestamp"),
            "predicted_harm": predicted_harm
        }
    
    def confirm_intervention(
        self,
        intervention: Dict,
        intervener: str
    ) -> Tuple[bool, str, float]:
        """Secondary witness (beneficiary) confirms intervention"""
        if self.persona.role != WitnessRole.SECONDARY:
            raise ValueError("Only SECONDARY witness can confirm interventions")
        
        system_prompt = f"""You are {self.persona.name}, the person who received help from {intervener}.
Be honest about whether the intervention actually helped you and prevented harm.
Consider your relationship with {intervener}: {self.persona.social_connection or 'neutral'}"""
        
        prompt = f"""Did {intervener} actually help you?

Intervention: {intervention.get('submission', {}).get('intervention_description', 'Unknown')}
Predicted harm prevented: {intervention.get('predicted_harm', 'Unknown')}

Respond with JSON:
- "confirmed": true/false
- "explanation": why you confirm or deny
- "improvement_score": 0.0 to 1.0 (how much this helped)
- "harm_prevented_score": 0.0 to 1.0 (how much harm was actually prevented)
"""
        
        response = self._call_ollama(prompt, system_prompt)
        
        # Parse response
        confirmation = self._extract_json(response)
        if confirmation:
            confirmed = confirmation.get("confirmed", False)
            improvement = confirmation.get("improvement_score", 0.5)
            explanation = confirmation.get("explanation", "No explanation provided")
        else:
            # Fallback based on persona
            confirmed = self.persona.bias_factor > -0.5
            improvement = max(0.0, min(1.0, 0.5 + self.persona.bias_factor * 0.3))
            explanation = response[:200] if len(response) > 0 else "Confirmation based on agent persona"
        
        return confirmed, explanation, improvement
    
    def validate_intervention(
        self,
        intervention: Dict,
        confirmation: Tuple[bool, str, float],
        intervener: str,
        beneficiary: str
    ) -> Tuple[bool, Dict[str, float], str]:
        """Tertiary witness validates intervention"""
        if self.persona.role != WitnessRole.TERTIARY:
            raise ValueError("Only TERTIARY witness can validate interventions")
        
        system_prompt = f"""You are {self.persona.name}, a neutral validator.
You are checking if an intervention claim is plausible and consistent.
Your trust level: {self.persona.trust_level}
Your bias: {'generous' if self.persona.bias_factor > 0 else 'skeptical' if self.persona.bias_factor < 0 else 'balanced'}"""
        
        prompt = f"""Validate this intervention claim:

Intervener: {intervener}
Beneficiary: {beneficiary}
Intervention: {intervention.get('submission', {}).get('intervention_description', 'Unknown')}
Beneficiary confirmed: {confirmation[0]}
Beneficiary explanation: {confirmation[1]}

Respond with JSON:
- "valid": true/false
- "scores": {{
    "H": 0-10 (severity of prevented harm),
    "T": 0-10 (timing sensitivity),
    "R": 0-10 (relational impact radius),
    "S": 0-10 (downstream stability),
    "E": 0-10 (emotional coherence),
    "W": 0-10 (your confidence)
  }}
- "reasoning": explanation of your validation
"""
        
        response = self._call_ollama(prompt, system_prompt)
        
        # Parse response
        validation = self._extract_json(response)
        if validation:
            valid = validation.get("valid", False)
            scores = validation.get("scores", {})
            reasoning = validation.get("reasoning", "No reasoning provided")
        else:
            # Fallback based on persona
            valid = self.persona.bias_factor > -0.3
            scores = {
                "H": max(1, min(10, 5 + int(self.persona.bias_factor * 3))),
                "T": max(1, min(10, 5 + int(self.persona.bias_factor * 2))),
                "R": max(1, min(10, 5 + int(self.persona.bias_factor * 2))),
                "S": max(1, min(10, 5 + int(self.persona.bias_factor * 3))),
                "E": max(1, min(10, 5 + int(self.persona.bias_factor * 2))),
                "W": max(1, min(10, int(self.persona.trust_level * 10)))
            }
            reasoning = response[:200] if len(response) > 0 else f"Validation based on {self.persona.response_style} persona"
        
        # Apply persona bias
        for key in scores:
            scores[key] = max(1, min(10, scores[key] + self.persona.bias_factor * 2))
        
        self.validation_history.append({
            "intervention": intervention,
            "valid": valid,
            "scores": scores,
            "reasoning": reasoning
        })
        
        return valid, scores, reasoning


def create_agent_pool(num_agents: int = 9) -> List[AIAgent]:
    """Create a pool of diverse AI agents for simulation"""
    agents = []
    
    # Create 3 primary witnesses (interveners)
    for i in range(3):
        agents.append(AIAgent(AgentPersona(
            name=f"Intervener_{i+1}",
            role=WitnessRole.PRIMARY,
            trust_level=0.7 + random.random() * 0.2,
            bias_factor=random.uniform(-0.2, 0.3),
            response_style=random.choice(["strict", "balanced", "generous"])
        )))
    
    # Create 3 secondary witnesses (beneficiaries)
    for i in range(3):
        agents.append(AIAgent(AgentPersona(
            name=f"Beneficiary_{i+1}",
            role=WitnessRole.SECONDARY,
            trust_level=0.6 + random.random() * 0.3,
            bias_factor=random.uniform(-0.1, 0.4),
            social_connection=f"Intervener_{(i % 3) + 1}"  # Some connection
        )))
    
    # Create 3 tertiary witnesses (validators)
    for i in range(3):
        agents.append(AIAgent(AgentPersona(
            name=f"Validator_{i+1}",
            role=WitnessRole.TERTIARY,
            trust_level=0.8 + random.random() * 0.15,
            bias_factor=random.uniform(-0.3, 0.2),  # More skeptical
            response_style=random.choice(["strict", "balanced"])
        )))
    
    return agents


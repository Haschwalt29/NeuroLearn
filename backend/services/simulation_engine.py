from dataclasses import dataclass
from typing import Dict, List

STRATEGIES = ["HARD_PROBLEM", "WORKED_EXAMPLE", "VISUAL_EXPLANATION", "QUIZ_GAME"]

@dataclass
class SimulationResult:
    predicted_mastery_delta: float
    predicted_frustration_delta: float


class SimulationEngine:
    def __init__(self):
        pass

    def simulate(self, mastery_vector: Dict[int, float], emotion_state: Dict[str, float], strategy: str) -> SimulationResult:
        # Simple heuristic:
        # - HARD_PROBLEM: +0.06 mastery, +0.05 frustration (more if low current mastery)
        # - WORKED_EXAMPLE: +0.04 mastery, -0.02 frustration
        # - VISUAL_EXPLANATION: +0.03 mastery, -0.03 frustration
        # - QUIZ_GAME: +0.035 mastery, -0.01 frustration
        strategy = strategy.upper()
        avg_mastery = 0.0
        if mastery_vector:
            avg_mastery = sum(mastery_vector.values()) / len(mastery_vector)
        frustration = float(emotion_state.get("frustration", 0.0))

        if strategy == "HARD_PROBLEM":
            base_m = 0.06 + max(0.0, 0.05 * (0.5 - avg_mastery))
            base_f = 0.05 + max(0.0, 0.05 * (0.5 - avg_mastery))
        elif strategy == "WORKED_EXAMPLE":
            base_m = 0.04
            base_f = -0.02
        elif strategy == "VISUAL_EXPLANATION":
            base_m = 0.03
            base_f = -0.03
        elif strategy == "QUIZ_GAME":
            base_m = 0.035
            base_f = -0.01
        else:
            base_m = 0.02
            base_f = 0.0

        # Frustration sensitivity: if already frustrated, avoid increasing too much
        base_f += 0.02 * frustration

        return SimulationResult(predicted_mastery_delta=base_m, predicted_frustration_delta=base_f)



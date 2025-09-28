from typing import Dict, Optional
from sqlalchemy import desc
from ..models import PerformanceLog


def _compute_average_score(logs) -> Optional[float]:
    scores = [l.score for l in logs if l.score is not None]
    if scores:
        return sum(scores) / len(scores)
    # Fallback to correctness ratio if score is missing
    if logs:
        correct_ratio = sum(1 for l in logs if l.correct) / len(logs)
        return correct_ratio
    return None


def get_next_question(user_id: int, module: str) -> Dict:
    # Query last 5 logs for this module
    recent = (
        PerformanceLog.query
        .filter(PerformanceLog.user_id == user_id, PerformanceLog.module == module)
        .order_by(desc(PerformanceLog.timestamp))
        .limit(5)
        .all()
    )

    avg = _compute_average_score(recent)

    if avg is None:
        difficulty = "medium"
    elif avg > 0.8:
        difficulty = "hard"
    elif avg < 0.5:
        difficulty = "easy"
    else:
        difficulty = "medium"

    # For now return a dummy question descriptor
    return {
        "module": module,
        "difficulty": difficulty,
        "strategy": "adaptive_by_recent_performance",
        "context": {
            "recent_count": len(recent),
            "average": avg,
        }
    }



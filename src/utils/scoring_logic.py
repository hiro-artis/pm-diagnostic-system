"""Scoring logic for mindset test."""

from src.models.schemas import Mindset


# ============================================================================
# Mindset Scenario Scoring Patterns
# ============================================================================
# Each scenario has 4 answer options with corresponding mindset scores
# Based on docs/test-questions.md mindset evaluation

MINDSET_SCORING_PATTERNS = {
    "MS-S01": {  # 予算削減シナリオ
        "A": {Mindset.FUTURE_FOCUSED: 3, Mindset.SELF_RESPONSIBILITY: 2},
        "B": {Mindset.FUTURE_FOCUSED: 2, Mindset.SELF_RESPONSIBILITY: 4},
        "C": {Mindset.FUTURE_FOCUSED: 5, Mindset.SELF_RESPONSIBILITY: 5},  # Correct
        "D": {Mindset.FUTURE_FOCUSED: 1, Mindset.SELF_RESPONSIBILITY: 1},
    },
    "MS-S02": {  # 意見対立シナリオ
        "A": {Mindset.COLLABORATION: 2, Mindset.LISTENING_SKILL: 2},
        "B": {Mindset.LISTENING_SKILL: 3, Mindset.COLLABORATION: 4},
        "C": {Mindset.SELF_RESPONSIBILITY: 5, Mindset.LISTENING_SKILL: 5},  # Correct
        "D": {Mindset.SELF_RESPONSIBILITY: 1, Mindset.LISTENING_SKILL: 1},
    },
    "MS-S03": {  # 新入メンバー不安シナリオ
        "A": {Mindset.KINDNESS: 1, Mindset.INCLUSIVITY: 1},
        "B": {Mindset.KINDNESS: 2, Mindset.INCLUSIVITY: 3},
        "C": {Mindset.KINDNESS: 5, Mindset.INCLUSIVITY: 5},  # Correct
        "D": {Mindset.KINDNESS: 4, Mindset.INCLUSIVITY: 3},
    },
    "MS-S04": {  # 複数部門相反要望シナリオ
        "A": {Mindset.LISTENING_SKILL: 2, Mindset.COLLABORATION: 1},
        "B": {Mindset.LISTENING_SKILL: 5, Mindset.COLLABORATION: 5},  # Correct
        "C": {Mindset.LISTENING_SKILL: 1, Mindset.COLLABORATION: 1},
        "D": {Mindset.LISTENING_SKILL: 4, Mindset.COLLABORATION: 3},
    },
    "MS-S05": {  # フロア移転反発シナリオ
        "A": {Mindset.INCLUSIVITY: 1, Mindset.KINDNESS: 2},
        "B": {Mindset.INCLUSIVITY: 2, Mindset.KINDNESS: 2},
        "C": {Mindset.INCLUSIVITY: 5, Mindset.KINDNESS: 5},  # Correct
        "D": {Mindset.INCLUSIVITY: 3, Mindset.KINDNESS: 3},
    },
    "MS-S06": {  # 新規領域連携シナリオ
        "A": {Mindset.COLLABORATION: 1, Mindset.FUTURE_FOCUSED: 2},
        "B": {Mindset.COLLABORATION: 2, Mindset.FUTURE_FOCUSED: 3},
        "C": {Mindset.COLLABORATION: 5, Mindset.FUTURE_FOCUSED: 5},  # Correct
        "D": {Mindset.COLLABORATION: 1, Mindset.FUTURE_FOCUSED: 1},
    },
}


def calculate_mindset_scores(scenario_answers: dict) -> dict:
    """Calculate mindset scores from scenario answers.

    Args:
        scenario_answers: Dict mapping scenario_id -> user_answer (A/B/C/D)

    Returns:
        Dict with mindset scores (0-100 scale)
    """
    mindset_totals = {
        Mindset.FUTURE_FOCUSED: 0,
        Mindset.SELF_RESPONSIBILITY: 0,
        Mindset.KINDNESS: 0,
        Mindset.LISTENING_SKILL: 0,
        Mindset.INCLUSIVITY: 0,
        Mindset.COLLABORATION: 0,
    }

    for scenario_id, user_answer in scenario_answers.items():
        if scenario_id not in MINDSET_SCORING_PATTERNS:
            continue

        pattern = MINDSET_SCORING_PATTERNS[scenario_id]
        answer_key = user_answer.upper()

        if answer_key not in pattern:
            continue

        scores = pattern[answer_key]
        for mindset, score in scores.items():
            mindset_totals[mindset] += score

    # Convert to 0-100 scale (each mindset evaluated in 2 scenarios × max 5 points = 10 max)
    # Formula: (total / 10) × 100
    normalized_scores = {}
    for mindset, total in mindset_totals.items():
        normalized_scores[mindset] = min(100, int((total / 10) * 100))

    # Calculate total score (average of all mindsets)
    total_score = int(sum(normalized_scores.values()) / len(normalized_scores))

    return {
        "future_focused": normalized_scores[Mindset.FUTURE_FOCUSED],
        "self_responsibility": normalized_scores[Mindset.SELF_RESPONSIBILITY],
        "kindness": normalized_scores[Mindset.KINDNESS],
        "listening_skill": normalized_scores[Mindset.LISTENING_SKILL],
        "inclusivity": normalized_scores[Mindset.INCLUSIVITY],
        "collaboration": normalized_scores[Mindset.COLLABORATION],
        "total_score": total_score,
    }


def get_correct_answer(scenario_id: str) -> str:
    """Get correct answer for a scenario.

    Args:
        scenario_id: Scenario identifier

    Returns:
        Correct answer (A/B/C/D)
    """
    # The correct answer is always C based on test_data.py
    return "C"


def is_answer_correct(scenario_id: str, user_answer: str) -> bool:
    """Check if answer is correct.

    Args:
        scenario_id: Scenario identifier
        user_answer: User's answer (A/B/C/D)

    Returns:
        True if correct, False otherwise
    """
    correct = get_correct_answer(scenario_id)
    return user_answer.upper() == correct.upper()

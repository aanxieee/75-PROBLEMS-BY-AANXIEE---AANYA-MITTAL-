"""
SM-2 Spaced Repetition Algorithm
Based on the SuperMemo SM-2 algorithm by Piotr Wozniak (1987).

Quality ratings (0-5):
  5 - Perfect response
  4 - Correct response after a hesitation
  3 - Correct response recalled with serious difficulty
  2 - Incorrect response; where the correct one seemed easy to recall
  1 - Incorrect response; the correct one remembered
  0 - Complete blackout

Reference: https://www.supermemo.com/en/blog/application-of-a-computer-to-improve-the-results-obtained-in-working-with-the-supermemo-method
"""

from datetime import datetime, timedelta


def update_srs(word_data: dict, quality: int) -> dict:
    """
    Update SRS metadata for a word based on recall quality.

    Args:
        word_data: dict containing 'interval', 'repetitions', 'ease_factor', 'next_review'
        quality: int 0-5 representing recall quality

    Returns:
        Updated word_data dict with new SRS values
    """
    # Extract current SRS values (with defaults for new words)
    repetitions = word_data.get("repetitions", 0)
    ease_factor = word_data.get("ease_factor", 2.5)
    interval = word_data.get("interval", 1)

    if quality < 3:
        # Failed recall: reset repetitions, review tomorrow
        repetitions = 0
        interval = 1
    else:
        # Successful recall: increase interval
        if repetitions == 0:
            interval = 1
        elif repetitions == 1:
            interval = 6
        else:
            interval = round(interval * ease_factor)

        repetitions += 1

    # Update ease factor (always, regardless of quality)
    ease_factor = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))

    # Clamp ease factor: minimum 1.3
    ease_factor = max(1.3, ease_factor)

    # Set next review date
    next_review = (datetime.now() + timedelta(days=interval)).strftime("%Y-%m-%d")

    word_data["repetitions"] = repetitions
    word_data["ease_factor"] = round(ease_factor, 4)
    word_data["interval"] = interval
    word_data["next_review"] = next_review
    word_data["last_reviewed"] = datetime.now().strftime("%Y-%m-%d")
    word_data["last_quality"] = quality

    return word_data


def is_due(word_data: dict) -> bool:
    """Check if a word is due for review today or overdue."""
    next_review = word_data.get("next_review")
    if not next_review:
        return True
    today = datetime.now().strftime("%Y-%m-%d")
    return next_review <= today


def new_word_srs() -> dict:
    """Return default SRS metadata for a brand new word."""
    return {
        "repetitions": 0,
        "ease_factor": 2.5,
        "interval": 1,
        "next_review": datetime.now().strftime("%Y-%m-%d"),
        "last_reviewed": None,
        "last_quality": None,
    }

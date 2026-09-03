"""
Pay-scale lookups and Section 5 step-matching (New Basic Salary determination).

Section 5 rule (paraphrased from the gazette):
(a) If the employee's current basic exactly matches the starting step of the
    old scale, the new basic is the starting step of the new scale.
(b) Otherwise, find the difference between the current basic and the nearest
    lower step of the old scale; add that difference to the corresponding
    step of the new scale.
    - If the result matches a step of the new scale exactly, that is the
      new basic.
    - If it falls between two steps, the next HIGHER step of the new scale
      is used.
"""
from data.salary_rules import GRADE_SCALES, SPECIAL_FIXED_PAY


def get_special_fixed_pay(post_key: str) -> float:
    """Section 1(2): Cabinet/Chief Secretary and Senior Secretary are not
    on the graded scale — their new pay is a fixed amount."""
    if post_key not in SPECIAL_FIXED_PAY:
        raise ValueError(f"Unknown special post: {post_key}")
    return float(SPECIAL_FIXED_PAY[post_key])


def get_scales(grade: int):
    if grade not in GRADE_SCALES:
        raise ValueError(f"Unknown grade: {grade}")
    return GRADE_SCALES[grade]


def get_available_grades():
    return sorted(GRADE_SCALES.keys())


def validate_basic(grade: int, basic: float):
    """Returns (is_valid, message, min_value, max_value)."""
    scale = get_scales(grade)["old"]
    lo, hi = scale[0], scale[-1]
    if basic is None or basic <= 0:
        return False, "Please enter a basic salary.", lo, hi
    if basic < lo or basic > hi:
        return False, f"Basic salary for this grade should be between {lo:,.0f} and {hi:,.0f} (as per the 2015 scale).", lo, hi
    return True, "", lo, hi


def determine_new_basic(grade: int, old_basic: float) -> float:
    """Full (100%) new basic salary per Section 5, before phasing."""
    scales = get_scales(grade)
    old_scale, new_scale = scales["old"], scales["new"]

    if len(old_scale) == 1:  # fixed-pay grade (e.g. Grade 1)
        return float(new_scale[0])

    # Find index of the nearest lower-or-equal step in the old scale
    idx = 0
    for i, val in enumerate(old_scale):
        if val <= old_basic:
            idx = i
        else:
            break

    diff = old_basic - old_scale[idx]
    new_idx = min(idx, len(new_scale) - 1)
    target = new_scale[new_idx] + diff

    if target in new_scale:
        return float(target)

    higher_steps = [v for v in new_scale if v > target]
    if higher_steps:
        return float(min(higher_steps))
    return float(new_scale[-1])

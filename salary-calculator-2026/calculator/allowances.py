"""
Each function computes ONE allowance and returns:
    (amount: float, applicable: bool, explanation_key: str, formula_values: dict)

Nothing here assumes an allowance applies by default — every allowance has an
explicit eligibility condition drawn from the gazette clause noted in the
docstring.
"""
from data import salary_rules as R


def house_rent(new_basic: float, location: str, in_government_housing: bool):
    """Section 17(1),(2),(7). Not payable if living in government housing."""
    if in_government_housing:
        return 0.0, False, "house_rent_govt_housing", {}

    for lo, hi, rates in R.HOUSE_RENT_TABLE:
        if lo <= new_basic <= hi:
            percent, minimum = rates[location]
            amount = max(new_basic * percent, minimum)
            return amount, True, "house_rent", {
                "basic": new_basic, "percent": percent * 100, "minimum": minimum, "amount": amount
            }
    return 0.0, False, "house_rent_no_band", {}


def medical_allowance():
    """Section 15(1) — flat monthly rate for all in-service employees."""
    amount = R.MEDICAL_ALLOWANCE_MONTHLY
    return float(amount), True, "medical", {"amount": amount}


def tiffin_allowance(grade: int, has_canteen_or_free_lunch: bool):
    """Section 21 — Grade 11-20 only, unless canteen/free lunch provided."""
    if grade in R.TIFFIN_ELIGIBLE_GRADES and not has_canteen_or_free_lunch:
        amount = R.TIFFIN_ALLOWANCE_MONTHLY
        return float(amount), True, "tiffin", {"amount": amount}
    return 0.0, False, "tiffin_not_eligible", {}


def transport_allowance(grade: int, in_city_corporation_area: bool):
    """Section 23(1) — Grade 11-20, workplace in a City Corporation area."""
    if grade in R.TRANSPORT_ELIGIBLE_GRADES and in_city_corporation_area:
        amount = R.TRANSPORT_ALLOWANCE_MONTHLY
        return float(amount), True, "transport", {"amount": amount}
    return 0.0, False, "transport_not_eligible", {}


def washing_allowance(eligible: bool):
    """Section 24 — applicable only where the employer designates it applicable."""
    if eligible:
        amount = R.WASHING_ALLOWANCE_MONTHLY
        return float(amount), True, "washing", {"amount": amount}
    return 0.0, False, "washing_not_eligible", {}


def charge_allowance(new_basic: float, on_additional_charge: bool):
    """Section 22 — 10% of basic, capped, only while holding additional charge."""
    if on_additional_charge:
        amount = min(new_basic * R.CHARGE_ALLOWANCE_PERCENT, R.CHARGE_ALLOWANCE_MAX_MONTHLY)
        return float(amount), True, "charge", {
            "basic": new_basic, "percent": R.CHARGE_ALLOWANCE_PERCENT * 100,
            "cap": R.CHARGE_ALLOWANCE_MAX_MONTHLY, "amount": amount
        }
    return 0.0, False, "charge_not_eligible", {}


def domestic_aid_allowance(prescribed_eligible: bool):
    """Section 26 — only for officially prescribed ('প্রাধিকারভুক্ত') employees."""
    if prescribed_eligible:
        amount = R.DOMESTIC_AID_ALLOWANCE_MONTHLY
        return float(amount), True, "domestic_aid", {"amount": amount}
    return 0.0, False, "domestic_aid_not_eligible", {}


def hill_allowance(new_basic: float, hill_area: str):
    """Section 27. hill_area in {'none','sadar','other_upazila'}."""
    if hill_area not in ("sadar", "other_upazila"):
        return 0.0, False, "hill_not_eligible", {}
    cap = R.HILL_ALLOWANCE_MAX[hill_area]
    amount = min(new_basic * R.HILL_ALLOWANCE_PERCENT, cap)
    return float(amount), True, "hill", {
        "basic": new_basic, "percent": R.HILL_ALLOWANCE_PERCENT * 100, "cap": cap, "amount": amount
    }


def education_assistance(children_count: int):
    """Section 20 — Tk 1000/child up to 2 children, capped at Tk 2000/month."""
    if children_count <= 0:
        return 0.0, False, "education_not_eligible", {}
    counted = min(children_count, R.EDUCATION_ASSISTANCE_MAX_CHILDREN)
    amount = min(counted * R.EDUCATION_ASSISTANCE_PER_CHILD, R.EDUCATION_ASSISTANCE_MAX_MONTHLY)
    return float(amount), True, "education", {
        "children_counted": counted, "per_child": R.EDUCATION_ASSISTANCE_PER_CHILD, "amount": amount
    }


def entertainment_allowance(level: str):
    """Section 25 — post-based fixed monthly amount."""
    amount = R.ENTERTAINMENT_ALLOWANCE.get(level, 0)
    if amount > 0:
        return float(amount), True, "entertainment", {"amount": amount, "level": level}
    return 0.0, False, "entertainment_not_eligible", {}


def bangla_new_year_allowance(new_basic: float):
    """Section 16 — 20% of basic, paid ONCE yearly. Shown separately, not
    included in the monthly gross salary."""
    amount = new_basic * R.BANGLA_NEW_YEAR_PERCENT_OF_BASIC
    return float(amount), True, "bangla_new_year", {
        "basic": new_basic, "percent": R.BANGLA_NEW_YEAR_PERCENT_OF_BASIC * 100, "amount": amount
    }

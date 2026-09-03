"""
Main calculation engine. Pure functions only — no UI code here.
"""
from dataclasses import dataclass, field
from typing import Optional

from calculator import pay_scale, allowances, deductions
from data.salary_rules import STAGE_FRACTIONS


@dataclass
class CalculatorInput:
    grade: int
    old_basic: float
    stage: str                      # key into STAGE_FRACTIONS
    gpf_percent: float
    location: str                   # 'dhaka' | 'other_metro' | 'other'
    special_post: str = "none"      # 'none' | 'cabinet_or_chief_secretary' | 'senior_secretary' (Section 1(2))
    in_government_housing: bool = False
    has_canteen_or_free_lunch: bool = False
    in_city_corporation_area: bool = False
    washing_eligible: bool = False
    on_additional_charge: bool = False
    domestic_aid_eligible: bool = False
    hill_area: str = "none"         # 'none' | 'sadar' | 'other_upazila'
    children_count: int = 0
    entertainment_level: str = "none"


@dataclass
class CalculatorResult:
    inputs: CalculatorInput
    old_basic: float
    full_new_basic: float           # 100% new-scale basic (Section 5)
    stage_fraction: float
    stage_label_en: str
    stage_label_bn: str
    new_basic_effective: float      # basic actually payable at chosen stage

    old_allowances_total: float
    new_allowances_total: float
    allowance_lines: list           # list of dicts: name_key, old, new, applicable

    old_gross: float
    new_gross: float
    gross_increase: float
    gross_increase_percent: float

    gpf_amount: float
    total_deductions: float
    net_salary: float

    bangla_new_year_amount: float   # annual, shown separately

    calc_notes: list = field(default_factory=list)


def _old_allowance_estimate(grade: int, old_basic: float, inp: CalculatorInput):
    """
    Best-effort 'previous' (pre-2026, under the 2015 order) allowance total,
    using only the allowance rules this gazette explicitly carries forward
    or references as pre-existing (medical, house rent structure, tiffin,
    transport). Amounts that are NEW to the 2026 order (e.g. revised flat
    rates) are estimated using the same eligibility rules for a fair
    before/after comparison; this is clearly labeled as an estimate.
    """
    hr_amt, hr_ok, _, _ = allowances.house_rent(old_basic, inp.location, inp.in_government_housing)
    med_amt, med_ok, _, _ = allowances.medical_allowance()
    tif_amt, tif_ok, _, _ = allowances.tiffin_allowance(grade, inp.has_canteen_or_free_lunch)
    tr_amt, tr_ok, _, _ = allowances.transport_allowance(grade, inp.in_city_corporation_area)
    total = (hr_amt if hr_ok else 0) + (med_amt if med_ok else 0) + \
            (tif_amt if tif_ok else 0) + (tr_amt if tr_ok else 0)
    return total


def calculate(inp: CalculatorInput) -> CalculatorResult:
    notes = []

    if inp.special_post != "none":
        # Section 1(2): fixed-pay posts, not on the graded scale. Grade-11-20
        # -only allowances (tiffin/transport) correctly do not apply — use a
        # sentinel grade that matches no eligibility set.
        if inp.old_basic is None or inp.old_basic <= 0:
            raise ValueError("Please enter the current basic salary.")
        full_new_basic = pay_scale.get_special_fixed_pay(inp.special_post)
        allowance_grade = -1
        notes.append("special_fixed_pay_post")
    else:
        valid, msg, lo, hi = pay_scale.validate_basic(inp.grade, inp.old_basic)
        if not valid:
            raise ValueError(msg)
        full_new_basic = pay_scale.determine_new_basic(inp.grade, inp.old_basic)
        allowance_grade = inp.grade

    stage_info = STAGE_FRACTIONS[inp.stage]
    fraction = stage_info["fraction"]
    if inp.stage == "stage4":
        notes.append("stage4_not_defined")

    increase = full_new_basic - inp.old_basic
    new_basic_effective = inp.old_basic + fraction * increase

    # --- New allowances (computed on the effective new basic) ---
    lines = []

    def add_line(key, old_val, new_val, applicable):
        lines.append({"key": key, "old": old_val, "new": new_val, "applicable": applicable})

    hr_new, hr_ok, hr_key, hr_vals = allowances.house_rent(new_basic_effective, inp.location, inp.in_government_housing)
    hr_old, _, _, _ = allowances.house_rent(inp.old_basic, inp.location, inp.in_government_housing)
    add_line("house_rent", hr_old if hr_ok else 0, hr_new if hr_ok else 0, hr_ok)

    med_new, med_ok, _, _ = allowances.medical_allowance()
    add_line("medical", med_new if med_ok else 0, med_new if med_ok else 0, med_ok)

    tif_new, tif_ok, _, _ = allowances.tiffin_allowance(allowance_grade, inp.has_canteen_or_free_lunch)
    add_line("tiffin", tif_new if tif_ok else 0, tif_new if tif_ok else 0, tif_ok)

    tr_new, tr_ok, _, _ = allowances.transport_allowance(allowance_grade, inp.in_city_corporation_area)
    add_line("transport", tr_new if tr_ok else 0, tr_new if tr_ok else 0, tr_ok)

    wash_new, wash_ok, _, _ = allowances.washing_allowance(inp.washing_eligible)
    add_line("washing", wash_new if wash_ok else 0, wash_new if wash_ok else 0, wash_ok)

    charge_new, charge_ok, _, _ = allowances.charge_allowance(new_basic_effective, inp.on_additional_charge)
    charge_old, _, _, _ = allowances.charge_allowance(inp.old_basic, inp.on_additional_charge)
    add_line("charge", charge_old if charge_ok else 0, charge_new if charge_ok else 0, charge_ok)

    dom_new, dom_ok, _, _ = allowances.domestic_aid_allowance(inp.domestic_aid_eligible)
    add_line("domestic_aid", dom_new if dom_ok else 0, dom_new if dom_ok else 0, dom_ok)

    hill_new, hill_ok, _, _ = allowances.hill_allowance(new_basic_effective, inp.hill_area)
    hill_old, _, _, _ = allowances.hill_allowance(inp.old_basic, inp.hill_area)
    add_line("hill", hill_old if hill_ok else 0, hill_new if hill_ok else 0, hill_ok)

    edu_new, edu_ok, _, _ = allowances.education_assistance(inp.children_count)
    add_line("education", edu_new if edu_ok else 0, edu_new if edu_ok else 0, edu_ok)

    ent_new, ent_ok, _, _ = allowances.entertainment_allowance(inp.entertainment_level)
    add_line("entertainment", ent_new if ent_ok else 0, ent_new if ent_ok else 0, ent_ok)

    new_allowances_total = sum(l["new"] for l in lines if l["applicable"])
    old_allowances_total = sum(l["old"] for l in lines if l["applicable"])

    old_gross = inp.old_basic + old_allowances_total
    new_gross = new_basic_effective + new_allowances_total
    gross_increase = new_gross - old_gross
    gross_increase_percent = (gross_increase / old_gross * 100.0) if old_gross > 0 else 0.0

    gpf_amount, _ = deductions.gpf_contribution(new_basic_effective, inp.gpf_percent)
    total_deductions = gpf_amount
    net_salary = new_gross - total_deductions

    bny_amount, _, _, _ = allowances.bangla_new_year_allowance(new_basic_effective)

    return CalculatorResult(
        inputs=inp,
        old_basic=inp.old_basic,
        full_new_basic=full_new_basic,
        stage_fraction=fraction,
        stage_label_en=stage_info["label_en"],
        stage_label_bn=stage_info["label_bn"],
        new_basic_effective=new_basic_effective,
        old_allowances_total=old_allowances_total,
        new_allowances_total=new_allowances_total,
        allowance_lines=lines,
        old_gross=old_gross,
        new_gross=new_gross,
        gross_increase=gross_increase,
        gross_increase_percent=gross_increase_percent,
        gpf_amount=gpf_amount,
        total_deductions=total_deductions,
        net_salary=net_salary,
        bangla_new_year_amount=bny_amount,
        calc_notes=notes,
    )

"""
Run with:  python -m pytest tests/ -v
(or simply: python tests/test_salary_calculator.py)
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from calculator import pay_scale
from calculator.salary_calculator import CalculatorInput, calculate
from pdf.report_generator import build_pdf


def test_grade1_fixed_pay():
    new_basic = pay_scale.determine_new_basic(1, 78000)
    assert new_basic == 156000


def test_grade9_starting_step():
    new_basic = pay_scale.determine_new_basic(9, 22000)
    assert new_basic == 45100


def test_grade9_mid_step_matches_exact():
    new_basic = pay_scale.determine_new_basic(9, 23100)
    assert new_basic == 47355


def test_validate_basic_out_of_range():
    valid, msg, lo, hi = pay_scale.validate_basic(9, 1000)
    assert not valid


def test_validate_basic_in_range():
    valid, msg, lo, hi = pay_scale.validate_basic(9, 22000)
    assert valid


def test_stage_fractions():
    inp1 = CalculatorInput(grade=9, old_basic=22000, stage="stage1", gpf_percent=10, location="dhaka")
    inp3 = CalculatorInput(grade=9, old_basic=22000, stage="stage3", gpf_percent=10, location="dhaka")
    r1 = calculate(inp1)
    r3 = calculate(inp3)
    assert r1.new_basic_effective < r3.new_basic_effective
    assert r3.new_basic_effective == r3.full_new_basic


def test_house_rent_govt_housing_excluded():
    inp = CalculatorInput(grade=9, old_basic=22000, stage="stage3", gpf_percent=10,
                           location="dhaka", in_government_housing=True)
    r = calculate(inp)
    hr_lines = [l for l in r.allowance_lines if l["key"] == "house_rent"]
    assert hr_lines[0]["applicable"] is False


def test_gross_and_net_relationship():
    inp = CalculatorInput(grade=9, old_basic=22000, stage="stage3", gpf_percent=10, location="dhaka")
    r = calculate(inp)
    assert r.net_salary == r.new_gross - r.total_deductions
    assert r.gross_increase == r.new_gross - r.old_gross


def test_tiffin_only_grade_11_20():
    inp8 = CalculatorInput(grade=8, old_basic=23000, stage="stage3", gpf_percent=10, location="dhaka")
    inp15 = CalculatorInput(grade=15, old_basic=9700, stage="stage3", gpf_percent=10, location="dhaka")
    r8 = calculate(inp8)
    r15 = calculate(inp15)
    tif8 = [l for l in r8.allowance_lines if l["key"] == "tiffin"][0]
    tif15 = [l for l in r15.allowance_lines if l["key"] == "tiffin"][0]
    assert tif8["applicable"] is False
    assert tif15["applicable"] is True


def test_gpf_percent_choices():
    for pct in (5, 10, 15, 20):
        inp = CalculatorInput(grade=9, old_basic=22000, stage="stage3", gpf_percent=pct, location="dhaka")
        r = calculate(inp)
        assert round(r.gpf_amount, 2) == round(r.new_basic_effective * pct / 100, 2)


def test_all_grades_calculate_without_error():
    for g in pay_scale.get_available_grades():
        lo = pay_scale.get_scales(g)["old"][0]
        inp = CalculatorInput(grade=g, old_basic=lo, stage="stage3", gpf_percent=10, location="other")
        r = calculate(inp)
        assert r.new_gross > 0


def test_pdf_generation_en():
    inp = CalculatorInput(grade=9, old_basic=22000, stage="stage3", gpf_percent=10, location="dhaka")
    r = calculate(inp)
    pdf_bytes = build_pdf(r, "en")
    assert pdf_bytes[:4] == b"%PDF"


def test_pdf_generation_bn():
    inp = CalculatorInput(grade=9, old_basic=22000, stage="stage3", gpf_percent=10, location="dhaka")
    r = calculate(inp)
    pdf_bytes = build_pdf(r, "bn")
    assert pdf_bytes[:4] == b"%PDF"


def test_special_fixed_pay_post_cabinet_secretary():
    inp = CalculatorInput(grade=1, old_basic=100000, stage="stage3", gpf_percent=10,
                           location="dhaka", special_post="cabinet_or_chief_secretary")
    r = calculate(inp)
    assert r.full_new_basic == 170000
    assert r.new_basic_effective == 170000  # stage3 = 100%
    # Tiffin/Transport are Grade 11-20 only and must not apply to a fixed-pay post
    tif = [l for l in r.allowance_lines if l["key"] == "tiffin"][0]
    assert tif["applicable"] is False


def test_special_fixed_pay_post_senior_secretary_phased():
    inp = CalculatorInput(grade=1, old_basic=100000, stage="stage1", gpf_percent=10,
                           location="dhaka", special_post="senior_secretary")
    r = calculate(inp)
    assert r.full_new_basic == 160000
    expected = 100000 + 0.30 * (160000 - 100000)
    assert round(r.new_basic_effective, 2) == round(expected, 2)


if __name__ == "__main__":
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
    passed, failed = 0, 0
    for fn in tests:
        try:
            fn()
            print(f"PASS: {fn.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"FAIL: {fn.__name__} -> {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")

"""
Section 9: GPF (General Provident Fund) contribution.
Percentage is the employee's own choice/subscription rate; base is the
employee's basic salary.

Income tax (Section 33) is explicitly NOT calculated here — the gazette
gives no formula, only a general obligation to self-assess and file returns.
"""


def gpf_contribution(basic: float, gpf_percent: float):
    amount = basic * (gpf_percent / 100.0)
    return float(amount), {"basic": basic, "percent": gpf_percent, "amount": amount}

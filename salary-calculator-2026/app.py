import base64

import streamlit as st

from calculator import pay_scale
from calculator.salary_calculator import CalculatorInput, calculate
from data.salary_rules import (
    STAGE_FRACTIONS, HOUSE_RENT_LOCATIONS, GPF_PERCENT_CHOICES, ENTERTAINMENT_ALLOWANCE,
    SPECIAL_POST_LABELS, OUT_OF_SCOPE_NOTES, SPECIAL_FIXED_PAY,
)
from ui.translations import t, allowance_name
from ui.components import fmt_money, fmt_percent
from pdf.report_generator import build_pdf

st.set_page_config(page_title="BD Govt Salary Calculator 2026", page_icon="🇧🇩", layout="wide")

if "lang" not in st.session_state:
    st.session_state.lang = "en"
if "result" not in st.session_state:
    st.session_state.result = None
if "pdf_bytes" not in st.session_state:
    st.session_state.pdf_bytes = None


def L(key):
    return t(st.session_state.lang, key)


# ---------------- Header ----------------
col_title, col_lang = st.columns([5, 1])
with col_title:
    st.title(L("app_title"))
    st.caption(L("app_subtitle"))
with col_lang:
    if st.button(L("lang_switch"), use_container_width=True):
        st.session_state.lang = "bn" if st.session_state.lang == "en" else "en"
        st.rerun()

with st.expander(L("help_button")):
    st.write(L("not_official"))
    st.write(L("disclaimer"))

st.divider()

# ---------------- Input form ----------------
st.subheader(L("salary_information"))

grades = pay_scale.get_available_grades()


def _grade_label(g):
    scale = pay_scale.get_scales(g)["old"]
    return f"Grade {g} — Tk {fmt_money(scale[0])}–{fmt_money(scale[-1])}"


special_post = st.selectbox(
    "Special Fixed-Pay Post (Section 1(2))" if st.session_state.lang == "en" else "বিশেষ নির্ধারিত-বেতন পদ (ধারা ১(২))",
    list(SPECIAL_POST_LABELS.keys()),
    format_func=lambda k: SPECIAL_POST_LABELS[k][st.session_state.lang],
    key="special_post",
)
is_special = special_post != "none"
if is_special:
    st.info(
        f"{'Fixed new basic salary' if st.session_state.lang=='en' else 'নির্ধারিত নতুন মূল বেতন'}: "
        f"৳ {fmt_money(SPECIAL_FIXED_PAY[special_post])}. "
        f"{'Grade selection below is ignored for this post.' if st.session_state.lang=='en' else 'এই পদের জন্য নিচের গ্রেড নির্বাচন উপেক্ষা করা হবে।'}"
    )

c1, c2, c3 = st.columns(3)
with c1:
    grade = st.selectbox(L("grade"), grades, index=grades.index(9) if 9 in grades else 0,
                          format_func=_grade_label, key="grade", disabled=is_special)

_, _, lo, hi = pay_scale.validate_basic(grade, pay_scale.get_scales(grade)["old"][0])
with c2:
    old_basic = st.number_input(L("current_basic_salary"), min_value=0.0,
                                 value=float(lo), step=100.0, key="old_basic")
    if is_special:
        st.caption("Enter your current fixed basic salary under the 2015 order."
                    if st.session_state.lang == "en" else
                    "২০১৫ সালের আদেশ অনুযায়ী আপনার বর্তমান নির্ধারিত মূল বেতন প্রদান করুন।")
    else:
        st.caption(f"{L('allowed_range')}: {fmt_money(lo)} – {fmt_money(hi)}")
with c3:
    stage_keys = list(STAGE_FRACTIONS.keys())
    stage_labels = [
        (f"{STAGE_FRACTIONS[k]['label_bn']} — {STAGE_FRACTIONS[k]['fraction']*100:.0f}%"
         if st.session_state.lang == "bn"
         else f"{STAGE_FRACTIONS[k]['label_en']} — {STAGE_FRACTIONS[k]['fraction']*100:.0f}% implemented")
        for k in stage_keys
    ]
    stage_idx = st.selectbox(L("stage"), range(len(stage_keys)), format_func=lambda i: stage_labels[i], key="stage_idx")
    stage = stage_keys[stage_idx]
    _stage_pct = STAGE_FRACTIONS[stage]["fraction"] * 100
    st.caption(
        f"{_stage_pct:.0f}% of the basic-salary increase is paid at this stage."
        if st.session_state.lang == "en" else
        f"এই পর্যায়ে মূল বেতন বৃদ্ধির {_stage_pct:.0f}% প্রদান করা হয়।"
    )
    if stage == "stage4":
        st.warning(L("stage4_warning"))

c4, c5 = st.columns(2)
with c4:
    gpf_percent = st.selectbox(L("gpf_percent"), GPF_PERCENT_CHOICES, index=1, key="gpf_percent")
    st.caption(L("gpf_formula"))
    try:
        if is_special:
            _preview_full_new_basic = SPECIAL_FIXED_PAY[special_post]
        else:
            _preview_full_new_basic = pay_scale.determine_new_basic(grade, old_basic)
        _preview_fraction = STAGE_FRACTIONS[stage_keys[st.session_state.stage_idx]]["fraction"]
        _preview_basic = old_basic + _preview_fraction * (_preview_full_new_basic - old_basic)
        _preview_gpf = _preview_basic * (gpf_percent / 100.0)
        st.info(f"{L('gpf_percent')} {gpf_percent}% → ৳ {fmt_money(_preview_basic)} × {gpf_percent}% "
                f"= **৳ {fmt_money(_preview_gpf)}**")
    except Exception:
        pass
with c5:
    loc_labels = {"dhaka": L("loc_dhaka"), "other_metro": L("loc_other_metro"), "other": L("loc_other")}
    location = st.selectbox(L("location"), HOUSE_RENT_LOCATIONS, format_func=lambda k: loc_labels[k], key="location")
    st.caption(L("house_rent_help"))

govt_housing = st.checkbox(L("govt_housing"), value=False, key="govt_housing")

with st.expander(L("other_eligibility")):
    e1, e2 = st.columns(2)
    with e1:
        canteen = st.checkbox(L("canteen_free_lunch"), value=False, key="canteen")
        city_corp = st.checkbox(L("city_corp_area"), value=False, key="city_corp")
        washing = st.checkbox(L("washing_eligible"), value=False, key="washing")
        additional_charge = st.checkbox(L("additional_charge"), value=False, key="additional_charge")
        domestic_aid = st.checkbox(L("domestic_aid"), value=False, key="domestic_aid")
    with e2:
        hill_labels = {"none": L("hill_none"), "sadar": L("hill_sadar"), "other_upazila": L("hill_other")}
        hill_area = st.selectbox(L("hill_area"), list(hill_labels.keys()), format_func=lambda k: hill_labels[k], key="hill_area")
        children_count = st.number_input(L("children_count"), min_value=0, max_value=10, value=0, step=1, key="children_count")
        ent_labels = {
            "none": L("ent_none"),
            "joint_secretary_or_equivalent": L("ent_joint"),
            "additional_secretary": L("ent_additional"),
            "senior_secretary_or_secretary": L("ent_senior"),
            "cabinet_or_chief_secretary": L("ent_cabinet"),
        }
        entertainment_level = st.selectbox(L("entertainment_level"), list(ent_labels.keys()),
                                            format_func=lambda k: ent_labels[k], key="entertainment_level")

b1, b2 = st.columns([1, 1])
calc_clicked = b1.button(L("calculate_button"), type="primary", use_container_width=True)
reset_clicked = b2.button(L("reset_button"), use_container_width=True)

INPUT_WIDGET_KEYS = [
    "grade", "old_basic", "stage_idx", "gpf_percent", "location", "govt_housing",
    "canteen", "city_corp", "washing", "additional_charge", "domestic_aid",
    "hill_area", "children_count", "entertainment_level", "special_post",
]

if reset_clicked:
    for k in INPUT_WIDGET_KEYS:
        st.session_state.pop(k, None)
    st.session_state.result = None
    st.session_state.pdf_bytes = None
    st.rerun()

if calc_clicked:
    st.session_state.pdf_bytes = None
    try:
        inp = CalculatorInput(
            grade=grade, old_basic=old_basic, stage=stage, gpf_percent=gpf_percent,
            location=location, special_post=special_post, in_government_housing=govt_housing,
            has_canteen_or_free_lunch=canteen, in_city_corporation_area=city_corp,
            washing_eligible=washing, on_additional_charge=additional_charge,
            domestic_aid_eligible=domestic_aid, hill_area=hill_area,
            children_count=int(children_count), entertainment_level=entertainment_level,
        )
        st.session_state.result = calculate(inp)
    except ValueError as e:
        st.error(str(e))
    except Exception:
        st.error(L("error_generic"))

# ---------------- Results ----------------
result = st.session_state.result
if result:
    st.divider()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric(L("previous_gross"), f"৳ {fmt_money(result.old_gross)}")
    m2.metric(L("new_gross"), f"৳ {fmt_money(result.new_gross)}")
    m3.metric(L("increase"), f"+৳ {fmt_money(result.gross_increase)}")
    m4.metric(L("increase_percent"), f"+{fmt_percent(result.gross_increase_percent)}")

    st.subheader(L("breakdown_title"))
    rows = [{
        L("component"): L("basic_salary"),
        L("previous"): fmt_money(result.old_basic),
        L("new"): fmt_money(result.new_basic_effective),
        L("difference"): fmt_money(result.new_basic_effective - result.old_basic),
    }]
    for line in result.allowance_lines:
        if not line["applicable"]:
            continue
        rows.append({
            L("component"): allowance_name(st.session_state.lang, line["key"]),
            L("previous"): fmt_money(line["old"]),
            L("new"): fmt_money(line["new"]),
            L("difference"): fmt_money(line["new"] - line["old"]),
        })
    rows.append({
        L("component"): f"**{L('gross_salary')}**",
        L("previous"): f"**{fmt_money(result.old_gross)}**",
        L("new"): f"**{fmt_money(result.new_gross)}**",
        L("difference"): f"**{fmt_money(result.gross_increase)}**",
    })
    st.table(rows)

    st.subheader(L("deductions_title"))
    st.table([
        {L("deduction"): "GPF", L("amount"): fmt_money(result.gpf_amount)},
        {L("deduction"): f"**{L('total_deduction')}**", L("amount"): f"**{fmt_money(result.total_deductions)}**"},
    ])

    st.success(f"**{L('net_salary')}: ৳ {fmt_money(result.net_salary)}**")
    st.caption(L("net_formula"))

    with st.expander(L("annual_allowances_title")):
        st.write(f"{L('bangla_new_year')}: ৳ {fmt_money(result.bangla_new_year_amount)}")

    with st.expander(L("full_calc_title")):
        lang = st.session_state.lang
        st.markdown(f"**1. {L('basic_salary')}**")
        st.write(f"{L('previous')}: ৳{fmt_money(result.old_basic)} → "
                 f"{'Full new-scale basic' if lang=='en' else 'সম্পূর্ণ নতুন স্কেল মূল বেতন'}: ৳{fmt_money(result.full_new_basic)}")
        st.write(f"{result.stage_label_bn if lang=='bn' else result.stage_label_en} "
                 f"({'stage percentage' if lang=='en' else 'পর্যায়ের শতাংশ'}={result.stage_fraction*100:.0f}%)")
        st.latex(r"\text{New Basic (effective)} = \text{Old Basic} + \text{Stage%} \times (\text{Full New Basic} - \text{Old Basic})")
        st.write(f"= {fmt_money(result.old_basic)} + {result.stage_fraction*100:.0f}% × "
                 f"({fmt_money(result.full_new_basic)} − {fmt_money(result.old_basic)}) = ৳{fmt_money(result.new_basic_effective)}")

        st.markdown(f"**2. {L('breakdown_title')}**")
        for line in result.allowance_lines:
            if line["applicable"]:
                st.write(f"- {allowance_name(lang, line['key'])}: ৳{fmt_money(line['new'])}")

        st.markdown(f"**3. {L('gross_salary')}**")
        st.write(f"= {L('basic_salary')} + {L('breakdown_title')} = ৳{fmt_money(result.new_basic_effective)} + "
                 f"৳{fmt_money(result.new_allowances_total)} = ৳{fmt_money(result.new_gross)}")

        st.markdown(f"**4. GPF**")
        st.write(f"= {fmt_money(result.new_basic_effective)} × {result.inputs.gpf_percent}% = ৳{fmt_money(result.gpf_amount)}")

        st.markdown(f"**5. {L('net_salary')}**")
        st.write(f"= ৳{fmt_money(result.new_gross)} − ৳{fmt_money(result.total_deductions)} = ৳{fmt_money(result.net_salary)}")

    st.divider()
    if st.session_state.pdf_bytes is None:
        if st.button(f"📄 {L('download_pdf')}", type="primary", use_container_width=True, key="prepare_pdf"):
            st.session_state.pdf_bytes = build_pdf(result, "en")  # PDF is always generated in English
            st.rerun()
    else:
        # NOTE: intentionally NOT using st.download_button here. It round-trips
        # through Streamlit's server and triggers a full app rerun on click,
        # which can race with the file being served — repeated clicks can then
        # download a stale/incomplete file under an internal hash filename
        # instead of "salary_report_2026.pdf". Embedding the PDF as a base64
        # data URL lets the browser download directly from memory: no server
        # request, no rerun, no race, regardless of how many times it's clicked.
        b64_pdf = base64.b64encode(st.session_state.pdf_bytes).decode("ascii")
        st.markdown(
            f'<a href="data:application/pdf;base64,{b64_pdf}" '
            f'download="salary_report_2026.pdf" '
            f'style="display:block;width:100%;box-sizing:border-box;text-align:center;'
            f'padding:0.55em 0;background-color:#ff4b4b;color:#ffffff;'
            f'border-radius:0.5em;text-decoration:none;font-weight:600;'
            f'font-family:inherit;">📄 {L("download_pdf")}</a>',
            unsafe_allow_html=True,
        )
    st.caption("Note: the downloaded PDF report is always generated in English."
               if st.session_state.lang == "en" else
               "নোট: ডাউনলোডকৃত পিডিএফ রিপোর্ট সর্বদা ইংরেজিতে তৈরি হয়।")

st.divider()
with st.expander(L("rules_title")):
    st.write("- Section 3: Grade-wise National Pay Scale 2026 (corresponding scale).")
    st.write("- Section 5: New Basic Salary determined by step-matching between the 2015 and 2026 scales.")
    st.write("- Section 1(2): Cabinet/Chief Secretary (৳170,000) and Senior Secretary (৳160,000) have fixed pay, outside the graded scale.")
    st.write("- Section 1(3): Phased implementation — 30% from 1 Jul 2026, 65% cumulative from 1 Jan 2027, 100% from 1 Jul 2027.")
    st.write("- Section 17(7): House Rent — % of basic with a location-based minimum; not payable in government housing.")
    st.write("- Section 15: Medical Allowance flat Tk 3,000/month.")
    st.write("- Section 16: Bangla New Year Allowance — 20% of basic, once yearly (not part of monthly gross).")
    st.write("- Section 21/23: Tiffin & Transport Allowance — Grade 11–20 only, subject to conditions.")
    st.write("- Section 9: GPF per General Provident Fund Rules, 1979.")
    st.write(L("stage4_warning"))
    st.write(L("disclaimer"))
    st.markdown("---")
    st.markdown("**"
                 + ("Known gaps / out of scope:" if st.session_state.lang == "en" else "পরিচিত সীমাবদ্ধতা / আওতার বাইরে:")
                 + "**")
    for note in OUT_OF_SCOPE_NOTES[st.session_state.lang]:
        st.write(f"- {note}")

st.caption(L("not_official"))

st.markdown(
    "<hr style='margin-top:2.5em;margin-bottom:0.8em;border:none;border-top:1px solid #e6e6e6;'>"
    "<div style='text-align:center;color:#9a9a9a;font-size:0.8em;letter-spacing:0.03em;"
    "padding-bottom:1.2em;'>Developed by&nbsp;<span style='color:#6b7280;font-weight:600;'>SV</span></div>",
    unsafe_allow_html=True,
)

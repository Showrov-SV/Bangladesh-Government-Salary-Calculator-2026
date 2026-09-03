"""
Source of truth: চাকরি (বেতন ও ভাতাদি) আদেশ, ২০২৬
Bangladesh Gazette, Extraordinary, 31 August 2026 (S.R.O No. 369-Law/2026)

All figures below are transcribed directly from the gazette. Values marked
`# VERIFY` were visually ambiguous in the scanned PDF (OCR risk) and should
be cross-checked against the official gazette before production use — they
do not affect the calculation *logic*, only the specific step numbers.

Clause references are noted so every rule is auditable back to the source.
"""

# ---------------------------------------------------------------------------
# Section 3: জাতীয় বেতনস্কেল, ২০২৬ — Grade-wise pay scale steps
# Format: grade -> {"old": [2015 scale steps], "new": [2026 scale steps]}
# ---------------------------------------------------------------------------
GRADE_SCALES = {
    1: {"old": [78000], "new": [156000]},  # fixed / নির্ধারিত
    2: {
        "old": [66000, 68480, 71050, 73720, 76490],  # VERIFY: old scale has 5 steps but new scale has only 4 — the step-matching algorithm caps at the last new step for the highest old-scale positions; no official correspondence table was available to confirm this edge case
        "new": [132000, 138600, 145530, 152800],
    },
    3: {
        "old": [56500, 58760, 61120, 63570, 66120, 68770, 71530, 74400],  # VERIFY
        "new": [113000, 118650, 124580, 130800, 137340, 144200],
    },
    4: {
        "old": [50000, 52000, 54080, 56250, 58500, 60840, 63280, 65820, 68460, 71200],
        "new": [100000, 105000, 110250, 115760, 121540, 127610, 133990],
    },
    5: {
        "old": [43000, 44940, 46970, 49090, 51300, 53610, 56030, 58560, 61200, 63960, 66840, 69850],
        "new": [86000, 90300, 94815, 99550, 104520, 109740, 115220, 120980],
    },
    6: {
        "old": [35500, 37280, 39150, 41110, 43170, 45330, 47600, 49980, 52480, 55110, 57870, 60770, 63810, 67010],
        "new": [71000, 74550, 78270, 82180, 86290, 90600, 95130, 99880, 104870],
    },
    7: {
        "old": [29000, 30450, 31980, 35260, 37030, 38890, 40840, 42890, 45040, 47300, 49670, 52160, 54770, 57510, 60390, 63410],
        "new": [58000, 60900, 63945, 67140, 70490, 74010, 77710, 81590, 85670, 89950, 94440],
    },
    8: {
        "old": [23000, 24150, 25360, 26630, 27970, 29370, 30840, 32390, 34110, 35720, 37510, 39390, 41360, 43430, 45610, 47900, 50300, 52820, 55470],  # VERIFY
        "new": [47200, 49560, 52030, 54630, 57360, 60220, 63230, 66390, 69700, 73180, 76840, 80680],
    },
    9: {
        "old": [22000, 23100, 24260, 25480, 26760, 28100, 29510, 30990, 32540, 34170, 35880, 37680, 39570, 41550, 43630, 45820, 48120, 50530, 53060],
        "new": [45100, 47355, 49720, 52200, 54810, 57550, 60420, 63440, 66610, 69940, 73430, 77100, 80950],
    },
    10: {
        "old": [16000, 16800, 17640, 18530, 19460, 20440, 21470, 22550, 23680, 24870, 26120, 27430, 28810, 30260, 31770, 33370, 35040, 36800, 38640],
        "new": [32000, 33600, 35280, 37040, 38890, 40830, 42870, 45010, 47260, 49620, 52100, 54700, 57430, 60300],
    },
    11: {
        "old": [12500, 13130, 13790, 14480, 15210, 15980, 16780, 17620, 18510, 19440, 20420, 21450, 22530, 23660, 24850, 26100, 27410, 28790, 30230],
        "new": [25000, 26250, 27560, 28930, 30370, 31880, 33470, 35140, 36890, 38730, 40660, 42690, 44820, 47060],
    },
    12: {
        "old": [11300, 11870, 12470, 13100, 13760, 14450, 15180, 15940, 16740, 17580, 18460, 19390, 20360, 21380, 22450, 23580, 24760, 26000, 27300],  # VERIFY
        "new": [24300, 25515, 26790, 28130, 29530, 31000, 32550, 34170, 35870, 37660, 39540, 41510, 43580, 45760],
    },
    13: {
        "old": [11000, 11550, 12130, 12740, 13380, 14050, 14760, 15500, 16280, 17010, 17960, 18860, 19810, 20810, 21860, 22960, 24110, 25320, 26590],
        "new": [24000, 25200, 26460, 27780, 29170, 30620, 32150, 33750, 35430, 37200, 39060, 41010, 43060, 45210],
    },
    14: {
        "old": [10200, 10710, 11250, 11820, 12420, 13050, 13710, 14400, 15120, 15880, 16680, 17520, 18400, 19320, 20290, 21310, 22380, 23500, 24680],
        "new": [23500, 24675, 25900, 27190, 28550, 29970, 31460, 33030, 34680, 36410, 38230, 40140, 42140, 44240],
    },
    15: {
        "old": [9700, 10190, 10700, 11240, 11810, 12410, 13040, 13700, 14390, 15110, 15870, 16670, 17510, 18390, 19310, 20280, 21300, 22370, 23490],  # VERIFY
        "new": [22800, 23940, 25130, 26380, 27700, 29080, 30530, 32050, 33650, 35330, 37090, 38940, 40880, 42920],
    },
    16: {
        "old": [9300, 9770, 10260, 10780, 11320, 11890, 12490, 13120, 13780, 14470, 15200, 15960, 16760, 17600, 18480, 19410, 20390, 21410, 22490],
        "new": [21900, 22995, 24140, 25340, 26600, 27930, 29320, 30780, 32320, 33930, 35620, 37400, 39270, 41230],
    },
    17: {
        "old": [9000, 9450, 9930, 10430, 10960, 11510, 12090, 12700, 13340, 14010, 14720, 15460, 16240, 17060, 17920, 18820, 19770, 20760, 21800],
        "new": [21400, 22470, 23590, 24770, 26000, 27300, 28660, 30090, 31590, 33160, 34810, 36550, 38370, 40280],
    },
    18: {
        "old": [8800, 9240, 9710, 10200, 10710, 11250, 11820, 12420, 13050, 13710, 14400, 15120, 15880, 16680, 17520, 18400, 19320, 20290, 21310],  # VERIFY
        "new": [21000, 22050, 23150, 24300, 25515, 26790, 28130, 29530, 31000, 32550, 34170, 35870, 37660, 39540],
    },
    19: {
        "old": [8500],  # gazette shows only the starting figure ("৮৫০০ থেকে শুরু")
        "new": [20500],  # "২০৫০০ থেকে শুরু"
    },
    20: {
        "old": [8250, 8670, 9110, 9570, 10050, 10560, 11090, 11650, 12240, 12860, 13510, 14190, 14900, 15650, 16440, 17270, 18140, 19050, 20010],
        "new": [20000, 21000, 22050, 23150, 24305, 25520, 26790, 28130, 29530, 31000, 32550, 34170, 35870, 37660],
    },
}

# Section 1(2): Cabinet/Chief Secretary & Senior Secretary fixed pay (not graded)
SPECIAL_FIXED_PAY = {
    "cabinet_or_chief_secretary": 170000,
    "senior_secretary": 160000,
}

SPECIAL_POST_LABELS = {
    "none": {"en": "None — use graded pay scale (Grade 1–20)",
             "bn": "কোনটি নয় — গ্রেডভিত্তিক বেতনস্কেল (গ্রেড ১–২০) ব্যবহার করুন"},
    "cabinet_or_chief_secretary": {"en": "Cabinet Secretary / Chief Secretary — fixed ৳170,000",
                                    "bn": "মন্ত্রিপরিষদ সচিব / মুখ্য সচিব — নির্ধারিত ৳১,৭০,০০০"},
    "senior_secretary": {"en": "Senior Secretary or equivalent — fixed ৳160,000",
                          "bn": "সিনিয়র সচিব বা সমমর্যাদা — নির্ধারিত ৳১,৬০,০০০"},
}

# ---------------------------------------------------------------------------
# Gazette sections that exist but are intentionally NOT calculated here,
# because the source order does not itself specify a computable new rate
# (it only references pre-existing/external orders), or because the
# provision applies only to pensioners/specific agencies outside the scope
# of an in-service, cross-cadre salary calculator. Listed transparently so
# users know these are gaps, not silent omissions.
# ---------------------------------------------------------------------------
OUT_OF_SCOPE_NOTES = {
    "en": [
        "Section 19 — Festival Allowance (উৎসবভাতা): this order does not set a new rate; it "
        "continues under the 1988 order and Bangladesh Services (Recreation Allowance) Rules, "
        "1979. Not calculated here.",
        "Section 18 — Travel/removal allowance for personal effects on transfer: a one-off, "
        "transfer-linked allowance, not part of monthly salary. Not calculated here.",
        "Sections 28–31 — Training-institution deputation allowance, and Fire Service/Ansar-VDP/"
        "NSI/RAB/Nurses/Coast Guard/Prison/DGFI/SSF/PGR/Tribunal-specific risk & special "
        "allowances: agency-specific provisions outside this calculator's scope.",
        "Section 32 — Deputation Allowance (প্রেষণভাতা) is abolished from 1 July 2026 and is "
        "correctly treated as ৳0.",
        "Sections 10, 15(2), 16(3), 19 (pensioner clauses) — pension, gratuity, and pensioner "
        "medical/festival benefits are not calculated; this tool covers in-service employees only.",
    ],
    "bn": [
        "ধারা ১৯ — উৎসবভাতা: এই আদেশে নতুন কোনো হার নির্ধারণ করা হয়নি; ১৯৮৮ সালের আদেশ ও Bangladesh "
        "Services (Recreation Allowance) Rules, 1979 অনুযায়ী বলবৎ থাকবে। এখানে হিসাব করা হয়নি।",
        "ধারা ১৮ — বদলিজনিত মালামাল পরিবহণ ভাতা: এটি একবারের, বদলি-সংক্রান্ত ভাতা, মাসিক বেতনের অংশ নয়। "
        "এখানে হিসাব করা হয়নি।",
        "ধারা ২৮–৩১ — প্রশিক্ষণ প্রতিষ্ঠানে প্রেষণভাতা এবং ফায়ার সার্ভিস/আনসার-ভিডিপি/এনএসআই/র‍্যাব/সেবিকা/"
        "কোস্টগার্ড/কারা/ডিজিএফআই/এসএসএফ/পিজিআর/ট্রাইব্যুনাল-সংশ্লিষ্ট ঝুঁকি ও বিশেষ ভাতা: নির্দিষ্ট সংস্থাভিত্তিক "
        "বিধান, এই ক্যালকুলেটরের আওতার বাইরে।",
        "ধারা ৩২ — প্রেষণভাতা ১ জুলাই ২০২৬ হইতে বিলুপ্ত; তাই সঠিকভাবে ৳০ ধরা হয়েছে।",
        "ধারা ১০, ১৫(২), ১৬(৩), ১৯ (পেনশনভোগী সংক্রান্ত) — পেনশন, গ্র্যাচুইটি ও অবসরভোগীদের চিকিৎসা/উৎসবভাতা "
        "হিসাব করা হয়নি; এই টুলটি শুধুমাত্র কর্মরত কর্মচারীদের জন্য।",
    ],
}

# ---------------------------------------------------------------------------
# Section 1(3): Phased implementation.
# NOTE: The gazette defines three dated phases only. A "4th stage" is not
# defined in the source document; it is included in the UI only because it
# was requested, and is treated identically to full (100%) implementation
# with an explicit on-screen notice.
# Interpretation note: "মূল বেতনের ৩০ শতাংশ" is applied here as 30% of the
# INCREASE (New Basic − Old Basic), consistent with standard phased pay
# implementation practice. This is an interpretation, not a literal PDF
# formula — flagged in the UI "Calculation Rules" section.
# ---------------------------------------------------------------------------
STAGE_FRACTIONS = {
    "stage1": {"label_en": "1st Stage (from 1 Jul 2026)", "label_bn": "১ম পর্যায় (১ জুলাই ২০২৬ হইতে)", "fraction": 0.30},
    "stage2": {"label_en": "2nd Stage (from 1 Jan 2027)", "label_bn": "২য় পর্যায় (১ জানুয়ারি ২০২৭ হইতে)", "fraction": 0.65},
    "stage3": {"label_en": "3rd Stage (from 1 Jul 2027 — full)", "label_bn": "৩য় পর্যায় (১ জুলাই ২০২৭ হইতে — সম্পূর্ণ)", "fraction": 1.00},
    "stage4": {"label_en": "4th Stage (not defined in source — treated as full)", "label_bn": "৪র্থ পর্যায় (উৎসে সংজ্ঞায়িত নয় — সম্পূর্ণ ধরা হয়েছে)", "fraction": 1.00},
}

# ---------------------------------------------------------------------------
# Section 17(7): House Rent Allowance table
# Bands of NEW basic salary -> location category -> (percent, minimum taka)
# ---------------------------------------------------------------------------
HOUSE_RENT_LOCATIONS = ["dhaka", "other_metro", "other"]

HOUSE_RENT_TABLE = [
    # (basic_min, basic_max, {location: (percent, minimum_tk)})
    (0, 22800, {"dhaka": (0.55, 12500), "other_metro": (0.50, 11500), "other": (0.45, 10500)}),
    (22801, 32000, {"dhaka": (0.50, 13000), "other_metro": (0.45, 12500), "other": (0.40, 11500)}),
    (32001, 71000, {"dhaka": (0.45, 14500), "other_metro": (0.40, 13000), "other": (0.35, 7000)}),  # VERIFY (7000 looks low vs pattern)
    (71001, float("inf"), {"dhaka": (0.40, 30000), "other_metro": (0.35, 25000), "other": (0.30, 21500)}),
]

# ---------------------------------------------------------------------------
# Flat-rate / fixed allowances (clauses noted)
# ---------------------------------------------------------------------------
MEDICAL_ALLOWANCE_MONTHLY = 3000          # Section 15(1)
BANGLA_NEW_YEAR_PERCENT_OF_BASIC = 0.20   # Section 16(1) — paid once yearly, NOT monthly
TIFFIN_ALLOWANCE_MONTHLY = 600            # Section 21 — Grade 11-20 only
TIFFIN_ELIGIBLE_GRADES = set(range(11, 21))
CHARGE_ALLOWANCE_PERCENT = 0.10           # Section 22
CHARGE_ALLOWANCE_MAX_MONTHLY = 3000       # Section 22
TRANSPORT_ALLOWANCE_MONTHLY = 600         # Section 23(1) — Grade 11-20, city corp area only
TRANSPORT_ELIGIBLE_GRADES = set(range(11, 21))
WASHING_ALLOWANCE_MONTHLY = 200           # Section 24
DOMESTIC_AID_ALLOWANCE_MONTHLY = 3000     # Section 26 — prescribed employees only

# Section 27: Hill Allowance
HILL_ALLOWANCE_PERCENT = 0.20
HILL_ALLOWANCE_MAX = {"sadar": 5000, "other_upazila": 10000}

# Section 20: Education Assistance
EDUCATION_ASSISTANCE_PER_CHILD = 1000
EDUCATION_ASSISTANCE_MAX_CHILDREN = 2
EDUCATION_ASSISTANCE_MAX_MONTHLY = 2000

# Section 25: Entertainment / Hosting Allowance (post-based, monthly)
ENTERTAINMENT_ALLOWANCE = {
    "none": 0,
    "joint_secretary_or_equivalent": 600,
    "additional_secretary": 1000,
    "senior_secretary_or_secretary": 2000,
    "cabinet_or_chief_secretary": 5000,
}

# GPF percentage choices (General Provident Fund, Section 9 — GPF Rules 1979 apply)
GPF_PERCENT_CHOICES = [5, 10, 15, 20, 25]

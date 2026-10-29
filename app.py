# =====================================================================
# BrightPath Online Coaching - Course Fee Calculator
# Course  : Python Programming for Business Students (End Term Project)
# Business: Online Coaching / Tuition Centre  (idea #12: Fee Calculator)
# Run with: streamlit run app.py
# =====================================================================

import math                # math.ceil() rounds the number of instalments UP
import streamlit as st     # Streamlit turns this Python script into a web page


# ---------------------------------------------------------------------
# PART 1 : BUSINESS DATA AND CALCULATION LOGIC
# ---------------------------------------------------------------------

# Dictionary 1: price (in rupees) of ONE live class for each subject (group batch, middle school)
SUBJECT_RATES = {
    "Mathematics": 250,
    "Science": 225,
    "English": 200,
    "Accountancy & Commerce": 275,
    "Python Programming": 350,
    "Competitive Exam Prep": 400,
}

# Dictionary 2: higher levels need more experienced teachers, so the rate is multiplied (float values)
LEVEL_FACTORS = {
    "Primary (Class 1-5)": 0.8,
    "Middle School (Class 6-8)": 1.0,
    "Secondary (Class 9-10)": 1.2,
    "Senior Secondary (Class 11-12)": 1.4,
    "College / Professional": 1.6,
}

# Dictionary 3: smaller batches get more personal attention, so they cost more
MODE_FACTORS = {
    "Group Batch (up to 25 students)": 1.0,
    "Small Group (up to 5 students)": 1.8,
    "One-to-One": 3.0,
}

# Dictionary 4: optional extras charged per month
ADD_ONS = {
    "Recorded Lectures": 300,
    "Doubt-Clearing Sessions": 400,
    "Weekly Test Series": 250,
}

# Dictionary 5: valid promo codes and the percentage discount each one gives
PROMO_CODES = {"WELCOME10": 10, "SIBLING15": 15, "SCHOLAR5": 5}

# Constants (written in CAPITALS because their values never change)
STUDY_MATERIAL_FEE = 500    # one-time fee for printed + PDF study material
WEEKS_PER_MONTH = 4         # we assume 4 teaching weeks in every month
GST_RATE = 0.18             # 18% GST is charged on coaching services in India


def get_duration_discount(months):
    """Return the discount % for a long enrolment (longer course = bigger discount)."""
    if months >= 12:
        return 15
    elif months >= 6:
        return 10
    elif months >= 3:
        return 5
    else:
        return 0


def get_plan_adjustment(payment_plan):
    """Return the % change for the payment plan (negative = discount, positive = extra fee)."""
    if payment_plan == "Pay Full Upfront":
        return -2              # 2% reward for paying everything at once
    elif payment_plan == "Pay Monthly":
        return 3               # 3% convenience fee for monthly instalments
    else:
        return 0               # quarterly payment: no change


def calculate_fee(subject, level, mode, classes_per_week, months,
                  selected_addons, study_material, promo_code, payment_plan):
    """Work out the full fee quote and return every number in a dictionary."""

    # Step 0: validation - stop early with a clear message if something is wrong
    if subject not in SUBJECT_RATES or level not in LEVEL_FACTORS or mode not in MODE_FACTORS:
        raise ValueError("Please choose a valid subject, level and class type.")
    if months <= 0:
        raise ValueError("Number of months must be at least 1.")
    if classes_per_week <= 0:
        raise ValueError("Classes per week must be at least 1.")

    # Step 1: price of one class = subject rate x level factor x class-type factor
    rate_per_class = SUBJECT_RATES[subject] * LEVEL_FACTORS[level] * MODE_FACTORS[mode]

    # Step 2: course fee = price per class x total number of classes
    total_classes = classes_per_week * WEEKS_PER_MONTH * months
    course_fee = rate_per_class * total_classes

    # Step 3: discount for long enrolment (uses if/elif/else inside the function above)
    duration_pct = get_duration_discount(months)
    duration_discount = course_fee * duration_pct / 100

    # Step 4: promo code - clean the text first, then check it against the dictionary
    promo_code = promo_code.strip().upper()
    promo_pct = 0
    if promo_code == "":
        promo_status = "none"          # student did not type anything
    elif promo_code in PROMO_CODES:
        promo_status = "applied"       # valid code
        promo_pct = PROMO_CODES[promo_code]
    else:
        promo_status = "invalid"       # unknown code: ignore it, do not crash
    promo_discount = (course_fee - duration_discount) * promo_pct / 100

    # Step 5: add-ons - a loop adds the monthly price of every ticked add-on
    addons_cost = 0
    for addon_name in selected_addons:
        addons_cost += ADD_ONS[addon_name] * months
    if study_material:                 # bool: True if the checkbox is ticked
        addons_cost += STUDY_MATERIAL_FEE

    # Step 6: subtotal, then discount/extra fee for the payment plan
    subtotal = course_fee - duration_discount - promo_discount + addons_cost
    plan_pct = get_plan_adjustment(payment_plan)
    plan_adjustment = subtotal * plan_pct / 100

    # Step 7: GST is charged on the amount after all discounts and fees
    taxable_amount = subtotal + plan_adjustment
    gst = taxable_amount * GST_RATE
    total = taxable_amount + gst

    # Step 8: how many instalments, and how much is each one?
    if payment_plan == "Pay Full Upfront":
        instalments = 1
    elif payment_plan == "Pay Monthly":
        instalments = months
    else:
        instalments = math.ceil(months / 3)    # one payment every 3 months, rounded up
    per_instalment = total / instalments

    # Return everything so the web page can display it
    return {
        "rate_per_class": rate_per_class, "total_classes": total_classes,
        "course_fee": course_fee, "duration_pct": duration_pct,
        "duration_discount": duration_discount, "promo_status": promo_status,
        "promo_code": promo_code, "promo_pct": promo_pct,
        "promo_discount": promo_discount, "addons_cost": addons_cost,
        "subtotal": subtotal, "plan_pct": plan_pct, "plan_adjustment": plan_adjustment,
        "gst": gst, "total": total, "instalments": instalments,
        "per_instalment": per_instalment,
    }


# ---------------------------------------------------------------------
# PART 2 : THE WEB PAGE (Streamlit widgets collect input and show output)
# ---------------------------------------------------------------------

st.set_page_config(page_title="BrightPath Fee Calculator", page_icon="🎓")
st.title("🎓 BrightPath Online Coaching")
st.subheader("Course Fee Calculator")
st.write("Choose your course on the left, customise your plan below, and see your fee instantly.")

# ----- INPUTS in the sidebar: who is studying and what they want to learn -----
st.sidebar.header("Student & Course")
student_name = st.sidebar.text_input("Student Name", value="Aarav Sharma")                        # input 1 (str)
subject = st.sidebar.selectbox("Subject", list(SUBJECT_RATES.keys()))                              # input 2 (str)
level = st.sidebar.selectbox("Class / Level", list(LEVEL_FACTORS.keys()), index=1)                 # input 3 (str)
mode = st.sidebar.radio("Class Type", list(MODE_FACTORS.keys()))                                   # input 4 (str)

# ----- INPUTS on the main page: schedule, extras and payment -----
st.header("Your Plan")
classes_per_week = st.slider("Live classes per week", min_value=1, max_value=6, value=3)           # input 5 (int)
months = st.number_input("Course duration (months)", min_value=1, max_value=24, value=3, step=1)   # input 6 (int)

st.write("**Optional add-ons**")
selected_addons = []                         # empty list: ticked add-ons will be added to it
for addon_name, addon_price in ADD_ONS.items():
    if st.checkbox(f"{addon_name} (+₹{addon_price}/month)"):     # inputs 7-9 (bool)
        selected_addons.append(addon_name)
study_material = st.checkbox(f"Printed + PDF study material (+₹{STUDY_MATERIAL_FEE} one-time)")  # input 10 (bool)

payment_plan = st.radio("Payment plan",
                        ["Pay Full Upfront", "Pay Quarterly", "Pay Monthly"], index=1)             # input 11 (str)
promo_code = st.text_input("Promo code (optional)", placeholder="e.g. WELCOME10")                  # input 12 (str)

st.divider()

# ----- VALIDATION: the student's name is required -----
if student_name.strip() == "":
    st.warning("Please enter the student's name in the sidebar to see the fee quote.")
    st.stop()                                # stop here so nothing below runs

# ----- CALCULATION inside try-except so that bad input never crashes the app -----
try:
    result = calculate_fee(subject, level, mode, classes_per_week, months,
                           selected_addons, study_material, promo_code, payment_plan)
except (ValueError, KeyError) as error:
    st.error(f"Could not calculate the fee: {error}")
    st.stop()

# ----- OUTPUT: headline amount -----
st.success(f"Total payable for {student_name.strip()}: ₹{result['total']:,.2f} (including 18% GST)")

# Three key numbers side by side
col1, col2, col3 = st.columns(3)
col1.metric("Total live classes", result["total_classes"])
col2.metric("Average cost per month", f"₹{result['total'] / months:,.0f}")
col3.metric("Instalments", f"{result['instalments']} x ₹{result['per_instalment']:,.0f}")

# Message about the promo code (if/elif so each case gets its own message)
if result["promo_status"] == "applied":
    st.success(f"Promo code {result['promo_code']} applied: {result['promo_pct']}% off the course fee.")
elif result["promo_status"] == "invalid":
    st.warning(f"Promo code '{result['promo_code']}' is not valid, so no promo discount was applied.")

# ----- OUTPUT: line-by-line fee breakdown -----
st.subheader("Fee Breakdown")
rows = [{"Item": f"Course fee ({result['total_classes']} classes x ₹{result['rate_per_class']:,.2f})",
         "Amount (₹)": f"{result['course_fee']:,.2f}"}]

if result["duration_discount"] > 0:
    rows.append({"Item": f"Long-course discount ({result['duration_pct']}%)",
                 "Amount (₹)": f"-{result['duration_discount']:,.2f}"})
if result["promo_discount"] > 0:
    rows.append({"Item": f"Promo discount ({result['promo_pct']}%)",
                 "Amount (₹)": f"-{result['promo_discount']:,.2f}"})
for addon_name in selected_addons:           # one row for every ticked add-on
    rows.append({"Item": f"{addon_name} ({months} months)",
                 "Amount (₹)": f"{ADD_ONS[addon_name] * months:,.2f}"})
if study_material:
    rows.append({"Item": "Study material", "Amount (₹)": f"{STUDY_MATERIAL_FEE:,.2f}"})

if result["plan_adjustment"] < 0:
    rows.append({"Item": f"Pay-in-full discount ({abs(result['plan_pct'])}%)",
                 "Amount (₹)": f"-{abs(result['plan_adjustment']):,.2f}"})
elif result["plan_adjustment"] > 0:
    rows.append({"Item": f"Monthly instalment fee ({result['plan_pct']}%)",
                 "Amount (₹)": f"{result['plan_adjustment']:,.2f}"})

rows.append({"Item": "GST (18%)", "Amount (₹)": f"{result['gst']:,.2f}"})
rows.append({"Item": "TOTAL PAYABLE", "Amount (₹)": f"{result['total']:,.2f}"})
st.table(rows)

st.caption("Fees are indicative and include 18% GST. Book a free demo class before you enrol.")

import asyncio
import html
import json
import sys
import time
from pathlib import Path

import streamlit as st

# `streamlit run app/streamlit_app.py` executes this file as a script and
# places `app/` (rather than the project root) on the import path. Add the
# project root so the shared `app.*` package can always be imported.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.config import get_settings
from app.schemas import MANDATORY_FIELD_NAMES
from app.services import ClaimExtractionService


# ---------------------------------------------------------
# Application services
# ---------------------------------------------------------

st.set_page_config(
    page_title="Insurance Claim Extractor",
    layout="wide",
)

try:
    settings = get_settings()
except RuntimeError as exc:
    st.error(str(exc))
    st.stop()


async def extract_claim(
    description: str,
    custom_fields: list[str],
) -> dict:
    """Run one extraction with a client bound to this request's event loop."""

    # Do not cache the async Gemini client. Streamlit reruns use a new event
    # loop, while the SDK's async client remains bound to the loop that first
    # used it. A fresh service per extraction prevents "Event loop is closed".
    service = ClaimExtractionService(settings)
    return await service.extract(
        description=description,
        custom_fields=custom_fields,
    )


GEMINI_MODEL = settings.gemini_model


# ---------------------------------------------------------
# Custom CSS (grey / black palette, white notes box)
# ---------------------------------------------------------

st.markdown(
    """
<style>
.chip-box {
    max-height: 340px;
    overflow-y: auto;
    padding: 12px;
    border: 1px solid rgba(128, 128, 128, 0.35);
    border-radius: 10px;
    background: rgba(128, 128, 128, 0.06);
}

.chip-wrap {
    display: flex;
    flex-wrap: wrap;
    gap: 7px;
}

.chip {
    display: inline-block;
    max-width: 100%;
    padding: 5px 12px;
    border-radius: 6px;
    font-size: 12.5px;
    line-height: 1.35;
    word-break: break-word;
}

.chip-mandatory {
    background: rgba(128, 128, 128, 0.15);
    border: 1px solid rgba(128, 128, 128, 0.50);
}

.chip-custom {
    background: #111111;
    border: 1px solid #111111;
    color: #ffffff;
}

.latency-card, .model-card {
    padding: 12px 14px;
    border: 1px solid rgba(128, 128, 128, 0.35);
    border-radius: 10px;
    background: rgba(128, 128, 128, 0.06);
}

.latency-card {
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.latency-value {
    font-size: 28px;
    font-weight: 700;
    line-height: 1.1;
}

.latency-unit, .latency-sub {
    font-size: 12px;
    opacity: 0.65;
}

.badge {
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 11.5px;
    font-weight: 600;
}

.badge-fast {
    background: #111111;
    color: #ffffff;
}

.badge-ok {
    background: rgba(128, 128, 128, 0.25);
    border: 1px solid rgba(128, 128, 128, 0.60);
}

.badge-slow {
    border: 1px solid rgba(128, 128, 128, 0.80);
}

/* Notes view: white background, black text */
.notes-box {
    background: #ffffff;
    color: #111111;
    border: 1px solid #d0d0d0;
    border-radius: 10px;
    overflow: hidden;
}

.note-row {
    display: grid;
    grid-template-columns: 34% 66%;
    background: #ffffff;
    border-bottom: 1px solid #e3e3e3;
}

.note-row:last-child {
    border-bottom: none;
}

.note-key {
    padding: 10px 14px;
    font-size: 13px;
    font-weight: 700;
    color: #111111;
    background: #ffffff;
    border-right: 1px solid #e3e3e3;
    word-break: break-word;
}

.note-value {
    padding: 10px 14px;
    font-size: 14px;
    color: #111111;
    background: #ffffff;
    word-break: break-word;
    white-space: pre-wrap;
}

.note-null {
    font-family: "Source Code Pro", monospace;
    font-size: 13px;
    color: #111111;
}

.notes-count {
    font-size: 12.5px;
    opacity: 0.65;
    margin-bottom: 8px;
}
</style>
""",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Session state
# ---------------------------------------------------------

if "field_input_version" not in st.session_state:
    st.session_state.field_input_version = 0

if "custom_fields" not in st.session_state:
    st.session_state.custom_fields = []

if "claim_description" not in st.session_state:
    st.session_state.claim_description = ""

if "last_latency" not in st.session_state:
    st.session_state.last_latency = None

if "last_result" not in st.session_state:
    st.session_state.last_result = None


MANDATORY_FIELDS = MANDATORY_FIELD_NAMES


# ---------------------------------------------------------
# Example claim descriptions
# ---------------------------------------------------------

CLAIM_EXAMPLES = {

    "Claim 1": """ProductServiceLOB_Ext: HOM
Contract Type: HO08
Loss Email Address: 3j728c3hp22@claims.usaa.com
Stucture: Residential home
Year Built: 1939
Footage Risk: 1649
Number of Stories: 1.50
Roof Type: Composition shingle
Legal Name: RYAN AIDEN MCCARTHY
Interior Damage: No
Loss Location Country: United States
Endorsement: HO-9R(02) (07-08)
Endorsement: HO-208;(07-08);WTR BKUP/Pump Overflow;10000.00 usd

Deductible Type: Wind Hail Deductible
Deductible Amount: 7240.00 usd
Deductible Type: All Other Perils Deductible
Deductible Amount: 2000.00 usd

Coverage:
Dwelling Coverage Limit: 362000.00 usd
Unscheduled Personal Property Limit: 181000.00 usd
Appurtenant Structures: 36200.00 usd
Additional Living Expenses: 99999999.00 usd
PL (BI/PD) - Limit: 500000.00 usd
MP - Limit: 5000.00 usd

Contact Information:
Contact Name: RYAN MCCARTHY
Cell Phone: 918-892-5651

Loss Description: there was a hailstorm that damaged ni roof""",

    "Claim 2": """ProductServiceLOB_Ext: HOM
Contract Type: HO08
Loss Email Address: 3j7zg8qvhkz4h@claims.usaa.com
Stucture: Residential home
Year Built: 2000
Footage Risk: 2686
Number of Stories: 2.00
Roof Type: Fiberglass
Legal Name: FRANK LEO FAUST
Member's Rank or Title: lieutenant
Interior Damage: No
Loss Location Country: United States

Last 10 Prior Losses:
Claim Number - 001022153-800
Date of Loss - 2025-08-19
Type of Loss - Other
Insured Item - 3226 Avebury Ln
ProductServiceLOB_Ext - HOM
Status - Closed

Claim Number - 001022153-22
Date of Loss - 2019-10-28
Type of Loss - Other
Insured Item - 3226 Avebury Ln
ProductServiceLOB_Ext - HOM
Status - Closed

Member Primary Mailing Address: 3226 Avebury Ln

Endorsement: HO-9RVA (01-23)

Deductible Type: Wind Hail Deductible
Deductible Amount: 17440.00 usd
Deductible Type: All Other Perils Deductible
Deductible Amount: 17440.00 usd

Coverage:
Dwelling Coverage Limit: 872000.00 usd
Unscheduled Personal Property Limit: 436000.00 usd
Appurtenant Structures: 87200.00 usd
Additional Living Expenses: 99999999.00 usd
PL (BI/PD) - Limit: 300000.00 usd
MP - Limit: 5000.00 usd

Contact Information:
Contact Name: Frank Faust
Home Phone: 434-295-4422
Cell Phone: 434-409-3644

Loss Description: There was a severe hail storm that afternoon and we felt bombarded by large hail storms - for some time the golf course was covered white. Fortunately no windows were broken and our cars were garaged. Others in the area have had to replace their roof so I think your inspector should check our roof.""",

    "Claim 3": """ProductServiceLOB_Ext: HOM
Contract Type: HO08
Loss Email Address: 3j7dxc3qx9vjz@claims.usaa.com
Stucture: Residential home
Year Built: 2008
Footage Risk: 1555
Number of Stories: 1.00
Roof Type: Fiberglass
Legal Name: JOSEPH S SOLDATO AND JENNIFER R SOLDATO
Member's Rank or Title: staffsergent
Interior Damage: Yes
Loss Location Country: United States

Endorsement: HO-3RTX (07-08)
Endorsement: HO-208;(07-08);WTR BKUP/Pump Overflow;10000.00 usd

Deductible Type: Wind Hail Deductible
Deductible Amount: 5900.00 usd
Deductible Type: All Other Perils Deductible
Deductible Amount: 2000.00 usd

Coverage:
Dwelling Coverage Limit: 295000.00 usd
Unscheduled Personal Property Limit: 147500.00 usd
Appurtenant Structures: 29500.00 usd
Additional Living Expenses: 59000.00 usd
PL (BI/PD) - Limit: 300000.00 usd
MP - Limit: 5000.00 usd

Contact Information:
Contact Name: Joseph Soldato
Home Phone: 254-350-0785
Cell Phone: 254-350-0785

Loss Description:
Wind damage loss of shingles
Hail damage to shingles
Interior damage""",

    "Claim 4": """ProductServiceLOB_Ext: HOM
Contract Type: HO08

Loss Description:
there is sewer water in the basement of this property. Please have an adjuster contact the claimant and Bob to schedule an inspection ASAP.

To avoid further damage, I am allowing them to photograph soft goods and dispose of them. Those items can be added to the estimate later.

Restoration Company: Bob Bielich
Phone: 412-596-9911""",

    "Claim 5": """ProductServiceLOB_Ext: HOM

Claim Description:

Insured called to report lightening struck in their yard, causing half of their electronics, fans not working, automatic couches not working, mini split for ac not working.

Internet repair guy going this evening. Security cameras may be out as well, will not know until internet is repaired.

Messed wbreakers, havent checked all the outlets.

Computers turn on but stated they are waiting for internet to be turned.

She stated mostly the front of the home, light bulbs in back of home.

ACKNOWLEDGED CLAIM WILL BE SET UP, ADJUSTER ASSIGNED.
The adjuster will complete their inspection, review your policy, and coverage will be determined based on your policy.
ACKNOWLEDGED CLAIM VIA PHONE""",
}


def render_chips(fields: list[str], css_class: str) -> str:
    """Build the sidebar field chips."""

    chips = "".join(
        f'<span class="chip {css_class}">{html.escape(field)}</span>'
        for field in fields
    )
    return (
        '<div class="chip-box"><div class="chip-wrap">'
        f"{chips}"
        "</div></div>"
    )


def render_latency_html(seconds: float | None) -> str:
    """Build the extraction-latency card displayed in the sidebar."""

    if seconds is None:
        return (
            '<div class="latency-card"><div>'
            '<div class="latency-value">--</div>'
            '<div class="latency-sub">Not measured yet</div>'
            "</div></div>"
        )

    if seconds < 3:
        badge_class, badge_text = "badge-fast", "FAST"
    elif seconds < 8:
        badge_class, badge_text = "badge-ok", "NORMAL"
    else:
        badge_class, badge_text = "badge-slow", "SLOW"

    return (
        '<div class="latency-card"><div>'
        f'<div class="latency-value">{seconds:.2f}'
        '<span class="latency-unit"> sec</span></div>'
        '<div class="latency-sub">End-to-end request time</div>'
        "</div>"
        f'<span class="badge {badge_class}">{badge_text}</span>'
        "</div>"
    )


def is_empty_value(value) -> bool:
    """
    True when the extracted value has no real content.
    """

    if value is None:
        return True

    if isinstance(value, str) and not value.strip():
        return True

    if isinstance(value, (list, dict)) and not value:
        return True

    return False


def format_note_value(value) -> str:
    """
    Convert any extracted value into readable text.
    """

    if isinstance(value, list):
        return "\n".join(
            format_note_value(item) for item in value
        )

    if isinstance(value, dict):
        return "\n".join(
            f"{key}: {format_note_value(item)}"
            for key, item in value.items()
        )

    return str(value)


def render_notes_html(result: dict, hide_empty: bool) -> str:
    """
    Build the Notes view: one row per key with its value.
    Empty values are shown as null.
    """

    rows = []

    for key, value in result.items():

        empty = is_empty_value(value)

        if empty and hide_empty:
            continue

        if empty:
            value_html = '<span class="note-null">null</span>'
        else:
            value_html = html.escape(format_note_value(value))

        rows.append(
            '<div class="note-row">'
            f'<div class="note-key">{html.escape(str(key))}</div>'
            f'<div class="note-value">{value_html}</div>'
            "</div>"
        )

    if not rows:
        return ""

    return f'<div class="notes-box">{"".join(rows)}</div>'


# ---------------------------------------------------------
# Custom-field confirmation
# ---------------------------------------------------------

@st.dialog("Field added successfully")
def show_field_added_popup(field_name: str) -> None:
    """Confirm that a custom field is active for this browser session."""

    st.success(f'"{field_name}" has been added successfully.')
    st.write("The field will be included in future claim extractions.")
    if st.button("OK", type="primary", width="stretch"):
        st.rerun()


# ---------------------------------------------------------
# Sidebar (session information intentionally omitted)
# ---------------------------------------------------------

with st.sidebar:
    st.subheader("Model & Performance")
    st.caption("Selected model")
    st.markdown(
        f'<div class="model-card">{html.escape(GEMINI_MODEL)}</div>',
        unsafe_allow_html=True,
    )

    st.caption("Last extraction latency")
    latency_placeholder = st.empty()
    latency_placeholder.markdown(
        render_latency_html(st.session_state.last_latency),
        unsafe_allow_html=True,
    )

    st.subheader("Mandatory Fields")
    st.caption(f"{len(MANDATORY_FIELDS)} fields are always extracted.")
    search_text = st.text_input(
        "Search mandatory fields",
        placeholder="Search fields...",
        label_visibility="collapsed",
        key="mandatory_search",
    )
    visible_fields = [
        field
        for field in MANDATORY_FIELDS
        if search_text.strip().lower() in field.lower()
    ]
    if visible_fields:
        st.markdown(
            render_chips(visible_fields, "chip-mandatory"),
            unsafe_allow_html=True,
        )
    else:
        st.caption("No matching fields.")

    st.divider()
    st.subheader("Add Custom Field")
    st.caption("Add a field without changing application code.")
    input_key = f"custom_field_input_{st.session_state.field_input_version}"
    custom_key = st.text_input(
        "Field key",
        placeholder="Example: Claim Number",
        key=input_key,
    )

    if st.button("Add Field", type="primary", width="stretch"):
        key = custom_key.strip()
        existing_fields = {field.lower() for field in st.session_state.custom_fields}
        mandatory_fields = {field.lower() for field in MANDATORY_FIELDS}

        if not key:
            st.error("Enter a field key.")
        elif key.lower() in mandatory_fields:
            st.error("This field is already a mandatory field.")
        elif key.lower() in existing_fields:
            st.error("This custom field already exists.")
        else:
            st.session_state.custom_fields.append(key)
            st.session_state.field_input_version += 1
            show_field_added_popup(key)

    st.divider()
    st.subheader("Active Custom Fields")
    if st.session_state.custom_fields:
        st.markdown(
            render_chips(st.session_state.custom_fields, "chip-custom"),
            unsafe_allow_html=True,
        )
    else:
        st.caption("No custom fields added yet.")


# ---------------------------------------------------------
# Main page
# ---------------------------------------------------------

st.title("Insurance Claim Field Extractor")

st.write(
    "Paste an unstructured insurance claim description "
    "and extract structured claim information using AI."
)


# ---------------------------------------------------------
# Example Claims
# ---------------------------------------------------------

st.subheader("Example Claims")

st.caption(
    "Select an example to automatically load "
    "the claim description below."
)

example_columns = st.columns(5, gap="small", wrap=False)

for column, claim_name in zip(example_columns, CLAIM_EXAMPLES, strict=True):
    with column:
        if st.button(
            claim_name,
            key=f"example_{claim_name}",
            width="stretch",
        ):
            st.session_state.claim_description = CLAIM_EXAMPLES[claim_name]
            st.rerun()


# ---------------------------------------------------------
# Claim Description
# ---------------------------------------------------------

st.subheader("Claim Description")

description = st.text_area(
    "Paste the complete claim description",
    height=350,
    key="claim_description",
    placeholder=(
        "Paste an unstructured insurance claim "
        "description here..."
    ),
    label_visibility="collapsed",
)


# ---------------------------------------------------------
# Extraction
# ---------------------------------------------------------

if st.button(
    "Extract Claim Data",
    type="primary",
    width="stretch",
):

    if not description.strip():
        st.warning("Please paste a claim description first.")
        st.stop()

    with st.spinner("Analyzing claim and extracting fields..."):

        start_time = time.perf_counter()

        try:
            result = asyncio.run(
                extract_claim(
                    description,
                    st.session_state.custom_fields,
                )
            )

        except ValueError as exc:

            elapsed = time.perf_counter() - start_time
            st.session_state.last_latency = elapsed
            latency_placeholder.markdown(
                render_latency_html(elapsed),
                unsafe_allow_html=True,
            )

            st.error(str(exc))
            st.stop()

        except Exception as exc:

            elapsed = time.perf_counter() - start_time
            st.session_state.last_latency = elapsed
            latency_placeholder.markdown(
                render_latency_html(elapsed),
                unsafe_allow_html=True,
            )

            st.error(f"Extraction failed: {exc}")
            st.stop()

        elapsed = time.perf_counter() - start_time
        st.session_state.last_latency = elapsed
        latency_placeholder.markdown(
            render_latency_html(elapsed),
            unsafe_allow_html=True,
        )

    # -----------------------------------------------------
    # Save result so it survives reruns (tabs, checkbox)
    # -----------------------------------------------------

    st.session_state.last_result = result


# ---------------------------------------------------------
# Output: Notes view and JSON view
# ---------------------------------------------------------

result = st.session_state.last_result

if result is not None:

    st.success("Claim extraction completed successfully.")

    st.subheader("Extracted Claim Data")

    notes_tab, json_tab = st.tabs(["Notes", "JSON"])

    # -----------------------------------------------------
    # Notes view
    # -----------------------------------------------------

    with notes_tab:

        if isinstance(result, dict):

            hide_empty = st.checkbox(
                "Hide fields with no value",
                value=False,
                key="hide_empty_fields",
            )

            filled_count = sum(
                1 for value in result.values()
                if not is_empty_value(value)
            )

            st.markdown(
                f'<div class="notes-count">'
                f"{filled_count} of {len(result)} fields have a value"
                f"</div>",
                unsafe_allow_html=True,
            )

            notes_html = render_notes_html(result, hide_empty)

            if notes_html:
                st.markdown(notes_html, unsafe_allow_html=True)
            else:
                st.caption("No fields to show.")

        else:
            st.write(result)

    # -----------------------------------------------------
    # JSON view
    # -----------------------------------------------------

    with json_tab:

        st.json(result)

        st.download_button(
            "Download JSON",
            data=json.dumps(result, indent=2, ensure_ascii=False),
            file_name="claim_extraction.json",
            mime="application/json",
        )

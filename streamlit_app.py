import os
import tempfile
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Cyber Crime System",
    page_icon="image.webp",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background: #0b1220;
    color: #e5e7eb;
}

[data-testid="stSidebar"] {
    background: #111827;
}

.block-container {
    padding-top: 2rem;
    max-width: 1500px;
}

h1, h2, h3, h4 {
    color: #f8fafc;
}

div[data-testid="stMetric"] {
    background: #111827;
    border: 1px solid #374151;
    border-radius: 10px;
    padding: 10px;
}

.queue-box {
    background: #111827;
    border: 1px solid #374151;
    border-radius: 10px;
    padding: 12px;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# API FUNCTIONS
# =========================================================

def submit_complaint(
    complaint_text,
    user_name,
    contact_number,
    transaction_id
):
    payload = {
        "complaint_text": complaint_text,
        "user_name": user_name,
        "contact_number": contact_number,
        "transaction_id": transaction_id
    }

    try:
        response = requests.post(
            f"{API_URL}/complaints",
            json=payload,
            timeout=60
        )

        if response.status_code == 200:
            return response.json()

        st.error(
            f"Backend error: {response.text}"
        )
        return None

    except requests.exceptions.RequestException as error:
        st.error(
            f"Cannot connect to FastAPI backend: {error}"
        )
        return None


def get_complaint(complaint_id):
    try:
        response = requests.get(
            f"{API_URL}/complaints/{complaint_id}",
            timeout=30
        )

        if response.status_code == 200:
            return response.json()

        if response.status_code == 404:
            st.error(
                "Complaint not found."
            )
        else:
            st.error(
                f"Backend error: {response.text}"
            )

        return None

    except requests.exceptions.RequestException as error:
        st.error(
            f"Cannot connect to FastAPI backend: {error}"
        )
        return None


def get_pending_complaints():
    try:
        response = requests.get(
            f"{API_URL}/complaints/pending",
            timeout=30
        )

        if response.status_code == 200:
            return response.json()

        st.error(
            f"Pending queue error: {response.text}"
        )
        return None

    except requests.exceptions.RequestException as error:
        st.error(
            f"Cannot connect to FastAPI backend: {error}"
        )
        return None


def submit_decision(
    complaint_id,
    decision
):
    try:
        response = requests.post(
            f"{API_URL}/complaints/{complaint_id}/decision",
            json={
                "decision": decision
            },
            timeout=30
        )

        if response.status_code == 200:
            return response.json()

        st.error(
            f"Decision error: {response.text}"
        )
        return None

    except requests.exceptions.RequestException as error:
        st.error(
            f"Cannot connect to FastAPI backend: {error}"
        )
        return None


# =========================================================
# VOICE TRANSCRIPTION
# =========================================================

def transcribe_audio(audio_file):
    try:
        from openai import OpenAI

        api_key = os.getenv(
            "OPENAI_API_KEY"
        )

        if not api_key:
            st.error(
                "OPENAI_API_KEY not found in .env"
            )
            return None

        client = OpenAI(
            api_key=api_key
        )

        audio_bytes = audio_file.getvalue()

        with tempfile.NamedTemporaryFile(
            suffix=".wav",
            delete=False
        ) as temp_file:

            temp_file.write(
                audio_bytes
            )

            temp_path = temp_file.name

        try:
            with open(
                temp_path,
                "rb"
            ) as audio:

                result = client.audio.transcriptions.create(
                    model="gpt-4o-mini-transcribe",
                    file=audio
                )

            return result.text

        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    except Exception as error:
        st.error(
            f"Voice transcription failed: {error}"
        )
        return None


# =========================================================
# CITIZEN PAGE
# =========================================================

def citizen_page():

    st.title("Citizen Complaint")

    st.caption(
        "Submit a cyber-crime complaint using text or voice."
    )

    st.markdown(
        "##Complaint Details"
    )

    col1, col2 = st.columns(2)

    with col1:

        user_name = st.text_input(
            "Full Name",
            placeholder="Enter your full name"
        )

    with col2:

        contact_number = st.text_input(
            "Contact Number",
            placeholder="9876543210"
        )

    st.markdown(
        "##Complaint"
    )

    input_mode = st.radio(
        "Complaint Input",
        [
            "Text",
            "Voice"
        ],
        horizontal=True
    )

    complaint_text = ""

    if input_mode == "Text":

        complaint_text = st.text_area(
            "Describe what happened",
            height=180,
            placeholder=(
                "Example: I was cheated through a UPI scam. "
                "The fraudster asked me to transfer ₹60000. "
                "Transaction ID TXN123456. "
                "They also sent a suspicious link."
            )
        )

    else:

        st.info(
            "Record your complaint in Telugu, English, "
            "or mixed Telugu-English."
        )

        audio_file = st.audio_input(
            "Record your complaint"
        )

        if audio_file:

            if st.button(
                "Convert Voice to Text",
                use_container_width=True
            ):

                with st.spinner(
                    "Converting voice to text..."
                ):

                    transcript = transcribe_audio(
                        audio_file
                    )

                if transcript:

                    st.session_state[
                        "voice_complaint"
                    ] = transcript

                    st.success(
                        "Voice converted successfully."
                    )

        complaint_text = st.text_area(
            "Complaint Text",
            value=st.session_state.get(
                "voice_complaint",
                ""
            ),
            height=180
        )

    st.markdown(
        "##Optional Transaction Information"
    )

    transaction_id = st.text_input(
        "Transaction ID (Optional)",
        placeholder="Leave blank if not applicable"
    )

    st.caption(
        "Transaction ID is optional. AI agents can extract "
        "transaction IDs, amounts, URLs, phone numbers "
        "and UPI IDs from the complaint."
    )

    st.divider()

    if st.button(
        "Submit Complaint",
        type="primary",
        use_container_width=True
    ):

        if not user_name.strip():

            st.warning(
                "Please enter your name."
            )
            return

        if not contact_number.strip():

            st.warning(
                "Please enter your contact number."
            )
            return

        if not complaint_text.strip():

            st.warning(
                "Please describe what happened."
            )
            return

        with st.spinner(
            "AI agents are processing your complaint..."
        ):

            result = submit_complaint(
                complaint_text.strip(),
                user_name.strip(),
                contact_number.strip(),
                transaction_id.strip()
            )

        if result:

            st.session_state[
                "submitted_case"
            ] = result

            st.session_state[
                "active_case_id"
            ] = result.get(
                "complaint_id"
            )

    result = st.session_state.get(
        "submitted_case"
    )

    if not result:
        return

    complaint_id = result.get(
        "complaint_id",
        "N/A"
    )

    status = result.get(
        "status",
        "Unknown"
    )

    risk = result.get(
        "risk_assessment"
    ) or {}

    fraud = result.get(
        "fraud_analysis"
    ) or {}

    evidence = result.get(
        "evidence_analysis"
    ) or {}

    routing = result.get(
        "routing_decision"
    ) or {}

    st.divider()

    st.success(
        f"Complaint submitted successfully. "
        f"Complaint ID: {complaint_id}"
    )

    st.markdown(
        "## 📋 Complaint Status"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Complaint ID",
            complaint_id
        )

    with col2:

        st.metric(
            "Status",
            str(status)
            .replace("_", " ")
            .upper()
        )

    with col3:

        st.metric(
            "Risk Level",
            str(
                risk.get(
                    "risk_level",
                    "Unknown"
                )
            ).upper()
        )

    with col4:

        st.metric(
            "Priority",
            str(
                risk.get(
                    "priority",
                    "Unknown"
                )
            ).upper()
        )

    # -----------------------------------------------------
    # GUARDRAIL STATUS
    # -----------------------------------------------------

    input_guardrail_status = result.get(
        "guardrail_status",
        "unknown"
    )

    output_guardrail_status = result.get(
        "output_guardrail_status",
        "unknown"
    )

    guardrail_col1, guardrail_col2 = st.columns(2)

    with guardrail_col1:
        if input_guardrail_status == "passed":
            st.success("🛡️ Input Guardrail: PASSED")
        elif input_guardrail_status == "blocked":
            st.error("🛡️ Input Guardrail: BLOCKED")
        else:
            st.info("🛡️ Input Guardrail: NOT AVAILABLE")

    with guardrail_col2:
        if output_guardrail_status == "passed":
            st.success("🛡️ Output Guardrail: PASSED")
        elif output_guardrail_status == "blocked":
            st.error("🛡️ Output Guardrail: BLOCKED → HUMAN REVIEW")
        else:
            st.info("🛡️ Output Guardrail: NOT AVAILABLE")

    if input_guardrail_status == "blocked":
        errors = result.get("guardrail_errors", [])
        if errors:
            st.warning("Input validation issues:")
            for error in errors:
                st.write(f"• {error}")

    if output_guardrail_status == "blocked":
        errors = result.get("output_guardrail_errors", [])
        if errors:
            st.warning("Output validation issues:")
            for error in errors:
                st.write(f"• {error}")

    if status == "human_review_required":

        st.warning(
            "⚠️ This complaint requires human officer review."
        )

        st.info(
            "The complaint has been sent to the "
            "Officer Workbench for HITL review."
        )

        if st.button(
            "🛡️ Go to Officer Workbench",
            type="primary",
            use_container_width=True
        ):

            st.session_state[
                "selected_module"
            ] = "🛡️ Officer Workbench"

            case = get_complaint(
                complaint_id
            )

            if case:

                st.session_state[
                    "active_case"
                ] = case

            st.rerun()

    st.divider()

    st.markdown(
        "## 🤖 AI Processing Result"
    )

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            "### ⚠️ Risk Assessment"
        )

        st.metric(
            "Risk Score",
            f"{risk.get('risk_score', 'N/A')}/100"
        )

        st.write(
            "**Risk Level:**",
            risk.get(
                "risk_level",
                "N/A"
            )
        )

        st.write(
            "**Priority:**",
            risk.get(
                "priority",
                "N/A"
            )
        )

        risk_factors = risk.get(
            "risk_factors",
            []
        )

        if risk_factors:

            st.write(
                "**Risk Factors:**"
            )

            for factor in risk_factors:

                st.write(
                    f"• {factor}"
                )

    with col2:

        st.markdown(
            "### 🚦 Routing Decision"
        )

        st.write(
            "**Route:**",
            routing.get(
                "route",
                "N/A"
            )
        )

        st.write(
            "**Message:**",
            routing.get(
                "message",
                "N/A"
            )
        )

    st.divider()

    st.markdown(
        "### 🧾 Evidence Analysis"
    )

    col1, col2 = st.columns(2)

    with col1:

        st.write(
            "**Evidence Found:**"
        )

        found = evidence.get(
            "evidence_found",
            []
        )

        if found:

            for item in found:
                st.write(
                    f"✅ {item}"
                )

        else:

            st.info(
                "No evidence detected."
            )

    with col2:

        st.write(
            "**Missing Evidence:**"
        )

        missing = evidence.get(
            "missing_evidence",
            []
        )

        if missing:

            for item in missing:
                st.write(
                    f"⚠️ {item}"
                )

        else:

            st.success(
                "No missing evidence detected."
            )

    st.divider()

    st.markdown(
        "### 🚨 Fraud Analysis"
    )

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Fraud Score",
            f"{fraud.get('fraud_score', 'N/A')}/10"
        )

        st.write(
            "**Fraud Level:**",
            fraud.get(
                "fraud_level",
                "N/A"
            )
        )

    with col2:

        st.write(
            "**Fraud Indicators:**"
        )

        indicators = fraud.get(
            "fraud_indicators",
            []
        )

        if not indicators:

            indicators = fraud.get(
                "indicators",
                []
            )

        if indicators:

            for indicator in indicators:

                st.write(
                    f"• {indicator}"
                )

        else:

            st.info(
                "No fraud indicators detected."
            )


# =========================================================
# OFFICER WORKBENCH
# =========================================================

def officer_page():

    st.title(
        "🛡️ Cyber Crime Officer Workbench"
    )

    st.caption(
        "AI-assisted Cyber Crime Complaint Review System"
    )

    pending_data = get_pending_complaints()

    if pending_data is None:
        return

    pending_cases = pending_data.get(
        "cases",
        []
    )

    col_queue, col_main = st.columns(
        [1.1, 3.4]
    )

    # =====================================================
    # LEFT SIDE - PENDING HUMAN REVIEW
    # =====================================================

    with col_queue:

        st.markdown(
            "## 📋 Pending Human Review"
        )

        st.write(
            f"**{len(pending_cases)} case(s) "
            f"awaiting action**"
        )

        if st.button(
            "🔄 Refresh Queue",
            use_container_width=True
        ):

            st.rerun()

        st.divider()

        if not pending_cases:

            st.success(
                "No complaints are currently "
                "waiting for human review."
            )

        for case in pending_cases:

            case_id = case.get(
                "complaint_id",
                "Unknown"
            )

            risk = case.get(
                "risk_assessment"
            ) or {}

            score = risk.get(
                "risk_score",
                0
            )

            crime = str(
                case.get(
                    "crime_category",
                    "Unknown"
                )
            ).replace(
                "_",
                " "
            ).title()

            if score >= 70:

                priority = "🔴 CRITICAL"

            elif score >= 40:

                priority = "🟠 HIGH"

            else:

                priority = "🟡 MEDIUM"

            # ---------------------------------------------
            # CASE CARD
            # ---------------------------------------------

            with st.container(border=True):

                st.markdown(
                    f"### Case {case_id}"
                )

                col_a, col_b = st.columns(2)

                with col_a:

                    st.write(
                        priority
                    )

                with col_b:

                    st.write(
                        f"**Risk: {score}/100**"
                    )

                st.write(
                    f"**Crime:** {crime}"
                )

                st.caption(
                    "Awaiting Action"
                )

                if st.button(
                    f"Open Case {case_id}",
                    key=f"open_{case_id}",
                    use_container_width=True
                ):

                    loaded_case = get_complaint(
                        case_id
                    )

                    if loaded_case:

                        st.session_state[
                            "active_case"
                        ] = loaded_case

                        st.session_state[
                            "active_case_id"
                        ] = case_id

                        st.rerun()

            st.write("")

    # =====================================================
    # RIGHT SIDE - ACTIVE CASE
    # =====================================================

    with col_main:

        active_case = st.session_state.get(
            "active_case"
        )

        if not active_case:

            st.info(
                "Select a pending human-review case "
                "from the queue."
            )

            return

        case = active_case

        complaint_id = case.get(
            "complaint_id",
            "Unknown"
        )

        risk = case.get(
            "risk_assessment"
        ) or {}

        fraud = case.get(
            "fraud_analysis"
        ) or {}

        evidence = case.get(
            "evidence_analysis"
        ) or {}

        routing = case.get(
            "routing_decision"
        ) or {}

        st.markdown(
            f"# ACTIVE CASE: {complaint_id}"
        )

        # =================================================
        # CASE DETAILS
        # =================================================

        st.markdown(
            "## 📄 Complaint Details"
        )

        with st.container(border=True):

            st.write(
                "**Citizen:**",
                case.get(
                    "user_name",
                    "N/A"
                )
            )

            st.write(
                "**Contact:**",
                case.get(
                    "contact_number",
                    "N/A"
                )
            )

            transaction_id = case.get(
                "transaction_id"
            )

            st.write(
                "**Transaction ID:**",
                transaction_id
                if transaction_id
                else "Not provided"
            )

            st.write(
                "**Original Complaint:**"
            )

            st.info(
                case.get(
                    "complaint_text",
                    "N/A"
                )
            )

        # =================================================
        # PIPELINE
        # =================================================

        st.markdown(
            "## 🤖 Agent State Analysis"
        )

        col1, col2, col3 = st.columns(3)

        # =================================================
        # NODE 1
        # =================================================

        with col1:

            with st.container(border=True):

                st.markdown(
                    "### 🔎 NODE 1"
                )

                st.markdown(
                    "**Complaint Analysis**"
                )

                st.write(
                    "**Crime Category:**"
                )

                st.success(
                    str(
                        case.get(
                            "crime_category",
                            "Unknown"
                        )
                    )
                )

                st.write(
                    "**Extracted Information:**"
                )

                extracted = case.get(
                    "extracted_information"
                ) or {}

                if extracted:

                    st.json(
                        extracted
                    )

                else:

                    st.info(
                        "No extracted information."
                    )

        # =================================================
        # NODE 2
        # =================================================

        with col2:

            with st.container(border=True):

                st.markdown(
                    "### 🧾 NODE 2"
                )

                st.markdown(
                    "**Evidence & Fraud Analysis**"
                )

                fraud_score = fraud.get(
                    "fraud_score",
                    0
                )

                st.metric(
                    "Fraud Score",
                    f"{fraud_score}/10"
                )

                st.write(
                    "**Fraud Level:**",
                    fraud.get(
                        "fraud_level",
                        "N/A"
                    )
                )

                indicators = fraud.get(
                    "fraud_indicators",
                    []
                )

                if not indicators:

                    indicators = fraud.get(
                        "indicators",
                        []
                    )

                st.write(
                    "**Fraud Indicators:**"
                )

                if indicators:

                    for indicator in indicators:

                        st.write(
                            f"• {indicator}"
                        )

                else:

                    st.info(
                        "No fraud indicators."
                    )

                st.write(
                    "**Evidence Found:**"
                )

                found = evidence.get(
                    "evidence_found",
                    []
                )

                if found:

                    for item in found:

                        st.write(
                            f"✅ {item}"
                        )

                else:

                    st.write(
                        "None"
                    )

                st.write(
                    "**Missing Evidence:**"
                )

                missing = evidence.get(
                    "missing_evidence",
                    []
                )

                if missing:

                    for item in missing:

                        st.write(
                            f"⚠️ {item}"
                        )

                else:

                    st.write(
                        "None"
                    )

        # =================================================
        # NODE 3
        # =================================================

        with col3:

            with st.container(border=True):

                st.markdown(
                    "### ⚠️ NODE 3"
                )

                st.markdown(
                    "**Risk & Decision**"
                )

                risk_score = risk.get(
                    "risk_score",
                    0
                )

                st.metric(
                    "Risk Score",
                    f"{risk_score}/100"
                )

                st.write(
                    "**Risk Level:**",
                    risk.get(
                        "risk_level",
                        "N/A"
                    )
                )

                st.write(
                    "**Priority:**",
                    risk.get(
                        "priority",
                        "N/A"
                    )
                )

                st.write(
                    "**Routing:**",
                    routing.get(
                        "route",
                        "N/A"
                    )
                )

                st.write(
                    "**Risk Factors:**"
                )

                factors = risk.get(
                    "risk_factors",
                    []
                )

                if factors:

                    for factor in factors:

                        st.write(
                            f"• {factor}"
                        )

                else:

                    st.info(
                        "No risk factors."
                    )

        # =================================================
        # NODE 4 - HITL
        # =================================================

        st.divider()

        st.markdown(
            "## 🧑‍⚖️ NODE 4: HUMAN REVIEW"
        )

        st.warning(
            "ACTION REQUIRED: Approve, Reject, or Escalate"
        )

        st.write(
            "The AI agents have completed their analysis. "
            "The officer must make the final decision."
        )

        col1, col2, col3 = st.columns(3)

        # APPROVE
        with col1:

            if st.button(
                "✅ APPROVE",
                type="primary",
                use_container_width=True
            ):

                with st.spinner(
                    "Submitting approval..."
                ):

                    result = submit_decision(
                        complaint_id,
                        "approve"
                    )

                if result:

                    st.success(
                        "Complaint approved successfully."
                    )

                    st.session_state[
                        "active_case"
                    ] = None

                    st.session_state[
                        "active_case_id"
                    ] = None

                    st.rerun()

        # REJECT
        with col2:

            if st.button(
                "❌ REJECT",
                use_container_width=True
            ):

                with st.spinner(
                    "Submitting rejection..."
                ):

                    result = submit_decision(
                        complaint_id,
                        "reject"
                    )

                if result:

                    st.success(
                        "Complaint rejected successfully."
                    )

                    st.session_state[
                        "active_case"
                    ] = None

                    st.session_state[
                        "active_case_id"
                    ] = None

                    st.rerun()

        # ESCALATE
        with col3:

            if st.button(
                "🚨 ESCALATE",
                use_container_width=True
            ):

                with st.spinner(
                    "Escalating complaint..."
                ):

                    result = submit_decision(
                        complaint_id,
                        "escalate"
                    )

                if result:

                    st.success(
                        "Complaint escalated successfully."
                    )

                    st.session_state[
                        "active_case"
                    ] = None

                    st.session_state[
                        "active_case_id"
                    ] = None

                    st.rerun()


# =========================================================
# MAIN NAVIGATION
# =========================================================

if "selected_module" not in st.session_state:

    st.session_state[
        "selected_module"
    ] = "👤 Citizen Complaint"


selected_module = st.sidebar.radio(
    "Select Module",
    [
        "👤 Citizen Complaint",
        "🛡️ Officer Workbench"
    ],
    index=[
        "👤 Citizen Complaint",
        "🛡️ Officer Workbench"
    ].index(
        st.session_state[
            "selected_module"
        ]
    )
)

st.session_state[
    "selected_module"
] = selected_module

st.sidebar.divider()

st.sidebar.caption(
    "AI Cyber Crime Complaint Processing System"
)

if selected_module == "👤 Citizen Complaint":

    citizen_page()

else:

    officer_page()
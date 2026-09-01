import streamlit as st
import requests

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="AI Crime Complaint System",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>
    .stApp {
        background-color: #f8fafc;
    }
    .main-header {
        padding: 1.5rem 2rem;
        border-radius: 12px;
        background: linear-gradient(135deg, #0f172a, #1e3a8a);
        color: white;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    .main-header h1 {
        margin: 0;
        font-size: 2.2rem;
        font-weight: 700;
    }
    .main-header p {
        margin-top: 0.4rem;
        margin-bottom: 0;
        opacity: 0.85;
        font-size: 1rem;
    }
    .info-card {
        background: white;
        padding: 1.25rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        height: 100%;
    }
    .card-title {
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748b;
        margin-bottom: 0.5rem;
    }
    .card-value {
        font-size: 1.4rem;
        font-weight: 700;
        color: #0f172a;
    }
    .review-box {
        background: #fff7ed;
        border: 1px solid #fed7aa;
        padding: 1.25rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
    }
    .success-box {
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        padding: 1.25rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
    }
    .section-title {
        margin-top: 0.5rem;
        margin-bottom: 1rem;
        color: #0f172a;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# API CONFIGURATION
# =========================================================

API_URL = "http://127.0.0.1:8000"

# =========================================================
# SESSION STATE INITIALIZATION
# =========================================================

if "complaint_id" not in st.session_state:
    st.session_state.complaint_id = None

if "review_data" not in st.session_state:
    st.session_state.review_data = None

if "final_data" not in st.session_state:
    st.session_state.final_data = None

if "nav_page" not in st.session_state:
    st.session_state.nav_page = "Submit Complaint"

# =========================================================
# HEADER
# =========================================================

st.markdown(
    """
    <div class="main-header">
        <h1>🚨 AI Cyber Crime Intake & Triaging System</h1>
        <p>Real-time AI risk assessment, automated classification, and human officer review pipeline.</p>
    </div>
    """,
    unsafe_allow_html=True
)

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:
    st.markdown("### 🛡️ Navigation")

    selected_page = st.radio(
        "Select Page",
        ["Submit Complaint", "Case Result"],
        index=0 if st.session_state.nav_page == "Submit Complaint" else 1,
        key="nav_selection"
    )

    st.session_state.nav_page = selected_page

    st.divider()
    st.markdown("### 🔄 Workflow")
    st.markdown(
        """
        1. 📥 Complaint Intake
        2. 🤖 AI Analysis
        3. ⚖️ Risk Assessment
        4. 👮 Human Review
        5. 🎯 Final Decision
        """
    )

    st.divider()

    if st.button("🔄 Reset Workflow", use_container_width=True):
        st.session_state.complaint_id = None
        st.session_state.review_data = None
        st.session_state.final_data = None
        st.session_state.nav_page = "Submit Complaint"
        st.rerun()

# =========================================================
# SUBMIT COMPLAINT PAGE
# =========================================================

if st.session_state.nav_page == "Submit Complaint":

    if st.session_state.review_data:
        st.warning("⚠️ You have a case pending officer review. Please complete the officer decision below.")

    st.markdown('<h3 class="section-title">📝 New Complaint Intake</h3>', unsafe_allow_html=True)
    st.write("Provide the complaint details and supporting evidence.")

    with st.form("complaint_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        with col1:
            user_name = st.text_input("Complainant Full Name", placeholder="e.g. John Doe")
        with col2:
            contact_number = st.text_input("Contact Phone/Email", placeholder="e.g. 9999999999")

        complaint_text = st.text_area(
            "Incident Description",
            placeholder="Describe what happened. Mention communication method, financial loss, OTP, UPI, suspicious links, phone numbers, etc.",
            height=160
        )

        st.subheader("📎 Supporting Evidence")
        ev_col1, ev_col2 = st.columns(2)

        with ev_col1:
            transaction_id = st.text_input("Transaction ID (Optional)", placeholder="e.g. TXN123456789")
            transaction_receipt = st.file_uploader(
                "Transaction Receipt",
                type=["png", "jpg", "jpeg", "pdf"],
                help="Upload a transaction or payment receipt."
            )

        with ev_col2:
            screenshot = st.file_uploader(
                "Screenshots (Chat/Fraud Site)",
                type=["png", "jpg", "jpeg"],
                help="Upload screenshots of chats, websites, or fraud messages."
            )
            other_doc = st.file_uploader(
                "Other Supporting Documents",
                type=["pdf", "txt", "docx"],
                help="Upload additional supporting documents."
            )

        submitted = st.form_submit_button("🚀 Run AI Analysis & Submit", type="primary", use_container_width=True)

    if submitted:
        if not user_name.strip():
            st.warning("Please provide the complainant's name.")
        elif not contact_number.strip():
            st.warning("Please provide the contact number.")
        elif not complaint_text.strip():
            st.warning("Please provide the complaint details.")
        else:
            payload = {
                "complaint_text": complaint_text.strip(),
                "user_name": user_name.strip(),
                "contact_number": contact_number.strip(),
                "transaction_id": transaction_id.strip()
            }

            files = {}
            if transaction_receipt:
                files["transaction_receipt"] = (
                    transaction_receipt.name,
                    transaction_receipt.getvalue(),
                    transaction_receipt.type
                )
            if screenshot:
                files["screenshot"] = (
                    screenshot.name,
                    screenshot.getvalue(),
                    screenshot.type
                )
            if other_doc:
                files["other_evidence"] = (
                    other_doc.name,
                    other_doc.getvalue(),
                    other_doc.type
                )

            try:
                with st.spinner("🤖 AI agents are analyzing the complaint..."):
                    response = requests.post(
                        f"{API_URL}/complaints",
                        data=payload,
                        files=files if files else None,
                        timeout=120
                    )

                if response.status_code == 200:
                    try:
                        data = response.json()
                    except ValueError:
                        st.error("FastAPI returned an invalid JSON response.")
                        st.code(response.text)
                        st.stop()

                    status = data.get("status")

                    if status == "human_review_required":
                        st.session_state.complaint_id = data.get("complaint_id")
                        st.session_state.review_data = data
                        st.session_state.final_data = None
                        st.success("✅ AI analysis completed. Human officer review is required.")
                        st.rerun()

                    elif status == "completed":
                        st.session_state.final_data = data
                        st.session_state.review_data = None
                        st.session_state.complaint_id = data.get("complaint_id")
                        st.session_state.nav_page = "Case Result"
                        st.success("✅ Complaint processing completed.")
                        st.rerun()

                    else:
                        st.error("The API returned an unexpected workflow status.")
                        st.json(data)
                else:
                    st.error(f"API Error: {response.status_code}")
                    st.code(response.text)

            except requests.exceptions.ConnectionError:
                st.error("Backend unreachable.")
                st.info("Start FastAPI in another terminal:")
                st.code("uvicorn api.main:app --reload")

            except requests.exceptions.Timeout:
                st.error("The AI workflow timed out after 120 seconds.")

            except Exception as e:
                st.error(f"Execution Error: {str(e)}")

    if st.session_state.review_data:
        data = st.session_state.review_data
        risk = data.get("risk_assessment", {})
        evidence = data.get("evidence_analysis", {})
        fraud = data.get("fraud_analysis", {})

        st.divider()
        st.markdown(
            """
            <div class="review-box">
                <h3 style="margin:0; color:#9a3412;">⚠️ Human Officer Review Required</h3>
                <p style="margin-top:0.4rem; color:#c2410c;">The automated system flagged this complaint for manual officer review.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        col1, col2, col3, col4 = st.columns(4)
        col1.markdown(f'<div class="info-card"><div class="card-title">Complaint ID</div><div class="card-value">{data.get("complaint_id", "N/A")}</div></div>', unsafe_allow_html=True)
        col2.markdown(f'<div class="info-card"><div class="card-title">Category</div><div class="card-value">{data.get("crime_category", "N/A")}</div></div>', unsafe_allow_html=True)
        col3.markdown(f'<div class="info-card"><div class="card-title">Risk Level</div><div class="card-value">{risk.get("risk_level", "N/A")}</div></div>', unsafe_allow_html=True)
        col4.markdown(f'<div class="info-card"><div class="card-title">Priority</div><div class="card-value">{risk.get("priority", "N/A")}</div></div>', unsafe_allow_html=True)

        st.write("")
        st.subheader("📊 Analysis Insights")
        r1, r2, r3 = st.columns(3)
        r1.metric("Risk Score", f"{risk.get('risk_score', 'N/A')}/100")
        r2.metric("Fraud Score", f"{fraud.get('fraud_score', 'N/A')}/10")
        r3.metric("Fraud Level", fraud.get("fraud_level", "N/A"))

        factors = risk.get("risk_factors", [])
        if factors:
            st.write("**Identified Risk Factors:**")
            for item in factors:
                st.write(f"• {item}")

        indicators = fraud.get("indicators", [])
        if indicators:
            st.write("**Fraud Indicators:**")
            for item in indicators:
                st.write(f"🔎 {item}")

        st.subheader("📎 Evidence Analysis")
        if evidence.get("evidence_available", False):
            st.success("Evidence detected.")
        else:
            st.warning("No supporting evidence detected.")

        evidence_found = evidence.get("evidence_found", [])
        if evidence_found:
            st.write("**Evidence Found:**")
            for item in evidence_found:
                st.write(f"✅ {item}")

        missing = evidence.get("missing_evidence", [])
        if missing:
            st.write("**Missing Evidence:**")
            for item in missing:
                st.write(f"• {item}")

        st.divider()
        st.subheader("👮 Officer Decision Panel")
        st.caption(data.get("question", "Approve, reject, or escalate this complaint?"))

        d_col1, d_col2, d_col3 = st.columns(3)

        def send_decision(decision_type):
            complaint_id = st.session_state.complaint_id
            if not complaint_id:
                st.error("Complaint ID is missing.")
                return

            try:
                with st.spinner("Submitting officer decision..."):
                    res = requests.post(
                        f"{API_URL}/complaints/{complaint_id}/decision",
                        json={"complaint_id": complaint_id, "decision": decision_type},
                        timeout=120
                    )

                if res.status_code == 200:
                    final_data = res.json()
                    st.session_state.final_data = final_data
                    st.session_state.review_data = None
                    st.session_state.nav_page = "Case Result"
                    st.rerun()
                else:
                    st.error(f"Decision API Error: {res.status_code}")
                    st.code(res.text)

            except requests.exceptions.ConnectionError:
                st.error("Backend unreachable. Make sure FastAPI is running.")
            except requests.exceptions.Timeout:
                st.error("Officer decision request timed out.")
            except Exception as e:
                st.error(f"Failed to submit decision: {str(e)}")

        with d_col1:
            if st.button("✅ Approve Case", use_container_width=True, type="primary"):
                send_decision("approve")

        with d_col2:
            if st.button("❌ Reject Case", use_container_width=True):
                send_decision("reject")

        with d_col3:
            if st.button("⬆️ Escalate", use_container_width=True):
                send_decision("escalate")

# =========================================================
# CASE RESULT PAGE
# =========================================================

elif st.session_state.nav_page == "Case Result":

    if not st.session_state.final_data:
        st.info("No completed case is available. Please submit a complaint first.")

    else:
        data = st.session_state.final_data
        result = data.get("result", {})
        if not isinstance(result, dict):
            result = {}

        risk = result.get("risk_assessment", {})
        fraud = result.get("fraud_analysis", {})
        routing = result.get("routing_decision", {})
        evidence = result.get("evidence_analysis", {})

        st.markdown(
            """
            <div class="success-box">
                <h3 style="margin:0; color:#166534;">✅ Complaint Processing Completed</h3>
                <p style="margin-top:0.4rem; color:#15803d;">The complaint has completed the AI triage and human review workflow.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.subheader("📋 Final Complaint Result")
        c1, c2, c3, c4 = st.columns(4)

        complaint_id = result.get("complaint_id", data.get("complaint_id", "N/A"))
        case_status = result.get("case_status", "N/A")
        category = result.get("crime_category", "N/A")

        c1.metric("Complaint ID", complaint_id)
        c2.metric("Case Status", case_status)
        c3.metric("Crime Category", category)
        c4.metric("Priority", risk.get("priority", "N/A"))

        st.divider()
        st.subheader("🔍 Crime & Fraud Analysis")

        a1, a2, a3, a4 = st.columns(4)
        a1.metric("Fraud Score", f"{fraud.get('fraud_score', 'N/A')}/10")
        a2.metric("Fraud Level", fraud.get("fraud_level", "N/A"))
        a3.metric("Risk Score", f"{risk.get('risk_score', 'N/A')}/100")
        a4.metric("Risk Level", risk.get("risk_level", "N/A"))

        indicators = fraud.get("indicators", [])
        if indicators:
            st.write("**Fraud Indicators:**")
            for item in indicators:
                st.write(f"🔎 {item}")

        st.divider()
        st.subheader("⚠️ Risk Assessment")

        risk_factors = risk.get("risk_factors", [])
        if risk_factors:
            for item in risk_factors:
                st.write(f"• {item}")
        else:
            st.write("No additional risk factors.")

        st.divider()
        st.subheader("👮 Routing Decision")

        route_col1, route_col2 = st.columns(2)
        with route_col1:
            st.write("**Route:**")
            st.write(routing.get("route", "N/A"))
        with route_col2:
            st.write("**Next Action:**")
            st.write(routing.get("next_action", "N/A"))

        st.divider()
        st.subheader("📎 Evidence Analysis")

        if evidence.get("evidence_available", False):
            st.success("Evidence Available")
        else:
            st.warning("Evidence Not Available")

        evidence_found = evidence.get("evidence_found", [])
        if evidence_found:
            st.write("**Evidence Found:**")
            for item in evidence_found:
                st.write(f"✅ {item}")

        missing_evidence = evidence.get("missing_evidence", [])
        if missing_evidence:
            st.write("**Missing Evidence:**")
            for item in missing_evidence:
                st.write(f"• {item}")

        st.divider()
        st.subheader("👮 Final Officer Decision")

        decision = data.get("officer_decision", result.get("officer_decision", "N/A"))
        decision = str(decision).lower()

        if decision == "approve":
            st.success("✅ APPROVED")
        elif decision == "reject":
            st.error("❌ REJECTED")
        elif decision == "escalate":
            st.warning("⬆️ ESCALATED TO HIGHER AUTHORITY")
        else:
            st.info(f"ℹ️ {decision.upper()}")
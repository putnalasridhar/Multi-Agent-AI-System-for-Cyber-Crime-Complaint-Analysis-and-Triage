from typing import Dict, TypedDict, List, Optional, Any, cast
import re
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command
from langchain_openai import ChatOpenAI
import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
complaint_registry = {}

# =========================================================
# COMPLAINT INPUT
# =========================================================

class ComplaintInput(TypedDict):
    complaint_text: str
    user_name: str
    contact_number: str
    transaction_id: str

# =========================================================
# AGENT STATE
# =========================================================

class AgentState(TypedDict, total=False):
    complaint_text: str
    user_name: str
    contact_number: str
    transaction_id: str
    complaint_id: str
    validation_status: str
    missing_fields: List[str]
    extracted_information: Dict[str, Any]
    crime_category: str
    intake_status: str
    evidence_analysis: Dict[str, Any]
    fraud_analysis: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    routing_decision: Dict[str, Any]
    officer_decision: Optional[str]
    case_status: str
    final_response: str

    #Guardrail fields
    guardrail_status: str
    guardrail_errors: List[str]
    output_guardrail_status: str
    output_guardrail_errors: List[str]

# =========================================================
# INPUT GUARDRAIL
# =========================================================

def input_guardrail(state: AgentState) -> AgentState:
    """
    Validates and sanitizes complaint input before
    sending it to the AI agents.
    """

    complaint_text = str(state.get("complaint_text", "")).strip()
    user_name = str(state.get("user_name", "")).strip()
    contact_number = str(state.get("contact_number", "")).strip()
    transaction_id = str(state.get("transaction_id", "")).strip()

    guardrail_errors = []

    # Check required fields
    if not complaint_text:
        guardrail_errors.append("Complaint text is required.")

    if not user_name:
        guardrail_errors.append("User name is required.")

    if not contact_number:
        guardrail_errors.append("Contact number is required.")

    # Complaint length validation
    if len(complaint_text) > 10000:
        guardrail_errors.append(
            "Complaint text is too long. Maximum 10,000 characters allowed."
        )

    # Minimum complaint length
    if complaint_text and len(complaint_text) < 10:
        guardrail_errors.append(
            "Complaint description is too short."
        )

    # Basic contact number validation
    if contact_number:
        digits = re.sub(r"\D", "", contact_number)

        if len(digits) < 10 or len(digits) > 15:
            guardrail_errors.append(
                "Invalid contact number."
            )

    # Transaction ID length validation
    if len(transaction_id) > 100:
        guardrail_errors.append(
            "Invalid transaction ID."
        )

    # Return guardrail result
    if guardrail_errors:
        return {
            **state,
            "guardrail_status": "blocked",
            "guardrail_errors": guardrail_errors,
            "case_status": "input_rejected",
            "final_response": (
                "Complaint could not be processed because "
                "the submitted information is invalid."
            )
        }

    return {
        **state,
        "complaint_text": complaint_text,
        "user_name": user_name,
        "contact_number": contact_number,
        "transaction_id": transaction_id,
        "guardrail_status": "passed",
        "guardrail_errors": []
    }


# =========================================================
# AGENT 1 - COMPLAINT ANALYSIS
# =========================================================

def complaint_analysis_agent(complaint: ComplaintInput) -> Dict:
    print("\n--- Complaint Analysis Agent ---")
    complaint_text = complaint.get("complaint_text", "")
    user_name = complaint.get("user_name", "")
    contact_number = complaint.get("contact_number", "")
    transaction_id = complaint.get("transaction_id", "")
    print("Complaint received successfully.")

    required_fields = ["complaint_text", "user_name", "contact_number"]
    missing_fields = []
    for field in required_fields:
        value = complaint.get(field)
        if not value or not str(value).strip():
            missing_fields.append(field)

    if missing_fields:
        validation_status = "incomplete"
        print("Complaint validation failed.")
        print("Missing fields:", missing_fields)
    else:
        validation_status = "valid"
        print("Complaint validation successful.")

    text = complaint_text.lower()
    crime_category = "unknown"

    if any(keyword in text for keyword in ["upi", "upi payment", "upi fraud", "upi scam"]):
        crime_category = "upi_fraud"
    elif any(keyword in text for keyword in ["phishing", "fake link", "suspicious link", "login link"]):
        crime_category = "phishing"
    elif any(keyword in text for keyword in ["investment", "trading scam", "crypto scam", "investment fraud"]):
        crime_category = "investment_fraud"
    elif any(keyword in text for keyword in ["online shopping", "fake product", "product scam", "shopping fraud"]):
        crime_category = "online_shopping_fraud"
    elif any(keyword in text for keyword in ["otp", "one time password", "bank officer", "bank account"]):
        crime_category = "banking_fraud"
    elif any(keyword in text for keyword in ["identity theft", "stolen identity", "personal information"]):
        crime_category = "identity_theft"
    elif any(keyword in text for keyword in ["instagram", "facebook", "social media", "social media account"]):
        crime_category = "social_media_fraud"
    elif any(keyword in text for keyword in ["job scam", "fake job", "employment fraud"]):
        crime_category = "job_fraud"
    elif any(keyword in text for keyword in ["ransomware", "encrypted files", "files encrypted"]):
        crime_category = "ransomware"

    print(f"Detected category: {crime_category}")

    amount = None
    amount_patterns = [
        r"₹\s?([\d,]+)",
        r"rs\.?\s?([\d,]+)",
        r"rupees?\s?([\d,]+)",
        r"INR\s?([\d,]+)"
    ]

    for pattern in amount_patterns:
        match = re.search(pattern, complaint_text, re.IGNORECASE)
        if match:
            try:
                amount = int(match.group(1).replace(",", ""))
                break
            except ValueError:
                pass

    phone_numbers = re.findall(
        r"(?<!\d)(?:\+91[\s-]?)?[6-9]\d{9}(?!\d)",
        complaint_text
    )
    phone_numbers = list(dict.fromkeys(phone_numbers))

    email_addresses = re.findall(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        complaint_text
    )
    email_addresses = list(dict.fromkeys(email_addresses))

    urls = re.findall(r"https?://[^\s]+", complaint_text)
    urls = list(dict.fromkeys(urls))

    upi_id = None
    upi_pattern = r"\b[\w.-]+@[\w.-]+\b"
    matches = re.findall(upi_pattern, complaint_text)

    for value in matches:
        value_lower = value.lower()
        if not any(value_lower.endswith(extension) for extension in [".com", ".in", ".org", ".net"]):
            upi_id = value
            break

    if not transaction_id:
        transaction_patterns = [
            r"transaction\s*(?:id|number|reference)\s*[:#-]?\s*([A-Za-z0-9_-]{6,})",
            r"txn\s*(?:id|number)?\s*[:#-]?\s*([A-Za-z0-9_-]{6,})"
        ]
        for pattern in transaction_patterns:
            match = re.search(pattern, complaint_text, re.IGNORECASE)
            if match:
                transaction_id = match.group(1)
                break

    extracted_information = {
        "amount": amount,
        "phone_numbers": phone_numbers,
        "email_addresses": email_addresses,
        "urls": urls,
        "upi_id": upi_id,
        "transaction_id": transaction_id
    }

    print("Extracted information:")
    print(extracted_information)

    return {
        **complaint,
        "validation_status": validation_status,
        "missing_fields": missing_fields,
        "extracted_information": extracted_information,
        "crime_category": crime_category,
        "intake_status": "received"
    }

# =========================================================
# AGENT 2 - EVIDENCE & FRAUD ANALYSIS
# =========================================================

def evidence_fraud_agent(state: AgentState) -> Dict:
    print("\n--- Evidence & Fraud Analysis Agent ---")

    complaint_text = state.get("complaint_text", "")
    extracted = state.get("extracted_information", {})
    text = complaint_text.lower()

    evidence = []
    missing_evidence = []

    transaction_id = extracted.get("transaction_id")
    if transaction_id:
        evidence.append("transaction_id")
    else:
        missing_evidence.append("transaction_id")

    if any(word in text for word in ["receipt", "payment receipt", "transaction receipt"]):
        evidence.append("transaction_receipt")
    else:
        missing_evidence.append("transaction_receipt")

    if any(word in text for word in ["screenshot", "screen shot", "image"]):
        evidence.append("screenshot")
    else:
        missing_evidence.append("screenshot")

    if any(word in text for word in ["document", "proof", "attachment"]):
        evidence.append("other_document")

    if any(word in text for word in ["message", "chat", "whatsapp"]):
        evidence.append("message_chat")

    if extracted.get("email_addresses"):
        evidence.append("email")

    if extracted.get("phone_numbers"):
        evidence.append("phone_number")

    if extracted.get("urls"):
        evidence.append("url")

    evidence = list(dict.fromkeys(evidence))
    evidence_available = len(evidence) > 0

    evidence_analysis = {
        "evidence_found": evidence,
        "missing_evidence": missing_evidence,
        "evidence_available": evidence_available,
        "evidence_status": "available" if evidence_available else "not_available"
    }

    fraud_score = 0
    indicators = []

    if any(word in text for word in ["otp", "one time password"]):
        fraud_score += 2
        indicators.append("OTP related activity")

    if any(word in text for word in ["bank officer", "bank employee", "bank official"]):
        fraud_score += 2
        indicators.append("Possible bank impersonation")

    if any(word in text for word in ["upi", "upi payment", "digital payment"]):
        fraud_score += 2
        indicators.append("UPI or digital payment")

    amount = extracted.get("amount")

    if amount is not None:
        if amount >= 50000:
            fraud_score += 3
            indicators.append("High financial loss")
        elif amount >= 10000:
            fraud_score += 2
            indicators.append("Significant financial loss")
        else:
            fraud_score += 1
            indicators.append("Financial loss")
    elif any(word in text for word in ["money", "lost money", "payment", "transferred", "transfer"]):
        fraud_score += 2
        indicators.append("Financial loss mentioned")

    if extracted.get("urls"):
        fraud_score += 2
        indicators.append("Suspicious URL")

    if extracted.get("phone_numbers"):
        fraud_score += 1
        indicators.append("Phone number available")

    if extracted.get("upi_id"):
        fraud_score += 1
        indicators.append("UPI ID available")

    fraud_score = min(fraud_score, 10)

    if fraud_score >= 7:
        fraud_level = "high"
    elif fraud_score >= 4:
        fraud_level = "medium"
    else:
        fraud_level = "low"

    indicators = list(dict.fromkeys(indicators))

    fraud_analysis = {
        "fraud_score": fraud_score,
        "fraud_level": fraud_level,
        "fraud_indicators": indicators
    }

    print("Evidence:", evidence_analysis)
    print("Fraud:", fraud_analysis)

    return {
        **state,
        "evidence_analysis": evidence_analysis,
        "fraud_analysis": fraud_analysis
    }

# =========================================================
# AGENT 3 - RISK & DECISION
# =========================================================

def risk_decision_agent(state: AgentState) -> Dict:
    print("\n--- Risk & Decision Agent ---")

    fraud_analysis = state.get("fraud_analysis", {})
    evidence_analysis = state.get("evidence_analysis", {})
    crime_category = state.get("crime_category", "unknown")

    fraud_score = fraud_analysis.get("fraud_score", 0)
    risk_score = fraud_score * 10
    risk_factors = []

    evidence_available = evidence_analysis.get(
        "evidence_available",
        False
    )

    missing_evidence = evidence_analysis.get(
        "missing_evidence",
        []
    )

    if not evidence_available:
        risk_score += 20
        risk_factors.append("Supporting evidence is limited")
    elif len(missing_evidence) >= 2:
        risk_score += 10
        risk_factors.append("Some important evidence is missing")

    if crime_category == "upi_fraud":
        risk_score += 10
        risk_factors.append(
            "Category requires careful review: upi_fraud"
        )

    risk_score = min(risk_score, 100)

    if risk_score >= 70:
        risk_level = "high"
    elif risk_score >= 40:
        risk_level = "medium"
    else:
        risk_level = "low"

    if risk_score >= 70:
        priority = "critical"
    elif risk_score >= 40:
        priority = "high"
    elif risk_score >= 20:
        priority = "medium"
    else:
        priority = "low"

    if risk_level == "high":
        route = "urgent_human_review"
        routing_message = (
            "Send complaint for urgent officer review."
        )
    elif risk_level == "medium":
        route = "human_review"
        routing_message = (
            "Send complaint for officer review."
        )
    else:
        route = "normal_processing"
        routing_message = (
            "Continue with normal complaint processing."
        )

    risk_assessment = {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "priority": priority,
        "risk_factors": risk_factors
    }

    routing_decision = {
        "route": route,
        "message": routing_message
    }

    print("Risk assessment:", risk_assessment)
    print("Routing decision:", routing_decision)

    return {
        **state,
        "risk_assessment": risk_assessment,
        "routing_decision": routing_decision
    }

# =========================================================
# OUTPUT GUARDRAIL
# =========================================================

def output_guardrail(state: AgentState) -> AgentState:
    """
    Validates AI-generated output before it is used
    for routing and human review.
    """

    errors = []

    risk_assessment = state.get("risk_assessment", {})
    routing_decision = state.get("routing_decision", {})
    fraud_analysis = state.get("fraud_analysis", {})

    # -----------------------------------------------------
    # Validate Risk Score
    # -----------------------------------------------------

    risk_score = risk_assessment.get("risk_score")

    if risk_score is None:
        errors.append("Risk score is missing.")

    else:
        try:
            risk_score = float(risk_score)

            if risk_score < 0 or risk_score > 100:
                errors.append(
                    "Risk score must be between 0 and 100."
                )

        except (TypeError, ValueError):
            errors.append(
                "Risk score must be numeric."
            )

    # -----------------------------------------------------
    # Validate Risk Level
    # -----------------------------------------------------

    valid_risk_levels = {
        "low",
        "medium",
        "high"
    }

    risk_level = risk_assessment.get("risk_level")

    if risk_level not in valid_risk_levels:
        errors.append(
            "Invalid risk level generated by AI."
        )

    # -----------------------------------------------------
    # Validate Priority
    # -----------------------------------------------------

    valid_priorities = {
        "low",
        "medium",
        "high",
        "critical"
    }

    priority = risk_assessment.get("priority")

    if priority not in valid_priorities:
        errors.append(
            "Invalid priority generated by AI."
        )

    # -----------------------------------------------------
    # Validate Routing Decision
    # -----------------------------------------------------

    valid_routes = {
        "normal_processing",
        "human_review",
        "urgent_human_review"
    }

    route = routing_decision.get("route")

    if route not in valid_routes:
        errors.append(
            "Invalid routing decision generated by AI."
        )

    # -----------------------------------------------------
    # Validate Fraud Score
    # -----------------------------------------------------

    fraud_score = fraud_analysis.get("fraud_score")

    if fraud_score is not None:

        try:
            fraud_score = float(fraud_score)

            if fraud_score < 0 or fraud_score > 10:
                errors.append(
                    "Fraud score must be between 0 and 10."
                )

        except (TypeError, ValueError):
            errors.append(
                "Fraud score must be numeric."
            )

    # -----------------------------------------------------
    # If Output Guardrail Fails
    # -----------------------------------------------------

    if errors:

        print("OUTPUT GUARDRAIL BLOCKED:", errors)

        return {
            **state,

            "output_guardrail_status": "blocked",

            "output_guardrail_errors": errors,

            # Force manual review
            "routing_decision": {
                "route": "urgent_human_review",
                "message": (
                    "AI output failed validation. "
                    "Manual officer review is required."
                )
            },

            "case_status": "guardrail_review",

            "final_response": (
                "AI analysis requires human verification "
                "before the complaint can be processed."
            )
        }

    # -----------------------------------------------------
    # If Output Guardrail Passes
    # -----------------------------------------------------

    print("OUTPUT GUARDRAIL PASSED")

    return {
        **state,

        "output_guardrail_status": "passed",

        "output_guardrail_errors": []
    }

# =========================================================
# INPUT GUARDRAIL ROUTER
# =========================================================

def input_guardrail_router(state: AgentState):
    if state.get("guardrail_status") == "blocked":
        return "blocked"
    return "passed"


# =========================================================
# OUTPUT GUARDRAIL ROUTER
# =========================================================

def output_guardrail_router(state: AgentState):
    if state.get("output_guardrail_status") == "blocked":
        return "blocked"
    return "passed"


# =========================================================
# NODE 1 - COMPLAINT ANALYSIS
# =========================================================

def complaint_analysis_node(state: AgentState) -> AgentState:
    result = complaint_analysis_agent({
        "complaint_text": state.get("complaint_text", ""),
        "user_name": state.get("user_name", ""),
        "contact_number": state.get("contact_number", ""),
        "transaction_id": state.get("transaction_id", "")
    })
    merged_state = dict(state)
    merged_state.update(result)
    return cast(AgentState, merged_state)
# =========================================================
# NODE 2 - EVIDENCE & FRAUD ANALYSIS
# =========================================================

def evidence_fraud_node(state: AgentState) -> AgentState:
    result = evidence_fraud_agent(state)
    merged_state = dict(state)
    merged_state.update(result)
    return cast(AgentState, merged_state)

# =========================================================
# NODE 3 - RISK & DECISION
# =========================================================

def risk_decision_node(state: AgentState) -> AgentState:
    result = risk_decision_agent(state)
    merged_state = dict(state)
    merged_state.update(result)
    return cast(AgentState, merged_state)
# =========================================================
# NODE 4 - HUMAN REVIEW
# =========================================================

def human_review_node(state: AgentState) -> AgentState:
    routing = state.get("routing_decision", {})
    route = routing.get("route", "normal_processing")

    if route == "normal_processing":
        return {
            **state,
            "officer_decision": "auto_approved",
            "case_status": "approved",
            "final_response": (
                "Complaint processed successfully "
                "through normal processing."
            )
        }

    decision = interrupt({
        "message": "Officer review required.",
        "question": "Please approve, reject, or escalate this complaint.",
        "risk_assessment": state.get("risk_assessment", {}),
        "routing_decision": routing,
        "crime_category": state.get("crime_category"),
        "fraud_analysis": state.get("fraud_analysis"),
        "evidence_analysis": state.get("evidence_analysis")
    })

    officer_decision = decision.get("decision", "escalate")

    if officer_decision == "approve":
        case_status = "approved"
        final_response = "Complaint approved by human officer."
    elif officer_decision == "reject":
        case_status = "rejected"
        final_response = "Complaint rejected by human officer."
    else:
        case_status = "escalated"
        final_response = "Complaint escalated for further investigation."

    return {
        **state,
        "officer_decision": officer_decision,
        "case_status": case_status,
        "final_response": final_response
    }

# =========================================================
# BUILD LANGGRAPH WORKFLOW
# =========================================================

def build_workflow():
    workflow = StateGraph(AgentState)

    # =====================================================
    # NODES
    # =====================================================

    workflow.add_node(
        "input_guardrail",
        input_guardrail
    )

    workflow.add_node(
        "complaint_analysis",
        complaint_analysis_node
    )

    workflow.add_node(
        "evidence_fraud_analysis",
        evidence_fraud_node
    )

    workflow.add_node(
        "risk_decision",
        risk_decision_node
    )

    workflow.add_node(
        "output_guardrail",
        output_guardrail
    )

    workflow.add_node(
        "human_review",
        human_review_node
    )

    # =====================================================
    # EDGES
    # =====================================================

    workflow.add_edge(
        START,
        "input_guardrail"
    )

    # Input guardrail decides whether the complaint is safe
    # and valid enough to enter the AI processing pipeline.
    workflow.add_conditional_edges(
        "input_guardrail",
        input_guardrail_router,
        {
            "passed": "complaint_analysis",
            "blocked": END
        }
    )

    workflow.add_edge(
        "complaint_analysis",
        "evidence_fraud_analysis"
    )

    workflow.add_edge(
        "evidence_fraud_analysis",
        "risk_decision"
    )

    # Output guardrail validates the complete AI result before
    # it is used for routing and human decision-making.
    workflow.add_edge(
        "risk_decision",
        "output_guardrail"
    )

    # A failed output guardrail forces the case to human review.
    # A passed result also goes through the existing HITL node,
    # which automatically approves low-risk cases and interrupts
    # for officer review when required.
    workflow.add_conditional_edges(
        "output_guardrail",
        output_guardrail_router,
        {
            "passed": "human_review",
            "blocked": "human_review"
        }
    )

    workflow.add_edge(
        "human_review",
        END
    )

    memory = MemorySaver()

    return workflow.compile(
        checkpointer=memory
    )


graph = build_workflow()


# =========================================================
# FASTAPI BACKEND
# =========================================================


app = FastAPI(
    title="Cyber Crime Complaint API",
    description="AI-based Cyber Crime Complaint Processing System",
    version="1.0.0"
)

class ComplaintRequest(BaseModel):
    complaint_text: str
    user_name: str
    contact_number: str
    transaction_id: str = ""

class OfficerDecision(BaseModel):
    decision: str

complaint_registry = {}

# =========================================================
# CREATE COMPLAINT
# =========================================================

@app.post("/complaints")
def create_complaint(payload: ComplaintRequest):
    complaint_id = f"CC{abs(hash(payload.complaint_text)) % 100000:05d}"

    complaint = {
        "complaint_id": complaint_id,
        "complaint_text": payload.complaint_text,
        "user_name": payload.user_name,
        "contact_number": payload.contact_number,
        "transaction_id": payload.transaction_id
    }

    config = {
        "configurable": {
            "thread_id": complaint_id
        }
    }

    result = graph.invoke(
        complaint,
        config=config
    )

    complaint_registry[complaint_id] = {
        "complaint_id": complaint_id,
        "user_name": payload.user_name,
        "contact_number": payload.contact_number,
        "complaint_text": payload.complaint_text,
        "transaction_id": payload.transaction_id,
        "status": "human_review_required" if "__interrupt__" in result else result.get("case_status", "processed"),
        "crime_category": result.get("crime_category"),
        "extracted_information": result.get("extracted_information"),
        "risk_assessment": result.get("risk_assessment"),
        "fraud_analysis": result.get("fraud_analysis"),
        "evidence_analysis": result.get("evidence_analysis"),
        "routing_decision": result.get("routing_decision"),
        "guardrail_status": result.get("guardrail_status"),
        "guardrail_errors": result.get("guardrail_errors", []),
        "output_guardrail_status": result.get("output_guardrail_status"),
        "output_guardrail_errors": result.get("output_guardrail_errors", []),
        "officer_decision": result.get("officer_decision"),
        "final_response": result.get("final_response")
    }

    if "__interrupt__" in result:
        interrupt_data = result["__interrupt__"][0]

        return {
            "complaint_id": complaint_id,
            "status": "human_review_required",
            "crime_category": result.get("crime_category"),
            "extracted_information": result.get("extracted_information"),
            "evidence_analysis": result.get("evidence_analysis"),
            "fraud_analysis": result.get("fraud_analysis"),
            "risk_assessment": result.get("risk_assessment", {}),
            "routing_decision": result.get("routing_decision", {}),
            "guardrail_status": result.get("guardrail_status"),
            "guardrail_errors": result.get("guardrail_errors", []),
            "output_guardrail_status": result.get("output_guardrail_status"),
            "output_guardrail_errors": result.get("output_guardrail_errors", []),
            "review": interrupt_data.value
        }

    return {
        "complaint_id": complaint_id,
        "status": result.get("case_status", "processed"),
        "crime_category": result.get("crime_category"),
        "extracted_information": result.get("extracted_information"),
        "evidence_analysis": result.get("evidence_analysis"),
        "fraud_analysis": result.get("fraud_analysis"),
        "risk_assessment": result.get("risk_assessment"),
        "routing_decision": result.get("routing_decision"),
        "guardrail_status": result.get("guardrail_status"),
        "guardrail_errors": result.get("guardrail_errors", []),
        "output_guardrail_status": result.get("output_guardrail_status"),
        "output_guardrail_errors": result.get("output_guardrail_errors", []),
        "final_response": result.get("final_response")
    }

# =========================================================
# PENDING HUMAN REVIEW
# IMPORTANT: KEEP THIS BEFORE /complaints/{complaint_id}
# =========================================================

@app.get("/complaints/pending")
def get_pending_complaints():
    pending = []

    for case in complaint_registry.values():
        if case.get("status") == "human_review_required":
            pending.append(case)

    pending.sort(
        key=lambda x: (
            x.get("risk_assessment") or {}
        ).get("risk_score", 0),
        reverse=True
    )

    return {
        "count": len(pending),
        "cases": pending
    }

# =========================================================
# HUMAN OFFICER DECISION
# =========================================================

@app.post("/complaints/{complaint_id}/decision")
def submit_decision(
    complaint_id: str,
    decision: OfficerDecision
):
    decision_value = decision.decision.lower().strip()

    if decision_value not in [
        "approve",
        "reject",
        "escalate"
    ]:
        raise HTTPException(
            status_code=400,
            detail="Decision must be approve, reject, or escalate."
        )

    config = {
        "configurable": {
            "thread_id": complaint_id
        }
    }

    try:
        current_state = graph.get_state(config)

        if not current_state or not current_state.values:
            raise HTTPException(
                status_code=404,
                detail="Complaint not found."
            )

        result = graph.invoke(
            Command(
                resume={
                    "decision": decision_value
                }
            ),
            config=config
        )

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to resume complaint: {error}"
        )

    # Update pending-case registry
    if complaint_id in complaint_registry:
        complaint_registry[complaint_id]["status"] = result.get(
            "case_status"
        )
        complaint_registry[complaint_id]["officer_decision"] = result.get(
            "officer_decision"
        )
        complaint_registry[complaint_id]["final_response"] = result.get(
            "final_response"
        )

    return {
        "complaint_id": complaint_id,
        "status": result.get("case_status"),
        "officer_decision": result.get("officer_decision"),
        "final_response": result.get("final_response")
    }

# =========================================================
# GET COMPLAINT STATUS
# IMPORTANT: KEEP THIS AFTER /complaints/pending
# =========================================================

@app.get("/complaints/{complaint_id}")
def get_complaint(complaint_id: str):
    config = {
        "configurable": {
            "thread_id": complaint_id
        }
    }

    state = graph.get_state(config)

    if not state or not state.values:
        raise HTTPException(
            status_code=404,
            detail="Complaint not found."
        )

    values = state.values

    return {
        "complaint_id": complaint_id,
        "user_name": values.get("user_name"),
        "contact_number": values.get("contact_number"),
        "transaction_id": values.get("transaction_id"),
        "complaint_text": values.get("complaint_text"),
        "case_status": values.get("case_status"),
        "crime_category": values.get("crime_category"),
        "extracted_information": values.get("extracted_information"),
        "evidence_analysis": values.get("evidence_analysis"),
        "fraud_analysis": values.get("fraud_analysis"),
        "risk_assessment": values.get("risk_assessment"),
        "routing_decision": values.get("routing_decision"),
        "guardrail_status": values.get("guardrail_status"),
        "guardrail_errors": values.get("guardrail_errors", []),
        "output_guardrail_status": values.get("output_guardrail_status"),
        "output_guardrail_errors": values.get("output_guardrail_errors", []),
        "officer_decision": values.get("officer_decision"),
        "final_response": values.get("final_response")
    }

#OPENAI_API_KEY
llm = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0
)

# =========================================================
# TEST THE WORKFLOW
# =========================================================

if __name__ == "__main__":
    complaint = {
        "complaint_id": "CC001",
        "complaint_text": (
            "I was cheated through a UPI scam. "
            "The fraudster asked me to transfer ₹60000. "
            "Transaction ID: TXN123456. "
            "They also sent me a suspicious link."
        ),
        "user_name": "Test User",
        "contact_number": "9876543210",
        "transaction_id": ""
    }

    config = {
        "configurable": {
            "thread_id": "case_CC001"
        }
    }

    print("\n========================================")
    print("CYBER CRIME COMPLAINT SYSTEM")
    print("========================================")

    result = graph.invoke(
        complaint,
        config=config
    )

    if "__interrupt__" in result:
        print("\n========================================")
        print("HUMAN REVIEW REQUIRED")
        print("========================================")

        print("Risk:", result["risk_assessment"])
        print("Routing:", result["routing_decision"])

        decision = input(
            "\nOfficer decision "
            "(approve/reject/escalate): "
        ).strip().lower()

        while decision not in ["approve", "reject", "escalate"]:
            print("Invalid decision.")
            decision = input(
                "Enter approve, reject, or escalate: "
            ).strip().lower()

        result = graph.invoke(
            Command(
                resume={
                    "decision": decision
                }
            ),
            config=config
        )

    print("\n========================================")
    print("FINAL RESULT")
    print("========================================")

    print("Case Status:", result.get("case_status"))
    print("Officer Decision:", result.get("officer_decision"))
    print("Final Response:", result.get("final_response"))
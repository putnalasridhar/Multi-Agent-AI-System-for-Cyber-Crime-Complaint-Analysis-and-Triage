from langgraph.types import Command

from app.graph.workflow import cyber_crime_graph


def main():

    complaint = {
        "complaint_id": "CC-005",

        "complaint_text": (
            "I received a fake bank call. "
            "The caller asked for my OTP and "
            "I lost 50000 rupees through UPI."
        ),

        "user_name": "Test User",
        "contact_number": "9999999999",

        "intake_status": "",
        "validation_status": "",
        "missing_fields": [],

        "extracted_information": {},
        "crime_category": "",

        "fraud_analysis": {},
        "evidence_analysis": {},

        "risk_assessment": {},
        "routing_decision": {},

        "officer_decision": None,
        "case_status": "",
        "final_response": ""
    }

    print("\n==============================")
    print(" CYBER CRIME AI SYSTEM")
    print("==============================\n")

    print("Complaint submitted...")
    print("Starting LangGraph workflow...\n")

    # LangGraph checkpointer configuration
    config = {
        "configurable": {
            "thread_id": "complaint-CC-005"
        }
    }

    # ==========================================
    # FIRST RUN
    # ==========================================

    result = cyber_crime_graph.invoke(
        complaint,
        config=config
    )

    # ==========================================
    # CHECK HUMAN REVIEW INTERRUPT
    # ==========================================

    state = cyber_crime_graph.get_state(config)

    if state.interrupts:

        interrupt_data = state.interrupts[0].value

        print("\n==============================")
        print(" HUMAN REVIEW REQUIRED")
        print("==============================\n")

        print("Message:")
        print(interrupt_data["message"])

        print("\nComplaint ID:")
        print(interrupt_data["complaint_id"])

        print("\nCrime Category:")
        print(interrupt_data["crime_category"])

        print("\nRisk Assessment:")
        print(interrupt_data["risk_assessment"])

        print("\nEvidence Analysis:")
        print(interrupt_data["evidence_analysis"])

        print("\nQuestion:")
        print(interrupt_data["question"])

        print("\nOfficer Decision Options:")
        print("1. approve")
        print("2. reject")
        print("3. escalate")

        decision = input(
            "\nEnter officer decision: "
        ).strip().lower()

        while decision not in [
            "approve",
            "reject",
            "escalate"
        ]:
            print("Invalid decision.")

            decision = input(
                "Enter approve / reject / escalate: "
            ).strip().lower()

        print("\nResuming workflow...")

        # ==========================================
        # RESUME AFTER HUMAN DECISION
        # ==========================================

        result = cyber_crime_graph.invoke(
            Command(resume=decision),
            config=config
        )

    # ==========================================
    # WORKFLOW COMPLETED
    # ==========================================

    print("\n==============================")
    print(" WORKFLOW COMPLETED")
    print("==============================\n")

    print("Final State:")
    print(result)


if __name__ == "__main__":
    main()
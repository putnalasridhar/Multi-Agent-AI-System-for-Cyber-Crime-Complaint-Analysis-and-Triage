# AI-Based Cyber Crime Complaint Intake & Triage System

## 📌 Overview

The **AI-Based Cyber Crime Complaint Intake & Triage System** is a multi-agent AI application designed to automate the initial processing, analysis, risk assessment, and routing of cyber-crime complaints.

The system accepts a complaint from a user and processes it through a sequence of specialized agents. Each agent performs a specific task such as validating the complaint, extracting important information, identifying the type of cyber crime, analyzing fraud indicators, evaluating evidence, calculating risk, and determining whether human intervention is required.

The system also includes **human-in-the-loop review** for high-risk or sensitive complaints.

---

## 🎯 Objectives

The main objectives of this project are:

* Automate the initial analysis of cyber-crime complaints.
* Extract important information from unstructured complaint text.
* Classify complaints into different cyber-crime categories.
* Identify potential fraud indicators.
* Evaluate the availability of supporting evidence.
* Calculate a risk score for each complaint.
* Automatically route complaints based on their risk level.
* Escalate high-risk complaints to human officers.
* Provide safety checks for both input and output.
* Maintain a structured and traceable complaint-processing workflow.

---

## 🏗️ System Architecture

The system follows a multi-agent workflow implemented using **LangGraph**.

```text
                    ┌────────────────────┐
                    │   User Complaint   │
                    └─────────┬──────────┘
                              ↓
                    ┌────────────────────┐
                    │  Input Guardrail   │
                    └─────────┬──────────┘
                              ↓
                    ┌────────────────────┐
                    │   Intake Agent     │
                    └─────────┬──────────┘
                              ↓
                    ┌────────────────────┐
                    │ Validation Agent   │
                    └─────────┬──────────┘
                              ↓
                    ┌────────────────────┐
                    │ Extraction Agent   │
                    └─────────┬──────────┘
                              ↓
              ┌───────────────┼───────────────┐
              ↓               ↓               ↓
       Classification     Fraud Analysis   Evidence
          Agent              Agent          Agent
              └───────────────┼───────────────┘
                              ↓
                    ┌────────────────────┐
                    │    Risk Agent      │
                    └─────────┬──────────┘
                              ↓
                    ┌────────────────────┐
                    │  Routing Agent     │
                    └─────────┬──────────┘
                              ↓
                    ┌────────────────────┐
                    │ Human Review if    │
                    │ Required           │
                    └─────────┬──────────┘
                              ↓
                    ┌────────────────────┐
                    │ Output Guardrail   │
                    └─────────┬──────────┘
                              ↓
                    ┌────────────────────┐
                    │   Final Result     │
                    └────────────────────┘
```

---

## 🤖 Multi-Agent Workflow

### 1. Intake Agent

Receives the cyber-crime complaint and initializes the complaint-processing workflow.

### 2. Validation Agent

Checks whether the complaint contains sufficient information for further processing.

It can validate information such as:

* Complaint description
* User details
* Contact information
* Required fields

### 3. Extraction Agent

Extracts useful entities from the complaint, including:

* Phone numbers
* Email addresses
* URLs
* UPI IDs
* Transaction IDs
* Transaction amounts
* Other relevant identifiers

### 4. Classification Agent

Determines the likely category of cyber crime.

Examples include:

* UPI Fraud
* Banking Fraud
* Phishing
* Investment Fraud
* Identity Theft
* Job Fraud
* Ransomware
* Other cyber-crime categories

### 5. Fraud Analysis Agent

Analyzes the complaint for fraud-related indicators.

Examples:

* OTP requests
* Suspicious links
* UPI transactions
* Unauthorized banking activity
* Financial loss
* Impersonation
* Account compromise

A fraud score is generated based on the identified indicators.

### 6. Evidence Agent

Checks whether useful supporting evidence is available.

Examples:

* Transaction ID
* Payment receipt
* Screenshot
* Email
* SMS
* Suspicious URL
* Other digital evidence

### 7. Risk Agent

Combines the results from the previous agents and calculates an overall risk score.

The system can categorize complaints as:

```text
Low Risk
Medium Risk
High Risk
```

### 8. Routing Agent

Determines the next step based on the risk level.

Possible outcomes include:

```text
Normal Processing
Human Review
Urgent Human Review
```

---

## 👨‍💼 Human-in-the-Loop

For cases that require additional verification, the workflow can pause and request a human decision.

The officer can:

* Approve
* Reject
* Escalate

This prevents the system from making critical decisions entirely automatically.

The human-in-the-loop functionality is implemented using **LangGraph workflow interruption and resumption**.

---

## 🛡️ Safety & Guardrails

The application contains safety mechanisms at both the input and output stages.

### Input Guardrail

The input guardrail checks for:

* Empty complaints
* Invalid input
* Excessively long input
* Potential prompt injection attempts

### Output Guardrail

The output guardrail checks generated results for potentially sensitive information such as:

* API keys
* Passwords
* Access tokens
* Other sensitive credentials

---

## 🧰 Technology Stack

| Technology    | Purpose                            |
| ------------- | ---------------------------------- |
| Python        | Core programming language          |
| LangGraph     | Multi-agent workflow orchestration |
| LangChain     | AI/agent framework                 |
| FastAPI       | Backend REST API                   |
| Streamlit     | User interface                     |
| SQLite        | Data storage                       |
| FastMCP       | MCP integration                    |
| LangSmith     | Monitoring and tracing             |
| InMemorySaver | Workflow state/checkpointing       |

---

## 📁 Project Structure

```text
cyber-crime-complaint/
│
├── agents/
│   ├── intake_agent.py
│   ├── validation_agent.py
│   ├── extraction_agent.py
│   ├── classification_agent.py
│   ├── fraud_agent.py
│   ├── evidence_agent.py
│   ├── risk_agent.py
│   └── routing_agent.py
│
├── guardrails/
│   ├── input_guardrail.py
│   └── output_guardrail.py
│
├── api/
│   └── ...
│
├── database/
│   └── ...
│
├── streamlit/
│   └── ...
│
├── mcp/
│   └── ...
│
├── requirements.txt
├── .env.example
└── README.md
```

> The exact folder structure may vary depending on the current project version.

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd cyber-crime-complaint
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the environment

#### Windows

```bash
venv\Scripts\activate
```

#### Linux/macOS

```bash
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🔐 Environment Variables

Create a `.env` file in the project root.

Example:

```env
OPENAI_API_KEY=your_api_key_here
LANGCHAIN_API_KEY=your_langsmith_key_here
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=cyber-crime-complaint
```

Do not commit your `.env` file or API keys to GitHub.

---

## ▶️ Running the Application

### Start the FastAPI backend

```bash
uvicorn main:app --reload
```

The API will normally be available at:

```text
http://localhost:8000
```

### Start the Streamlit interface

```bash
streamlit run app.py
```

The Streamlit application will normally be available at:

```text
http://localhost:8501
```

---

## 📝 Example Complaint

Example input:

```text
I received a call from someone claiming to be from my bank.
They asked me to share my OTP to verify my account.
After sharing the OTP, ₹50,000 was transferred from my bank account
through UPI without my permission.
```

### Example analysis

```text
Crime Type:
Banking / UPI Fraud

Fraud Indicators:
- OTP request
- Bank impersonation
- Unauthorized transaction
- UPI transaction
- Financial loss

Risk Level:
High

Recommended Action:
Urgent Human Review
```

---

## 🔄 Processing Flow

The complete complaint lifecycle is:

```text
Complaint Submission
        ↓
Input Validation
        ↓
Information Extraction
        ↓
Crime Classification
        ↓
Fraud Analysis
        ↓
Evidence Evaluation
        ↓
Risk Scoring
        ↓
Routing Decision
        ↓
Human Review (if required)
        ↓
Final Response
```

---

## ⭐ Key Features

* Multi-agent architecture
* Automated cyber-crime classification
* Entity and evidence extraction
* Fraud indicator detection
* Risk scoring
* Automated case routing
* Human-in-the-loop decision making
* Input/output safety guardrails
* REST API support
* Streamlit user interface
* SQLite-based storage
* LangGraph state management
* LangSmith monitoring support

---

## 🚀 Future Improvements

Possible future enhancements include:

* Integration with real cyber-crime complaint portals.
* LLM-based classification and reasoning.
* OCR for uploaded screenshots and documents.
* Automatic analysis of suspicious URLs.
* Integration with fraud databases.
* Email/SMS evidence analysis.
* Real-time transaction verification.
* Advanced RAG-based cyber-crime knowledge retrieval.
* Role-based access control for police/cyber-crime officers.
* Production-grade database such as PostgreSQL.
* Authentication and authorization.
* Advanced analytics dashboard.
* Model evaluation and benchmarking.
* Multilingual complaint processing.

---

## ⚠️ Disclaimer

This project is intended for **educational, research, and prototype purposes**.

The system should not be treated as a replacement for trained cyber-crime investigators or law-enforcement personnel. Automated risk scores and classifications should be reviewed by qualified personnel before taking significant action.

---

## 👨‍💻 Project

**Project Title:**
**AI-Based Cyber Crime Complaint Intake & Triage System**

**Architecture:**
Multi-Agent AI Workflow

**Primary Framework:**
LangGraph

**Backend:**
FastAPI

**Frontend:**
Streamlit

**Language:**
Python

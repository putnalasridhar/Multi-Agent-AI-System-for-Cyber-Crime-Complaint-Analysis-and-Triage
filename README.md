# Multi-Agent AI System for Cyber Crime Complaint Analysis and Risk Assessment

## 📌 Project Overview

The **Agentic AI-Powered Cyber Crime Complaint Management and Risk Assessment System** is an intelligent complaint processing system designed to help cyber crime officers handle a large number of online complaints efficiently.

With the rapid growth of **digital technology, online services, digital payments, and online transactions**, cyber crime complaints are increasing. Online complaints can contain a large amount of information such as transaction IDs, dates, times, phone numbers, website links, payment details, and fraud-related information.

Manually analyzing every complaint can be time-consuming for officers, and important information may sometimes be missed.

This project uses **Agentic AI and a multi-agent workflow** to automatically analyze complaints, extract useful information, identify cyber crime categories, analyze fraud indicators, calculate risk, and prioritize cases for appropriate action.

The system also includes **Input Guardrails, Output Guardrails, and Human-in-the-Loop review** to improve the reliability and safety of AI-assisted decision-making.

---

## 🎯 Business Problem

The increasing number of cyber crime complaints creates a heavy workload for cyber crime officers, making manual complaint processing time-consuming.

A system is needed to **automatically analyze and prioritize complaints and send important or high-risk cases for officer review**, reducing manual effort and processing time.

---

## 💡 Proposed Solution

The proposed system uses an **Agentic AI architecture** to automatically process cyber crime complaints.

The system:

* Accepts complaints through an online interface
* Supports text and voice-based complaint submission
* Validates complaint information
* Extracts important case information
* Identifies the cyber crime category
* Analyzes evidence and fraud indicators
* Calculates a risk score
* Determines case priority
* Routes cases based on risk
* Sends important cases for human officer review
* Allows officers to approve, reject, or escalate cases

---

## 🏗️ System Architecture

```text
                    Citizen
                       │
                       ▼
              Online Complaint
                       │
             Text / Voice Input
                       │
                       ▼
              ┌─────────────────┐
              │ Input Guardrail │
              └────────┬────────┘
                       │
                       ▼
          ┌─────────────────────────┐
          │ Complaint Analysis Agent│
          └────────────┬────────────┘
                       │
                       ▼
       ┌──────────────────────────────┐
       │ Evidence & Fraud Analysis    │
       │            Agent              │
       └──────────────┬───────────────┘
                      │
                      ▼
          ┌────────────────────────┐
          │ Risk & Decision Agent  │
          └────────────┬───────────┘
                       │
                       ▼
             ┌─────────────────┐
             │ Output Guardrail│
             └────────┬────────┘
                      │
                      ▼
             ┌─────────────────┐
             │ Human-in-the-   │
             │ Loop Review     │
             └────────┬────────┘
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
       Approve      Reject     Escalate
```

---

## 🤖 AI Agents

### 1. Complaint Analysis Agent

Analyzes the submitted complaint and identifies important information.

Responsibilities:

* Validate required complaint fields
* Extract relevant information
* Identify the cyber crime category
* Determine whether the complaint is complete

The system can identify categories such as:

* UPI Fraud
* Phishing
* Investment Fraud
* Online Shopping Fraud
* Banking Fraud
* Identity Theft
* Social Media Fraud
* Job Scam

---

### 2. Evidence & Fraud Analysis Agent

Analyzes the available evidence and identifies potential fraud indicators.

The agent considers information such as:

* Transaction details
* Supporting evidence
* Suspicious links
* Fraud indicators
* Missing evidence

It generates a fraud assessment that is used by the risk analysis stage.

---

### 3. Risk & Decision Agent

The Risk & Decision Agent determines the risk and priority of the complaint.

The system generates:

* **Risk Score:** 0–100
* **Risk Level:** Low / Medium / High
* **Priority:** Low / Medium / High / Critical
* **Routing Decision**

Example routing:

```text
High Risk
    ↓
Urgent Human Review

Medium Risk
    ↓
Human Review

Low Risk
    ↓
Normal Processing
```

---

## 🛡️ Guardrails

### Input Guardrail

The Input Guardrail validates and sanitizes complaint information before it is processed by the AI agents.

It checks:

* Required complaint information
* Complaint length
* Minimum complaint description
* Contact number validity
* Transaction ID length

Invalid inputs are blocked before AI processing.

### Output Guardrail

The Output Guardrail validates AI-generated results before they are used for decision-making.

It checks:

* Risk score
* Risk level
* Priority
* Routing decision
* Fraud score

If the AI output fails validation, the case is routed for **urgent human review**.

---

## 👮 Human-in-the-Loop

The system does not completely replace the cyber crime officer.

Cases requiring human verification are sent to an officer for review.

The officer can:

```text
Approve
   │
   ├── Reject
   │
   └── Escalate
```

This provides human oversight for important or high-risk cases.

---

## 🔄 Complaint Processing Workflow

```text
1. Citizen submits complaint
          ↓
2. Input validation
          ↓
3. Complaint analysis
          ↓
4. Evidence & fraud analysis
          ↓
5. Risk assessment
          ↓
6. Output validation
          ↓
7. Case prioritization
          ↓
8. Human officer review
          ↓
9. Approve / Reject / Escalate
```

---

## 🎤 Voice Complaint Support

The system also supports voice-based complaint submission.

Voice input is converted into text using the OpenAI transcription model:

```text
gpt-4o-mini-transcribe
```

The transcribed complaint is then processed through the same complaint analysis workflow.

---

## 🧰 Technology Stack

| Technology       | Purpose                             |
| ---------------- | ----------------------------------- |
| Python           | Main programming language           |
| Streamlit        | Frontend / User Interface           |
| FastAPI          | Backend REST API                    |
| LangGraph        | Multi-agent workflow orchestration  |
| LangChain OpenAI | LLM integration                     |
| OpenAI           | AI analysis and voice transcription |
| Pydantic         | API data validation                 |
| MemorySaver      | LangGraph state persistence         |
| python-dotenv    | Environment variable management     |

The backend code uses FastAPI, LangGraph, LangChain OpenAI, OpenAI, Pydantic, and dotenv.

The frontend communicates with the FastAPI backend and provides citizen complaint submission and officer review functionality.

---

## 📁 Project Structure

```text
cyber-crime-project/
│
├── cyber_crime_core.py
│       └── FastAPI backend
│       └── AI agents
│       └── LangGraph workflow
│       └── Risk assessment
│       └── Human review
│
├── streamlit_app.py
│       └── Streamlit frontend
│       └── Citizen complaint interface
│       └── Voice complaint interface
│       └── Officer review interface
│
├── .env
│       └── API keys
│
└── README.md
```

---

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
cd YOUR-REPOSITORY
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

### 3. Activate the Virtual Environment

#### Windows

```bash
venv\Scripts\activate
```

#### Linux / macOS

```bash
source venv/bin/activate
```

### 4. Install Dependencies

Install the required Python packages:

```bash
pip install fastapi uvicorn streamlit requests pydantic langgraph langchain-openai openai python-dotenv
```

---

## 🔑 Environment Variables

Create a `.env` file in the project directory.

```env
OPENAI_API_KEY=your_openai_api_key
```

**Do not upload your `.env` file or API key to GitHub.**

Add the following to `.gitignore`:

```text
.env
venv/
__pycache__/
*.pyc
```

---

## ▶️ Running the Application

### Start the FastAPI Backend

Open a terminal and run:

```bash
uvicorn cyber_crime_core:app --reload
```

The backend will run at:

```text
http://127.0.0.1:8000
```

FastAPI automatically provides API documentation at:

```text
http://127.0.0.1:8000/docs
```

### Start the Streamlit Frontend

Open another terminal:

```bash
streamlit run streamlit_app.py
```

The Streamlit application will open in your browser.

---

## 🔌 Main API Endpoints

### Create Complaint

```http
POST /complaints
```

Used to submit a new cyber crime complaint.

### Get Pending Complaints

```http
GET /complaints/pending
```

Returns complaints that require human officer review.

### Get Complaint Status

```http
GET /complaints/{complaint_id}
```

Returns the current status and analysis of a complaint.

### Submit Officer Decision

```http
POST /complaints/{complaint_id}/decision
```

Officer decisions include:

```text
approve
reject
escalate
```

## The backend exposes these complaint and officer-review endpoints through FastAPI.

## 📊 Risk Assessment

The system calculates the risk score based on fraud indicators, evidence availability, and crime category.

```text
Risk Score: 0 - 100
```

### Risk Levels

| Risk Score | Risk Level | Action              |
| ---------: | ---------- | ------------------- |
|       0–39 | Low        | Normal Processing   |
|      40–69 | Medium     | Human Review        |
|     70–100 | High       | Urgent Human Review |

High-risk cases are routed for urgent officer review, while medium-risk cases are sent for officer review and low-risk cases continue through normal processing.

---

## 👥 Human Officer Decision

When a complaint requires human review, the officer can select:

### Approve

The complaint is approved for further processing.

### Reject

The complaint is rejected by the officer.

### Escalate

The complaint is escalated for further investigation.

The system uses LangGraph human-in-the-loop interruption to pause processing until an officer provides a decision.

---

## 🌟 Key Features

* ✅ Online cyber crime complaint submission
* ✅ Text-based complaint input
* ✅ Voice-based complaint input
* ✅ Automatic complaint analysis
* ✅ Cyber crime category identification
* ✅ Important information extraction
* ✅ Evidence analysis
* ✅ Fraud analysis
* ✅ Automated risk scoring
* ✅ Case priority determination
* ✅ Automatic case routing
* ✅ Input Guardrail
* ✅ Output Guardrail
* ✅ Human-in-the-Loop
* ✅ Officer approve/reject/escalate decisions
* ✅ FastAPI backend
* ✅ Streamlit frontend
* ✅ LangGraph multi-agent workflow

---

## 🎯 Benefits

The system is designed to:

* Reduce manual workload for cyber crime officers
* Reduce complaint processing time
* Automatically identify important complaint information
* Prioritize high-risk complaints
* Support faster officer decision-making
* Reduce the possibility of missing important information
* Improve complaint processing efficiency
* Provide human oversight for critical decisions
* Improve overall cyber crime response

---

## 🔮 Future Enhancements

Possible future improvements include:

* Integration with official cyber crime complaint databases
* Advanced fraud detection models
* Real-time transaction risk analysis
* Evidence/document upload and analysis
* Image and screenshot analysis
* URL reputation checking
* Database-based case management
* SMS/email notifications
* Advanced analytics dashboard
* Role-based access control
* Production database integration
* Audit logging and monitoring

---

## ⚠️ Disclaimer

This project is an **AI-assisted decision-support system** for cyber crime complaint management.

AI-generated analysis should not be treated as a final legal or investigative decision. Important cases should be reviewed by authorized cyber crime officers before taking further action.

---

## 👨‍💻 Project

**Project Title:**
**Agentic AI-Powered Cyber Crime Complaint Management and Risk Assessment System**

**Domain:** Artificial Intelligence / Cyber Security

**Architecture:** Multi-Agent AI + Human-in-the-Loop

**Frontend:** Streamlit

**Backend:** FastAPI

**AI Orchestration:** LangGraph

**LLM:** OpenAI

---

## 📜 License

This project is intended for **academic, research, and demonstration purposes**.

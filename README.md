# AssitFlow
# ⚡ AssistFlow – Enterprise AI Support & Operations Portal

> **Smarter Tickets. Faster Resolution. Better Support.**

AssistFlow is an **AI-powered enterprise support ticket management and operations portal** designed to modernize IT support workflows.

The system uses **local Large Language Models (LLMs) through Ollama** to analyze support tickets, provide instant troubleshooting recommendations, assist with ticket classification and priority analysis, and support intelligent escalation and technician routing.

---

## 🚀 Overview

Traditional IT support systems often depend on manual ticket reading, categorization, prioritization, and assignment. This can lead to delayed responses, increased workload, incorrect prioritization, and poor visibility into support operations.

**AssistFlow transforms this process into an AI-assisted workflow.**

When a user submits a support ticket, AssistFlow can:

1. Analyze the issue using a local LLM.
2. Identify the technical category.
3. Analyze urgency and priority.
4. Evaluate the user's sentiment.
5. Generate troubleshooting recommendations.
6. Allow the user to confirm whether the issue is resolved.
7. Escalate unresolved issues to the support team.
8. Route tickets to technicians.
9. Provide administrators with real-time operational analytics.

---

## ✨ Key Features

### 🤖 AI-Powered Ticket Diagnostics

Uses a locally hosted LLM through Ollama to understand support issues and generate troubleshooting guidance.

### 🏷️ Automatic Ticket Classification

Categorizes technical issues into areas such as:

* Network
* Hardware
* Software
* Access / Permissions

### 🚨 Priority Detection

Supports priority levels:

* Low
* Medium
* High
* Critical

### 😊 Sentiment Analysis

Analyzes the user's message to identify sentiment and potential frustration, providing additional context for support teams.

### ⚡ AI Automated Solutions

Users receive immediate AI-generated troubleshooting steps after submitting a ticket.

### 🔄 Smart Escalation

If the AI solution does not resolve the issue, the ticket can be escalated for human support.

### 👨‍💻 Technician Routing

Administrators can review unresolved tickets, assign technicians, and update ticket status.

### 💬 AI Support Assistant

AssistFlow includes a conversational AI assistant for interactive troubleshooting and system assistance.

### 📊 Operational Dashboard

Administrators can monitor:

* Total tickets
* In-progress tickets
* Resolved tickets
* Escalated tickets
* Resolution distribution
* Tickets by category
* Operational telemetry

### 🐛 Bug Tracking

A dedicated bug-reporting workflow allows application issues to be reported, categorized by severity, and assigned for resolution.

---

## 🧠 AI Workflow

```text
User Creates Ticket
        ↓
Text Preprocessing
        ↓
Local AI / NLP Analysis
        ↓
┌────────────┬────────────┬─────────────┐
│            │            │             │
Category    Priority    Sentiment     Intent
│            │            │             │
└────────────┴────────────┴─────────────┘
        ↓
AI Troubleshooting Recommendation
        ↓
     User Feedback
       ↙       ↘
   Resolved    Unresolved
      ↓            ↓
   Close       Escalate
                   ↓
            Technician Routing
                   ↓
              Resolution
                   ↓
             Analytics
```

---

## 🏗️ System Architecture

```text
┌─────────────────────┐
│        User         │
│ Employee / Admin    │
│     Technician      │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ Streamlit Frontend  │
│   Custom UI/CSS     │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ Authentication Layer│
│ Bcrypt + RBAC       │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│   Python Backend    │
│   Business Logic    │
└──────┬────────┬─────┘
       ↓        ↓
┌────────────┐ ┌──────────────┐
│   Ollama   │ │   MongoDB    │
│ Local LLM  │ │  Database    │
└────────────┘ └──────────────┘
       ↓
┌─────────────────────┐
│ Admin / Technician  │
│     Routing Desk    │
└─────────────────────┘
```

---

## 🛠️ Technology Stack

| Technology            | Purpose                                  |
| --------------------- | ---------------------------------------- |
| **Python 3**          | Backend and application logic            |
| **Streamlit**         | Frontend and web interface               |
| **HTML/CSS**          | UI customization and styling             |
| **MongoDB**           | Ticket and user data storage             |
| **PyMongo**           | MongoDB integration                      |
| **Ollama**            | Local LLM inference                      |
| **Llama 3 / Mistral** | AI-powered analysis                      |
| **Plotly**            | Interactive dashboards and charts        |
| **Pandas**            | Data processing and analytics            |
| **Bcrypt**            | Password hashing                         |
| **Requests**          | API communication                        |
| **Certifi**           | Secure database connection configuration |

---

## 🔐 Security & Privacy

A major design goal of AssistFlow is **enterprise data sovereignty**.

Instead of sending sensitive support information to public cloud AI APIs, AssistFlow can run the LLM locally using **Ollama**.

### Security features include:

* Bcrypt password hashing
* Role-Based Access Control (RBAC)
* Employee / Technician / Administrator roles
* Local AI inference
* MongoDB-based data persistence
* Secure database connection configuration

This architecture helps keep sensitive enterprise support information within the organization's infrastructure.

---

## 👥 User Roles

### Employee

* Register / Sign in
* Raise support tickets
* Receive AI troubleshooting
* Use AI Assistant
* Confirm resolution
* Escalate unresolved issues
* Report bugs

### Technician

* Receive assigned tickets
* Review ticket information
* Investigate technical issues
* Resolve tickets
* Update ticket status

### Administrator

* Monitor system dashboard
* View operational telemetry
* Run AI system analysis
* Manage tickets
* Assign technicians
* Update ticket status
* Monitor support performance

---

## 🔄 Ticket Lifecycle

```text
Login
  ↓
Raise Ticket
  ↓
AI Analysis
  ↓
Category + Priority + Sentiment
  ↓
AI Solution
  ↓
Is the Issue Resolved?
  ↓
 ┌───────────────┐
 │               │
YES              NO
 │               │
 ↓               ↓
Close        Escalate
                 ↓
          Technician Assignment
                 ↓
              Resolution
                 ↓
             Analytics
```

---

## 📊 Dashboard

The administrator dashboard provides operational visibility through:

* Total Tickets
* In Progress
* Resolved
* Escalated
* Resolution Rate
* Resolution Distribution
* Tickets by Category

The dashboard uses **Pandas** for data aggregation and **Plotly** for interactive visualization.

---

## 🖥️ Application Screens

The project includes:

* 🔐 Account Sign In
* 📝 Account Registration
* 🎫 Raise a Ticket
* 🤖 AI Automated Diagnostics
* 💬 AI Assistant
* 📊 Admin Dashboard
* 🛠️ Admin Desk
* 👨‍💻 Technician Routing
* 🐛 Bug Reporting
* 📈 Operational Telemetry

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/AssistFlow.git
cd AssistFlow
```

### 2. Install dependencies

```bash
pip install streamlit pandas plotly requests bcrypt pymongo certifi
```

### 3. Start MongoDB

Ensure MongoDB is running locally on:

```text
localhost:27017
```

### 4. Install and start Ollama

Install Ollama and download your preferred local model.

For example:

```bash
ollama run llama3
```

The local Ollama API is typically available at:

```text
http://localhost:11434
```

### 5. Run AssistFlow

```bash
streamlit run app.py
```

The application will open in your browser.

---


---

## 🧪 Testing & Evaluation

AssistFlow can be evaluated using a labeled support-ticket dataset.

Important evaluation metrics include:

| Metric                       | Purpose                                    |
| ---------------------------- | ------------------------------------------ |
| AI Classification Accuracy   | Measures correct ticket categorization     |
| Priority Prediction Accuracy | Measures correctness of priority detection |
| Sentiment Accuracy           | Measures sentiment prediction performance  |
| Automated Routing Rate       | Measures routing automation                |
| Average AI Response Time     | Measures AI response latency               |
| Resolution Rate              | Measures successfully resolved tickets     |

**Actual accuracy and performance values should be added after formal testing.**

---

## 🌟 Benefits

* ⚡ Faster initial support
* 🤖 Automated ticket analysis
* 🎯 Better prioritization
* 🔀 Intelligent ticket routing
* 👨‍💻 Reduced repetitive workload
* 🔐 Local AI and improved data privacy
* 📊 Real-time operational visibility
* 😊 Improved support experience
* 📚 More consistent troubleshooting guidance

---

## 🔮 Future Scope

AssistFlow can be extended with:

### 🎙️ Voice Support

Allow users to create and interact with support tickets using voice.

### 🌐 Multilingual AI

Support multiple languages for broader accessibility.

### 📈 Predictive Analytics

Predict ticket volume, recurring incidents and potential escalations.

### 🤖 Auto-Resolution

Automatically resolve common and repetitive technical issues.

### 🧠 Continuous Learning

Improve AI recommendations using historical tickets and user feedback.

### 🔔 Proactive Support

Identify potential issues before users create tickets.

### 🔗 Enterprise Integrations

Integrate with email, enterprise messaging platforms, monitoring systems and existing ITSM/CRM platforms.

---

## 🎯 Project Vision

AssistFlow aims to move enterprise support from:

**Manual Ticket Management**

to

**Intelligent, Automated & Data-Driven Support**

> **“From Ticket Management to Intelligent Support.”**

---

## 👨‍💻 Project

**AssistFlow – Enterprise AI Support & Operations Portal**

Built using **Python, Streamlit, MongoDB, Ollama and Local LLMs**.

---

## 📜 License
This project is provided as a portfolio/milestone demonstration. See repository history for attribution.

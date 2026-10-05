<div align="center">

# 🎓 ScholarSathi

### Agentic RAG Assistant for Scholarship Discovery, Explainable Eligibility Checking and Deadline Tracking

*Enter your profile once. Find every scholarship you qualify for, understand exactly why you don't qualify for the rest, and never miss a deadline again.*

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![scikit-learn](https://img.shields.io/badge/Retrieval-scikit--learn-F7931E?logo=scikitlearn&logoColor=white)
![Claude](https://img.shields.io/badge/Agent-Claude%20tool--use-D97757)
![Tests](https://img.shields.io/badge/tests-13%20passing-2EA44F)
![Offline](https://img.shields.io/badge/works-offline-6E7781)

[The Problem](#-the-problem) •
[What Makes It Different](#-what-makes-it-different) •
[Architecture](#%EF%B8%8F-architecture) •
[Quick Start](#-quick-start) •
[Evaluation](#-evaluation) •
[Roadmap](#%EF%B8%8F-limitations-and-roadmap) •
[Viva Prep](#-viva-preparation)

</div>

---

## 📌 The Problem

Every year, thousands of eligible students in India miss out on scholarships and fee waivers. Not because they don't qualify, but because the information is hard to reach and harder to read.

| Pain point | What actually happens |
|---|---|
| 📄 **Scattered rules** | Criteria such as category, family income, course level, minimum marks, gender and domicile are buried in long PDFs across many portals |
| 🧩 **Dense language** | Students misread clauses and wrongly assume they are ineligible |
| 📑 **Hidden document lists** | A missing certificate is discovered only after the window closes |
| ⏰ **Separate deadlines** | Each scheme has its own closing date, with no single place to track them |

### 💡 The Solution

ScholarSathi turns this into a single, guided workflow:

```
 1. 👤 Enter your profile once
 2. 🔍 The system reads every scheme document
 3. ✅ See the schemes you are eligible for, ranked
 4. ❌ See the exact rule that fails for the rest
 5. 📋 Get a document checklist for each match
 6. 🚨 Get warned about deadlines closing soon
```

---

## 🚀 What Makes It Different

ScholarSathi is not a chatbot wrapped around a language model. It separates **reading** from **deciding**, so every answer can be traced back to a document and a rule.

| | Basic chatbot | ScholarSathi |
|---|---|---|
| **Source of truth** | Model memory, prone to hallucinated rules | Official scheme documents via RAG, with the source scheme named |
| **Who decides eligibility** | The LLM | A deterministic Python rule engine. The LLM only *extracts* rules |
| **Auditability** | Opaque | Every decision lists the rules passed and the rule that failed |
| **Interaction** | Single question, single answer | An agent that plans and calls tools: `search_schemes`, `check_eligibility`, `get_documents` |
| **Actions** | None | Ranks matches, counts days left, flags urgent deadlines, builds checklists |

> **🔑 Core design principle**
> *The LLM reads. The rule engine decides.* This hybrid design removes hallucinated eligibility decisions while keeping the flexibility of an LLM for understanding free-form notices.

---

## 🏗️ Architecture

```mermaid
flowchart LR
    A[📄 Scheme PDFs / Notices] --> B[criteria.py<br/>LLM extracts rules to JSON<br/>cached, regex fallback offline]
    A --> C[rag.py<br/>Chunking + TF-IDF retrieval]
    P[👤 Student Profile] --> D[eligibility.py<br/>Deterministic rule engine]
    B --> D
    Q[❓ Student Question] --> E[agent.py<br/>Claude tool-use loop]
    E -- search_schemes --> C
    E -- check_eligibility --> D
    E -- get_documents --> C
    D --> F[app.py<br/>Streamlit UI]
    E --> F
    F --> T1[📊 Your Matches tab]
    F --> T2[💬 Ask the Agent tab]
```

<details>
<summary><b>🧱 Component breakdown (click to expand)</b></summary>

<br>

| Module | Responsibility | Key output |
|---|---|---|
| `criteria.py` | Uses the LLM to convert free-form eligibility text into structured JSON rules. Results are cached. Falls back to regex parsing when offline | Machine-readable criteria per scheme |
| `rag.py` | Splits scheme documents into chunks and retrieves relevant passages with TF-IDF | Grounded context for detail questions |
| `eligibility.py` | Evaluates a profile against each scheme's rules | Passed rules, failed rules, closed status, days left |
| `agent.py` | Runs a Claude tool-use loop that plans, calls tools and writes a grounded answer | Natural-language answer citing the scheme |
| `app.py` | Streamlit interface with two tabs | *Your Matches* and *Ask the Agent* |

</details>

<details>
<summary><b>📴 Offline mode (click to expand)</b></summary>

<br>

No API key? No internet? No problem. Without a key, the same tools run in a **fixed pipeline** instead of the agent loop, so the full demo works offline. Rule extraction falls back to regex parsing of the structured `ELIGIBILITY:` format used in the sample files.

</details>

---

## ⚡ Quick Start

### 1️⃣ Install

```bash
pip install -r requirements.txt
```

### 2️⃣ Run the tests

```bash
python tests/test_scholarsathi.py   # 8 eligibility cases + 5 retrieval cases
```

### 3️⃣ Launch the app

```bash
streamlit run app.py
```

### 4️⃣ (Optional) Enable the LLM agent

```bash
export ANTHROPIC_API_KEY=your_key_here
```

<details>
<summary><b>📂 Adding your own scheme documents</b></summary>

<br>

1. Copy the scheme text from the official portal.
2. Save it as a `.txt` file in `data/schemes/`.
3. Restart the app.

| Mode | What the file needs |
|---|---|
| **With API key** | Free-form text. The LLM extracts the criteria automatically |
| **Without API key** | Must follow the `ELIGIBILITY:` format used in the sample files |

</details>

> ⚠️ **Data note**
> The five files in `data/schemes/` are **fictional sample schemes** created for demonstration. Before presenting this as a real tool, replace them with official notices (for example, from your state scholarship portal) and verify the extracted rules by hand.

---

## 📊 Evaluation

| Test suite | Cases | Result |
|---|:---:|:---:|
| ✅ Eligibility engine (hand-written profile and scheme pairs) | 8 | **8 / 8 correct** |
| ✅ Retrieval (correct scheme returned at rank 1) | 5 | **5 / 5 correct** |
| | **13** | **All passing** |

> 📝 **Honest scope**
> These tests were written by the project author. They demonstrate that the logic works as designed, not that the system is accurate on real-world notices.

<details>
<summary><b>🔬 Proposed stronger evaluation</b></summary>

<br>

1. Collect **30 real scholarship notices** from official portals.
2. **Hand-label** the eligibility rules in each notice as ground truth.
3. Run the LLM extractor and measure **field-level extraction accuracy** (precision and recall per rule type: income, marks, category and so on).
4. Analyse failure cases to improve prompts or add validation rules.

</details>

---

## 🛣️ Limitations and Roadmap

### Current limitations

- 🔑 The LLM agent path needs an API key and was not exercised in the offline test environment.
- 🔤 TF-IDF retrieval matches keywords, not meaning.
- 📝 Sample data is fictional.

### Planned improvements

- [ ] 🧠 Replace TF-IDF with embeddings and a vector database
- [ ] 🌐 Add Marathi and Hindi support
- [ ] 📤 Allow PDF upload directly in the UI
- [ ] 🔔 Send deadline reminders by email or WhatsApp
- [ ] 🕷️ Build a scraper to refresh notices automatically
- [ ] 📏 Run the 30-notice extraction accuracy study

### 🔒 Privacy by design

Student data is sensitive. ScholarSathi follows three principles:

| Principle | In practice |
|---|---|
| **Stay local** | The profile stays on the device |
| **No logging** | Profile data is never written to logs |
| **Data minimisation** | Ask only for the fields the rules actually need |

---

## 📄 Resume Bullets

<details>
<summary><b>Copy-ready bullets (click to expand)</b></summary>

<br>

- Built **ScholarSathi**, an agentic RAG assistant (Python, scikit-learn, Streamlit, Claude tool-use) that matches students to scholarships and explains eligibility with rule-level reasons.
- Designed a **hybrid architecture** in which an LLM extracts eligibility criteria and a deterministic engine makes the decision, removing hallucinated eligibility outcomes; validated with 13 unit tests.

</details>

---

<div align="center">

**ScholarSathi** · *Helping every eligible student find the support they deserve* 🎓

</div>

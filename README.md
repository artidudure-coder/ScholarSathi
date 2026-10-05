# ScholarSathi
**Agentic RAG Assistant for Scholarship Discovery, Explainable Eligibility Checking and Deadline Tracking**

Prepared by: <your name>, Roll No. <your roll no> | TAE Mini Project

## Problem statement
Every year many students in India miss scholarships and fee waivers they qualify for. The rules (category, family income, course level, minimum marks, gender, domicile) are spread across long PDFs and notices on different portals, written in dense language, and each has its own deadline and document list. Students either never find the scheme, wrongly assume they are ineligible, or discover a missing certificate after the deadline.

ScholarSathi lets a student enter a profile once. The system reads scheme documents, works out which schemes the student is eligible for, explains the exact rule that fails for the others, lists the documents to prepare, and warns about closing deadlines.

## Why this is not a basic chatbot
| Basic chatbot | ScholarSathi |
|---|---|
| Answers from model memory, can hallucinate rules | Answers only from scheme documents (RAG) and names the source scheme |
| LLM decides eligibility | LLM only **extracts** rules; a deterministic Python engine **decides** eligibility, so it is auditable |
| Single question and answer | Agent plans and calls tools: `search_schemes`, `check_eligibility`, `get_documents` |
| No actions | Ranks matches, counts days left, flags urgent deadlines, builds a document checklist |

## Architecture
```
Scheme PDFs / notices --> criteria.py (LLM extracts rules to JSON, cached; regex fallback offline)
                      --> rag.py      (chunking + TF-IDF retrieval for detail questions)
Student profile -------> eligibility.py (rule engine: passed rules, failed rules, closed, days left)
Question --> agent.py (Claude tool-use loop: plans, calls tools, writes grounded answer)
                      --> app.py (Streamlit: Your matches tab + Ask the agent tab)
```
Offline mode: with no API key, the same tools run in a fixed pipeline, so the demo works without internet.

## How to run
```
pip install -r requirements.txt
python tests/test_scholarsathi.py        # 8 eligibility cases + 5 retrieval cases
streamlit run app.py                     # UI
export ANTHROPIC_API_KEY=...             # optional: turns on the LLM agent
```
Add real scheme text as `.txt` files in `data/schemes/` (copy from the official portal). With an API key the LLM extracts the criteria automatically from free-form text. Without a key the file must follow the `ELIGIBILITY:` format of the samples.

## Data note
The five files in `data/schemes/` are **fictional sample schemes** made for demonstration. Before presenting this as a real tool, replace them with official notices (for example from the state scholarship portal) and verify the extracted rules.

## Evaluation (included in tests/)
- Eligibility engine: 8 of 8 hand-written profile and scheme cases correct.
- Retrieval: 5 of 5 questions return the correct scheme at rank 1.
These are small tests written by the project author, so they show the logic works, not real-world accuracy. A stronger evaluation: collect 30 real notices, label their rules by hand, and measure the LLM extraction accuracy.

## Limitations and future work
- LLM agent path needs an API key; it was not run in the offline test environment.
- TF-IDF retrieval can be replaced by embeddings plus a vector database.
- Add Marathi/Hindi support, PDF upload in the UI, an email or WhatsApp deadline reminder, and a scraper to refresh notices.
- Student data is sensitive: keep the profile on the device, do not log it, and ask only for what the rules need.

## Viva questions to prepare
1. Why does a rule engine make the final decision instead of the LLM? (auditability, no hallucinated eligibility)
2. What is RAG and where is it used here? (detail questions: process, benefits, documents)
3. What makes this agentic? (the model chooses tools and loops until it can answer)
4. How would you measure extraction accuracy? How do you handle a wrong extraction?
5. What are the privacy risks of a student profile?

## Resume bullets
- Built ScholarSathi, an agentic RAG assistant (Python, scikit-learn, Streamlit, Claude tool-use) that matches students to scholarships and explains eligibility with rule-level reasons.
- Designed a hybrid architecture where an LLM extracts eligibility criteria and a deterministic engine decides, removing hallucinated decisions; validated with 13 unit tests.

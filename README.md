# PMA AI Teaching Assistant

An AI Teaching Assistant for **Probability Models and Applications** built using **Retrieval-Augmented Generation (RAG)**.

The system answers course-specific conceptual and mathematical questions using retrieved PMA course material rather than acting like a general-purpose chatbot.

---

## Features

- Course-specific question answering
- Retrieval-Augmented Generation using ChromaDB
- Semantic retrieval using Sentence Transformers
- Groq-based LLM generation
- Mathematical rendering using LaTeX
- Multi-turn conversation support
- Practice questions, hints, and worked solutions
- Source display for retrieved course material
- Out-of-scope question detection
- Streamlit-based user interface

---

## Course Coverage

The current knowledge base covers topics including:

- Random Variables
- Probability Mass Functions
- Probability Density Functions
- Cumulative Distribution Functions
- Expectation
- Variance
- Discrete Distributions
- Continuous Distributions
- Joint Distributions
- Conditional Probability
- Independence
- Functions of Random Variables
- Sums of Random Variables
- Moment Generating Functions
- Characteristic Functions
- Random Vectors
- Union Bound
- Markov Inequality
- Chebyshev Inequality
- Chernoff Bounds
- Cauchy-Schwarz Inequality
- Law of Large Numbers
- Central Limit Theorem
- Convergence in Distribution
- Convergence in Probability
- Convergence in Mean
- Almost Sure Convergence
- Point Estimation
- Maximum Likelihood Estimation

Measure theory material such as Sigma Algebra and Borel Algebra can be added later by extending the RAG knowledge base.

---

## Project Structure

```text
PMA_AI_TA/
├── app.py
├── requirements.txt
├── .gitignore
├── config/
│   └── sources.yaml
├── data/
│   ├── raw/
│   ├── processed/
│   └── chunks/
│       └── pma_chunks.json
├── evaluation/
│   ├── evaluate_answers.py
│   ├── evaluate_retrieval.py
│   ├── evaluate_scope.py
│   ├── questions.json
│   ├── summarize_results.py
│   └── results/
├── prompts/
│   └── system_prompt.txt
├── src/
│   ├── download_sources.py
│   ├── parse_documents.py
│   ├── chunk_documents.py
│   ├── build_vector_db.py
│   ├── test_retrieval.py
│   ├── scope_guard.py
│   └── rag.py
└── vector_db/
```

---

## RAG Pipeline

```text
Course Material
      ↓
Source Download
      ↓
Document Parsing
      ↓
Chunking + Metadata
      ↓
Sentence Transformer Embeddings
      ↓
Chroma Vector Database
      ↓
Semantic Retrieval
      ↓
Scope Check
      ↓
Retrieved Course Context
      ↓
Groq LLM
      ↓
Course-Grounded Answer
      ↓
Streamlit Interface
```

---

## Technologies Used

- Python
- Streamlit
- ChromaDB
- Sentence Transformers
- Groq API
- Hugging Face Transformers
- PyTorch
- python-dotenv

---

## Embedding Model

The project uses:

```text
all-MiniLM-L6-v2
```

for generating normalized semantic embeddings.

---

## Vector Database

The project uses **ChromaDB** as a persistent vector database.

The database is stored locally in:

```text
vector_db/
```

A prebuilt vector database is included in the repository.

---

## LLM

Answer generation is performed using the Groq API.

The default model is:

```text
openai/gpt-oss-20b
```

The model name can be changed using the `GROQ_MODEL` environment variable.

---

# How to Run the Project Locally

## 1. Clone the repository

```bash
git clone https://github.com/shrutikumbhar16/PMA-AI-Teaching-Assistant.git
```

Move into the project directory:

```bash
cd PMA-AI-Teaching-Assistant
```

---

## 2. Create a Python virtual environment

### Windows

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure the Groq API key

Create a file named:

```text
.env
```

in the project root.

Add:

```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-20b
```

Replace `your_groq_api_key` with your actual Groq API key.

The `.env` file is excluded from Git through `.gitignore`.

---

## 5. Run the Streamlit application

```bash
streamlit run app.py
```

If the `streamlit` command is not recognized, use:

```bash
python -m streamlit run app.py
```

The application should open automatically in your browser.

The default local URL is usually:

```text
http://localhost:8501
```

---

# Rebuilding the Knowledge Base

A prebuilt ChromaDB database is already included.

You only need to rebuild the knowledge base when adding or changing course material.

Run:

```bash
python src/download_sources.py
python src/parse_documents.py
python src/chunk_documents.py
python src/build_vector_db.py
```

After rebuilding, restart the Streamlit application.

---

# Adding New Course Material

To add new PMA topics such as Sigma Algebra or Borel Algebra:

1. Add the source material to the raw data pipeline.
2. Update `config/sources.yaml` if required.
3. Run the parsing script.
4. Run the chunking script.
5. Rebuild the vector database.
6. Restart or redeploy the application.

---

# Retrieval

The student's query is embedded using:

```text
all-MiniLM-L6-v2
```

The query embedding is compared against course chunks stored in ChromaDB.

The most relevant chunks are retrieved and passed to the LLM as context.

---

# Scope Guard

The assistant includes an out-of-scope detection mechanism.

Questions that do not sufficiently match PMA course material are rejected before answer generation.

Examples of out-of-scope questions include:

- QPSK
- TCP/IP
- Brownian Motion
- Martingales
- Unrelated general-purpose questions

---

# Mathematical Formatting

The assistant returns Markdown with LaTeX.

Inline mathematics uses:

```text
$ ... $
```

Display mathematics uses:

```text
$$
...
$$
```

Streamlit renders the equations directly in the interface.

---

# Conversation Support

The application maintains recent conversation context so follow-up requests such as:

```text
solve it
give me a hint
another one
make it harder
make it easier
explain it
```

can refer to the previous interaction.

---

# Evaluation

The project contains evaluation scripts for:

- Retrieval quality
- Scope detection
- Answer quality

Run retrieval evaluation:

```bash
python evaluation/evaluate_retrieval.py
```

Run scope evaluation:

```bash
python evaluation/evaluate_scope.py
```

Run answer evaluation:

```bash
python evaluation/evaluate_answers.py
```

Evaluation outputs are stored under:

```text
evaluation/results/
```

---

# Deployment

The application can be deployed using Railway.

Required environment variables:

```text
GROQ_API_KEY
GROQ_MODEL
```

Recommended Railway start command:

```bash
streamlit run app.py --server.address=0.0.0.0 --server.port=$PORT
```

---

# Security

Do not commit API keys or secrets.

The following should remain ignored by Git:

```text
.env
.venv/
venv/
__pycache__/
*.pyc
```

---

# Future Improvements

- Add Sigma Algebra material
- Add Borel Algebra material
- Expand measure theory coverage
- Increase evaluation coverage
- Improve ambiguous follow-up retrieval
- Add additional PMA examples and solved problems

---

## Project Goal

The goal of this project is to provide a **course-grounded AI Teaching Assistant** for Probability Models and Applications that can explain concepts, solve problems, generate practice questions, provide hints, and remain restricted to the PMA course domain.

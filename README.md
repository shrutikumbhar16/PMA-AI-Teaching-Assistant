# PMA AI Teaching Assistant

An AI Teaching Assistant for **Probability Models and Applications** built using **Retrieval-Augmented Generation (RAG)**.

The system is designed to answer course-specific conceptual and mathematical questions using retrieved course material rather than behaving like a general-purpose chatbot.

## Features

- Course-specific question answering
- Retrieval-Augmented Generation using ChromaDB
- Semantic search with Sentence Transformers
- Groq-based LLM generation
- Mathematical rendering with LaTeX
- Multi-turn conversation support
- Practice questions, hints, and worked solutions
- Source citations for retrieved course material
- Out-of-scope question detection
- Streamlit-based chat interface

## Course Coverage

The assistant currently covers topics including:

- Random Variables
- PMF, PDF, and CDF
- Expectation and Variance
- Discrete and Continuous Distributions
- Joint Distributions
- Conditional Probability and Independence
- Functions of Random Variables
- Sums of Random Variables
- Moment Generating Functions
- Characteristic Functions
- Random Vectors
- Markov Inequality
- Chebyshev Inequality
- Chernoff Bounds
- Cauchy-Schwarz Inequality
- Law of Large Numbers
- Central Limit Theorem
- Convergence of Random Variables
- Point Estimation
- Maximum Likelihood Estimation

Additional course material such as Sigma Algebra and Borel Algebra can be incorporated into the RAG knowledge base later.

## Project Structure

```text
PMA_AI_TA/
+-- app.py
+-- requirements.txt
+-- config/
+-- data/
¦   +-- raw/
¦   +-- processed/
¦   +-- chunks/
+-- evaluation/
+-- prompts/
¦   +-- system_prompt.txt
+-- src/
¦   +-- download_sources.py
¦   +-- parse_documents.py
¦   +-- chunk_documents.py
¦   +-- build_vector_db.py
¦   +-- rag.py
¦   +-- ...
+-- vector_db/

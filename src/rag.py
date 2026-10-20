from pathlib import Path
import os

import chromadb
from dotenv import load_dotenv
from groq import Groq
from sentence_transformers import SentenceTransformer


# ==================================================
# PATHS
# ==================================================

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

VECTOR_DB_DIR = BASE_DIR / "vector_db"

SYSTEM_PROMPT_PATH = (
    BASE_DIR
    / "prompts"
    / "system_prompt.txt"
)


# ==================================================
# CONFIGURATION
# ==================================================

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

GROQ_API_KEY = os.getenv(
    "GROQ_API_KEY"
)

GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-20b"
)

TOP_K = 5

MAX_DISTANCE = 1.20

MAX_GENERATION_TOKENS = 700


# ==================================================
# VALIDATE CONFIGURATION
# ==================================================

if not GROQ_API_KEY:

    raise ValueError(
        "GROQ_API_KEY was not found. "
        "Check your .env file."
    )


# ==================================================
# LOAD SYSTEM PROMPT
# ==================================================

def load_system_prompt():

    return SYSTEM_PROMPT_PATH.read_text(
        encoding="utf-8"
    )


# ==================================================
# EMBEDDING MODEL
# ==================================================

print(
    "Loading embedding model..."
)

embedding_model = SentenceTransformer(
    EMBEDDING_MODEL
)


# ==================================================
# CHROMADB
# ==================================================

chroma_client = chromadb.PersistentClient(
    path=str(VECTOR_DB_DIR)
)

collection = chroma_client.get_collection(
    name="pma_course"
)


# ==================================================
# GROQ CLIENT
# ==================================================

groq_client = Groq(
    api_key=GROQ_API_KEY
)


# ==================================================
# RETRIEVAL
# ==================================================

def retrieve(
    question,
    k=TOP_K
):

    query_embedding = embedding_model.encode(
        [question],
        normalize_embeddings=True
    )[0]

    results = collection.query(
        query_embeddings=[
            query_embedding.tolist()
        ],
        n_results=k,
        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )

    return results


# ==================================================
# SCOPE GUARD
# ==================================================

def is_in_scope(
    results
):

    distances = results[
        "distances"
    ][0]

    if not distances:
        return False

    best_distance = distances[0]

    return (
        best_distance
        <= MAX_DISTANCE
    )


# ==================================================
# BUILD RAG CONTEXT
# ==================================================

def build_context(
    results
):

    documents = results[
        "documents"
    ][0]

    metadatas = results[
        "metadatas"
    ][0]

    context_blocks = []

    for i, (
        document,
        metadata
    ) in enumerate(
        zip(
            documents,
            metadatas
        ),
        start=1
    ):

        block = f"""
[SOURCE {i}]

Title: {metadata["title"]}
Topic: {metadata["topic"]}
Content Type: {metadata["content_type"]}
URL: {metadata["source_url"]}

Course Material:

{document}
"""

        context_blocks.append(
            block
        )

    return "\n".join(
        context_blocks
    )


# ==================================================
# BUILD SOURCES
# ==================================================

def build_sources(
    results
):

    metadatas = results[
        "metadatas"
    ][0]

    sources = []

    seen_urls = set()

    for metadata in metadatas:

        url = metadata[
            "source_url"
        ]

        if url in seen_urls:
            continue

        seen_urls.add(
            url
        )

        sources.append(
            {
                "title": metadata[
                    "title"
                ],
                "topic": metadata[
                    "topic"
                ],
                "url": url
            }
        )

    return sources


# ==================================================
# NORMALIZE MODEL OUTPUT
# ==================================================

def normalize_markdown_math(
    answer
):

    """
    Perform only safe delimiter normalization.

    We do NOT try to interpret or reconstruct equations.

    Streamlit Markdown handles:
        $ ... $     inline math
        $$ ... $$   display math
    """

    answer = answer.strip()

    # Convert common LaTeX display delimiters
    # into Markdown/KaTeX delimiters.

    answer = answer.replace(
        "\\[",
        "$$"
    )

    answer = answer.replace(
        "\\]",
        "$$"
    )

    # Convert common inline delimiters.

    answer = answer.replace(
        "\\(",
        "$"
    )

    answer = answer.replace(
        "\\)",
        "$"
    )

    # Remove accidental fenced math blocks while
    # preserving the actual LaTeX inside them.

    answer = answer.replace(
        "```math",
        "$$"
    )

    answer = answer.replace(
        "```latex",
        "$$"
    )

    answer = answer.replace(
        "```",
        "$$"
    )

    return answer.strip()


# ==================================================
# GENERATE ANSWER
# ==================================================

def generate_answer(
    question,
    context,
    conversation_context=None
):

    system_prompt = (
        load_system_prompt()
    )


    # --------------------------------------------------
    # Conversation context
    # --------------------------------------------------

    conversation_section = ""

    if conversation_context:

        conversation_section = f"""
---------------- CONVERSATION CONTEXT ----------------

{conversation_context}

---------------- END CONVERSATION CONTEXT ----------------

Use the previous conversation when the current question
is a follow-up.

Examples include:

- solve it
- give me a hint
- another one
- explain it
- why
- how
- make it harder
- make it easier

If the assistant previously gave the student a practice
problem and the student says "solve it", solve that exact
problem.

If the student asks for another problem, remain on the
current topic unless they explicitly change topics.
"""


    # --------------------------------------------------
    # Main prompt
    # --------------------------------------------------

    user_prompt = f"""
Answer the student's Probability Models and Applications
question using ONLY the retrieved course material.

This applies to ALL topics in the course.

Examples include:

- random variables
- PMFs
- PDFs
- CDFs
- expectation
- variance
- discrete distributions
- continuous distributions
- joint distributions
- conditional probability
- transformations
- moment-generating functions
- characteristic functions
- Markov inequality
- Chebyshev inequality
- Chernoff bounds
- sums of random variables
- probability bounds
- random vectors
- law of large numbers
- central limit theorem
- modes of convergence
- estimators
- maximum likelihood estimation
- sigma algebra
- Borel algebra

Do NOT treat any one topic such as Chebyshev's inequality
as special.

Use whichever retrieved PMA material is relevant to the
student's question.


==================================================
MATHEMATICAL FORMATTING
==================================================

Return ordinary Markdown.

Do NOT return JSON.

Do NOT return <TEXT> or <MATH> tags.

Do NOT use XML-style tags.

For SMALL mathematical notation that belongs naturally
inside a sentence, use inline LaTeX:

$X$

$E[X]$

$\\mu$

$\\sigma^2$

$M_X(s)$


For equations, derivations, probability expressions,
fractions, sums, integrals, or other substantial
mathematics, use display math:

$$
P(X \\geq a)
\\leq
e^{{-sa}} M_X(s)
$$


Another example:

$$
P\\left(|X-E[X]| \\geq b\\right)
\\leq
\\frac{{\\operatorname{{Var}}(X)}}{{b^2}}
$$


Another example:

$$
E[X]
=
\\sum_{{x_k \\in R_X}}
x_k P_X(x_k)
$$


Another example:

$$
\\hat{{\\theta}}_{{ML}}
=
\\operatorname{{argmax}}_\\theta
L(\\theta)
$$


IMPORTANT:

Every LaTeX command must appear inside either:

$ ... $

or

$$ ... $$

Never output raw LaTeX commands directly in ordinary prose.

Bad:

P(X \\geq a)

Good:

$$
P(X \\geq a)
$$

Bad:

The variance is \\sigma^2.

Good:

The variance is $\\sigma^2$.


==================================================
PEDAGOGICAL BEHAVIOR
==================================================

For conceptual questions:

- explain clearly;
- use terminology from the course material;
- include the relevant formula when useful.

For mathematical problems:

- identify the formula or theorem;
- show the important steps;
- explain the reasoning;
- provide the final answer.

If the student asks only for a practice question:

- provide the question;
- do not immediately provide its solution.

If difficulty is not specified:

- prefer a simple direct application of the current topic.

If the student asks for a hint:

- provide a hint without giving the complete solution.

If the student says "solve it":

- solve the most recent relevant practice question in
  the conversation.


==================================================
SOURCES
==================================================

Do NOT generate a Sources section.

Do NOT output source URLs.

Do NOT say "according to Source 1".

The application displays retrieved sources separately.


{conversation_section}


==================================================
COURSE CONTEXT
==================================================

{context}

==================================================
END COURSE CONTEXT
==================================================


STUDENT QUESTION:

{question}
"""


    response = (
        groq_client
        .chat
        .completions
        .create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            temperature=0,
            max_tokens=MAX_GENERATION_TOKENS
        )
    )


    raw_answer = (
        response
        .choices[0]
        .message
        .content
    )


    answer = normalize_markdown_math(
        raw_answer
    )


    return answer


# ==================================================
# COMPLETE RAG PIPELINE
# ==================================================

def ask(
    question,
    conversation_context=None
):

    retrieval_query = question


    # --------------------------------------------------
    # Context-aware retrieval
    # --------------------------------------------------

    if conversation_context:

        retrieval_query = f"""
Previous PMA conversation:

{conversation_context}

Current student question:

{question}
"""


    results = retrieve(
        retrieval_query
    )


    distances = results[
        "distances"
    ][0]


    if not distances:

        return {
            "status": "out_of_scope",
            "answer": (
                "No relevant PMA course material "
                "could be retrieved."
            ),
            "distance": None,
            "sources": []
        }


    best_distance = (
        distances[0]
    )


    # --------------------------------------------------
    # Scope rejection before LLM
    # --------------------------------------------------

    if not is_in_scope(
        results
    ):

        return {
            "status": "out_of_scope",
            "answer": (
                "This question appears to be outside "
                "the scope of the Probability Models "
                "and Applications course."
            ),
            "distance": best_distance,
            "sources": []
        }


    # --------------------------------------------------
    # Build course context
    # --------------------------------------------------

    context = build_context(
        results
    )


    # --------------------------------------------------
    # Generate answer
    # --------------------------------------------------

    answer = generate_answer(
        question,
        context,
        conversation_context=conversation_context
    )


    # --------------------------------------------------
    # Build source list
    # --------------------------------------------------

    sources = build_sources(
        results
    )


    return {
        "status": "answered",
        "answer": answer,
        "distance": best_distance,
        "sources": sources
    }


# ==================================================
# TERMINAL MODE
# ==================================================

def main():

    print(
        "\nPMA AI Teaching Assistant"
    )

    print(
        "-" * 50
    )


    while True:

        question = input(
            "\nAsk a question "
            "(type 'exit' to quit): "
        ).strip()


        if question.lower() == "exit":
            break


        if not question:
            continue


        result = ask(
            question
        )


        print(
            "\n" + "=" * 70
        )


        print(
            "\nANSWER:\n"
        )

        print(
            result["answer"]
        )


        if (
            result["distance"]
            is not None
        ):

            print(
                "\nRetrieval distance:",
                round(
                    result[
                        "distance"
                    ],
                    4
                )
            )


        if result["sources"]:

            print(
                "\nSOURCES:"
            )

            for i, source in enumerate(
                result["sources"],
                start=1
            ):

                print(
                    f"\n[{i}] "
                    f"{source['title']}"
                )

                print(
                    f"Topic: "
                    f"{source['topic']}"
                )

                print(
                    source["url"]
                )


        print(
            "\n" + "=" * 70
        )


if __name__ == "__main__":
    main()
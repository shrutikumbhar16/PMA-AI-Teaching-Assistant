import sys
from pathlib import Path
from uuid import uuid4

import streamlit as st


# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="PMA AI Teaching Assistant",
    page_icon="📘",
    layout="wide"
)


# ==================================================
# PROJECT SETUP
# ==================================================

BASE_DIR = Path(__file__).resolve().parent

sys.path.append(
    str(BASE_DIR / "src")
)

from rag import ask


# ==================================================
# RENDER ANSWER
# ==================================================

def render_answer(answer):

    """
    The current RAG pipeline returns normal Markdown
    containing inline and display LaTeX.

    Streamlit renders:
        $...$   -> inline math
        $$...$$ -> display math
    """

    if answer is None:
        return

    # Backward compatibility in case an older saved
    # session still contains structured blocks.
    if isinstance(answer, dict):

        blocks = answer.get(
            "blocks",
            []
        )

        for block in blocks:

            block_type = block.get(
                "type"
            )

            content = block.get(
                "content",
                ""
            )

            if not content:
                continue

            if block_type == "math":

                st.latex(
                    content
                )

            else:

                st.markdown(
                    content
                )

        return

    # New RAG format:
    # regular Markdown + $ / $$ LaTeX
    st.markdown(
        str(answer)
    )


# ==================================================
# CONVERT MESSAGE TO TEXT FOR CONVERSATION CONTEXT
# ==================================================

def message_to_text(
    message
):

    if message[
        "role"
    ] == "user":

        return (
            "Student: "
            + message["content"]
        )

    answer = message.get(
        "answer",
        ""
    )

    # Backward compatibility with older structured
    # responses still stored in this Streamlit session.
    if isinstance(
        answer,
        dict
    ):

        parts = []

        for block in answer.get(
            "blocks",
            []
        ):

            content = block.get(
                "content",
                ""
            )

            if content:
                parts.append(
                    content
                )

        return (
            "Assistant: "
            + "\n".join(parts)
        )

    return (
        "Assistant: "
        + str(answer)
    )


# ==================================================
# SESSION STATE
# ==================================================

if "chats" not in st.session_state:

    first_chat_id = str(
        uuid4()
    )

    st.session_state.chats = {
        first_chat_id: {
            "title": "New Chat",
            "messages": []
        }
    }

    st.session_state.current_chat_id = (
        first_chat_id
    )


if (
    "current_chat_id"
    not in st.session_state
):

    st.session_state.current_chat_id = next(
        iter(
            st.session_state.chats
        )
    )


# ==================================================
# CREATE NEW CHAT
# ==================================================

def create_new_chat():

    chat_id = str(
        uuid4()
    )

    st.session_state.chats[
        chat_id
    ] = {
        "title": "New Chat",
        "messages": []
    }

    st.session_state.current_chat_id = (
        chat_id
    )


# ==================================================
# SIDEBAR
# ==================================================

with st.sidebar:

    st.title(
        "📘 PMA Tutor"
    )

    if st.button(
        "➕ New Chat",
        use_container_width=True
    ):

        create_new_chat()

        st.rerun()

    st.divider()

    st.subheader(
        "Chat History"
    )

    for (
        chat_id,
        chat
    ) in st.session_state.chats.items():

        if st.button(
            chat["title"],
            key=f"chat_{chat_id}",
            use_container_width=True
        ):

            st.session_state.current_chat_id = (
                chat_id
            )

            st.rerun()


# ==================================================
# CURRENT CHAT
# ==================================================

current_chat_id = (
    st.session_state
    .current_chat_id
)

current_chat = (
    st.session_state
    .chats[
        current_chat_id
    ]
)


# ==================================================
# HEADER
# ==================================================

st.title(
    "📘 Probability Models and Applications"
)

st.caption(
    "Course-specific AI Teaching Assistant"
)


# ==================================================
# DISPLAY PREVIOUS MESSAGES
# ==================================================

for message in current_chat[
    "messages"
]:

    role = message[
        "role"
    ]

    with st.chat_message(
        role
    ):

        if role == "user":

            st.markdown(
                message[
                    "content"
                ]
            )

        else:

            render_answer(
                message[
                    "answer"
                ]
            )

            sources = message.get(
                "sources",
                []
            )

            if sources:

                with st.expander(
                    "Sources"
                ):

                    for (
                        i,
                        source
                    ) in enumerate(
                        sources[:3],
                        start=1
                    ):

                        st.markdown(
                            f"**{i}. "
                            f"{source['title']}**"
                        )

                        st.markdown(
                            f"[View course source]"
                            f"({source['url']})"
                        )


# ==================================================
# CHAT INPUT
# ==================================================

question = st.chat_input(
    "Ask a PMA question..."
)


# ==================================================
# HANDLE QUESTION
# ==================================================

if question:

    # --------------------------------------------------
    # Build conversation context BEFORE adding
    # the new user question.
    # --------------------------------------------------

    previous_messages = (
        current_chat[
            "messages"
        ][-4:]
    )

    conversation_context = (
        "\n\n".join(
            message_to_text(
                message
            )
            for message
            in previous_messages
        )
    )

    if not (
        conversation_context
        .strip()
    ):

        conversation_context = None


    # --------------------------------------------------
    # Store user message
    # --------------------------------------------------

    current_chat[
        "messages"
    ].append(
        {
            "role": "user",
            "content": question
        }
    )


    # --------------------------------------------------
    # Automatically title new chat
    # --------------------------------------------------

    if (
        current_chat[
            "title"
        ]
        == "New Chat"
    ):

        title = (
            question
            .strip()
        )

        if len(
            title
        ) > 35:

            title = (
                title[:35]
                + "..."
            )

        current_chat[
            "title"
        ] = title


    # --------------------------------------------------
    # Display current user question
    # --------------------------------------------------

    with st.chat_message(
        "user"
    ):

        st.markdown(
            question
        )


    # --------------------------------------------------
    # Generate assistant response
    # --------------------------------------------------

    with st.chat_message(
        "assistant"
    ):

        with st.spinner(
            "Searching course material..."
        ):

            try:

                result = ask(
                    question,
                    conversation_context=(
                        conversation_context
                    )
                )


                # ==========================================
                # OUT OF SCOPE
                # ==========================================

                if (
                    result[
                        "status"
                    ]
                    == "out_of_scope"
                ):

                    answer = (
                        result.get(
                            "answer"
                        )
                        or
                        (
                            "This question appears "
                            "to be outside the scope "
                            "of the Probability Models "
                            "and Applications course."
                        )
                    )

                    render_answer(
                        answer
                    )

                    current_chat[
                        "messages"
                    ].append(
                        {
                            "role": "assistant",
                            "answer": answer,
                            "sources": []
                        }
                    )


                # ==========================================
                # VALID PMA RESPONSE
                # ==========================================

                else:

                    answer = result[
                        "answer"
                    ]

                    render_answer(
                        answer
                    )


                    # --------------------------------------
                    # Remove duplicate sources
                    # --------------------------------------

                    unique_sources = []

                    seen_urls = set()

                    for source in result[
                        "sources"
                    ]:

                        url = source[
                            "url"
                        ]

                        if (
                            url
                            not in seen_urls
                        ):

                            unique_sources.append(
                                source
                            )

                            seen_urls.add(
                                url
                            )


                    unique_sources = (
                        unique_sources[:3]
                    )


                    # --------------------------------------
                    # Display sources
                    # --------------------------------------

                    if unique_sources:

                        with st.expander(
                            "Sources"
                        ):

                            for (
                                i,
                                source
                            ) in enumerate(
                                unique_sources,
                                start=1
                            ):

                                st.markdown(
                                    f"**{i}. "
                                    f"{source['title']}**"
                                )

                                st.markdown(
                                    f"[View course source]"
                                    f"({source['url']})"
                                )


                    # --------------------------------------
                    # Store assistant response
                    # --------------------------------------

                    current_chat[
                        "messages"
                    ].append(
                        {
                            "role": "assistant",
                            "answer": answer,
                            "sources": (
                                unique_sources
                            )
                        }
                    )


            except Exception as e:

                st.error(
                    f"An error occurred: {e}"
                )
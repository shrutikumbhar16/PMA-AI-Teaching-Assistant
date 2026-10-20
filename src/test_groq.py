import os

from dotenv import load_dotenv
from groq import Groq


load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-20b"
)


client = Groq(
    api_key=GROQ_API_KEY
)


response = client.chat.completions.create(
    model=GROQ_MODEL,
    messages=[
        {
            "role": "user",
            "content": (
                "Explain expectation of a "
                "random variable briefly."
            ),
        }
    ],
    temperature=0,
    max_tokens=500,
)


print(
    response.choices[0].message.content
)
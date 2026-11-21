from langchain_groq import ChatGroq
from dotenv import load_dotenv
load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-20b"
)

question = "Iska kya use hai?"

prompt = f"""
Rewrite the user's question into
a clear and meaningful search query.

Original question: {question}

Rewritten query:
"""

response = llm.invoke(prompt)

print(response.content)
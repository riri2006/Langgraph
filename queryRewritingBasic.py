from langchain_groq import ChatGroq
from dotenv import load_dotenv
load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-20b"
)

question = input("ASK: ")

prompt = f"""
Rewrite the user's question into
a clear and meaningful search query.

Original question: {question}

Rewritten query:

AND ALSO GIVE ANSWER FOR THAT QUERY
"""

response = llm.invoke(prompt)
print(response.content)
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-20b"
)

memory = MemorySaver()

system_prompt = """
You are a helpful conversational assistant.

Your job is to understand the user's questions
and convert it into a prompt so that ai can understand

Rewritten Query:
Answer:
"""

agent = create_agent(
    model=llm,
    system_prompt=system_prompt,
    checkpointer=memory
)

config = {
    "configurable": {
        "thread_id": "1"
    }
}

while True:

    question = input("ASK: ")

    if question.lower() in ["terminate", "exit"]:
        print("TERMINATING CONVERSATION.. THANK YOU!")
        break

    response = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": question
                }
            ]
        },
        config=config
    )

    print("\nAnswer:")
    print(response["messages"][-1].content)
    print()

from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(model="openai/gpt-oss-20b")


# AI node
def chatbot(state: MessagesState):

    response = llm.invoke(state["messages"])

    return {
        "messages": [response]
    }


# Graph
builder = StateGraph(MessagesState)

builder.add_node("chatbot", chatbot)
builder.add_edge(START, "chatbot")
builder.add_edge("chatbot", END)

with SqliteSaver.from_conn_string("chat_history.sqlite") as memory:

    app = builder.compile(checkpointer=memory)

    configuration = {
        "configurable": {
            "thread_id": "riddhi_personal_chat"
        }
    }

    while True:

        query = input("\nYou: ")

        if query.lower() == "exit":
            break

        response = app.invoke(
            {
                "messages": [
                    HumanMessage(content=query)
                ]
            },
            config=configuration
        )
        print("\nAI:", response["messages"][-1].content)
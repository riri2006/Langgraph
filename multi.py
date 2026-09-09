from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel
from dotenv import load_dotenv
load_dotenv()

llm=ChatGroq(model="openai/gpt-oss-20b")

class State(BaseModel):
    query:str
    route: str=""
    answer: str=""

def classifier(state:State):
    r = llm.invoke(f"Classify the question in three category and answer only that wheter it belongs to tavily, llm, addition according to question: {state.query}")
    return {"route": r.content}

def addition(a:int, b:int):
    """add the numbers given by user"""
    return  {"answer":a+b}

def llmchat(state:State):
    r=llm.invoke(f"give relevant answer for user's question: {state.query}")
    return{"answer":r.content}

def tavily(state:State):
    tool = TavilySearch(max_results =2)
    res = tool.invoke(state.query)
    return{"answer": res["results"]}

def decide(state:State):
    return state.route

graph= StateGraph(State)

graph.add_node("router", classifier)
graph.add_node("addition", addition)
graph.add_node("llm", llmchat)
graph.add_node("tavily", tavily)

graph.add_edge(START,"router")

graph.add_conditional_edges(
    "router",
    decide,
    {
        "additon": "addition",
        "llm":"llm",
        "tavily":"tavily"
    }
)
graph.add_edge("addition", END)
graph.add_edge("llm", END)
graph.add_edge("tavily", END)

app = graph.compile()

User_question = input("Ask: ")

response = app.invoke(State(query=User_question))

print("Assistant: ", response["answer"])
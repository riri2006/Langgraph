from langchain_experimental.tools import PythonREPLTool
from langchain_community.tools import WikipediaQueryRun
from langchain.agents import create_agent
from langchain_groq import ChatGroq
from pydantic import BaseModel
from langchain_community.utilities import WikipediaAPIWrapper
from langgraph.graph import StateGraph, START, END
from typing import Literal
from dotenv import load_dotenv
load_dotenv()

llm = ChatGroq(model="openai/gpt-oss-20b")

class State(BaseModel):
    query: str
    answer: str = ""
    route: str = ""

def router(state: State):

    class RouteDecision(BaseModel):
        route: Literal["Python", "Wikipedia"]

    structured_llm = llm.with_structured_output(RouteDecision)

    res = structured_llm.invoke(
        f"""
        Classify the user's query into one category.

        Python: Coding questions, Python programs,
        calculations, or code generation.

        Wikipedia: General information, history,
        people, places, concepts, or factual questions.

        User query: {state.query}
        """
    )

    return {"route": res.route}

def PythonTool(state: State):

    python_tool = PythonREPLTool()

    agent = create_agent(
        model=llm,
        tools=[python_tool]
    )

    result = agent.invoke({
        "messages": [
            {
                "role": "user",
                "content": state.query
            }
        ]
    })

    return {
        "answer": result["messages"][-1].content
    }

def WikiTool(state: State):

    api = WikipediaAPIWrapper(
        top_k_results=3,
        doc_content_chars_max=2000
    )

    wikitool = WikipediaQueryRun(api_wrapper=api)

    result = wikitool.invoke(state.query)

    return {
        "answer": result
    }

def decide(state: State):
    return state.route

graph = StateGraph(State)

graph.add_node("Router", router)
graph.add_node("PythonNode", PythonTool)
graph.add_node("WikiNode", WikiTool)

graph.add_edge(START, "Router")

graph.add_conditional_edges(
    "Router",
    decide,
    {
        "Python": "PythonNode",
        "Wikipedia": "WikiNode"
    })

graph.add_edge("PythonNode", END)
graph.add_edge("WikiNode", END)

demo = graph.compile()
query = input("Ask: ")

result = demo.invoke({
    "query": query })

print("Assistant:", result["answer"])
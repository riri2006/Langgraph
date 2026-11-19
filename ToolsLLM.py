from langchain_experimental.tools import PythonREPLTool
from langchain_community.tools import WikipediaQueryRun
from langchain.agents import create_agent
from langchain_groq import ChatGroq
from pydantic import BaseModel
from langchain_community.utilities import WikipediaAPIWrapper

llm=ChatGroq(model="openai/gpt-oss-20b")

class State(BaseModel):
    query: str
    answer: str=""
    route: str=""

def router(State):
    res=llm.invoke(f"CLASSIFY THE USER'S QUERY {State.query} IN TWO CLASSES ONLY 1. Python OR 2.Wikipedia.. If user is asking about writing or any coding question then choose PYTHON and if user is asking about some information then choose WIKIPEDIA ")
    return {"route":res.content}


def ToolNode1():
    python_tool = PythonREPLTool()

    agent=create_agent(
        model=llm,
        tools=[python_tool]
    )
    
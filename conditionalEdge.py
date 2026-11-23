from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel
from dotenv import load_dotenv
load_dotenv()

#step 1 - we will create llm 
llm = ChatGroq(model="openai/gpt-oss-20b")

#step 2- create state schema 

class StateSchema(BaseModel):
    question : str
    route : str =""
    answer: str =""

#step 3- Nodes 
def router(state:StateSchema):
    r = llm.invoke(f"Answer only in one word wheter its general or coding by classifying the question that whetere it is coding or general for question: {state.question}")
    return{"route": r.content}

def coding(state:StateSchema):
    r= llm.invoke(f"Answer as coding expert for question: {state.question}")
    return{"answer":r.content}

def general(state:StateSchema):
    r= llm.invoke(f"Answer as general expert for question: {state.question}")
    return{"answer":r.content}

def decide(state:StateSchema):
    return state.route

#step 4- stategraph and nodes and edges

graph = StateGraph(StateSchema)

graph.add_node("router_node", router)
graph.add_node("coding_node", coding)
graph.add_node("general_node", general)

graph.add_edge(START , "router_node")
graph.add_conditional_edges(
    "router_node",
    decide,
    {
        "coding": "coding_node",
        "general" : "general_node"
    }
)

graph.add_edge("coding_node", END)
graph.add_edge("general_node", END)

#step 5 - graph compile and llm invoke of final user question
app = graph.compile()

User_question = input("Ask: ")

response = app.invoke(StateSchema(question=User_question))

print("Assistant: ", response["answer"])
from langgraph.graph import StateGraph,START,END
from langchain_groq import ChatGroq
from pydantic import BaseModel
from dotenv import load_dotenv
load_dotenv()

llm=ChatGroq(model="openai/gpt-oss-20b")

class State(BaseModel):
    query: str=""
    prompt:str=""
    answer:str=""

def Rewriting(State):
    res=llm.invoke(f"convert the user query {State.query} into a clear and understandable prompt")
    return{"prompt":res.content}

def Generation(State):
    res=llm.invoke(f"understand the prompt and give answer for that in the way as mentioned in prompt {State.prompt}")
    return{"answer":res.content}

graph=StateGraph(State)

graph.add_node("PromptNode",Rewriting)
graph.add_node("AnswerNode",Generation)

graph.add_edge(START,"PromptNode")
graph.add_edge("PromptNode","AnswerNode")
graph.add_edge("AnswerNode",END)

demo = graph.compile()

user=input("ASK: ")
res= demo.invoke({"query":user})
print("\nAI Generated PROMPT: ",res["prompt"])
print("\nAI Generated ANSWER: ",res["answer"])
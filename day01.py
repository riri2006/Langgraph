from pydantic import BaseModel
from langgraph.graph import StateGraph, START, END

class Fruits(BaseModel):
    name : str
    unit : int

def function1(state:Fruits):
    print("First Fruit: ", state.name)
    print("First fruit unit: ", state.unit)

def function2(state: Fruits):
    print("\nSecond Fruit: Lychee ")
    print("Second fruit unit: 100")

def function3(state:Fruits):
    print("\nThird Fruit: ", state.name)
    print("Third fruit unit: ", state.unit)

def function4(state:Fruits):
    print("\nFourth Fruit: Apple")
    print("Fourth fruit unit: 200")

graph = StateGraph(Fruits)

#Nodes
graph.add_node("Node1", function1)
graph.add_node("Node2", function2)
graph.add_node("Node3", function3)
graph.add_node("Node4", function4)

#Edges
graph.add_edge(START, "Node1")
graph.add_edge("Node1", "Node2")
graph.add_edge("Node2", "Node3")
graph.add_edge("Node3", "Node4")
graph.add_edge("Node4", END)

#COMPILATION
demo = graph.compile()
result = demo.invoke({"name": "Mango", "unit":150})
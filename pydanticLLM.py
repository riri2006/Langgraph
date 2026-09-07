from pydantic import BaseModel
from langchain_groq import ChatGroq
from dotenv import load_dotenv
load_dotenv()

class Person(BaseModel):
    name:str
    age: int

llm= ChatGroq(model="openai/gpt-oss-20b")

structured_llm = llm.with_structured_output(Person)

# result = structured_llm.invoke("Hi my name is Riddhi and i am 20 years old")
query= input("ASK: ")
result = structured_llm.invoke(query)
print(result)
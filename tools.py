from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain_tavily import TavilySearch
load_dotenv()
llm = ChatGroq(
    model="openai/gpt-oss-20b"
)
user = input("ASK: ")
tool = TavilySearch(max_results =2)
res = tool.invoke(user)
print(res["results"][0]["content"])

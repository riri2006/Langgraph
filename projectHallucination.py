from langchain_groq import ChatGroq
from llama_cloud import LlamaCloud
from langchain_core.documents import Document
from langchain_experimental.text_splitter import SemanticChunker
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel
from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()

llm = ChatGroq(model="openai/gpt-oss-20b")
memory = MemorySaver()
agent = create_agent(
    model=llm,
    checkpointer=memory
)

class State(BaseModel):
    query :str
    route: str=""
    answer: str=""

class Rag():
    path = input("Enter path of your file or any reference: ")

    connection = LlamaCloud(
        api_key=os.getenv("LLAMA_CLOUD_API_KEY"),
        timeout=120.0)

    file = connection.files.create(
        file= Path(path),
        purpose="parse"
    )

    job= connection.parsing.create(
        tier="agentic",
        version="latest",
        file_id=file.id
    )

    parsed = connection.parsing.get(
        job.id
        expand ="markdown"
    )
    documents =[]

    for doc in parsed.markdown.pages:
        documents.append(
            Document(
                page_content=doc.markdown,
            )
        )

    embeddings = OllamaEmbeddings(model="nomic-embed-text:latest")
    spiltter = SemanticChunker(embeddings=embeddings)


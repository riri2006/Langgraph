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
from langchain_tavily import TavilySearch
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
    def __init__(self, path):

        self.path = path
        self.connection = LlamaCloud(
            api_key=os.getenv("LLAMA_CLOUD_API_KEY"),
            timeout=120.0
        )
        self.file = self.connection.files.create(
            file=Path(path),
            purpose="parse"
        )
        self.job = self.connection.parsing.create(
            tier="agentic",
            version="latest",
            file_id=self.file.id
        )
        self.parsed = self.connection.parsing.get(
            self.job.id,
            expand="markdown"
        )
        self.documents = []

        for doc in self.parsed.markdown.pages:

            self.documents.append(
                Document(
                    page_content=doc.markdown
                )
            )
        self.embeddings = OllamaEmbeddings(
            model="nomic-embed-text:latest"
        )
        self.splitter = SemanticChunker(
            embeddings=self.embeddings
        )
        self.chunks = self.splitter.split_documents(
            self.documents
        )
        self.vdb = Chroma.from_documents(
            documents=self.chunks,
            embedding=self.embeddings,
            persist_directory="./ph_db"
        )
        def answer(self, query):
            response = self.vdb.similarity_search(
                query=query,
                k=5
            )
            context = "\n\n".join(
                doc.page_content
                for doc in response
            )

            prompt = f"""
                You are a strict document-grounded AI assistant.

                User Question:
                {query}
                Retrieved Document Context:
                {context}
                Answer the question using ONLY the information
                supported by the document context.
                Rules:
                1. If the answer is available in the document,
                answer clearly and accurately.
                2. Do not invent, assume, guess, or hallucinate
                information.
                3. If the document does not contain enough information,
                say:
                "I could not find this information in the
                provided reference document."
                4. If only part of the answer is available,
                provide only the supported information.
                5. If the user asks for an explanation or meaning,
                explain the document information in simple language.
                6. Do not use unrelated general knowledge.
                7. Keep the answer simple and direct.
                """

            result = llm.invoke(prompt)

            return result.content

def tavily(state: State):

    tool = TavilySearch(max_results=2)

    res = tool.invoke(state.query)

    prompt = f"""
You are a reliable AI assistant.

User Question:
{state.query}

Tavily Search Results:
{res["results"]}

Your task is to answer the user's question using the Tavily
search results.

Rules:

1. If the search results contain enough reliable information
   to answer the question, provide the answer clearly.

2. Do not guess, assume, or hallucinate any information.

3. If the search results are empty, irrelevant, or do not contain
   enough information to answer the question accurately, DO NOT
   answer using your own knowledge.

4. In that case, respond exactly:

"I could not find enough reliable information to answer this
question. Please upload a relevant reference document or file,
and I will use it to answer your question."

5. If the information is partially available, provide only the
   information supported by the search results and ask the user
   to upload a reference document for the missing information.

6. Keep the response clear and concise.
"""

    response = llm.invoke(prompt)

    if "Please upload a relevant reference document" in response.content:
        return {
            "route": "rag",
            "answer": response.content
        }

    return {
        "route": "tavily",
        "answer": response.content
    }

def decide(state: State):
    return state.route

def rag_node(state: State):
    path = input(
        "Please enter the path of your document: "
    )
    rag = Rag(path)
    answer = rag.answer(state.query)
    return {
        "answer": answer,
        "route": "rag"
    }

graph = StateGraph(State)

graph.add_node("router", router)
graph.add_node("tavily", tavily)
graph.add_node("rag", rag_node)

graph.add_edge(START, "router")
graph.add_conditional_edges(
    "router",
    decide,
    {
        "tavily": "tavily",
        "rag": "rag"
    }
)

graph.add_edge("tavily", END)
graph.add_edge("rag", END)
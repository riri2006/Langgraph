from langchain_groq import ChatGroq
from llama_cloud import LlamaCloud
from langchain_core.documents import Document
from langchain_experimental.text_splitter import SemanticChunker
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_tavily import TavilySearch
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel, Field
from pathlib import Path
from dotenv import load_dotenv
import os
import time

load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0
)


class State(BaseModel):
    query: str
    route: str = ""
    answer: str = ""
    history: list[str] = Field(default_factory=list)
    document_path: str = ""


class Rag:

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

        job_id = self.job.id

        while True:
            parsed = self.connection.parsing.get(
                job_id,
                expand="markdown"
            )
            status = str(
                getattr(parsed, "status", "")
            ).lower()
            if status in ["completed", "success", "successful"]:
                break
            if status in ["failed", "error"]:
                raise Exception("LlamaCloud parsing failed.")
            time.sleep(2)
            self.parsed = parsed

        if self.parsed.markdown is None:
            raise Exception(
                "LlamaCloud did not return markdown content."
            )

        self.documents = [
            Document(page_content=page.markdown)
            for page in self.parsed.markdown.pages
        ]

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

    def answer(self, query, history=""):

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

Conversation History:
{history}

User Question:
{query}

Retrieved Document Context:
{context}

Answer ONLY using the retrieved document context.

Rules:
1. Do not use general knowledge.
2. Do not invent, assume, guess, or hallucinate.
3. If the answer exists in the document, answer clearly.
4. If the answer does not exist in the document, say exactly:
"I could not find this information in the provided reference document."
5. Use conversation history to understand follow-up questions such as:
"his projects", "his email", "what about his skills".
6. Keep the answer simple and direct.
"""

        result = llm.invoke(prompt)

        return result.content


rag_instance = None


def router(state: State):

    prompt = f"""
Classify the user's question into exactly ONE category.

rag:
Use rag when the answer requires information from any
user-provided document, file, image, PDF, resume, Word file,
Excel file, or other user data.

tavily:
Use tavily when the answer requires information from the
internet, current information, latest information, news,
or web sources.

Examples:

"What are the skills in this resume?" → rag
"What are his projects?" → rag
"What is his email?" → rag
"What is written in this PDF?" → rag
"What is written in this image?" → rag
"Summarize my document" → rag

"What is today's weather?" → tavily
"What is the latest AI news?" → tavily
"Who is the current CEO of OpenAI?" → tavily

Do not answer the question.
Return ONLY:
rag
OR
tavily

Question:
{state.query}
"""

    result = llm.invoke(prompt)

    route = result.content.strip().lower()

    if "tavily" in route:
        return {"route": "tavily"}

    return {"route": "rag"}


def decide(state: State):
    return state.route


def tavily(state: State):

    tool = TavilySearch(
        max_results=3
    )

    results = tool.invoke(
        state.query
    )

    prompt = f"""
You are a reliable AI assistant.

User Question:
{state.query}

Web Search Results:
{results}

Answer ONLY using the web search results.

Do not guess or hallucinate.

If the search results do not contain enough information,
say:

"I could not find enough reliable information to answer this question."

Keep the answer concise.
"""

    response = llm.invoke(prompt)

    return {
        "answer": response.content,
        "route": "tavily"
    }


def rag_node(state: State):

    global rag_instance

    if rag_instance is None:

        path = input(
            "\nPlease enter the path of your document/image/file: "
        )

        path = path.strip().strip('"')

        if not os.path.exists(path):
            return {
                "answer": "The provided file path does not exist.",
                "route": "rag"
            }

        rag_instance = Rag(path)

    history = "\n".join(
        state.history[-6:]
    )

    answer = rag_instance.answer(
        state.query,
        history
    )

    return {
        "answer": answer,
        "route": "rag",
        "document_path": rag_instance.path
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

app = graph.compile()

history = []

while True:

    query = input(
        "\nEnter your question: "
    ).strip()

    if query.lower() in [
        "exit",
        "bye",
        "quit",
        "terminate"
    ]:
        print("Terminating conversation...")
        break

    result = app.invoke(
        State(
            query=query,
            history=history
        )
    )

    print("\nAnswer:")
    print(result.get("answer", "No answer returned."))

    history.append(
        f"User: {query}"
    )

    history.append(
        f"Assistant: {result.get('answer', '')}"
    )
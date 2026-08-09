import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser

try:
    from langchain_groq import ChatGroq
except ImportError:  # pragma: no cover - optional dependency
    ChatGroq = None

ROOT_DIR = Path(__file__).resolve().parents[2]
ENV_PATH = ROOT_DIR / ".env"


def _load_env():
    try:
        load_dotenv(dotenv_path=ENV_PATH)
    except Exception:
        pass


def retrival(vector_db):
    return "\n\n".join(doc.page_content for doc in vector_db)


def get_llm():
    _load_env()

    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise RuntimeError("GROQ_API_KEY is not configured.")
    if ChatGroq is None:
        raise RuntimeError("langchain_groq is not installed.")

    return ChatGroq(
        model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
        temperature=0,
        groq_api_key=groq_api_key,
    )


llm = None


def get_default_llm():
    global llm
    if llm is None:
        llm = get_llm()
    return llm


def response_generator(vector_store, llm_instance=None):

    retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 8})
    model = llm_instance or get_default_llm()

    rag_chain = (
        {
            "context": retriever | RunnableLambda(retrival), 
            "question": RunnablePassthrough()
        }
        | ChatPromptTemplate.from_template(
            """You are answering questions about a software repository.

                Rely primarily on the retrieved context below to answer the question.

                Rules:

                - If the retrieved context contains the answer or relevant clues, explain it clearly.
                - If the context does not contain enough information, you can use general programming and software engineering knowledge to explain how it would normally be implemented or configured, but clearly specify what is general knowledge versus what is explicitly present in the codebase.
                - Never make up specific variable names or file structures that are not in the context.
                - When answering, explicitly reference the relevant file or function from the context whenever possible.
                - Keep the answer concise, accurate, and direct.
                - try to give the shorter answer by providin the response in less words if youser didnt ask for it.

                Context:
                {context}

                Question:
                {question}

                Answer:"""
        )
        | model
        | StrOutputParser()
    )
    
    return rag_chain
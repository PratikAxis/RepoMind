from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama


def retrival(vector_db):
    return "\n\n".join(doc.page_content for doc in vector_db)

llm = ChatOllama(
    model="phi3:mini", 
    temperature=0,
    base_url="http://localhost:11434"
)

def response_generator(vector_store):

    retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 5})

    rag_chain = (
        {
            "context": retriever | RunnableLambda(retrival), 
            "question": RunnablePassthrough()
        }
        | ChatPromptTemplate.from_template(
            """You are answering questions about a software repository.

                Use ONLY the retrieved context.

                Rules:

                - Never use outside knowledge.
                - Never assume missing implementation details.
                - Never write "likely", "probably", "assume", or similar speculative language.
                - If the retrieved context does not contain enough information, reply:

                "I couldn't find enough information in the retrieved codebase context."

                - When answering, explicitly reference the relevant file or function whenever possible.

                Context:
                {context}

                Question:
                {question}

                Answer:"""
        )
        | llm
        | StrOutputParser()
    )
    
    return rag_chain
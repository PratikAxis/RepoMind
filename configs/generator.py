from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama


def retrival(vector_db):
    return "\n\n".join(doc.page_content for doc in vector_db)

llm = ChatOllama(
    model="phi3:mini", 
    temperature=0.7,
    base_url="http://localhost:11434"
)

def response_generator(vector_store):

    retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 4})

    rag_chain = (
        {
            "context": retriever | RunnableLambda(retrival), 
            "question": RunnablePassthrough()
        }
        | ChatPromptTemplate.from_template(
            """You are a coding assistant. Use the following code context to answer the question.
            If the answer is not in the context, say "I don't know".

            Context:
            {context}

            Question: {question}
            Answer:"""
        )
        | llm
        | StrOutputParser()
    )
    
    return rag_chain
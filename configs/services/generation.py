from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from ritrival import retrieval

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)   


def response_generation(query):

    context = retrieval(query)

    template = """You are a coding assistant. Use the following code context to answer the question.
    If the answer is not in the context, say "I don't know".

    Context:
    {context}

    Question: {query}
    Answer:"""

    prompt = ChatPromptTemplate.from_template(template)

    llm = ChatOllama(
        model="phi-4-mini", 
        temperature=0.7,
        base_url="http://localhost:11434"
    )

    rag_chain = ( 
                {"context": retrieval | RunnableLambda(format_docs),
                "question": RunnablePassthrough()
                }
            | prompt
            | llm
            | StrOutputParser()
                )
    
    response = rag_chain.invoke(query)
    return response

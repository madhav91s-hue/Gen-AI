import os
from pathlib import Path
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# Load environment variables from .env
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

PDF_PATH = "Dietary.pdf"
FAISS_INDEX_PATH = "faiss_dietary_index"

# Initialize OpenAI components
embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


def build_and_save_faiss(pdf_path: str, save_path: str) -> FAISS:
    """Parses PDF, chunks text, creates FAISS index, and saves locally."""
    print(f"Reading and loading {pdf_path}...")
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    print("Splitting text into chunks...")
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = splitter.split_documents(documents)
    print(f"Generated {len(chunks)} chunks.")

    print("Generating embeddings and building local FAISS index...")
    vector_store = FAISS.from_documents(chunks, embedding_model)

    print(f"Persisting FAISS index locally to folder '{save_path}'...")
    vector_store.save_local(save_path)
    return vector_store


# Load existing local vector DB or build a new one
if not os.path.exists(FAISS_INDEX_PATH):
    vector_store = build_and_save_faiss(PDF_PATH, FAISS_INDEX_PATH)
else:
    print(f"Loading local FAISS database from '{FAISS_INDEX_PATH}'...")
    vector_store = FAISS.load_local(
        FAISS_INDEX_PATH,
        embedding_model,
        allow_dangerous_deserialization=True,
    )

retriever = vector_store.as_retriever(search_kwargs={"k": 4})


def format_docs(docs):
    """Formats retrieved document chunks with 1-based page numbers."""
    formatted_chunks = []
    for d in docs:
        page = d.metadata.get("page", 0) + 1
        formatted_chunks.append(f"[Page {page}]:\n{d.page_content}")
    return "\n\n".join(formatted_chunks)


# Context-grounded prompt for dietary guidelines
prompt = ChatPromptTemplate.from_template(
    """You are an assistant answering questions strictly based on the Dietary Guidelines for Indians manual.
Use ONLY the following context retrieved from the PDF to answer the question.
If the answer is not present in the context, clearly state: "The document does not contain information to answer this question."

Context:
{context}

Question: {question}

Answer:"""
)

# Build RAG Chain
rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# Interactive User Q&A Loop
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Dietary Guidelines Q&A App Ready!")
    print("Ask any question regarding Dietary.pdf.")
    print("Type 'exit' or 'quit' to end the session.")
    print("=" * 60 + "\n")

    while True:
        try:
            user_question = input("Your Question: ").strip()
            if not user_question:
                continue
            if user_question.lower() in ["exit", "quit", "q"]:
                print("\nExiting. Stay healthy!")
                break

            print("\nSearching vector DB and generating answer...\n")
            response = rag_chain.invoke(user_question)
            print(f"Answer:\n{response}\n")
            print("-" * 60)

        except (KeyboardInterrupt, EOFError):
            print("\nSession interrupted. Exiting.")
            break
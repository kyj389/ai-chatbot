import os
import chromadb
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from docx import Document as DocxLoader
from langchain.document_loaders import PyPDFLoader


def read_docx(path: str):
    doc = DocxLoader(path)
    text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
    return [Document(page_content=text, metadata={"source": path})]

def read_pdf(file_path: str):
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    return documents

def get_document(file_path: str):
    if file_path.endswith(".docx"):
        return read_docx(file_path)
    elif file_path.endswith(".pdf"):
        return read_pdf(file_path)
    else:
        print(f"지원하지 않는 파일 형식입니다.{file_path.split('/')[-1]}")


def create_langchain(dir_path):
    documents = []
    collection = chromadb.Client().create_collection(name="docs")

    for file_name in os.listdir(dir_path):
        file_path = os.path.join(dir_path, file_name)
        documents += get_document(file_path)
        

    # 3. 문서 분할 (chunking)
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    split_docs = text_splitter.split_documents(documents)


    # 4. 임베딩 모델 준비 (OpenAI)
    embedding = OpenAIEmbeddings()

    # 5. Chroma 벡터 DB에 저장
    vectordb = Chroma.from_documents(split_docs, embedding, persist_directory="./chroma_db")
    vectordb.persist()

    # 6. Retriever 생성
    retriever = vectordb.as_retriever(search_kwargs={"k": 3})

    # 7. QA 체인 생성 (Retriever + ChatGPT)
    qa_chain = RetrievalQA.from_chain_type(
        # llm=ChatOpenAI(model_name="gpt-4o-mini", temperature=0.2),
        llm=ChatOpenAI(model_name="gpt-4", temperature=0.2),
        chain_type="stuff",  # 또는 "map_reduce" 등
        retriever=retriever,
        return_source_documents=True
    )

    return qa_chain


# 8. 질의
query = "신한은행의 최근 신사업은?"
langchain = create_langchain("./test")
result = langchain(query)

print("\n📌 답변:")
print(result["result"])

print("\n📚 관련 문서:")
for doc in result["source_documents"]:
    print(f"- {doc.metadata['source']}")

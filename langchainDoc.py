
from langchain.document_loaders import PyPDFLoader
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
import os
import streamlit as st


# OpenAI API 키 설정
os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

# 임베딩 모델 설정
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


def process(file_path):
    if file_path.endswith('.pdf'):
        return process_pdf(file_path)
    else:
        raise ValueError("지원되지 않는 파일 형식입니다.")


# PDF 파일 처리 함수
def process_pdf(pdf_file):
    loader = PyPDFLoader(pdf_file)
    documents = loader.load()

    vector_store = FAISS.from_documents(documents, embedding_model)
    vector_store.save_local("faiss_index")

    return "PDF 처리 및 임베딩 저장 완료."

# 질문 응답 생성 함수
def answer_question(query):
    vector_store = FAISS.load_local("faiss_index", embedding_model, allow_dangerous_deserialization=True)
    # llm = ChatOpenAI(model_name="gpt-4o")
    llm = ChatOpenAI(model_name="gpt-3.5-turbo")
    qa_chain = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=vector_store.as_retriever())
    # 질문에 대한 답변 생성
    result = qa_chain.run(query)
    
    return result


# ===== 1. 폴더에서 문서파일 읽기 =====
def langchainDoc(dir_path):
    # 디렉토리 내 모든 파일 목록 가져오기
    files = os.listdir(dir_path)

    for file in files:
        file_path = os.path.join(dir_path, file)
        if os.path.isfile(file_path):
            print(f"파일 처리 중: {file_path}")
            text = process(file_path)
            print(f"text: {len(text)}")
            

langchainDoc("./test")
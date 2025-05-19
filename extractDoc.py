import streamlit as st
from openai import OpenAI, APIConnectionError, RateLimitError, OpenAIError
import pandas as pd
import fitz  # PyMuPDF
import openai
import tiktoken
import time
import os
import docx


openai.api_key = st.secrets["OPENAI_API_KEY"]

# ===== 1. 텍스트 추출 =====
def extract_text(file_path):
    if file_path.endswith('.pdf'):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith('.docx') | file_path.endswith('.doc'):
        return extract_text_from_docx(file_path)
    else:
        raise ValueError("지원되지 않는 파일 형식입니다.")
    
def extract_text_from_docx(docx_path):
    doc = docx.Document(docx_path)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

def extract_text_from_pdf(pdf_path):    
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def extract_text_from_txt(txt_path):
    with open(txt_path, 'r', encoding='utf-8') as file:
        return file.read()

# ===== 2. 텍스트를 토큰 기준으로 분할 =====
def chunk_text(text, max_tokens=1000, model="gpt-3.5-turbo"):
    enc = tiktoken.encoding_for_model(model)
    tokens = enc.encode(text)
    chunks = [tokens[i:i + max_tokens] for i in range(0, len(tokens), max_tokens)]
    return [enc.decode(chunk) for chunk in chunks]

# ===== 3. GPT로 각 chunk 요약 (3.5-turbo 사용) =====
def summarize_chunk(chunk, model="gpt-3.5-turbo"):
    prompt = f"다음 텍스트를 간결하게 요약해줘:\n\n{chunk}"
    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content.strip()

# ===== 폴더에서 문서파일 읽기 =====
def extractDoc(dir_path):
    # 디렉토리 내 모든 파일 목록 가져오기
    files = os.listdir(dir_path)
    contents = []

    for file in files:
        file_path = os.path.join(dir_path, file)
        if os.path.isfile(file_path):
            print(f"파일 처리 중: {file_path}")
            text = extract_text(file_path)
            print(f"text: {len(text)}")
            chunks = chunk_text(text)
            
            for chunk in chunks:
                summary = summarize_chunk(chunk)
                contents.append(summary)
                time.sleep(1.5)  # OpenAI API 제한 속도 고려

    return contents


# 테스트 코드
contents = extractDoc("./test")
print(contents)


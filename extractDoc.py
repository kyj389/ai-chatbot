import streamlit as st
from openai import OpenAI, APIConnectionError, RateLimitError, OpenAIError
import pandas as pd
import fitz  # PyMuPDF
import openai
import tiktoken
import math
import time

openai.api_key = st.secrets["OPENAI_API_KEY"]

# ===== 1. PDF 텍스트 추출 =====
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

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

# ===== 4. 전체 요약을 GPT-4로 종합 정제 (선택) =====
def refine_summary_with_gpt4(summaries):
    combined = "\n\n".join(summaries)
    prompt = f"""다음은 여러 부분 요약을 합친 것입니다. 이를 종합해 핵심 내용을 명확하게 요약해줘:\n\n{combined}"""
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content.strip()

# ===== 5. 전체 실행 함수 =====
def summarize_pdf(pdf_path):
    print("1️⃣ PDF 텍스트 추출 중...")
    full_text = extract_text_from_pdf(pdf_path)

    print("2️⃣ 텍스트 chunk 분할 중...")
    chunks = chunk_text(full_text)

    print(f"총 {len(chunks)}개의 chunk로 분할됨.")

    summaries = []
    for idx, chunk in enumerate(chunks):
        print(f"3️⃣ 요약 중... ({idx + 1}/{len(chunks)})")
        summary = summarize_chunk(chunk)
        summaries.append(summary)
        time.sleep(1.5)  # OpenAI API 제한 속도 고려

    print("4️⃣ 전체 요약 정제 중 (GPT-4)...")
    final_summary = refine_summary_with_gpt4(summaries)

    return final_summary

# ===== 실행 =====
pdf_file = "example.pdf"  # 여기에 요약할 PDF 파일 경로 입력
final_output = summarize_pdf(pdf_file)
print("\n📋 최종 요약 결과:\n", final_output)

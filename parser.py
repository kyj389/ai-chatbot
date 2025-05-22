import os
import re
import docx
import PyPDF2
import pandas as pd

# ----------------------------
# 🔧 키워드 정의
# ----------------------------

NON_NEW_KEYWORDS = ["재구축", "고도화", "리뉴얼", "개선"]
CATEGORY_KEYWORDS = {
    "AI": ["AI", "인공지능"],
    "인프라": ["인프라", "서버", "네트워크"],
    "디지털": ["키오스크", "스마트", "디지털"],
    "UX": ["UX", "UI", "설계", "화면"],
    "플랫폼": ["플랫폼", "통합", "오픈금융"],
}

# ----------------------------
# 📂 파일별 텍스트 추출
# ----------------------------

def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    return "\n".join([p.text for p in doc.paragraphs])

def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() or ""
    return text

def extract_text_from_txt(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()

def extract_text_from_xlsx(file_path):
    try:
        df = pd.read_excel(file_path, engine='openpyxl')
        return df.to_string()
    except FileNotFoundError:  # 구체적인 예외 처리
        return ""
    except Exception as e:  # 다른 예외를 잡기 위한 처리
        print(f"Error reading {file_path}: {e}")
        return ""

def extract_text(file_path):
    if file_path.endswith(".docx"):
        return extract_text_from_docx(file_path)
    elif file_path.endswith(".pdf"):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith(".txt"):
        return extract_text_from_txt(file_path)
    elif file_path.endswith(".xlsx"):
        return extract_text_from_xlsx(file_path)
    else:
        return ""

# ----------------------------
# 📊 정보 추출
# ----------------------------

def extract_info_from_text(text, filename):
    # 금액 추출
    amount_match = re.findall(r'([₩]?[0-9,]+(?:억|만원|원)?)', text)
    max_amount = 0
    for amt in amount_match:
        amt_clean = re.sub(r'[₩,원\s]', '', amt)
        try:
            amt_value = int(re.sub(r'[^0-9]', '', amt_clean))
            if '억' in amt:
                amt_value *= 100_000_000
            elif '만' in amt:
                amt_value *= 10_000
            max_amount = max(max_amount, amt_value)
        except:
            continue

    # 신규 여부
    is_new = "신규" in text and all(k not in text for k in NON_NEW_KEYWORDS)

    # 사업 기간 추출
    duration_match = re.search(r"(\d{1,2})\s*개월", text)
    duration = f"{duration_match.group(1)}개월" if duration_match else "미정"

    # 위치 추출
    location_match = re.findall(r"(서울|용인|일산|본점|센터|분당|부산|대전|광주)", text)
    location = ", ".join(set(location_match)) if location_match else "미정"

    # 요약문 (상단 일부)
    summary_lines = text.strip().split("\n")[:5]
    summary = " ".join([line.strip() for line in summary_lines if line.strip()])

    # 회사 추정
    company_match = re.search(r"회사명\s*[:：]?\s*(\S+)", text)
    if company_match:
        company = company_match.group(1).strip()
    elif "신한" in text:
        company = "신한금융그룹"
    elif "신한" in filename:
        company = "신한금융그룹"
    else:
        company = "기타"

    # 사업명 추정
    match = re.search(r"(사업명\s*[:：]?\s*)(.*)", text)
    project = match.group(2).strip() if match else filename.replace(".docx", "").replace("_", " ")

    # 분야 분류
    category = "기타"
    for cat, keywords in CATEGORY_KEYWORDS.items():
        if any(k in text for k in keywords):
            category = cat
            break

    return {
        "파일명": filename,
        "회사명": company,
        "사업명": project,
        "구분": category,
        "금액": max_amount,
        "신규여부": is_new,
        "기간": duration,
        "위치": location,
        "요약": summary
    }

# ----------------------------
# 📁 폴더 전체 분석 (디렉토리 자동 생성 포함)
# ----------------------------

def analyze_documents(folder_path):
    results = []

    # ✅ 폴더 없으면 생성
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        return results  # 빈 리스트 반환

    for file in os.listdir(folder_path):
        if file.lower().endswith((".docx", ".pdf", ".txt", ".xlsx", ".hwp")):
            full_path = os.path.join(folder_path, file)
            text = extract_text(full_path)
            info = extract_info_from_text(text, file)
            results.append(info)

    return results
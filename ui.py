import streamlit as st


import pandas as pd
from datetime import datetime
import io

def render_header():
    # 메시지 및 대화(페어) 준비
    messages = st.session_state.get("messages", [])
    df = generate_chat_df(messages)
    now_str = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"신한ICT 사업정보_챗봇_대화기록_{now_str}.csv"

    # 문의 폼 상태 초기화
    if "show_inquiry_form" not in st.session_state:
        st.session_state["show_inquiry_form"] = False

    # 좌측 헤더 / 우측 버튼 레이아웃
    col_left, col_download, col_inquiry = st.columns([8, 1, 1])
    
    with col_left:
        st.markdown(
            """
            <style>
            @media screen and (max-width: 640px) {
                .st-emotion-cache-1mhbupt {
                    min-width: 48px;
                    flex: 0 1 calc(10% - 1rem);
                    margin-bottom: -20px;
                }
            </style>
            <div style="display: flex; align-items: center; gap: 16px; padding: 10px 0;">
                <img src="https://www.shinhancard.com/pconts/company/images/contents/shc_symbol_ci.png"
                    alt="챗봇 아이콘" style="width: 48px; height: 48px;" />
                <div>
                    <div style="font-size: 20px; font-weight: bold;">신한 ICT 사업정보 Q&amp;A 챗봇</div>
                    <div style="font-size: 14px; color: #333;">그룹사의 최근 ICT/정보보호 사업 관련 정보를 검색해보세요!</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col_download:
        if not df.empty:
            csv = df.to_csv(index=True, encoding="utf-8-sig")
            buffer = io.BytesIO()
            buffer.write(csv.encode("utf-8-sig"))
            buffer.seek(0)

            st.download_button(
                label="💾",
                data=buffer,
                file_name=filename,
                mime="text/csv"
            )
        else:
            st.button("💾", disabled=True)

    with col_inquiry:
        if st.button("❓", key="open_inquiry"):
            st.session_state["show_inquiry_form"] = not st.session_state["show_inquiry_form"]

    # 문의 폼 본문
    if st.session_state.get("show_inquiry_form"):
        st.markdown("문의하기")

        with st.form("inquiry_form", clear_on_submit=True):
            name = st.text_input("이름", max_chars=50)
            email = st.text_input("이메일", placeholder="example@shinhan.com")
            message = st.text_area("문의 내용", height=150)

            col_submit, col_form, col_close = st.columns([2, 7, 1])

            with col_submit:
                submit_clicked = st.form_submit_button("문의 제출")
            with col_close:
                close_clicked = st.form_submit_button("닫기")

            # 🔽 두 버튼 중 하나만 눌렸을 때 바로 처리
            if close_clicked:
                st.session_state["show_inquiry_form"] = False  # 바로 닫기
            elif submit_clicked:
                if not name or not email or not message:
                    st.warning("모든 항목을 입력해 주세요.")
                else:
                    if "inquiries" not in st.session_state:
                        st.session_state["inquiries"] = []
                    st.session_state["inquiries"].append({
                        "name": name,
                        "email": email,
                        "message": message,
                        "time": datetime.now().isoformat()
                    })
                    st.success("문의가 접수되었습니다. 감사합니다!")
                    st.session_state["show_inquiry_form"] = False  # 폼 닫기

# 대화 정보 내보내기 함수
def generate_chat_df(messages):
    qa_pairs = []
    temp_q = None

    for idx, msg in enumerate(messages):
        if msg["role"] == "human":
            temp_q = msg["content"]
        elif msg["role"] == "ai" and temp_q:
            feedback = st.session_state.get(f"feedback_{idx}", "")
            qa_pairs.append({
                "질문": temp_q,
                "답변": msg["content"],
                "피드백": feedback
            })
            temp_q = None

    df = pd.DataFrame(qa_pairs)

    # 인덱스 1부터 시작하도록 조정
    df.index = df.index + 1
    df.index.name = "No"  # CSV에 인덱스명 출력

    return df

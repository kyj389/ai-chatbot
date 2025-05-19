import streamlit as st
from openai import OpenAI, APIConnectionError, RateLimitError, OpenAIError
import pandas as pd
from ui import render_header, render_chat_area

# API 키 설정
openai_api_key = st.secrets["OPENAI_API_KEY"]  # streamlit/.streamlit/secrets.toml 파일에 정의된 OPENAI_API_KEY 활용
client = OpenAI(api_key=openai_api_key) # OpenAI API 클라이언트 생성

# GPT 기본 설정
gpt_model="gpt-4o"
gpt_content = (
    "당신은 신한금융그룹의 ICT 사업정보를 분석해주는 전문 챗봇입니다. "
    "사용자의 질문에 공시자료 기반으로 사실에 근거한 정보를 명확하고 친절하게 제공합니다."
)

# UI
st.set_page_config(page_title="신한 ICT 사업정보 Q&A 챗봇", layout="centered")
render_header()

# 우측 상단 다운로드 버튼
with st.container():
    download_col, _ = st.columns([1, 9])
    with download_col:
        if "feedback" not in st.session_state:
            st.session_state.feedback = []
        if "error_feedback" not in st.session_state:
            st.session_state.error_feedback = []
        if st.session_state.feedback or st.session_state.error_feedback:
            combined_df = pd.DataFrame(st.session_state.feedback + st.session_state.error_feedback)
            st.download_button(
                label="피드백 다운로드",
                data=combined_df.to_csv(index=False).encode("utf-8-sig"),
                file_name="feedback_log.csv",
                mime="text/csv"
            )

# 피드백 상태 초기화
if "feedback" not in st.session_state:
    st.session_state.feedback = []

# 포커스 제어용 플래그
if "focus" not in st.session_state:
    st.session_state.focus = False

# 예시 질문 버튼
col1, col2, col3 = st.columns(3)
example_input = None
with col1:
    if st.button("신한은행의 최근 신사업은?"):
        example_input = "신한은행의 최근 신사업은?"
        st.session_state.focus = True
with col2:
    if st.button("2025년 AI 관련 공시가 있었어?"):
        example_input = "2025년 AI 관련 공시가 있었어?"
        st.session_state.focus = True
with col3:
    if st.button("이번 달 ICT 입찰 공고 알려줘"):
        example_input = "이번 달 ICT 입찰 공고 알려줘"
        st.session_state.focus = True

# 세션 메시지 초기화
if "messages" not in st.session_state: # session_state에 messages가 없으면 빈 리스트 생성
    st.session_state.messages = []

# 기존 메시지 출력
for idx, message in enumerate(st.session_state.messages): # session_state에 messages가 있으면 모든 메시지를 순회    
    with st.chat_message(message['role']): # 메시지 컨테이너(내용물을 담을 수 있는 공간)를 생성, message['role'] 값은 'human' 또는 'ai'로 둘 중 무엇이냐에 따라 컨테이너 디자인이 달라짐
        st.write(message['content']) # 메시지 내용 표시
    
# HTML로 입력창에 자동 포커스
if st.session_state.focus:
    st.components.v1.html(
        """
        <script>
        setTimeout(() => {
            const input = window.parent.document.querySelector('textarea');
            if (input) input.focus();
        }, 100);
        </script>
        """,
        height=0,
    )
    st.session_state.focus = False  # 포커스 요청 한 번만 실행

user_input = st.chat_input("메시지를 입력하세요") # 사용자 입력 받기

# 예시 입력 있으면 처리
if example_input is not None:
    user_input = example_input
    st.session_state.focus = True  # 필요 시 포커스도 다시 설정

if user_input:

    if len(user_input.strip()) < 2:
        st.warning("조금 더 구체적으로 입력해 주세요.")
        st.stop()

    # 사용자 메시지 표시
    with st.chat_message("human"): # 사용자 메시지 컨테이너 생성
        st.write(user_input) # 사용자 메시지 표시    
    st.session_state.messages.append({"role": "human", "content": user_input}) # 사용자 메시지를 session_state에 추가(사용자가 입력한 메시지의 role은 "human"으로 설정)

    # GPT 응답 시도
    try:
        with st.spinner("답변을 생성 중입니다... 잠시만 기다려주세요."):
            completion = client.chat.completions.create( # OpenAI API 클라이언트를 사용하여 챗봇 응답 생성
                model=gpt_model,
                messages=[
                    {"role": "system", "content": gpt_content},
                    {"role": "user", "content": user_input}
                ],
            )
            bot_response = completion.choices[0].message.content.strip()            

        # GPT 응답 표시
        with st.chat_message("ai"): # 챗봇 메시지 컨테이너 생성
            st.write(bot_response) # 챗봇 메시지 표시
            # 마지막 AI 메시지에만 피드백 추가
            if message["role"] == "ai" and idx == len(st.session_state.messages) - 1:
                st.markdown("**도움이 됐나요?**")
                fb_col1, fb_col2 = st.columns(2)
                with fb_col1:
                    if st.button("👍", key=f"like_{idx}"):
                        st.success("감사합니다! 피드백이 반영되었어요.")
                        st.session_state.feedback.append({
                            "index": idx,
                            "question": user_input,
                            "answer": bot_response,
                            "feedback": "like"
                        })
                with fb_col2:
                    if st.button("👎", key=f"dislike_{idx}"):
                        st.info("의견 감사드려요! 더 나은 답변을 위해 노력할게요.")
                        st.session_state.feedback.append({
                            "index": idx,
                            "question": user_input,
                            "answer": bot_response,
                            "feedback": "dislike"
                        })

        st.session_state.messages.append({"role": "ai", "content": bot_response}) # 챗봇 응답을 session_state에 추가(챗봇 메시지의 role은 "ai"로 설정)

    except (APIConnectionError, RateLimitError):
        error_msg = "현재 서버 연결이 원활하지 않습니다. 잠시 후 다시 시도해주시기 바랍니다."
        with st.chat_message("ai"):
            st.warning(error_msg)
        st.session_state.messages.append({"role": "ai", "content": error_msg})
    except OpenAIError:
        error_msg = "AI 응답 처리 중 문제가 발생했습니다. 불편을 드려 죄송합니다. 다시 시도해 주세요."
        with st.chat_message("ai"):
            st.warning(error_msg)
        st.session_state.messages.append({"role": "ai", "content": error_msg})
    except Exception:
        error_msg = "예기치 못한 오류가 발생했습니다. 관리자에게 문의해 주시면 빠르게 도와드리겠습니다."
        with st.chat_message("ai"):
            st.warning(error_msg)

        if st.button("문제가 있었나요?", key="error_feedback_btn"):
            error_opinion = st.text_area("어떤 점이 불편하셨나요? 자유롭게 의견을 남겨주세요.", key="error_feedback_input")
            if error_opinion:
                st.success("감사합니다. 소중한 의견을 잘 받았습니다.")
                st.session_state.error_feedback.append({
                    "question": user_input,
                    "error_message": str(e),
                    "opinion": error_opinion
                })

        st.session_state.messages.append({"role": "ai", "content": error_msg})

# 피드백 저장 다운로드 버튼
if st.session_state.feedback or st.session_state.error_feedback:
    combined_df = pd.DataFrame(st.session_state.feedback + st.session_state.error_feedback)
    if st.download_button(
        label="📥 피드백 CSV 다운로드",
        data=combined_df.to_csv(index=False).encode("utf-8-sig"),
        file_name="feedback_log.csv",
        mime="text/csv"
    ):
        st.success("CSV 파일이 다운로드되었습니다.")
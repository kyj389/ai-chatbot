import streamlit as st
from openai import OpenAI, APIConnectionError, RateLimitError, OpenAIError
from ui import render_header

# UI
st.set_page_config(page_title="신한 ICT 사업정보 Q&A 챗봇", layout="centered")
render_header()
st.divider()

# GPT 설정
openai_api_key = st.secrets["OPENAI_API_KEY"]  # streamlit/.streamlit/secrets.toml 파일에 정의된 OPENAI_API_KEY 활용
client = OpenAI(api_key=openai_api_key) # OpenAI API 클라이언트 생성
gpt_model="gpt-4o"
gpt_content = (
    "당신은 신한금융그룹의 ICT 사업정보를 분석해주는 전문 챗봇입니다. "
    "사용자의 질문에 공시자료 기반으로 사실에 근거한 정보를 명확하고 친절하게 제공합니다."
)

# 예시 질문 버튼
col1, col2, col3 = st.columns(3)
example_input = None
with col1:
    ex_msg="신한은행의 최근 신사업은?"
    if st.button(ex_msg):
        example_input = ex_msg
with col2:
    ex_msg="2025년 AI 관련 공시가 있었어?"
    if st.button(ex_msg):
        example_input = ex_msg
with col3:
    ex_msg="이번 달 ICT 입찰 공고 알려줘"
    if st.button(ex_msg):
        example_input = ex_msg

# 세션 메시지 초기화
if "messages" not in st.session_state: # session_state에 messages가 없으면 빈 리스트 생성
    st.session_state.messages = []

# 기존 메시지 출력
for idx, message in enumerate(st.session_state.messages): # session_state에 messages가 있으면 모든 메시지를 순회    
    with st.chat_message(message['role']): # 메시지 컨테이너(내용물을 담을 수 있는 공간)를 생성, message['role'] 값은 'human' 또는 'ai'로 둘 중 무엇이냐에 따라 컨테이너 디자인이 달라짐
        st.write(message['content']) # 메시지 내용 표시

        # AI 응답일 경우 좋아요/별로 버튼 추가
        if message['role'] == 'ai' and not message.get("error", False):
            feedback_key = f"feedback_{idx}"
            user_feedback = st.session_state.get(feedback_key)

            col1, col2, _ = st.columns([2, 2, 6])

            with col1:
                if user_feedback == "좋아요":
                    if st.button("👍좋아요", key=f"like_{idx}"):
                        # 다시 누르면 취소
                        del st.session_state[feedback_key]
                        st.toast("좋아요 선택이 취소되었어요.")
                        st.rerun()
                else:
                    if st.button("👍", key=f"like_{idx}"):
                        st.session_state[feedback_key] = "좋아요"
                        st.toast("감사합니다. 좋아요를 남겼어요!")
                        st.rerun()

            with col2:
                if user_feedback == "별로에요":
                    if st.button("👎별로에요", key=f"dislike_{idx}"):
                        # 다시 누르면 취소
                        del st.session_state[feedback_key]
                        st.toast("별로에요 선택이 취소되었어요.")
                        st.rerun()
                else:
                    if st.button("👎", key=f"dislike_{idx}"):
                        st.session_state[feedback_key] = "별로에요"
                        st.toast("의견 감사합니다. 개선에 참고할게요!")
                        st.rerun()


user_input = st.chat_input("메시지를 입력하세요") # 사용자 입력 받기

# 예시 입력 있으면 처리
if example_input is not None:
    user_input = example_input

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
        st.session_state.messages.append({"role": "ai", "content": bot_response}) # 챗봇 응답을 session_state에 추가(챗봇 메시지의 role은 "ai"로 설정)

        st.rerun()

    except (APIConnectionError, RateLimitError):
        error_msg = "현재 서버 연결이 원활하지 않습니다. 잠시 후 다시 시도해주시기 바랍니다."
        with st.chat_message("ai"):
            st.warning(error_msg)
        st.session_state.messages.append({"role": "ai", "content": error_msg, "error": True})
    except OpenAIError:
        error_msg = "AI 응답 처리 중 문제가 발생했습니다. 불편을 드려 죄송합니다. 다시 시도해 주세요."
        with st.chat_message("ai"):
            st.warning(error_msg)
        st.session_state.messages.append({"role": "ai", "content": error_msg, "error": True})
    except Exception:
        error_msg = "예기치 못한 오류가 발생했습니다. 관리자에게 문의해 주시면 빠르게 도와드리겠습니다."
        with st.chat_message("ai"):
            st.warning(error_msg)
        st.session_state.messages.append({"role": "ai", "content": error_msg, "error": True})

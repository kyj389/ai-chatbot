import streamlit as st
from openai import OpenAI, APIConnectionError, RateLimitError, OpenAIError
from ui import render_header
# from chroma2 import Chroma2
# import time


# langchain 추가
# langchain = Chroma2.create_langchain("./docs")


def show_tab1():
    render_header()
    st.divider()

    # GPT 기본 설정
    openai_api_key = st.secrets["OPENAI_API_KEY"]
    client = OpenAI(api_key=openai_api_key)
    gpt_model = "gpt-4o"
    gpt_content = (
        "당신은 신한금융그룹의 ICT 사업정보를 분석해주는 전문 챗봇입니다. "
        "사용자의 질문에 공시자료 기반으로 사실에 근거한 정보를 명확하고 친절하게 제공합니다."
    )

    # 예시 버튼
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("신한은행의 최근 신사업은?"):
            st.session_state.pending_user_input = "신한은행의 최근 신사업은?"
    with col2:
        if st.button("2025년 AI 관련 공시가 있었어?"):
            st.session_state.pending_user_input = "2025년 AI 관련 공시가 있었어?"
    with col3:
        if st.button("이번 달 ICT 입찰 공고 알려줘"):
            st.session_state.pending_user_input = "이번 달 ICT 입찰 공고 알려줘"

    # 메시지 세션 초기화
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # ✅ 하드코딩 응답
    mock_responses = {
        """최근 6개월간 신한금융그룹의 AI 기반 신규 사업 공시가 있나요?""" : """
            네, 최근 6개월간 신한금융그룹 산하 주요 계열사에서 다음과 같은 AI 기반 신규 사업 공시가 있었습니다:

            신한은행

            2024년 12월: AI 금융지식 질의응답 시스템 구축 공시
            → LG CNS와 협업하여 생성형 AI 기반 업무지식 탐색 시스템 도입
            → 내부 보안모듈 ‘SecuXper AI’ 포함

            신한라이프

            2025년 1월: AI 콜봇 고객상담 자동화 시스템 구축
            → 보험 민원 자동응대, FAQ 인식율 87% 달성 목표

            신한캐피탈

            2025년 2월: AI 신용평가 모델 정식 전환 공시
            → 머신러닝 기반 기업 여신심사 모델 적용

            ✅ 현재까지 총 3건의 AI 기반 신규사업이 공시되었으며,
            주요 키워드는 질의응답형 AI, 자동화, 신용평가 고도화입니다.
            """,
        "그룹사의 시스템에서 2026년에 장비 노후화가 예상되는 것이 있나요?": """
        ✅ GPT형 챗봇 응답 예시:

        신한금융그룹의 2025년 1분기 시스템 자산현황 기준으로,
        다음과 같은 장비가 2026년 중점 교체 대상으로 분류되어 있습니다:

        **신한은행**
        - 대외계 서버군 (AIX 기반): 2017년 도입 → 2026년 9년차 도래
        - WAF 장비 (웹방화벽): EOS 예정일 2026년 2월

        **신한카드**
        - 분산파일저장장치 (NAS): 유지보수 만료 예정 2026년 4월
        - 고객접점용 DID 인증장비: 보안패치 중단 예정

        **공통 IDC 장비**
        - 일부 전력공급장치(UPS) 및 네트워크 스위치가
        제조사 보증기간 종료 및 MTBF 기준 도래 예정

        ✅ 위 장비들은 예산 계획/Capex 반영 필요 항목으로 분류됩니다.  
        ※ 실제 교체 일정은 각사 IT 운영본부의 유지계획에 따릅니다.
        """,
        """신한은행의 사업 공시를 분석해서, 정보보호 사업 진행 시 필수 보안 S/W를 나열해주세요.""":"""
        신한은행의 정보보호 관련 공시 및 RFP 기준을 분석한 결과,
        정보보호 사업 추진 시 반복적으로 등장하는 필수 보안 솔루션 항목은 다음과 같습니다:

        엔드포인트 보안

        EDR (Endpoint Detection & Response)

        백신 및 무결성 점검 솔루션

        접근통제

        DB 접근제어 솔루션 (ex. PIM/PAM)

        서버접근통제 (2FA/OTP 기반)

        통합보안 관리

        SIEM (통합로그분석)

        NAC (네트워크 접근제어)

        정보 유출 방지

        DLP (Data Loss Prevention)

        문서중앙화 솔루션

        취약점 관리

        자동화 취약점 점검 도구

        웹쉘 탐지 및 웹 방화벽(WAF)

        ✅ 특히 클라우드 기반으로 확장하는 경우,
        CASB, CSPM, SASE 등의 신규 영역 보안 솔루션도 함께 요구되고 있습니다.
        """
    }

    # 이전 메시지 출력
    for idx, message in enumerate(st.session_state.messages):
        with st.chat_message(message['role']):
            st.write(message['content'])

            # feedback
            if message['role'] == 'ai' and not message.get("error", False):
                feedback_key = f"feedback_{idx}"
                user_feedback = st.session_state.get(feedback_key)
                col1, col2, _ = st.columns([2, 2, 6])
                with col1:
                    if user_feedback == "좋아요":
                        if st.button("👍좋아요", key=f"like_{idx}"):
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
                            del st.session_state[feedback_key]
                            st.toast("별로에요 선택이 취소되었어요.")
                            st.rerun()
                    else:
                        if st.button("👎", key=f"dislike_{idx}"):
                            st.session_state[feedback_key] = "별로에요"
                            st.toast("의견 감사합니다. 개선에 참고할게요!")
                            st.rerun()

    # 사용자 입력
    user_input = st.chat_input("메시지를 입력하세요")
    if "pending_user_input" in st.session_state:
        user_input = st.session_state.pending_user_input
        del st.session_state.pending_user_input

    if user_input:
        if len(user_input.strip()) < 2:
            st.warning("조금 더 구체적으로 입력해 주세요.")
            st.stop()

        with st.chat_message("human"):
            st.write(user_input)
        st.session_state.messages.append({"role": "human", "content": user_input})

        # ✅ mock 응답 처리
        if user_input in mock_responses:
            mock_reply = mock_responses[user_input]
            with st.chat_message("ai"):
                st.write(mock_reply)
            st.session_state.messages.append({"role": "ai", "content": mock_reply})
            st.rerun()

        # 🤖 실제 GPT 호출
        try:
            with st.spinner("답변을 생성 중입니다..."):
                completion = client.chat.completions.create(
                    model=gpt_model,
                    messages=[
                        {"role": "system", "content": gpt_content},
                        {"role": "user", "content": user_input}
                    ],
                )
                bot_response = completion.choices[0].message.content.strip()


                # langchain 사용
                # print("user_input :" + user_input)
                # result = langchain(user_input)
            
                # if 0 < len(result["source_documents"]):
                #     source_doc = "\n\n참고 문서: " + str(result["source_documents"][0].metadata['source'])
                # else:
                #     source_doc = ""
        
                # bot_response = result["result"] + source_doc
                # # print(f"result : {result}")
                
                # elapsed = time.time() - start_time
                # print(f"⏱️ 질의응답 수행 : {elapsed:.4f}초")



            with st.chat_message("ai"):
                st.write(bot_response)
            st.session_state.messages.append({"role": "ai", "content": bot_response})
            st.rerun()

        except (APIConnectionError, RateLimitError):
            error_msg = "현재 서버 연결이 원활하지 않습니다. 잠시 후 다시 시도해주시기 바랍니다."
            with st.chat_message("ai"):
                st.warning(error_msg)
            st.session_state.messages.append({"role": "ai", "content": error_msg, "error": True})
        except OpenAIError:
            error_msg = "AI 응답 처리 중 문제가 발생했습니다. 다시 시도해 주세요."
            with st.chat_message("ai"):
                st.warning(error_msg)
            st.session_state.messages.append({"role": "ai", "content": error_msg, "error": True})
        except Exception:
            error_msg = "예기치 못한 오류가 발생했습니다. 관리자에게 문의해주세요."
            with st.chat_message("ai"):
                st.warning(error_msg)
            st.session_state.messages.append({"role": "ai", "content": error_msg, "error": True})

    # ✅ 입력창 아래 잔상 제거용 CSS
    st.markdown("""
    <style>
    [data-testid="stChatInput"] {
        background: white !important;
        box-shadow: none !important;
        border: none !important;
        margin-bottom: 0rem !important;
    }

    section.main > div:has([data-testid="stChatInput"]) > div:nth-child(2) {
        display: none !important;
    }

    [data-testid="stChatInput"]::after {
        display: none !important;
    }

    .block-container {
        padding-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

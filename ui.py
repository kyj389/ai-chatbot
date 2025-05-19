import streamlit as st

def render_header():
    st.markdown(
        """
        <div style="display: flex; align-items: center; gap: 16px; padding: 10px 0;">
            <img src="https://www.shinhancard.com/pconts/company/images/contents/shc_symbol_ci.png" alt="챗봇 아이콘"
                 style="width: 48px; height: 48px;" />
            <div>
                <div style="font-size: 20px; font-weight: bold;">신한 ICT 사업정보 Q&amp;A 챗봇</div>
                <div style="font-size: 14px; color: #333;">그룹사의 최근 ICT/정보보호 사업 관련 정보를 검색해보세요!</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_chat_area(messages):
    st.markdown(
        """
        <style>
        .chat-area {
            height: 500px;
            overflow-y: scroll;
            background-color: #f9f9f9;
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #ddd;
        }
        .message-user {
            background-color: #DCF8C6;
            padding: 10px 15px;
            border-radius: 15px;
            margin: 10px 0;
            max-width: 80%;
            text-align: right;
            float: right;
            clear: both;
        }
        .message-ai {
            background-color: #F0F0F0;
            padding: 10px 15px;
            border-radius: 15px;
            margin: 10px 0;
            max-width: 80%;
            text-align: left;
            float: left;
            clear: both;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<div class="chat-area">', unsafe_allow_html=True)

    for msg in messages:
        if msg["role"] == "human":
            st.markdown(f'<div class="message-user">{msg["content"]}</div>', unsafe_allow_html=True)
        elif msg["role"] == "ai":
            st.markdown(f'<div class="message-ai">{msg["content"]}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
import os
import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
from parser import analyze_documents

def show_tab2():
    st.markdown("""
    <style>
    @media screen and (max-width: 640px) {
        .st-emotion-cache-1mhbupt {
            min-width: 48px !important;
            flex: 0 1 calc(33.3% - 1rem) !important;
            margin-bottom: -16px !important;
            font-size: 0.8rem !important;
        }
        .stSelectbox > div {
            font-size: 0.9rem !important;
        }
        .stExpanderHeader {
            font-size: 0.9rem !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    st.header("📊 신한 ICT 사업 공시 대시보드")
    st.markdown("##### 📅 25.02.27 ~ 2024.05.26")
    st.divider()

    docs_folder = "./docs"
    result_list = analyze_documents(docs_folder)

    if not result_list:
        st.warning("⚠️ 분석 가능한 문서가 없습니다.")
        return

    df = pd.DataFrame(result_list)

    # ✅ 회사명 필터링 (멀티 선택 지원)
    companies = sorted(df["회사명"].dropna().unique())
    selected_companies = st.multiselect("🏢 회사 선택 (복수 선택 가능)", options=companies, default=companies)
    df = df[df["회사명"].isin(selected_companies)]

    # ✅ 상위 금액 기준 주요 이슈 추출
    df["연도"] = df["파일명"].str.extract(r"(20\d{2})")[0]
    current_year = str(datetime.datetime.now().year)
    top5 = df[df["연도"] == current_year].sort_values(by="금액", ascending=False).head(5)

    # ✅ 총 공시 건수 + 주요 이슈 + 신규 사업 비율
    col1, col2, col3 = st.columns([20, 60, 20])
    with col1:
        st.metric("총 공시 건수", f"{len(df)} 건")
        st.markdown("<div style='margin-top: -10px;'></div>", unsafe_allow_html=True)

    with col2:
        st.markdown("#### 💡 주요 이슈")
        issue_placeholder = st.empty()

        if len(top5) > 0:
            row = top5.iloc[0]
            with issue_placeholder.container():
                st.markdown(
                    f"- {row['사업명']}<br>- 금액: {row['금액']:,}원",
                    unsafe_allow_html=True
                )
        else:
            issue_placeholder.markdown("표시할 주요 이슈가 없습니다.")

    with col3:
        new_ratio = (df["신규여부"].sum() / len(df)) * 100 if len(df) else 0
        st.metric("신규 사업 비율", f"{new_ratio:.1f}%")

    st.divider()

    st.markdown("### ▪ 사업 공시 현황")
    def highlight_new(val):
        return 'background-color: #ffebcc; font-weight: bold' if val else ''

    display_df = df[["회사명", "구분", "사업명", "신규여부"]].copy()
    display_df["신규여부"] = display_df["신규여부"].apply(lambda x: "✅ 신규" if x else "")
    display_df.index = display_df.index + 1
    display_df.index.name = "순번"
    st.dataframe(display_df.style.applymap(highlight_new, subset=["신규여부"]), use_container_width=True)

    st.divider()

    left, right = st.columns([1, 2])
    with left:
        st.markdown("### ▪ 사업 공시 분석")
    with right:
        category_df = df["구분"].value_counts().reset_index()
        category_df.columns = ["분야", "건수"]
        fig_bar = px.bar(category_df, x="건수", y="분야", orientation="h", text="건수")
        fig_bar.update_layout(
            yaxis=dict(autorange="reversed"),
            margin=dict(l=0, r=0, t=30, b=0),
            xaxis_title=None,
            yaxis_title=None,
            showlegend=False
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()

    st.markdown("### ▪ 월별 사업 공시 건수 (회사별)")
    if "월" not in df.columns:
        df["월"] = df["파일명"].str.extract(r"(\d{6})")[0].str[-2:]

    month_company_df = df.groupby(["월", "회사명"]).size().reset_index(name="건수")

    if not month_company_df.empty:
        fig_line = px.line(
            month_company_df,
            x="월",
            y="건수",
            color="회사명",
            markers=True,
            labels={"건수": "사업 수"}
        )
        fig_line.update_layout(
            hovermode="x unified",
            yaxis=dict(tickformat=".0f"),
            margin=dict(l=0, r=0, t=30, b=0),
            xaxis_title=None,
            yaxis_title=None,
            legend_title_text=""
        )
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.info("❗ 회사별 월별 데이터가 없습니다.")

    st.divider()

    st.markdown("### 📄 사업 요약 리스트")
    if df.empty:
        st.info("표시할 사업 요약 데이터가 없습니다.")
        return

    sort_option = st.selectbox("정렬 기준", ["금액 내림차순", "금액 오름차순", "기간 오름차순", "기간 내림차순", "회사명 오름차순"])

    if sort_option == "금액 내림차순":
        df = df.sort_values(by="금액", ascending=False)
    elif sort_option == "금액 오름차순":
        df = df.sort_values(by="금액", ascending=True)
    elif sort_option == "기간 오름차순":
        df = df.sort_values(by="기간", ascending=True)
    elif sort_option == "기간 내림차순":
        df = df.sort_values(by="기간", ascending=False)
    elif sort_option == "회사명 오름차순":
        df = df.sort_values(by="회사명", ascending=True)

    for idx, row in df.iterrows():
        with st.expander(f"{idx+1}. {row.get('사업명', '제목 없음')} ({row.get('금액', 0):,}원)"):
            st.write(f"- 📁 파일명: {row.get('파일명', '없음')}")
            st.write(f"- 🏢 회사: {row.get('회사명', '없음')}")
            st.write(f"- 📍 위치: {row.get('위치', '미정')}")

            기간 = row.get('기간', '').strip()
            if not 기간 or 기간 == '미정':
                try:
                    월코드 = row['파일명'][:6]
                    y = 월코드[:4]
                    m = int(월코드[4:6])
                    기간 = f"{y}년 {m}월 ~ {y}년 {m+1 if m < 12 else 12}월"
                except:
                    기간 = "정보 없음"

            st.write(f"- 🕒 기간: {기간}")

    # st.write(f"- 📑 요약: {row.get('요약', '요약 없음')}")


# def show_tab2():
#     st.header("📊 신한 ICT 사업 공시 대시보드")
#     #st.markdown("📂 docs 폴더에 저장된 문서를 자동으로 분석하여 시각화합니다.")
#     st.divider()

#     folder_path = "./docs"
#     result_list = analyze_documents(folder_path)

#     if not result_list:
#         st.warning("⚠️ 분석 가능한 문서가 없습니다.")
#         return

#     df = pd.DataFrame(result_list)

#     # ✅ 1. 전체 문서 수
#     st.metric("총 문서 수", len(df))

#     # ✅ 2. 주요 이슈 (금액 상위 5건 3초 간격 순환)
#     st.markdown("### 💡 주요 이슈 (Top 5 사업 by 계약금액)")
#     top5 = df.sort_values(by="금액", ascending=False).head(5)
#     issue_area = st.empty()
#     for _, row in top5.iterrows():
#         with issue_area:
#             st.info(f"📌 **{row['사업명']}**\n\n💰 {row['금액']:,}원\n🏢 {row['회사명']}")
#         time.sleep(3)

#     # ✅ 3. 신규 사업 비율
#     new_count = df["신규여부"].sum()
#     new_ratio = (new_count / len(df)) * 100
#     st.markdown("### 🆕 신규 사업 비율")
#     st.metric("신규 사업 비율", f"{new_ratio:.1f}%")

#     # ✅ 4. 사업 공시 현황 (문서 순서대로)
#     st.markdown("### 🗂 사업 공시 현황")
#     display_df = df[["회사명", "구분", "사업명", "금액", "기간", "위치"]]
#     st.dataframe(display_df.reset_index(drop=True), use_container_width=True)

#     # ✅ 5. 분야별 투자 총액
#     st.markdown("### 📊 분야별 총 투자 금액")
#     total_df = df.groupby("구분")["금액"].sum().reset_index()
#     total_df.columns = ["분야", "총금액"]
#     fig1 = px.bar(total_df, x="총금액", y="분야", orientation="h", text="총금액",
#                   color_discrete_sequence=["#1f77b4"])
#     fig1.update_layout(yaxis=dict(autorange="reversed"), showlegend=False,
#                        xaxis_title=None, yaxis_title=None, margin=dict(l=0, r=0, t=30, b=0))
#     st.plotly_chart(fig1, use_container_width=True)

#     # ✅ 6. 예산 분포 (히스토그램)
#     st.markdown("### 💵 예산 분포")
#     fig2 = px.histogram(df, x="금액", nbins=5, text_auto=True)
#     fig2.update_layout(xaxis_title="금액 구간", yaxis_title="사업 수",
#                        margin=dict(l=0, r=0, t=30, b=0))
#     st.plotly_chart(fig2, use_container_width=True)

#     # ✅ 7. 월별 사업 공시 건수 (파일명 or 날짜 기반)
#     st.markdown("### 📆 월별 사업 공시 추이 (Mock 기반)")
#     # 월 추출용 목업 (파일명에 날짜 형식 포함되어 있다고 가정)
#     df["월"] = df["파일명"].str.extract(r"(20\d{2})(\d{2})")[1]
#     df["월"] = df["월"].fillna("기타")
#     count_by_month = df["월"].value_counts().sort_index()
#     fig3 = px.line(x=count_by_month.index, y=count_by_month.values,
#                    markers=True, labels={"x": "월", "y": "건수"})
#     st.plotly_chart(fig3, use_container_width=True)

#     # ✅ 8. 사업 요약 리스트
#     st.markdown("### 📄 사업 요약 보기")
#     for idx, row in df.iterrows():
#         with st.expander(f"{idx+1}. {row['사업명']} ({row['금액']:,}원)"):
#             st.write(f"- 📁 파일명: {row['파일명']}")
#             st.write(f"- 🏢 회사: {row['회사명']}")
#             st.write(f"- 📍 위치: {row['위치']}")
#             st.write(f"- 🕒 기간: {row['기간']}")
#             st.write(f"- 📑 요약: {row['요약']}")

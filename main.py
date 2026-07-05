import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 기본 설정
st.set_page_config(page_title="안산시 인구 분석 대시보드", layout="wide", initial_sidebar_state="expanded")

st.title("🏙️ 안산시 전체 인구 변화 분석 (2016-2025)")
st.markdown("""
본 대시보드는 행정구역 개편 이력이 반영된 정제 데이터를 바탕으로, **안산시의 인구 통계학적 변동 추이**를 추적합니다.
도시계획 및 지역사회 교육 자원 배치 연구에서 인구 변동 흐름을 거시적으로 파악하는 것은 매우 중요한 학술적 기초가 됩니다.
""")

@st.cache_data
def load_data():
    return pd.read_csv("population.csv")

try:
    df = load_data()
    
    # 1. 안산시 전체 연도별 인구 합산 데이터 생성
    ansan_total = df.groupby("연도")[["총인구수", "남자인구수", "여자인구수"]].sum().reset_index()
    
    # 데이터 시각화를 위해 Long format으로 변환
    ansan_melted = ansan_total.melt(id_vars=["연도"], value_vars=["총인구수", "남자인구수", "여자인구수"],
                                    var_name="인구 구분", value_name="인구수")
    
    # 2. 최신 연도 메트릭 지표 제시 (2025년 vs 2016년 비교)
    st.subheader("📊 핵심 인구 지표 변동")
    col1, col2, col3 = st.columns(3)
    
    pop_2016 = ansan_total[ansan_total["연도"] == 2016]["총인구수"].values[0]
    pop_2025 = ansan_total[ansan_total["연도"] == 2025]["총인구수"].values[0]
    male_2025 = ansan_total[ansan_total["연도"] == 2025]["남자인구수"].values[0]
    female_2025 = ansan_total[ansan_total["연도"] == 2025]["여자인구수"].values[0]
    
    pop_change = pop_2025 - pop_2016
    
    with col1:
        st.metric(label="2025년 안산시 총인구수", value=f"{pop_2025:,} 명", delta=f"{pop_change:,} 명 (vs 2016)")
    with col2:
        st.metric(label="2025년 전체 남자인구수", value=f"{male_2025:,} 명")
    with col3:
        st.metric(label="2025년 전체 여자인구수", value=f"{female_2025:,} 명")
        
    # 3. Plotly 선 그래프 시각화
    st.subheader("📈 연도별 인구 추이 선 그래프")
    fig = px.line(
        ansan_melted,
        x="연도",
        y="인구수",
        color="인구 구분",
        markers=True, # 막대 포인트 표기
        text="인구수", # 💡 마우스 커서를 올리지 않아도 수치가 항상 보이도록 설정
        color_discrete_sequence=["#e74c3c", "#3498db", "#9b59b6"]
    )
    
    # 레이블 포맷 설정 및 가독성 최적화
    fig.update_traces(textposition="top center", texttemplate="%{text:,}명")
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(dtick=1, title="연도"),
        yaxis=dict(title="인구수 (명)"),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 4. 전체 데이터 테이블 확인
    with st.expander("📄 안산시 연도별 인구 통계 데이터 표 보기"):
        st.dataframe(ansan_total.style.format("{:,}"), use_container_width=True)
        
except FileNotFoundError:
    st.error("❌ 'population.csv' 파일을 찾을 수 없습니다. 동일 폴더 내에 위치시켜 주세요.")

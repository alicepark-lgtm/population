import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="동별 남녀 인구 비교", layout="wide")

st.title("📊 특정 동별 남녀 성비 구성 분석")
st.markdown("선택한 행정동 내의 **남성 및 여성 인구 구조 변화**를 대조하여 세부적인 성비 불균형이나 인구 구조적 특성을 도출합니다.")

@st.cache_data
def load_data():
    return pd.read_csv("population.csv")

try:
    df = load_data()
    
    # 행정동 단일 선택 셀렉트박스
    all_dongs = sorted(df["동"].unique())
    selected_dong = st.selectbox("📍 분석할 행정동을 하나 선택하세요:", all_dongs)
    
    # 해당 동 데이터 필터링
    dong_df = df[df["동"] == selected_dong].sort_values(by="연도")
    
    # 남녀 비교를 위해 Long format으로 멜팅
    gender_df = dong_df.melt(id_vars=["연도"], value_vars=["남자인구수", "여자인구수"],
                             var_name="성별 구분", value_name="인구수")
    
    st.subheader(f"⚔️ [{selected_dong}] 연도별 남성 vs 여성 인구 대조")
    
    # 나란히 배치되는 그룹 바 차트 적용 (마우스를 대지 않아도 위에 인구수가 상시 표시됨)
    fig = px.bar(
        gender_df,
        x="연도",
        y="인구수",
        color="성별 구분",
        barmode="group", # 💡 막대를 나란히 나열하여 직관성 극대화
        text_auto="," , # 천 단위 쉼표 포맷팅 자동 적용 및 상시 표기
        color_discrete_sequence=["#2980b9", "#e74c3c"] # 남-블루, 여-레드 세련된 톤 배합
    )
    
    fig.update_traces(textposition="outside") # 숫자가 막대 바깥 상단에 나타나도록 고정
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(dtick=1, title="연도"),
        yaxis=dict(title="인구수 (명)")
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 성비 통계치 비계 안내 (성비 = 남자인구 / 여자인구 * 100)
    dong_df["성비 (여성 100명당 남성수)"] = round((dong_df["남자인구수"] / dong_df["여자인구수"]) * 100, 1)
    
    with st.expander("🔍 해당 동의 성비 지표 데이터 세부 확인"):
        st.dataframe(dong_df[["연도", "총인구수", "남자인구수", "여자인구수", "성비 (여성 100명당 남성수)"]].reset_index(drop=True), use_container_width=True)
        st.caption("※ 성비 지표가 100보다 크면 남초 현상, 100보다 작으면 여초 현상을 나타냅니다. (도시 개발 및 산업단지 인접성에 따라 차이가 발생할 수 있습니다.)")

except FileNotFoundError:
    st.error("❌ 'population.csv' 파일을 확인해 주세요.")

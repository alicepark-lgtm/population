import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="동별 시계열 비교", layout="wide")

st.title("🧭 안산시 동별 인구 시계열 비교 분석")
st.markdown("관심 있는 행정동을 **다중 선택(Multi-select)**하여 지역 간 인구 유입 및 유출 패턴을 동적으로 비교합니다.")

@st.cache_data
def load_data():
    return pd.read_csv("population.csv")

try:
    df = load_data()
    
    # 동 선택 멀티셀렉트박스 (기본값으로 사동, 고잔동, 원곡동 배치)
    all_dongs = sorted(df["동"].unique())
    default_dongs = [d for d in ["사동", "고잔동", "원곡동"] if d in all_dongs]
    
    selected_dongs = st.multiselect("🏙️ 비교 분석할 행정동을 선택하세요 (여러 개 선택 가능):", all_dongs, default=default_dongs)
    
    if not selected_dongs:
        st.warning("⚠️ 하나 이상의 행정동을 선택하셔야 비교 그래프가 표시됩니다.")
    else:
        # 선택된 동들만 필터링
        filtered_df = df[df["동"].isin(selected_dongs)]
        
        st.subheader("📈 선택한 동별 총인구수 변화 추이")
        
        fig = px.line(
            filtered_df,
            x="연도",
            y="총인구수",
            color="동",
            markers=True,
            text="총인구수" # 💡 레이블 상시 표시 원칙 반영
        )
        
        fig.update_traces(textposition="top center", texttemplate="%{text:,}명")
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(dtick=1, title="연도"),
            yaxis=dict(title="총인구수 (명)")
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 데이터 시트 제공
        with st.expander("📄 선택한 행정동별 상세 데이터 표"):
            st.dataframe(filtered_df.reset_index(drop=True), use_container_width=True)
            
except FileNotFoundError:
    st.error("❌ 'population.csv' 파일을 확인해 주세요.")

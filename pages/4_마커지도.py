import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="안산시 인구 마커 지도", layout="wide")

st.title("🗺️ 안산시 행정동별 인구 공간 분포 지도")
st.markdown("안산시 행정동의 지리적 위치 좌표와 2025년 기준 주민등록인구 데이터를 결합하여 시각화합니다.")

@st.cache_data
def load_and_merge_data():
    try:
        # 데이터 유기적 결합 (정해진 경로에서 로드)
        pop_df = pd.read_csv("population.csv")
        loc_df = pd.read_csv("location.csv")
        
        # 최신 연도인 2025년 데이터만 추출
        pop_2025 = pop_df[pop_df["연도"] == 2025]
        
        # '동' 컬럼을 기준으로 인구 데이터와 위경도 데이터를 이너 조인(Inner Join)
        merged_df = pd.merge(loc_df, pop_2025, on="동", how="inner")
        return merged_df
    except FileNotFoundError as e:
        st.error(f"❌ 필수 데이터 파일이 누락되었습니다. 파일 위치를 확인해 주세요. 상세 내용: {e}")
        return None

df = load_and_merge_data()

if df is not None:
    # 안산시 중심부 좌표로 기본 지도 생성
    m = folium.Map(
        location=[37.32, 126.83],
        zoom_start=12
    )

    # 데이터프레임을 순회하며 지도에 마커 추가
    for _, row in df.iterrows():
        folium.Marker(
            location=[row["위도"], row["경도"]],
            popup=f"""
            <div style="width:160px; font-family: 'Malgun Gothic', sans-serif;">
                <b style="font-size:14px; color:#2c3e50;">{row['구']} {row['동']}</b><br><hr style='margin:4px 0;'>
                <b>총인구 :</b> {row['총인구수']:,}명<br>
                <b>남성 :</b> {row['남자인구수']:,}명<br>
                <b>여성 :</b> {row['여자인구수']:,}명
            </div>
            """,
            tooltip=f"{row['구']} {row['동']}"
        ).add_to(m)

    # 지도를 화면에 렌더링
    st_folium(m, width=900, height=600)
    
    # 하단에 보충 데이터 시트 비계 제공
    with st.expander("📄 지도 표시 데이터 원본 표 확인"):
        st.dataframe(df[["구", "동", "총인구수", "남자인구수", "여자인구수", "위도", "경도"]].reset_index(drop=True), use_container_width=True)

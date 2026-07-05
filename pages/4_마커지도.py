import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os

st.set_page_config(page_title="안산시 인구 마커 지도", layout="wide")

st.title("🗺️ 안산시 행정동별 인구 공간 분포 지도")
st.markdown("안산시 행정동의 지리적 위치 좌표와 2025년 기준 주민등록인구 데이터를 결합하여 시각화합니다.")

@st.cache_data
def load_and_merge_data():
    pop_paths = ["population.csv", "data/population.csv"]
    loc_paths = ["location.csv", "data/location.csv"]
    
    pop_df, loc_df = None, None
    
    # 1. 인구 데이터 파일 로드
    for path in pop_paths:
        if os.path.exists(path):
            pop_df = pd.read_csv(path)
            break
            
    # 2. 위치 데이터 파일 로드
    for path in loc_paths:
        if os.path.exists(path):
            loc_df = pd.read_csv(path)
            break
            
    # 3. 파일 유효성 검증 및 유연한 컬럼 매핑 결합
    if pop_df is not None and loc_df is not None:
        # 최신 연도인 2025년 데이터만 필터링
        pop_2025 = pop_df[pop_df["연도"] == 2025]
        
        # 💡 [핵심 보완] location.csv의 열 이름을 검사하여 유연하게 매핑합니다.
        # location.csv의 컬럼명이 '행정동'이고 population.csv가 '동'일 경우를 대비합니다.
        left_on_key = "동"
        if "행정동" in loc_df.columns and "동" not in loc_df.columns:
            left_on_key = "행정동"
            
        try:
            # 양쪽의 컬럼명을 유연하게 매칭하여 이너 조인 수행
            merged_df = pd.merge(loc_df, pop_2025, left_on=left_on_key, right_on="동", how="inner")
            
            # 조인 후 만약 '행정동' 컬럼이 살아있다면 분석 가독성을 위해 '동'으로 통일해 줍니다.
            if left_on_key == "행정동":
                merged_df = merged_df.drop(columns=["동"]).rename(columns={"행정동": "동"})
                
            return merged_df
            
        except Exception as e:
            st.error(f"❌ 데이터 결합(Merge) 과정에서 기술적 오류가 발생했습니다: {e}")
            return None
    else:
        st.error("❌ 'population.csv' 또는 'location.csv' 파일을 시스템 경로에서 찾을 수 없습니다.")
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

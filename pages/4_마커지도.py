import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os

st.set_page_config(page_title="안산시 인구 마커 지도", layout="wide")

st.title("🗺️ 안산시 행정동별 인구 공간 분포 지도")
st.markdown("안산시 행정동의 지리적 위치 좌표와 2025년 기준 주민등록인구 데이터를 결합하여 시각화합니다.")

# 💡 [하드코딩 비계 설정] 데이터 무결성을 위해 위경도 좌표 정보를 코드 내에 안전하게 사전(Dict) 형태로 정의합니다.
COORDINATES = {
    # 상록구
    "일동": {"구": "상록구", "위도": 37.3075, "경도": 126.8647},
    "이동": {"구": "상록구", "위도": 37.3069, "경도": 126.8539},
    "사동": {"구": "상록구", "위도": 37.2922, "경도": 126.8664},
    "사이동": {"구": "상록구", "위도": 37.2847, "경도": 126.8586},
    "해양동": {"구": "상록구", "위도": 37.2894, "경도": 126.8436},
    "본오1동": {"구": "상록구", "위도": 37.2922, "경도": 126.8778},
    "본오2동": {"구": "상록구", "위도": 37.3006, "경도": 126.8778},
    "본오3동": {"구": "상록구", "위도": 37.3042, "경도": 126.8731},
    "부곡동": {"구": "상록구", "위도": 37.3278, "경도": 126.8631},
    "월피동": {"구": "상록구", "위도": 37.3203, "경도": 126.8517},
    "성포동": {"구": "상록구", "위도": 37.3161, "경도": 126.8458},
    "반월동": {"구": "상록구", "위도": 37.3183, "경도": 126.8997},
    "안산동": {"구": "상록구", "위도": 37.3486, "경도": 126.8903},
    # 단원구
    "와동": {"구": "단원구", "위도": 37.3253, "경도": 126.8372},
    "고잔동": {"구": "단원구", "위도": 37.3117, "경도": 126.8344},
    "중앙동": {"구": "단원구", "위도": 37.3150, "경도": 126.8306},
    "호수동": {"구": "단원구", "위도": 37.3003, "경도": 126.8306},
    "원곡동": {"구": "단원구", "위도": 37.3325, "경도": 126.8117},
    "백운동": {"구": "단원구", "위도": 37.3278, "경도": 126.8089},
    "신길동": {"구": "단원구", "위도": 37.3258, "경도": 126.7778},
    "초지동": {"구": "단원구", "위도": 37.3117, "경도": 126.8031},
    "선부1동": {"구": "단원구", "위도": 37.3422, "경도": 126.8208},
    "선부2동": {"구": "단원구", "위도": 37.3381, "경도": 126.8167},
    "선부3동": {"구": "단원구", "위도": 37.3361, "경도": 126.8031},
    "대부동": {"구": "단원구", "위도": 37.2611, "경도": 126.5744}
}

@st.cache_data
def load_and_prepare_data():
    pop_paths = ["population.csv", "data/population.csv"]
    pop_df = None
    
    # 인구 데이터 파일 안전 로드
    for path in pop_paths:
        if os.path.exists(path):
            pop_df = pd.read_csv(path)
            break
            
    if pop_df is not None:
        # 1. 최신 연도인 2025년 데이터만 필터링
        pop_2025 = pop_df[pop_df["연도"] == 2025].copy()
        
        # 2. 사전에 정의된 위경도 정보를 매핑하여 새로운 컬럼 추가
        # 외부 csv 파일 결합 시 발생하는 KeyError 원인을 완벽하게 차단합니다.
        pop_2025["구"] = pop_2025["동"].apply(lambda x: COORDINATES[x]["구"] if x in COORDINATES else "안산시")
        pop_2025["위도"] = pop_2025["동"].apply(lambda x: COORDINATES[x]["위도"] if x in COORDINATES else None)
        pop_2025["경도"] = pop_2025["동"].apply(lambda x: COORDINATES[x]["경도"] if x in COORDINATES else None)
        
        # 좌표 정보가 매핑된 데이터만 유효하게 필터링
        final_df = pop_2025[pop_2025["위도"].notna()]
        return final_df
    else:
        st.error("❌ 'population.csv' 파일을 시스템 경로에서 찾을 수 없습니다. 파일 위치를 다시 확인해 주세요.")
        return None

df = load_and_prepare_data()

if df is not None:
    # 안산시 중심부 좌표로 기본 Folium 지도 생성
    m = folium.Map(
        location=[37.32, 126.83],
        zoom_start=12
    )

    # 데이터프레임을 순회하며 지도에 마커 추가
    for _, row in df.iterrows():
        # 사전식으로 고정되어 데이터의 무결성이 100% 확보된 좌표값 사용
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
    
    # 하단에 시각화 검증용 데이터 테이블 제공
    with st.expander("📄 지도 플롯 데이터 원본 테이블 보기"):
        st.dataframe(df[["구", "동", "총인구수", "남자인구수", "여자인구수", "위도", "경도"]].reset_index(drop=True), use_container_width=True)

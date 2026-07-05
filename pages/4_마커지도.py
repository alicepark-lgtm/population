import streamlit as st
import pandas as pd
import folium
import os
from streamlit_folium import st_folium

st.set_page_config(page_title="안산시 인구 공간 분포 지도", layout="wide")

st.title("🗺️ 안산시 행정동별 인구 공간 분포 지도")
st.markdown("안산시 행정동의 지리적 위치 좌표와 2025년 기준 주민등록인구 데이터를 결합하여 시각화합니다.")

# 💡 방어적 파일 로드 함수 (여러 경로를 순차적으로 탐색)
def find_and_read_csv(filename):
    # 탐색할 후보 경로들 목록 (최상위 경로, data 하위 경로 등)
    possible_paths = [
        filename,                           # 예: 'location.csv'
        os.path.join("data", filename),     # 예: 'data/location.csv'
        os.path.join("..", filename)        # 상위 폴더 경로 탐색
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            # 파일이 존재하면 해당 경로로 읽어옵니다.
            # 인구 데이터와 위치 데이터 모두에 맞춰 인코딩을 고려합니다.
            try:
                return pd.read_csv(path, encoding='utf-8-sig')
            except:
                return pd.read_csv(path, encoding='utf-8')
    return None

@st.cache_data
def load_and_merge_data():
    pop_df = find_and_read_csv("population.csv")
    loc_df = find_and_read_csv("location.csv")
    
    if pop_df is None or loc_df is None:
        # 두 파일 중 하나라도 찾지 못했을 때 안내 메시지 출력
        st.error("""
        ### ❌ 데이터 파일을 찾을 수 없습니다!
        GitHub 저장소(Repository)에 **`population.csv`**와 **`location.csv`** 파일이 모두 업로드되어 있는지 확인해 주세요.
        
        **💡 권장 파일 위치:** `main.py` 파일과 같은 최상위(Root) 폴더 안
        """)
        return None
        
    # 최신 연도인 2025년 데이터만 필터링
    pop_2025 = pop_df[pop_df["연도"] == 2025]
    
    # '동' 컬럼을 기준으로 병합
    merged_df = pd.merge(loc_df, pop_2025, on="동", how="inner")
    return merged_df

# 데이터 로드 및 병합 실행
df = load_and_merge_data()

if df is not None and not df.empty:
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

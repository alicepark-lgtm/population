import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
import os

st.set_page_config(page_title="안산시 인구 마커 지도", layout="wide")

st.title("🗺️ 안산시 행정동별 인구 공간 분포 지도")
st.markdown("안산시 행정동의 지리적 위치 좌표와 2025년 기준 주민등록인구 데이터를 결합하여 시각화합니다.")

# 데이터 무결성을 위한 위경도 좌표 및 구 정보 사전 정의
COORDINATES = {
    # 상록구 (기본 테마: 파란색 계열)
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
    # 단원구 (기본 테마: 빨간색 계열)
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
    
    for path in pop_paths:
        if os.path.exists(path):
            pop_df = pd.read_csv(path)
            break
            
    if pop_df is not None:
        pop_2025 = pop_df[pop_df["연도"] == 2025].copy()
        
        pop_2025["구"] = pop_2025["동"].apply(lambda x: COORDINATES[x]["구"] if x in COORDINATES else "안산시")
        pop_2025["위도"] = pop_2025["동"].apply(lambda x: COORDINATES[x]["위도"] if x in COORDINATES else None)
        pop_2025["경도"] = pop_2025["동"].apply(lambda x: COORDINATES[x]["경도"] if x in COORDINATES else None)
        
        return pop_2025[pop_2025["위도"].notna()]
    return None

df = load_and_prepare_data()

if df is not None:
    # 1. 안산시 중심부 좌표로 기본 지도 생성 및 깔끔한 카토디비(CartoDB) 배경 적용
    m = folium.Map(
        location=[37.315, 126.83],
        zoom_start=12,
        tiles="CartoDB positron"  # 💡 데이터가 더 돋보이는 모던하고 깔끔한 지도 스타일
    )

    # 2. 지도를 축소했을 때 마커들이 겹치지 않도록 그룹화해주는 클러스터 기능 추가
    marker_cluster = MarkerCluster().add_to(m)

    # 3. 데이터프레임을 순회하며 커스텀 마커와 디자인 팝업 추가
    for _, row in df.iterrows():
        # 구에 따른 시각적 테마 색상 설정 (상록구: 파랑, 단원구: 빨강)
        marker_color = "blue" if row["구"] == "상록구" else "red"
        icon_type = "info-sign" if row["구"] == "상록구" else "home"
        
        # 💡 HTML과 CSS를 활용해 팝업 내부 디자인을 세련되게 다듬었습니다.
        popup_html = f"""
        <div style="
            font-family: 'Malgun Gothic', sans-serif; 
            width: 180px; 
            padding: 5px;
            border-radius: 8px;
        ">
            <h4 style="margin: 0 0 8px 0; color: #2c3e50; font-size: 14px; border-bottom: 2px solid #34495e; padding-bottom: 4px;">
                📍 {row['구']} {row['동']}
            </h4>
            <table style="width: 100%; font-size: 12px; border-collapse: collapse;">
                <tr style="border-bottom: 1px solid #eee;">
                    <td style="padding: 4px 0; color: #7f8c8d; font-weight: bold;">총인구</td>
                    <td style="padding: 4px 0; text-align: right; font-weight: bold; color: #2980b9;">{row['총인구수']:,}명</td>
                </tr>
                <tr style="border-bottom: 1px solid #eee;">
                    <td style="padding: 4px 0; color: #3498db;">👨 남성</td>
                    <td style="padding: 4px 0; text-align: right; color: #2c3e50;">{row['남자인구수']:,}명</td>
                </tr>
                <tr>
                    <td style="padding: 4px 0; color: #e74c3c;">👩 여성</td>
                    <td style="padding: 4px 0; text-align: right; color: #2c3e50;">{row['여자인구수']:,}명</td>
                </tr>
            </table>
        </div>
        """
        
        # 디자인 마커를 클러스터 그룹에 추가
        folium.Marker(
            location=[row["위도"], row["경도"]],
            popup=folium.Popup(popup_html, max_width=220),
            tooltip=f"<b>{row['구']} {row['동']}</b> (클릭하여 인구 확인)",
            icon=folium.Icon(color=marker_color, icon=icon_type, prefix="glyphicon")
        ).add_to(marker_cluster)

    # 지도를 화면에 렌더링
    st_folium(m, width=900, height=600)
    
    # 하단 데이터 테이블
    with st.expander("📄 지도 플롯 데이터 원본 테이블 보기"):
        st.dataframe(df[["구", "동", "총인구수", "남자인구수", "여자인구수", "위도", "경도"]].reset_index(drop=True), use_container_width=True)

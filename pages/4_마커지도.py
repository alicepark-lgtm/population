import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os

st.set_page_config(page_title="안산시 인구 마커 지도", layout="wide")

st.title("🗺️ 안산시 행정동별 인구 공간 분포 지도")
st.markdown("인구수가 많을수록 **원의 크기가 커지고 색상이 짙어지며(불투명)**, 인구가 적을수록 **원의 크기가 작아지고 투명해집니다.**")

# 1. 위경도 사전 정의 (오타 완벽 수정 버전)
COORDINATES = {
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

# 2. 데이터 파일 로드 함수 정의 (캐싱 적용)
@st.cache_data
def load_raw_data():
    pop_paths = ["population.csv", "data/population.csv"]
    for path in pop_paths:
        if os.path.exists(path):
            return pd.read_csv(path)
    return None

# 💡 [NameError 해결 지점] 데이터를 명시적으로 호출하여 raw_df 변수를 생성합니다.
raw_df = load_raw_data()

# 3. 데이터 필터링 및 매핑 
if raw_df is not None:
    available_years = sorted(raw_df["연도"].unique(), reverse=True)
    selected_year = st.sidebar.selectbox("📅 분석 연도 선택", available_years, index=0)
    st.subheader(f"📊 {selected_year}년 인구 밀집도 시각화")

    df_filtered = raw_df[raw_df["연도"] == selected_year].copy()
    
    # 안전하게 .get() 구조로 매핑
    df_filtered["구"] = df_filtered["동"].apply(lambda x: COORDINATES[x]["구"] if x in COORDINATES else "안산시")
    df_filtered["위도"] = df_filtered["동"].apply(lambda x: COORDINATES[x].get("위도") if x in COORDINATES else None)
    df_filtered["경도"] = df_filtered["동"].apply(lambda x: COORDINATES[x].get("경도") if x in COORDINATES else None)
    
    # 위경도 좌표가 정상적으로 매핑된 데이터만 최종 추출
    df = df_filtered[df_filtered["위도"].notna() & df_filtered["경도"].notna()].copy()
    
    # ------------------ [투명도 & 맵핑을 위한 지표 계산] ------------------
    max_pop = df["총인구수"].max() if not df.empty else 1
    min_pop = df["총인구수"].min() if not df.empty else 0
    pop_range = max_pop - min_pop if max_pop != min_pop else 1

    # 기본 지도 생성
    m = folium.Map(location=[37.315, 126.83], zoom_start=12, tiles="CartoDB positron")

    # 데이터프레임을 순회하며 동적 투명도/색상 마커 추가
    for _, row in df.iterrows():
        ratio = (row["총인구수"] - min_pop) / pop_range
        
        # 반지름 및 투명도 스케일링
        pixel_radius = 8 + ratio * 30
        dynamic_opacity = 0.25 + (ratio * 0.60)
        
        # 색상 그라데이션 단계화
        if ratio < 0.25:
            color_hex = "#fecc5c"  # 연한 황색
        elif ratio < 0.5:
            color_hex = "#fd8d3c"  # 주황색
        elif ratio < 0.75:
            color_hex = "#f03b20"  # 주홍색
        else:
            color_hex = "#bd0026"  # 진한 빨강
        
        # 팝업 HTML 디자인
        popup_html = f"""
        <div style="font-family: 'Malgun Gothic', sans-serif; width: 180px; padding: 5px;">
            <h4 style="margin: 0 0 8px 0; color: #2c3e50; font-size: 14px; border-bottom: 2px solid #34495e; padding-bottom: 4px;">
                📍 {row['구']} {row['동']}
            </h4>
            <table style="width: 100%; font-size: 12px; border-collapse: collapse;">
                <tr style="border-bottom: 1px solid #eee;">
                    <td style="padding: 4px 0; color: #7f8c8d; font-weight: bold;">총인구</td>
                    <td style="padding: 4px 0; text-align: right; font-weight: bold; color: {color_hex};">{row['총인구수']:,}명</td>
                </tr>
                <tr style="border-bottom: 1px solid #eee;">
                    <td style="padding: 4px 0; color: #3498db;">👨 남성</td>
                    <td style="padding: 4px 0; text-align: right;">{row['남자인구수']:,}명</td>
                </tr>
                <tr>
                    <td style="padding: 4px 0; color: #e74c3c;">👩 여성</td>
                    <td style="padding: 4px 0; text-align: right;">{row['여자인구수']:,}명</td>
                </tr>
            </table>
        </div>
        """
        
        folium.CircleMarker(
            location=[row["위도"], row["경도"]],
            radius=pixel_radius,
            popup=folium.Popup(popup_html, max_width=220),
            tooltip=f"<b>{row['동']}</b>: {row['총인구수']:,}명",
            color=color_hex,
            weight=1,
            fill=True,
            fill_color=color_hex,
            fill_opacity=dynamic_opacity
        ).add_to(m)

    # 지도를 화면에 렌더링
    st_folium(m, width=900, height=600, key=f"map_{selected_year}")
    
    with st.expander("📄 선택된 연도 데이터 원본 테이블 보기"):
        st.dataframe(df[["연도", "구", "동", "총인구수", "남자인구수", "여자인구수", "위도", "경도"]].reset_index(drop=True), use_container_width=True)
else:
    st.error("데이터 파일(population.csv)을 찾을 수 없습니다. 경로를 확인해주세요.")

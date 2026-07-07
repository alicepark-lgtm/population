import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os

st.set_page_config(page_title="안산시 인구 마커 지도", layout="wide")

st.title("🗺️ 안산시 행정동별 인구 공간 분포 지도")
st.markdown("안산시 행정동의 지리적 위치 좌표와 주민등록인구 데이터를 결합하여 인구수에 비례하는 원형 마커로 시각화합니다.")

# 데이터 무결성을 위한 위경도 좌표 및 구 정보 사전 정의
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
    "호수동": {"구": "단원구", "위도": 37.3003, "gent": 126.8306}, # 기존 오타 수정 (경도)
    "원곡동": {"구": "단원구", "위도": 37.3325, "경도": 126.8117},
    "백운동": {"구": "단원구", "위도": 37.3278, "경도": 126.8089},
    "신길동": {"구": "단원구", "위도": 37.3258, "경도": 126.7778},
    "초지동": {"구": "단원구", "위도": 37.3117, "경도": 126.8031},
    "선부1동": {"구": "단원구", "위도": 37.3422, "경도": 126.8208},
    "선부2동": {"구": "단원구", "위도": 37.3381, "경도": 126.8167},
    "선부3동": {"구": "단원구", "위도": 37.3361, "경도": 126.8031},
    "대부동": {"구": "단원구", "위도": 37.2611, "경度": 126.5744}
}
# 오타 보정용 맵핑 딕셔너리 재정의
for k, v in COORDINATES.items():
    if 'gent' in v: v['경도'] = v.pop('gent')
    if '경度' in v: v['경도'] = v.pop('경度')

@st.cache_data
def load_raw_data():
    """CSV 파일을 읽어오는 기본 캐싱 함수"""
    pop_paths = ["population.csv", "data/population.csv"]
    for path in pop_paths:
        if os.path.exists(path):
            return pd.read_csv(path)
    return None

raw_df = load_raw_data()

if raw_df is not None:
    # ------------------ [연도 선택 컴포넌트 추가] ------------------
    # 데이터에 존재하는 연도 목록 추출 (내림차순 정렬)
    available_years = sorted(raw_df["연도"].unique(), reverse=True)
    
    # 사이드바에 연도 선택 박스 배치
    selected_year = st.sidebar.selectbox("📅 분석 연도 선택", available_years, index=0)
    st.subheader(f"📊 {selected_year}년 인구 데이터 시각화")

    # 선택된 연도 데이터만 필터링 및 공간 좌표 매핑
    df_filtered = raw_df[raw_df["연도"] == selected_year].copy()
    df_filtered["구"] = df_filtered["동"].apply(lambda x: COORDINATES[x]["구"] if x in COORDINATES else "안산시")
    df_filtered["위도"] = df_filtered["동"].apply(lambda x: COORDINATES[x]["위도"] if x in COORDINATES else None)
    df_filtered["경도"] = df_filtered["동"].apply(lambda x: COORDINATES[x]["경도"] if x in COORDINATES else None)
    df = df_filtered[df_filtered["위도"].notna()].copy()

    # 원 크기의 스케일링을 위해 선택된 연도의 최대 총인구수 파악
    max_pop = df["총인구수"].max() if not df.empty else 1

    # 1. 안산시 기본 지도 생성 (CartoDB Positron)
    m = folium.Map(
        location=[37.315, 126.83],
        zoom_start=12,
        tiles="CartoDB positron"
    )

    # 2. 데이터프레임을 순회하며 인구 비례 CircleMarker 추가
    for _, row in df.iterrows():
        # 구 테마 색상 설정
        theme_color = "#2980b9" if row["구"] == "상록구" else "#c0392b"
        fill_color = "#3498db" if row["구"] == "상록구" else "#e74c3c"
        
        # 💡 [핵심] 인구수에 비례하도록 반지름(Radius) 계산 
        # 가장 인구가 많은 동의 반지름이 35픽셀이 되도록 공식화 (최소 크기 8픽셀 보장)
        pixel_radius = 8 + (row["총인구수"] / max_pop) * 27
        
        # 팝업 디자인 HTML
        popup_html = f"""
        <div style="font-family: 'Malgun Gothic', sans-serif; width: 180px; padding: 5px;">
            <h4 style="margin: 0 0 8px 0; color: #2c3e50; font-size: 14px; border-bottom: 2px solid #34495e; padding-bottom: 4px;">
                📍 {row['구']} {row['동']} ({selected_year}년)
            </h4>
            <table style="width: 100%; font-size: 12px; border-collapse: collapse;">
                <tr style="border-bottom: 1px solid #eee;">
                    <td style="padding: 4px 0; color: #7f8c8d; font-weight: bold;">총인구</td>
                    <td style="padding: 4px 0; text-align: right; font-weight: bold; color: {theme_color};">{row['총인구수']:,}명</td>
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
        
        # 💡 [변경] Marker 대신 CircleMarker를 사용하여 인구 크기를 표현합니다.
        folium.CircleMarker(
            location=[row["위도"], row["경도"]],
            radius=pixel_radius,               # 인구 비례 반지름
            popup=folium.Popup(popup_html, max_width=220),
            tooltip=f"<b>{row['구']} {row['동']}</b><br>총인구: {row['총인구수']:,}명",
            color=theme_color,                 # 원 테두리 색상
            weight=1.5,                        # 원 테두리 두께
            fill=True,
            fill_color=fill_color,             # 원 내부 채우기 색상
            fill_opacity=0.6                   # 불투명도 (겹치는 구역 투명하게 처리)
        ).add_to(m)

    # 지도를 화면에 렌더링 (줌 이동 시 초기화 방지를 위해 key 지정)
    st_folium(m, width=900, height=600, key=f"map_{selected_year}")
    
    # 하단 데이터 테이블
    with st.expander("📄 선택된 연도 데이터 원본 테이블 보기"):
        st.dataframe(df[["연도", "구", "동", "총인구수", "남자인구수", "여자인구수", "위도", "경도"]].reset_index(drop=True), use_container_width=True)
else:
    st.error("데이터 파일(population.csv)을 찾을 수 없습니다. 경로를 확인해주세요.")

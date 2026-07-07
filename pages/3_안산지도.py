import streamlit as st
import folium
from streamlit_folium import st_folium

st.title("🗺️ 나만의 위치 북마크 지도")
st.write("지도에서 원하는 위치를 클릭하면 마커가 추가됩니다!")

# 1. 세션 상태 초기화
if "places" not in st.session_state:
    st.session_state.places = []
if "map_center" not in st.session_state:
    st.session_state.map_center = [37.5665, 126.9780]
if "map_zoom" not in st.session_state:
    st.session_state.map_zoom = 12

# 2. 지도 생성
m = folium.Map(location=st.session_state.map_center, zoom_start=st.session_state.map_zoom)

# 마커 표시 (깨짐 방지 아이콘 적용)
for name, lat, lon in st.session_state.places:
    folium.Marker(
        [lat, lon], 
        popup=name, 
        tooltip=name,
        icon=folium.Icon(color="red", icon="info-sign")
    ).add_to(m)

# 3. st_folium 설정 변경 (returned_objects 추가)
# 줌이나 이동할 때는 무시하고, 오직 'last_clicked' 데이터만 Streamlit으로 받아옵니다.
map_data = st_folium(
    m, 
    width=700, 
    height=500, 
    key="bookmark_map",
    returned_objects=["last_clicked"]  # 👈 핵심! 줌/이동 시 재실행을 막아줍니다.
)

# 4. 지도 클릭 이벤트 처리
if map_data and map_data.get("last_clicked") is not None:
    click_lat = map_data["last_clicked"]["lat"]
    click_lng = map_data["last_clicked"]["lng"]
    
    current_click = (click_lat, click_lng)
    
    # 중복 클릭 방지 
    if "last_processed_click" not in st.session_state or st.session_state.last_processed_click != current_click:
        place_name = f"북마크 {len(st.session_state.places) + 1}"
        st.session_state.places.append((place_name, click_lat, click_lng))
        st.session_state.last_processed_click = current_click
        
        # 클릭했을 때만 중심점과 줌을 저장하여 고정
        st.session_state.map_center = [click_lat, click_lng]
        st.rerun()

# --- 저장된 리스트 및 초기화 ---
st.write("---")
if st.session_state.places:
    st.subheader("📍 저장된 장소 리스트")
    for name, lat, lon in st.session_state.places:
        st.text(f"• {name}: 위도 {lat:.4f}, 경도 {lon:.4f}")
        
    if st.button("모든 마커 초기화"):
        st.session_state.places = []
        st.session_state.last_processed_click = None
        st.rerun()

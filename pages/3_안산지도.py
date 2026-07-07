import streamlit as st
import folium
from streamlit_folium import st_folium

st.title("🗺️ 나만의 위치 북마크 지도")
st.write("지도에서 **원하는 위치를 클릭**하면 마커가 추가됩니다! (줌을 당겨서 정확한 위치를 클릭해보세요)")

# 1. 세션 상태(Session State) 초기화
if "places" not in st.session_state:
    st.session_state.places = []

# 지도의 중심점과 줌 레벨을 기억하기 위한 세션 상태
if "map_center" not in st.session_state:
    st.session_state.map_center = [37.5665, 126.9780]  # 초기 위치: 서울시청
if "map_zoom" not in st.session_state:
    st.session_state.map_zoom = 12  # 초기 줌 레벨

# 2. 기본 지도 생성 (세션에 저장된 중심점과 줌 레벨 적용)
m = folium.Map(location=st.session_state.map_center, zoom_start=st.session_state.map_zoom)

# 저장된 마커들을 지도에 표시
# 기존 코드 수정 부분 (지도에 저장된 마커들을 표시하는 루프)
for name, lat, lon in st.session_state.places:
    folium.Marker(
        [lat, lon], 
        popup=name, 
        tooltip=name,
        # 📌 아래 icon 옵션을 추가하면 깨지지 않고 예쁜 마커가 나옵니다!
        icon=folium.Icon(color="red", icon="info-sign") 
    ).add_to(m)

# 3. 지도를 화면에 렌더링하고 사용자의 행동(클릭, 이동) 감지
# 중요: key를 지정해야 상태 변화를 정확히 추적할 수 있습니다.
map_data = st_folium(m, width=700, height=500, key="bookmark_map")

# 4. 지도 이동/줌 변경 시 해당 상태를 세션에 업데이트 (지도 초기화 방지)
if map_data.get("center") is not None:
    st.session_state.map_center = [map_data["center"]["lat"], map_data["center"]["lng"]]
if map_data.get("zoom") is not None:
    st.session_state.map_zoom = map_data["zoom"]

# 5. 지도 클릭 이벤트 처리
# 사용자가 지도를 클릭하면 'last_clicked'에 위경도 정보가 들어옵니다.
if map_data.get("last_clicked") is not None:
    click_lat = map_data["last_clicked"]["lat"]
    click_lng = map_data["last_clicked"]["lng"]
    
    # 중복 추가 방지를 위해 마지막으로 추가된 좌표와 비교
    current_click = (click_lat, click_lng)
    if "last_processed_click" not in st.session_state or st.session_state.last_processed_click != current_click:
        
        # 클릭한 위치의 마커 이름 정의 (여기서는 몇 번째 핀인지 표시)
        place_name = f"북마크 {len(st.session_state.places) + 1}"
        
        # 세션에 저장
        st.session_state.places.append((place_name, click_lat, click_lng))
        st.session_state.last_processed_click = current_click
        
        # 지도에 즉시 반영하기 위해 페이지 리런(재실행)
        st.rerun()

# --- 선택 기능: 저장된 리스트 보여주기 및 초기화 ---
st.write("---")
if st.session_state.places:
    st.subheader("📍 저장된 장소 리스트")
    for name, lat, lon in st.session_state.places:
        st.text(f"• {name}: 위도 {lat:.4f}, 경도 {lon:.4f}")
        
    if st.button("모든 마커 초기화"):
        st.session_state.places = []
        st.rerun()

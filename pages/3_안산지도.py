import streamlit as st
import folium
from streamlit_folium import st_folium
import math

st.title("🗺️ 나만의 위치 북마크 지도")
st.write("지도에서 원하는 위치를 클릭하고 이름을 지정해 마커를 추가해보세요!")

# 1. 세션 상태 초기화
if "places" not in st.session_state:
    st.session_state.places = []
if "map_center" not in st.session_state:
    st.session_state.map_center = [37.5665, 126.9780]
if "map_zoom" not in st.session_state:
    st.session_state.map_zoom = 12
# 현재 클릭되어 이름 입력을 기다리는 임시 좌표 상태
if "temp_click" not in st.session_state:
    st.session_state.temp_click = None

# 2. 지도 생성
m = folium.Map(location=st.session_state.map_center, zoom_start=st.session_state.map_zoom)

# 저장된 마커 표시 (깨짐 방지 아이콘 적용)
for name, lat, lon in st.session_state.places:
    folium.Marker(
        [lat, lon], 
        popup=name, 
        tooltip=name,
        icon=folium.Icon(color="red", icon="info-sign")
    ).add_to(m)

# 3. st_folium으로 클릭 감지
map_data = st_folium(
    m, 
    width=700, 
    height=500, 
    key="bookmark_map",
    returned_objects=["last_clicked"]
)

# 4. 지도 클릭 이벤트 처리 (임시 좌표로 저장)
if map_data and map_data.get("last_clicked") is not None:
    click_lat = map_data["last_clicked"]["lat"]
    click_lng = map_data["last_clicked"]["lng"]
    current_click = (click_lat, click_lng)
    
    if st.session_state.temp_click != current_click:
        # 중복 마커 저장을 방지하기 위해, 이미 등록된 좌표인지 확인
        already_exists = any(abs(p[1]-click_lat) < 1e-6 and abs(p[2]-click_lng) < 1e-6 for p in st.session_state.places)
        if not already_exists:
            st.session_state.temp_click = current_click
            st.rerun()

# 5. 마커 이름 입력 창 표시 (지도를 클릭했을 때만 나타남)
if st.session_state.temp_click is not None:
    st.info(f"📍 새로운 지점을 클릭했습니다! (위도: {st.session_state.temp_click[0]:.4f}, 경도: {st.session_state.temp_click[1]:.4f})")
    
    # 사용자에게 마커 이름 입력 받기
    default_name = f"북마크 {len(st.session_state.places) + 1}"
    new_place_name = st.text_input("마커의 이름을 입력하세요:", value=default_name)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("장소 추가하기", type="primary"):
            st.session_state.places.append((new_place_name, st.session_state.temp_click[0], st.session_state.temp_click[1]))
            st.session_state.map_center = [st.session_state.temp_click[0], st.session_state.temp_click[1]]
            st.session_state.temp_click = None  # 입력 창 닫기
            st.rerun()
    with col2:
        if st.button("취소"):
            st.session_state.temp_click = None
            st.rerun()

# --- 직선거리 계산 기능 ---
st.write("---")
st.subheader("📏 두 마커 간 직선거리 구하기")

if len(st.session_state.places) >= 2:
    # 등록된 마커들의 이름 리스트 생성
    place_names = [p[0] for p in st.session_state.places]
    
    col1, col2 = st.columns(2)
    with col1:
        start_place = st.selectbox("출발지 선택", place_names, index=0)
    with col2:
        # 센스 있게 목적지는 출발지와 다른 위치를 기본값으로 설정
        end_index = 1 if len(place_names) > 1 else 0
        end_place = st.selectbox("목적지 선택", place_names, index=end_index)
        
    if st.button("📐 직선거리 계산하기"):
        if start_place == end_place:
            st.warning("출발지와 목적지가 같습니다. 서로 다른 마커를 선택해주세요.")
        else:
            # 선택한 마커의 좌표 가져오기
            p1 = next(p for p in st.session_state.places if p[0] == start_place)
            p2 = next(p for p in st.session_state.places if p[0] == end_place)
            
            lat1, lon1 = p1[1], p1[2]
            lat2, lon2 = p2[1], p2[2]
            
            # 하버사인(Haversine) 공식을 이용한 대권 거리 계산 (지구 반지름 약 6371km)
            R = 6371.0
            phi1 = math.radians(lat1)
            phi2 = math.radians(lat2)
            delta_phi = math.radians(lat2 - lat1)
            delta_lambda = math.radians(lon2 - lon1)
            
            a = math.sin(delta_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            distance = R * c
            
            # 결과 출력 (1km 미만은 미터로 표시, 이상은 km로 표시)
            if distance < 1.0:
                st.success(f"✨ **{start_place}** ↔️ **{end_place}** 직선거리: **{distance * 1000:.1f} m**")
            else:
                st.success(f"✨ **{start_place}** ↔️ **{end_place}** 직선거리: **{distance:.2f} km**")
else:
    st.caption("💡 거리를 계산하려면 지도에 마커를 최소 2개 이상 등록해주세요.")


# --- 저장된 리스트 및 초기화 ---
st.write("---")
if st.session_state.places:
    st.subheader("📍 저장된 장소 리스트")
    for name, lat, lon in st.session_state.places:
        st.text(f"• {name}: 위도 {lat:.4f}, 경도 {lon:.4f}")
        
    if st.button("모든 마커 초기화"):
        st.session_state.places = []
        st.session_state.temp_click = None
        st.rerun()

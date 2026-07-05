import streamlit as st
import pandas as pd
import folium

from streamlit_folium import st_folium

df = pd.read_csv("data/population_map.csv")

m = folium.Map(
    location=[37.32,126.84],
    zoom_start=11
)

for _, row in df.iterrows():

    folium.Marker(
        location=[row["위도"], row["경도"]],
        popup=f"""
        <b>{row['행정동']}</b><br>
        총인구 : {row['총인구']:,}명<br>
        세대수 : {row['세대수']:,}세대
        """,
        tooltip=row["행정동"]
    ).add_to(m)

st_folium(m,width=900,height=600)

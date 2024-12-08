import streamlit as st
import plotly.express as px
from plotly import graph_objects as go
import geopandas as gpd
import json

FILENAME = "scotland_avi_zones_4326_simple.gpkg"
# FILENAME = "cairngorms_avi_zones_4326.gpkg"

forecast_colors = {
    "0": 'green',
    "1": 'yellow',
    "2": 'orange',
    "3": 'red',
    "4": 'black'
}

# the map polygons have an aspect_min attribute, this is how they map to the index of the colour string
map_aspect_min_to_category = {
    0: 0,
    22.5: 1,
    67.5: 2,
    112.5: 3,
    157.5: 4,
    202.5: 5,
    247.5: 6,
    292.5: 7,
    337.5: 0,
}

aspect_names = [
    'N',
    'NW',
    'E',
    'SE',
    'S',
    'SW',
    'W',
    'NW'
    ]

def forecast_string_to_url(fl, fh, sm, sb):
    val = ''.join([f"{int(l)+1}{int(h)+1}00" for l, h in zip(fl, fh)])
    return f"https://www.sais.gov.uk/_compassrose/?val={val}&txts={sb}&txtm={sm}&txte=1300"

@st.cache_data()   # to allow adding of the forecast column
def load_polygons(filename):
    print(f"Opening {filename}")
    map_df = gpd.read_file(filename).set_crs("EPSG:4326", allow_override=True)
    map_df['poly_id'] = map_df.index    # Create column of unique ids
    map_df['aspect_category'] = map_df.apply(lambda row: map_aspect_min_to_category[row.ASPECT_MIN], axis=1)
    map_df['aspect'] = map_df.apply(lambda row: aspect_names[row.aspect_category], axis=1)
    map_df['elevation'] = map_df.apply(lambda row: f"{row.ELEV_MIN:.0f}-{row.ELEV_MAX:.0f}m", axis=1)
    print(f"Polygon file opened")
    return map_df

def assign_forecast(df_row, fl, fh, sm, sb):
    if df_row.ELEV_MIN < sb:
        return '0'

    if df_row.ELEV_MIN < sm:
        return fl[df_row.aspect_category]
    else:
        return fh[df_row.aspect_category]

st.set_page_config(layout="wide")
st.title("Avalanche Painting Tool")
st.markdown(
    """
    Use the controls on the left to define the avalanche chart you want.
    All areas on the map will be coloured accordingly. Numbers 0-4 represent green, yellow, orange, red and black,
    counted around clockwise from N to NW. Make sure to set the elevation values correctly too.

    Once the chart looks right, hit the button to generate the map (takes some time)
    """)

elev_split = st.sidebar.number_input("Elevation Split", value=700, step=100)
elev_bottom = st.sidebar.number_input("Minimum Elevation", value=400, step=100)
forecast_high = st.sidebar.text_input("High Elevation Forecast", value="00000000", max_chars=8)
forecast_low = st.sidebar.text_input("Low Elevation Forecast", value="00000000", max_chars=8)

st.sidebar.image(forecast_string_to_url(forecast_low, forecast_high, elev_split, elev_bottom))

def draw_map(polygons):
    with st.spinner('Painting map...'):
        map_df = polygons
        map_df['forecast'] = map_df.apply(assign_forecast, 
                                        args=(forecast_low, forecast_high, elev_split, elev_bottom),
                                        axis=1)

        fig = px.choropleth_mapbox(map_df, geojson=map_df.geometry, 
                            locations="poly_id",
                            color="forecast",
                            color_discrete_map=forecast_colors,
                            mapbox_style="open-street-map",
                            zoom=8, center = {"lat": 57.123, "lon": -3.670},
                            opacity=0.5,
                            hover_data={"aspect":True, "forecast":False, "elevation":True, "poly_id":False}
                            )

        fig.update_geos(fitbounds="geojson", visible=True)
        fig.update_traces(marker_line_width=0)
        fig.update_layout(showlegend=False, height=600)

    st.plotly_chart(fig, use_container_width=True)

buttons = st.columns(5)
if buttons[0].button('Full map'):
    draw_map(load_polygons("scotland_avi_zones_4326_simple.gpkg"))

if buttons[1].button('Cairngorms only'):
    draw_map(load_polygons("cairngorms_avi_zones_4326.gpkg"))

st.markdown(
    """
    Important info:
    - Elevation data is the EU-DEM v1.1 dataset from [Copernicus](https://land.copernicus.eu/imagery-in-situ/eu-dem/eu-dem-v1.1)
    - Only areas vaguely in and around the SAIS forecast areas are drawn over, the rest of Scotland is ignored
    - The coloured slopes are angled 25-50 deg
    - The resolution of the base dataset is low (1 point per 25m). The slope calculation smooths this out too. Slope divisions are therefore quite loose
    - Areas that fit all other criteria but are smaller than 50x50m are not included
    - Even after all of this, the shapes are further simplified to give a reasonable filesize
    - For goodness sake use common sense
    """
)

with open(FILENAME, "rb") as f:
    st.download_button("Download .gpkg of zones", f, file_name=FILENAME)
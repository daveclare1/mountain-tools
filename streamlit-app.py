import streamlit as st
import plotly.express as px
import geopandas as gpd
import json

FILENAME = "cairngorms_avi_zones_4326.gpkg"

forecast_colors = {
    "0": 'green',
    "1": 'yellow',
    "2": 'orange',
    "3": 'red',
    "4": 'black'
}

def forecast_string_to_url(fl, fh, sm, sb):
    val = ''.join([f"{int(l)+1}{int(h)+1}00" for l, h in zip(fl, fh)])
    return f"https://www.sais.gov.uk/_compassrose/?val={val}&txts={sb}&txtm={sm}&txte=1300"

@st.cache(allow_output_mutation=True)   # to allow adding of the forecast column
def load_polygons():
    fp = FILENAME
    map_df = gpd.read_file(fp).set_crs("EPSG:4326", allow_override=True)
    map_df['poly_id'] = map_df.index    # Create column of unique ids
    return map_df

def assign_forecast(df_row, fl, fh, sm, sb):
    if df_row.ELEV_MIN < sb:
        return '0'

    if df_row.ELEV_MIN < sm:
        return fl[df_row.aspect-1]
    else:
        return fh[df_row.aspect-1]

st.set_page_config(layout="wide")
st.title("SAIS Painting Tool")
st.markdown(
    """
    Use the controls on the left to define the avalanche map you want.
    All areas on the map will be coloured accordingly. Numbers 0-4 represent green to black,
    counted around from N to NW. 
    """)

elev_split = st.sidebar.number_input("Elevation Split", value=700, step=100)
elev_bottom = st.sidebar.number_input("Minimum Elevation", value=400, step=100)
forecast_high = st.sidebar.text_input("High Elevation Forecast", value="00000000", max_chars=8)
forecast_low = st.sidebar.text_input("Low Elevation Forecast", value="00000000", max_chars=8)

st.sidebar.image(forecast_string_to_url(forecast_low, forecast_high, elev_split, elev_bottom))

map_df = load_polygons()

map_df['forecast'] = map_df.apply(assign_forecast, 
                                args=(forecast_low, forecast_high, elev_split, elev_bottom),
                                axis=1)

fig = px.choropleth_mapbox(map_df, geojson=map_df.geometry, 
                    locations="poly_id",
                    color="forecast",
                    color_discrete_map=forecast_colors,
                    mapbox_style="stamen-terrain",
                    zoom=8, center = {"lat": 57.123, "lon": -3.670},
                    opacity=0.5,
                    hover_data={"aspect":True, "forecast":False, "ELEV_MIN":True, "poly_id":False}
                    )

fig.update_geos(fitbounds="geojson", visible=True)
fig.update_traces(marker_line_width=0)
fig.update_layout(showlegend=False, height=600)

st.plotly_chart(fig, use_container_width=True)

st.markdown(
    """
    Important info:
    - Elevation data is the EU-DEM v1.1 dataset from [Copernicus](https://land.copernicus.eu/imagery-in-situ/eu-dem/eu-dem-v1.1)
    - The coloured slopes are angled 25-50 deg
    - The resolution of the dataset is low (1 point per 25m). The slope calculation smooths this out too. Slope boundaries are loose!
    - For goodness sake use common sense
    """
)

with open(FILENAME, "rb") as f:
    st.download_button("Download .gpkg of zones", f, file_name=FILENAME)
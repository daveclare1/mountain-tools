import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("SAIS Tool")

layout = go.Layout(
    # title_text ='USA Cities',
    # title_x =0.5,  
    # width=950,
    # height=700,
    mapbox = dict(
        center = dict(
            lat=57.13, lon=-4.31), zoom=7, style="stamen-terrain"))

df = pd.DataFrame(
    np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4],
    columns=['lat', 'lon'])

scatt = go.Scattermapbox(lat=df.lat, lon=df.lon, mode='markers+text',    
        below='False', marker=dict( size=12, color ='rgb(56, 44, 100)'))

fig = go.Figure(data=scatt, layout=layout)

st.plotly_chart(fig, use_container_width=True)
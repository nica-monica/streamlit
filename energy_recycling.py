# -*- coding: utf-8 -*-

import streamlit as st
import numpy as np
import pandas as pd
import folium

from folium import plugins

import streamlit_folium
import numpy as np
from streamlit_folium import st_folium
import geopandas as gpd



APP_TITLE = 'Waste energy recycling in Sweden'

# st.title(APP_TITLE)
# st.caption('my subtitle')

def display_time_filters(recycling_data):
    year_list= list(recycling_data['year'].unique())
    year_list.sort(reverse= True)
    year= st.sidebar.selectbox('Year', year_list)
    # st.header(year)
    return year

def display_measure_filter():
    count=0
    return st.sidebar.radio('Measure', ['Total energy produced - Mwh', 'Energy per inhabitant'], key = count)
    st.write('You select:', 'Measure')
    count += 1


def display_map(recycling_data, year):
    recycling_data= recycling_data[recycling_data['year']== year]
    measure = display_measure_filter()
    # st.write(recycling_data['Län'].unique())
    map= folium.Map(location= [63,14], zoom_start=4.5, tiles= 'CartoDB positron')

    # this is a workaround to make sure the swedish characters are displayed
    import json
    sweden_geojson= gpd.read_file('data/sweden-counties_1680.geojson')
    back_geojson = sweden_geojson.to_json()
    j = json.loads(back_geojson)

    bins = list(recycling_data[measure].quantile([0,0.05, 0.20,0.3, 0.5,0.7,0.8, 0.90,0.95, 1]))

    choropleth= folium.Choropleth(
        geo_data=j,
        data=recycling_data,
        columns=['Län', measure],
        key_on='feature.properties.NAME_1',
        fill_color="YlGn",
        fill_opacity=0.7,
        line_opacity=0.5,
        legend_name='Energy produced in Mwh',
        bins=bins,
        reset=True)
    choropleth.geojson.add_to(map)
    for feature in choropleth.geojson.data['features']:
        kommun= feature['properties']['NAME_1']
        display1= recycling_data[recycling_data['Län'] == kommun]['Total energy produced - Mwh'].values[0]
        feature['properties']['energy']= str('Energy produced:') + f'{display1:,.2f}' + ' Mwh'
        display2= recycling_data[recycling_data['Län']==kommun]['Energy per inhabitant'].values[0]
        feature['properties']['energy per inhabitant']= 'Energy produced per inhabitant:'  + f'{display2:,.2f}' + ' Mwh'

    if measure== 'Energy per inhabitant':
        choropleth.geojson.add_child(folium.features.GeoJsonTooltip(['NAME_1', 'energy per inhabitant'], labels= False))
    if measure== 'Total energy produced - Mwh':
        choropleth.geojson.add_child(folium.features.GeoJsonTooltip(['NAME_1', 'energy'], labels= False))

    st_map= st_folium(map, width=400, height=800)

    # kommun= ''
    # if st.map['last_active_drawing']:
    #     kommun= st_map['last_active_drawing']['properties']['NAME_1']
    # return kommun


def main():
    st.set_page_config(APP_TITLE)
    st.title(APP_TITLE)
    #Load Data
    recycling_data = pd.read_csv(
        'data/recycling_data.csv')
    recycling_data['year'] = recycling_data['year'].astype(int)


    #Display Filters and Map
    year = display_time_filters(recycling_data)
    kommun = display_map(recycling_data, year)
    # state_name = display_state_filter(df_continental, state_name)
    # measure = display_measure_filter()


# DISPLAY METRICS



if __name__ == "__main__":
    main()

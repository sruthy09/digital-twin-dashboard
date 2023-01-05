import streamlit as st #creating an app
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import folium
from folium.plugins import MarkerCluster
from folium.plugins import HeatMap, HeatMapWithTime
from folium.features import ClickForMarker, LatLngPopup
from folium.plugins import Search, Draw, Fullscreen
import geopandas as gpd
import imageio
import json
import random
import requests
from geopandas import GeoDataFrame
from shapely.geometry import Polygon
import branca
from streamlit_folium import folium_static

p_gsp_gnode_directconnect_region_lookup = "gsp_gnode_directconnect_region_lookup.csv"
#p_gsp_gnode_directconnect_region_lookup="https://data.nationalgrideso.com/backend/dataset/2810092e-d4b2-472f-b955-d8bea01f9ec0/resource/bbe2cc72-a6c6-46e6-8f4e-48b879467368/download/gsp_gnode_directconnect_region_lookup.csv"

p_dno_license_areas_20200506 = "dno_license_areas_20200506.geojson"
#p_dno_license_areas_20200506 = "https://data.nationalgrideso.com/backend/dataset/0e377f16-95e9-4c15-a1fc-49e06a39cfa0/resource/e96db306-aaa8-45be-aecd-65b34d38923a/download/dno_license_areas_20200506.geojson"

p_gsp_regions_20181031 = "gsp_regions_20181031.geojson"
#p_gsp_regions_20181031 = "https://data.nationalgrideso.com/backend/dataset/2810092e-d4b2-472f-b955-d8bea01f9ec0/resource/a3ed5711-407a-42a9-a63a-011615eea7e0/download/gsp_regions_20181031.geojson"

p_fes_2022_building_blocks_version_4 = "fes-2022-building-blocks-version-4.0.csv"
#p_fes_2022_building_blocks_version_4 = "https://data.nationalgrideso.com/backend/dataset/30df2649-99cf-4f84-9128-6c58fc1ea72a/resource/36fd3aa9-6e42-418f-b1bb-a31bbfcf2008/download/fes-2022-building-blocks-version-4.0.csv"

#p_demand_file = "https://drive.google.com/file/d/1V3YSTaNfz9VKJ9v0aRbr2e6LAHkoKGHT/view?usp=share_link"
p_demand_file = "dipit3.csv" 

p_sub_image = "gb.png"
#p_sub_image = "https://drive.google.com/file/d/1zI-IiB21-6ei0TMWrSSJT4OAQhzCvojw/view?usp=share_link"

p_overwrite_file = "gsp_regions_filewrite.geojson"
#p_overwrite_file = "https://drive.google.com/file/d/1lFyi0AkPN0gueq9GbEEYRA3E2l-conLv/view?usp=share_link"
def style_function(x):
    df_points, heatmap = get_dataset()
    colormap = get_colormap(get_dataset())
    return {
        "fillColor": "#756bb1",#colormap(x["properties"]["2021"]),
        "color": "black",
        "weight": 2,
        "fillOpacity": 0.5,
    }
def rd2(x):
    return round(x, 2)
def get_min_max(heatmap):
    minimum, maximum = heatmap["2021"].quantile([0.05, 0.95]).apply(rd2)
    mean = round(heatmap["2021"].mean(), 2)
    return minimum, maximum, mean
def get_dataset():
    geojson_point = p_gsp_regions_20181031 #"/Users/Sruthy.Benny/Documents/gsp_regions_20181031.geojson"
    df_points = gpd.read_file(geojson_point)
    df_points = df_points.to_crs("EPSG:4326") 
    heat_path = p_fes_2022_building_blocks_version_4 #"/Users/Sruthy.Benny/Documents/FES_Region_Heat.csv"
    df_heat_region = pd.read_csv(heat_path)
    df_heat_region.drop(columns=['Share of GSP','Comment'], axis=1, inplace=True)
    df_heatregion_merged = pd.merge(df_heat_region, df_points, how='inner', left_on='GSP', right_on='RegionName')
    df_heatregion_merged1 = df_heatregion_merged[(df_heatregion_merged['FES Scenario'] == 'Leading the Way') & (df_heatregion_merged['Building Block ID Number'] == 'Gen_BB001')]
    df_heatregion_merged1 = df_heatregion_merged.drop_duplicates(subset='GSP', keep="first")
    df_heatregion_merged_map = df_heatregion_merged1[['GSP','geometry','2021','2022','2023','2024','2025','2026','2027','2028','2029','2030','2031','2032','2033','2034','2035','2036','2037','2038','2039','2040','2041','2042','2043','2044','2045','2046','2047','2048','2049','2050']]
    df_heatregion_merged_map = df_heatregion_merged_map.fillna(0) 
    df_heatregion_merged_map = GeoDataFrame(df_heatregion_merged_map, crs="EPSG:4326", geometry=df_heatregion_merged_map['geometry'])
    df_heatregion_merged_map = df_heatregion_merged_map[df_heatregion_merged_map['geometry'] != None]
    return df_points, df_heatregion_merged_map
def get_coordinates():
    path = p_gsp_gnode_directconnect_region_lookup #"/Users/Sruthy.Benny/Downloads/GIS_hit_coordinates.csv"
    df_coordinates = pd.read_csv(path)
    df_coordinates.dropna(subset=["gnode_lat","gnode_lon"],inplace=True)
    return df_coordinates
def get_licensearea():
    geojson_path = p_dno_license_areas_20200506 #"/Users/Sruthy.Benny/Documents/dno_license_areas_20200506.geojson"
    df_areas = gpd.read_file(geojson_path)
    df_areas = df_areas.to_crs("EPSG:4326")  
    return df_areas
def popup_html(row):
    i = row
    gnode_name=row.gnode_name
    gnode_url="https://ecsemea.sharepoint.com/:x:/r/sites/UKIEngineeringCentre/Shared%20Documents/Product/Digital%20Twin/GIS_hit_coordinates.xlsx?d=w9e5be2b6db744f0cbb693781dd3746cc&csf=1&web=1&e=VQEPdi"
    gnode_latitude=row.gnode_lat
    gnode_longitude = row.gnode_lon
    left_col_color = "#FFFFFF"
    right_col_color = "#FFFFFF"
    html = """<!DOCTYPE html>
<html>
<head>
<h4 style="margin-right:10"; width="200px">{}</h4>""".format(gnode_name) + """
</head>
    <table style="height: 80px; width: 150px;">
<tbody>
<tr>
<td style="background-color: """+ left_col_color +""";"><span style="color: #000000;">Gnode Name</span></td>
<td style="width: 150px;background-color: """+ right_col_color +""";">{}</td>""".format(gnode_name) + """
</tr>
<tr>
<td style="background-color: """+ left_col_color +""";"><span style="color: #000000;">Equip. Details</span></td>
<td style="width: 150px;background-color: """+ right_col_color +""";">
<a href="https://image1.slideserve.com/2555464/slide2-l.jpg">Network<\a>
</td>
</tr>
<tr>
<td style="background-color: """+ left_col_color +""";"><span style="color: #000000;">Latitude</span></td>
<td style="width: 150px;background-color: """+ right_col_color +""";">{}</td>""".format(gnode_latitude) + """
</tr>
<tr>
<td style="background-color: """+ left_col_color +""";"><span style="color: #000000;">Longitude</span></td>
<td style="width: 150px;background-color: """+ right_col_color +""";">{}</td>""".format(gnode_longitude) + """
</tr>
</tbody>
</table>
</html>
"""
    return html
def get_colormap(heatmap):
    minimum, maximum, mean = get_min_max(heatmap)
    colormap = branca.colormap.LinearColormap(
        colors=["#f2f0f7", "#cbc9e2", "#9e9ac8", "#756bb1", "#54278f"],
        index=heatmap["2021"].quantile([0.2, 0.4, 0.6, 0.8]),
        vmin=minimum,
        vmax=maximum,
    )
    colormap.caption = "UK GSP Regions"
    return colormap
def draw_basemap(tile_select):
    #Define coordinates of where we want to center our map
    boulder_coords = [53.509865 , -0.218092]
    mp = folium.Map(tiles=tile_select, location = boulder_coords, zoom_start = 6, scrollWheelZoom=False)
    fullscreen = Fullscreen(position='topleft', title='Full Screen', title_cancel='Exit Full Screen')
    fullscreen.add_to(mp)  
    return mp
def draw_region(base_map, tile_select):
    df_points, heatmap = get_dataset()
    colormap = get_colormap(heatmap)
    stategeo = folium.GeoJson(
        heatmap,
        name="GB GSP Region",
        style_function=style_function,
        tooltip=folium.GeoJsonTooltip(
            fields=["GSP", "2021"], aliases=["Region", "Area"], localize=True
        ),
    ).add_to(base_map)
    statesearch = Search(
        layer=stategeo,
        geom_type="Polygon",
        placeholder="Search for a UK Region",
        collapsed=False,
        search_label="GSP",
        weight=3,
    ).add_to(base_map)
    colormap.add_to(base_map)
    return base_map
def app_feature(mp, add_select, heatmap):
    fg=folium.FeatureGroup(name='Assets')
    mp.add_child(fg)
    draw = Draw(position="bottomleft")
    draw.add_to(mp)
    #heatmap = get_dataset()
    colormap = get_colormap(heatmap)
    df_coordinates = get_coordinates()
    df_areas = get_licensearea()
    stategeo = folium.GeoJson(
        heatmap,
        name="GSP Region",
        style_function=style_function,
        tooltip=folium.GeoJsonTooltip(
            fields=["GSP", "2021"], aliases=["Region", "Area"], localize=True
        ),
    ).add_to(mp)
    licensegeo = folium.GeoJson(
        df_areas,
        name="GSP License Area",
        style_function=lambda x: {'fillColor': 'orange'},
        tooltip=folium.GeoJsonTooltip(
            fields=["LongName"], aliases=["License Area"], localize=True
        ),
    ).add_to(mp)
    mc = MarkerCluster()
    for ix, row in df_coordinates.iterrows():
        lon = row.gnode_lon
        lat = row.gnode_lat
        html_popup = popup_html(row)
        iframe = branca.element.IFrame(html=html_popup,width=510,height=280)
        ic_image = p_sub_image #'/Users/Sruthy.Benny/Power Distribution network - Project/sub-img.png'
        custom_icon = folium.features.CustomIcon(ic_image,icon_size=(17, 17))
        popup = folium.Popup(folium.Html(html_popup, script=True), max_width=500)
        mp1 = folium.Marker(location=[lat, lon],icon=custom_icon,popup=popup)
        mc.add_child(mp1)
    fg.add_child(mc)
    folium.LayerControl().add_to(mp)
    statesearch = Search(
        layer=stategeo,
        geom_type="Polygon",
        position="topright",
        placeholder="Search for a UK  GSP Region",
        collapsed=False,
        search_label="GSP",
        weight=3,
    ).add_to(mp)
    return mp
def threshold(df_heatregion_merged_map, year):
    threshold_scale = np.linspace(df_heatregion_merged_map[year].values.min(),
                              df_heatregion_merged_map[year].values.max(),
                              10, dtype=float)
    # change the numpy array to a list
    threshold_scale = threshold_scale.tolist() 
    threshold_scale[-1] = threshold_scale[-1]
    return threshold_scale
# def show_demand_map(demand_data, year, tile_select):
# #     st.write(demand_data)
#     choropleth = folium.Choropleth(geo_data = json.load(open("https://drive.google.com/file/d/1lFyi0AkPN0gueq9GbEEYRA3E2l-conLv/view?usp=share_link")),
#                            data = demand_data,
#                            columns=('region_name','year'),
#                            key_on='feature.properties.GSP',
#                            #threshold_scale=threshold_scale,
#                            fill_color='YlOrRd',
#                            fill_opacity=0.7,
#                            line_opacity=0.2,
#                            legend_name='GSP Regions',
#                            highlight=True,
#                            )
#     choropleth.geojson.add_to(base_map)
#     for feature in choropleth.geojson.data['features']:
#         state_name = feature['properties']['GSP']
#     st.write(state_name)
#     choropleth.geojson.add_child(
#         folium.features.GeoJsonTooltip(fields=["GSP"], aliases=["Region"]))
#     st_map = folium_static(base_map, width=700, height=450)
#     regionname = ''
#     if st_map['last_active_drawing']:
#         st.write(state_name)
#         regionname = st_map['last_active_drawing']['properties']['GSP']
#     return regionname
def show_maps(hmt, threshold_scale, df_heatregion_merged_map, year, tile_select):
    maps= folium.Choropleth(geo_data = json.load(open(p_overwrite_file)),
                           data = df_heatregion_merged_map,
                           columns=['GSP',year],
                           key_on='feature.properties.GSP',
                           threshold_scale=threshold_scale,
                           fill_color='YlOrRd',
                           fill_opacity=0.7,
                           line_opacity=0.2,
                           legend_name='GSP Regions',
                           highlight=True,
                           reset=True).add_to(hmt)
    folium.GeoJsonTooltip(fields=["GSP", year], aliases=["Region", "Value"], localize=True).add_to(maps.geojson)
    folium.LayerControl().add_to(hmt)
    return hmt
def app_layout():
    #for changing tiles of the maps
    tile_select = st.sidebar.selectbox("Choose a Tile for the Map?",("OpenStreetMap", "Cartodb Positron", "Stamen Terrain","Stamen Toner"))
    base_map = draw_basemap(tile_select)
    dicts = {"GSP Region":'FES Scenario',
         "GSP Points or Assets": 'Unit',
         "Heatmap": 'DNO License Area'}
    select_data = st.sidebar.selectbox("Select the Map you want to see?",
    ("", "Grid Supply Points","Power Consumption - Future Energy Scenario", 
     "Power Consumption Demand - Future Energy Scenario")
    )
    #fetch the data
    df_points, df_heatregion_merged_map = get_dataset()
    #design for the app
    st.title('Select the Map to view')
    if select_data == "":
        map = base_map
    elif select_data == "Grid Supply Points":
        map = app_feature(base_map, tile_select, df_heatregion_merged_map)
        folium_static(map)
    elif select_data == "Power Consumption - Future Energy Scenario":
        df_heatregion_merged_map_cpy = df_heatregion_merged_map.copy()
        df_heatregion_merged_map_cpy = pd.melt(df_heatregion_merged_map_cpy, id_vars=['GSP','geometry'])
        df_heatregion_merged_map_cpy = df_heatregion_merged_map_cpy.set_index('variable')
        yearlist = list(set(df_heatregion_merged_map_cpy.index))
        yearlist.sort()
        year = st.sidebar.selectbox('Choose the year', yearlist)
        map = show_maps(base_map, threshold(df_heatregion_merged_map, year), df_heatregion_merged_map, year, tile_select)
        folium_static(map)
#     elif select_data == "Power Consumption Demand - Future Energy Scenario":
#         demand_data = pd.read_csv(p_demand_file)
#         df_heatregion_merged_map_cpy = df_heatregion_merged_map.copy()
#         df_heatregion_merged_map_cpy = pd.melt(df_heatregion_merged_map_cpy, id_vars=['GSP','geometry'])
#         df_heatregion_merged_map_cpy = df_heatregion_merged_map_cpy.set_index('variable')
#         yearlist = list(set(df_heatregion_merged_map_cpy.index))
#         yearlist.sort()
#         year = st.sidebar.selectbox('Choose the year', yearlist)
#         regionname = show_demand_map(draw_basemap(tile_select),  demand_data, year, tile_select)
if __name__=='__main__':
    app_layout()

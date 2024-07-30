import folium

map=folium.Map(zoom_level=0)
folium.Marker([userlat,userlon]).add_to(map)
folium.Marker([latitude,longitude],icon=folium.Icon(icon='cloud')).add_to(map)
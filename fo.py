import folium
#inicializacao do mapa
m = folium.Map(location=[20, 0], zoom_start=2,
tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}',
attr='Estri')
#localizacoes do servico atendido
folium.Marker(location=[-14.2350, -51.9253],popup='Brazil').add_to(m)
folium.Marker(location=[56.1304, -106.3468],popup='Canada').add_to(m)
folium.Marker(location=[46.2276, 2.2137],popup='France').add_to(m)
folium.Marker(location=[36.2048, 138.2529],popup='Japan').add_to(m)
folium.Marker(location=[41.8719, 12.5674],popup='Italy').add_to(m)
folium.Marker(location=[40.4637, -3.7492],popup='Espanha').add_to(m)
folium.Marker(location=[39.3999, -8.2245],popup='Portugal').add_to(m)
#salvamento do mapa em arquivo html
m.save("mapamundial.html")
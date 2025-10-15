#!/usr/bin/env python3
import json
import folium
import matplotlib.pyplot as plt
from pathlib import Path

with open("gps_data.json", "r") as f:
    points = []
    for line in f:
        data = json.loads(line)
        points.append([data['latitude'], data['longitude']])


m = folium.Map(location=points[0], zoom_start=15)
folium.PolyLine(points, '-o', weight=5).add_to(m)
folium.Marker(points[0], popup='Start', icon=folium.Icon(color='green')).add_to(m)
folium.Marker(points[-1], popup='End', icon=folium.Icon(color='red')).add_to(m)
m.save('map.html')
print("Map saved as map.html")

lats, lons = zip(*points)
plt.plot(lons, lats, '-o', linewidth=2, markersize=4, label="User path")
plt.scatter(lons[0], lats[0], color='green', s=80, label="Start")
plt.scatter(lons[-1], lats[-1], color='red', s=80, label="End")
plt.title("GPS Path")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.legend()
plt.grid(True)
plt.show()
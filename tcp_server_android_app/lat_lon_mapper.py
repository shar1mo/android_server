#!/usr/bin/env python3
import psycopg2
import folium
import matplotlib.pyplot as plt

DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "gps_db"
DB_USER = "shar1mo"
DB_PASS = "sharimo2005"

points = []

try:
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    cur = conn.cursor()
    cur.execute("""
        SELECT latitude, longitude 
        FROM device_measurements
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
        ORDER BY id;
    """)
    rows = cur.fetchall()
    for lat, lon in rows:
        points.append([lat, lon])

    cur.close()
    conn.close()
except Exception as e:
    print("Error connecting to DB:", e)
    exit(1)

if not points:
    print("No points to plot")
    exit(1)

m = folium.Map(location=points[0], zoom_start=15)
folium.PolyLine(points, weight=5, color="blue").add_to(m)
folium.Marker(points[0], popup='Start', icon=folium.Icon(color='green')).add_to(m)
folium.Marker(points[-1], popup='End', icon=folium.Icon(color='red')).add_to(m)
m.save('map.html')
print("Map saved as map.html")

lats, lons = zip(*points)
plt.plot(lons, lats, '-o', linewidth=2, markersize=4, label="Path")
plt.title("GPS Path")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.grid(True)
plt.legend()
plt.show()

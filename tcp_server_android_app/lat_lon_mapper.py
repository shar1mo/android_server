#!/usr/bin/env python3
import psycopg2
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.colors as mcolors
import numpy as np

DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "gps_db"
DB_USER = "shar1mo"
DB_PASS = "sharimo2005"

RSSI_MIN = -120
RSSI_MAX = -40
REFRESH_INTERVAL_MS = 3000


def clamp_rssi(rssi):
    if rssi is None:
        return RSSI_MIN
    try:
        r = float(rssi)
    except Exception:
        return RSSI_MIN
    return max(RSSI_MIN, min(RSSI_MAX, r))


def fetch_data():
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
            SELECT latitude, longitude, rssi
            FROM device_measurements
            WHERE latitude IS NOT NULL
              AND longitude IS NOT NULL
            ORDER BY id;
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows
    except Exception as e:
        print("DB ERROR:", e)
        return []


def main():
    print("[*] Starting live RSSI plot...")

    fig, ax = plt.subplots()

    norm = mcolors.Normalize(vmin=RSSI_MIN, vmax=RSSI_MAX)
    cmap = plt.get_cmap("inferno")

    scatter = ax.scatter([], [], c=[], cmap=cmap, norm=norm, s=60)

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax)
    cbar.set_label("RSSI (dBm)")

    ax.set_title("GPS Path (Live RSSI)")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.grid(True)

    rows = fetch_data()
    if rows:
        lats = [r[0] for r in rows]
        lons = [r[1] for r in rows]
        ax.set_xlim(min(lons) - 0.001, max(lons) + 0.001)
        ax.set_ylim(min(lats) - 0.001, max(lats) + 0.001)

    def update(frame):
        rows = fetch_data()
        if not rows:
            return scatter,

        lats = [r[0] for r in rows]
        lons = [r[1] for r in rows]
        rssis = [clamp_rssi(r[2]) for r in rows]

        coords = np.column_stack((lons, lats))
        scatter.set_offsets(coords)
        scatter.set_array(np.array(rssis))

        return scatter,

    anim = animation.FuncAnimation(
        fig,
        update,
        interval=REFRESH_INTERVAL_MS,
        blit=False,
        cache_frame_data=False
    )

    plt.show()


if __name__ == "__main__":
    main()

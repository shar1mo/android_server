#!/usr/bin/env python3
import zmq
import json
import psycopg2
from datetime import datetime

DB_HOST = "localhost"
DB_NAME = "gps_db"
DB_USER = "shar1mo"
DB_PASS = "sharimo2005"
DB_PORT = 5432

def insert_combined_row(conn, data):
    try:
        loc = data.get("location", {})
        cell_list = data.get("cell_info", [])
        device_id = data.get("device_id", "Unknown_Device")
        timestamp = data.get("timestamp", int(datetime.now().timestamp()*1000))
        latitude = loc.get("latitude")
        longitude = loc.get("longitude")
        altitude = loc.get("altitude")
        speed = loc.get("speed")

        rssi = rsrp = rsrq = rssnr = pci = mcc = mnc = None
        if len(cell_list) > 0:
            for cell in cell_list:
                if cell.get("type") == "LTE":
                    idt = cell.get("identity", {})
                    sig = cell.get("signal", {})
                    rssi = sig.get("rssi")
                    rsrp = sig.get("rsrp")
                    rsrq = sig.get("rsrq")
                    rssnr = sig.get("rssnr")
                    pci = idt.get("pci")
                    mcc = idt.get("mcc")
                    mnc = idt.get("mnc")
                    break  # берем первый LTE

        server_time = datetime.now()

        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO device_measurements
                (device_id, latitude, longitude, altitude, speed, timestamp, server_time,
                 rssi, rsrp, rsrq, rssnr, mcc, mnc, pci)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (device_id, latitude, longitude, altitude, speed, timestamp, server_time,
                  rssi, rsrp, rsrq, rssnr, mcc, mnc, pci))
        conn.commit()
        return True
    except Exception as e:
        print("DB INSERT ERROR:", e)
        return False

def main():
    print("Starting ZMQ server...")
    conn = psycopg2.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASS, port=DB_PORT)
    print("Connected to PostgreSQL")

    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://0.0.0.0:8080")
    print("Server listening...")

    while True:
        try:
            message = socket.recv_string()
        except KeyboardInterrupt:
            break
        if message.lower() == "exit":
            socket.send_string("bye")
            continue
        if message.lower() == "test":
            socket.send_string("OK")
            continue

        try:
            data = json.loads(message)
        except:
            socket.send_string("invalid json")
            continue

        data["server_time"] = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        ok = insert_combined_row(conn, data)
        socket.send_string("saved" if ok else "db_error")

    socket.close()
    context.term()
    conn.close()

if __name__ == "__main__":
    main()

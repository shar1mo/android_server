#!/usr/bin/env python3
import zmq
import json
from datetime import datetime
import traceback

def main(bind_addr="tcp://0.0.0.0:8080", out_file="gps_data.json"):
    context = zmq.Context()
    socket = context.socket(zmq.REP)

    try:
        socket.bind(bind_addr)
        print(f"ZMQ server started on {bind_addr}")
        print("Waiting for connections... (Ctrl-C to stop)")

        while True:
            try:
                message = socket.recv_string()
            except KeyboardInterrupt:
                print("\nServer interrupted by user, shutting down...")
                break
            except Exception as e:
                print(f"Recv error: {e}")
                continue

            print(f"Received: {message!r}")
            reply = "error"

            try:
                msg_lc = message.lower()

                if msg_lc == "exit":
                    reply = "bye"
                    socket.send_string(reply)
                    print("Client requested disconnect.")
                    continue

                if msg_lc == "test":
                    reply = "OK - server is working!"
                    socket.send_string(reply)
                    print("Test message handled.")
                    continue

                try:
                    data = json.loads(message)
                except json.JSONDecodeError:
                    reply = "OK - message received"
                    socket.send_string(reply)
                    continue

                data["server_time"] = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

                try:
                    with open(out_file, "a", encoding="utf-8") as f:
                        f.write(json.dumps(data, ensure_ascii=False) + "\n")
                        f.flush()
                except Exception as e:
                    print(f"Failed to write to {out_file}: {e}")
                    traceback.print_exc()

                lat = data.get("latitude")
                lon = data.get("longitude")
                if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
                    print(f"Saved GPS data: {lat:.6f}, {lon:.6f}")
                else:
                    print(f"Saved GPS data (no numeric lat/lon): {data}")

                reply = "GPS data saved"

            except Exception as e:
                print("Processing error:", e)
                traceback.print_exc()
                reply = "error"

            try:
                socket.send_string(reply)
            except Exception as e:
                print("Failed to send reply:", e)
                continue

    finally:
        try:
            socket.close()
            context.term()
        except Exception:
            pass
        print("Server stopped.")

if __name__ == "__main__":
    main()

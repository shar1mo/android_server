import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('localhost', 8080)
server_socket.bind(server_address)
server_socket.listen(2)

print("Server started and waiting for connections...")

while True:
    try:
        client_socket, client_address = server_socket.accept()
        print(f"Connection established with {client_address}")
        
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
                
            message = data.decode('utf-8')
            print(f"Data received: {message}")
            
            if message.lower() == 'exit':
                print("Client requested exit")
                break
                
            response = "ok"
            client_socket.send(response.encode('utf-8'))
        
        
        print(f"Connection with {client_address} closed\n")
        
    except KeyboardInterrupt:
        print("\nServer shutting down...")
        break
    except Exception as e:
        print(f"Error: {e}")
        continue

server_socket.close()
print("Server stopped")
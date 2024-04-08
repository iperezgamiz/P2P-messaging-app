import socket
import threading
import json


class Server:
    def __init__(self, host='0.0.0.0', port=12345):
        self.users = {}  # Format: {username: {'ip': ip_address, 'port': port_number}}
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Server listening on {self.host}:{self.port}")

    def handle_client(self, client_socket):
        try:
            while True:
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    break  # Client disconnected

                data = json.loads(data)
                action = data.get('action')

                if action == 'register':
                    self.users[data['username']] = {'ip': data['ip'], 'port': data['port']}
                    client_socket.sendall(b"User registered successfully.")
                elif action == 'lookup':
                    user = self.users.get(data['username'])
                    if user:
                        client_socket.sendall(json.dumps(user).encode('utf-8'))
                    else:
                        client_socket.sendall(b"User not found.")
                else:
                    client_socket.sendall(b"Invalid action.")
        finally:
            client_socket.close()

    def run(self):
        while True:
            client_socket, address = self.server_socket.accept()
            print("Accepted new connection.")
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_thread.start()


if __name__ == '__main__':
    server = Server()
    server.run()

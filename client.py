import socket
import json
import sqlite3
import threading
import uuid
from datetime import datetime


class Client:
    def __init__(self, server_ip, server_port, username, client_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.username = username
        self.client_ip = self.get_local_ip()
        self.client_port = client_port
        self.conn = sqlite3.connect('p2p_messaging_app.db')
        self.cursor = self.conn.cursor()
        self.stop_listening = False

    def get_local_ip(self):
        """Get the local IP address of the client."""
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('10.255.255.255', 1))
            IP = s.getsockname()[0]
        except Exception:
            IP = '127.0.0.1'
        finally:
            s.close()
        return IP

    def start_listening(self):
        """Starts a server to listen for incoming messages from other clients."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.client_ip, self.client_port))
            s.listen()
            print(f"Listening for messages on {self.client_ip}:{self.client_port}")
            while not self.stop_listening:
                conn, addr = s.accept()
                threading.Thread(target=self.handle_incoming_message, args=(conn,)).start()

    def handle_incoming_message(self, conn, addr):
        """Handles an incoming message from another client and possibly stores sender as a new contact."""
        with conn:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                try:
                    message_info = json.loads(data.decode('utf-8'))
                    sender_username = message_info.get('sender_username')
                    message_text = message_info.get('message_text')
                    print(f"Message from {sender_username}: {message_text}")

                    # Add sender to contacts if new
                    self.add_contact_if_new(sender_username)

                    self.store_received_message(sender_username, self.username, message_text)
                except json.JSONDecodeError as e:
                    print(f"Failed to decode message: {e}")
                    continue

    def add_contact_if_new(self, username):
        """Adds a new contact if they're not already in the Contacts table."""
        if not self.is_contact(username):
            try:
                self.cursor.execute("INSERT INTO Contacts (Username) VALUES (?)", (username,))
                self.conn.commit()
                print(f"Added {username} to contacts.")
            except sqlite3.IntegrityError as e:
                print(f"Could not add {username} to contacts: {e}")

    def is_contact(self, username):
        """Check if the username is already a contact."""
        self.cursor.execute("SELECT Username FROM Contacts WHERE Username = ?", (username,))
        return self.cursor.fetchone() is not None

    def store_received_message(self, sender_username, receiver_username, message_text):
        """Stores a received message in the database."""
        message_id = str(uuid.uuid4())
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        delivered = 1  # Assuming the message is considered delivered upon receipt

        self.cursor.execute('''
        INSERT INTO Messages (MessageID, SenderUsername, ReceiverUsername, MessageText, Delivered, Timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (message_id, sender_username, receiver_username, message_text, delivered, timestamp))
        self.conn.commit()
        print("Received message stored in the database.")

    def send_message(self, receiver_username, ip, port, message):
        """Sends a message to another client. Stores the message if the recipient is offline."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)  # Timeout to avoid hanging indefinitely
                s.connect((ip, port))
                s.sendall(message.encode('utf-8'))
                self.store_sent_message(receiver_username, message)
        except Exception as e:
            print(e)

    def register_in_server(self):
        """Register this client with the central server."""
        data = json.dumps({
            'action': 'register',
            'username': self.username,
            'ip': self.client_ip,
            'port': self.client_port
        }).encode('utf-8')
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.server_ip, self.server_port))
            s.sendall(data)
            response = s.recv(1024)
            print(f"Server response: {response.decode('utf-8')}")

    def lookup_user(self, username):
        """Request the IP and port of another user from the server."""
        data = json.dumps({
            'action': 'lookup',
            'username': username
        }).encode('utf-8')
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.server_ip, self.server_port))
            s.sendall(data)
            response = s.recv(1024).decode('utf-8')
            if response != 'User not found.':
                return json.loads(response)

    def start_chat_session(self):
        receiver_username = input("Enter the username of the user you want to chat with: ")
        if receiver_username == "exit":
            return run()
        user_info = self.lookup_user(receiver_username)
        print(f"Starting chat with {receiver_username}...")
        while True:
            message = input("You: ")
            if message.lower() == 'exit':
                return self.start_chat_session()
            # If receiver is online
            if user_info:
                self.send_message(receiver_username, user_info['ip'], user_info['port'], message)
            # If receiver is offline
            else:
                self.store_sent_message(receiver_username, message, delivered=0)

    def store_sent_message(self, receiver_username, message, delivered=1):
        """Stores an undelivered message in the database."""
        message_id = str(uuid.uuid4())
        self.cursor.execute('''
        INSERT INTO Messages (MessageID, SenderUsername, ReceiverUsername, MessageText, Delivered, Timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (
        message_id, self.username, receiver_username, message, delivered, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        self.conn.commit()

    def send_undelivered_messages(self):
        """Attempts to send any messages stored as undelivered."""
        self.cursor.execute('''
        SELECT MessageID, ReceiverUsername, MessageText FROM Messages WHERE Delivered = 0 AND SenderUsername = ?
        ''', (self.username,))
        undelivered_messages = self.cursor.fetchall()

        for message_id, receiver_username, message_text in undelivered_messages:
            # Lookup the receiver's current IP and port
            user_info = self.lookup_user(receiver_username)
            if user_info:
                try:
                    # Attempt to send the message
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.settimeout(5)
                        s.connect((user_info['ip'], user_info['port']))
                        s.sendall(message_text.encode('utf-8'))

                    # If successful, mark the message as delivered
                    self.cursor.execute('''
                    UPDATE Messages SET Delivered = 1 WHERE MessageID = ?
                    ''', (message_id,))
                    self.conn.commit()
                    print(f"Undelivered message to {receiver_username} sent successfully.")
                except Exception as e:
                    print(f"Failed to send undelivered message to {receiver_username}: {e}")


def run():
    server_ip = '127.0.0.1'  # Running locally
    server_port = 12345
    client_port = int(input("Introduce your port number: "))
    username = input("Introduce your username: ")
    client = Client(server_ip, server_port, username, client_port)
    client.register_in_server()

    threading.Thread(target=client.start_listening, daemon=True).start()
    threading.Thread(target=client.send_undelivered_messages, daemon=True).start()
    client.start_chat_session()


if __name__ == '__main__':
    run()

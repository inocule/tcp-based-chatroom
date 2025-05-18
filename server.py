# TCP Chatroom Server
import socket
import threading
from datetime import datetime

# Get the local host IP address dynamically
HOST = socket.gethostbyname(socket.gethostname())
PORT = 9090
ENCODER = 'utf-8'

# Create and configure the server socket (IP and Port)
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()  # Server starts listening for incoming connections

clients = []     # Stores all connected client sockets
usernames = []   # Stores usernames corresponding to client sockets

# Broadcasts a message to all connected clients
def broadcast(msg):
    for client in clients:
        try:
            client.send(msg)
        except:
            continue  # Skip if sending fails (e.g., client disconnected)

# Handles individual client communication
def handle(client):
    while True:
        try:
            msg = client.recv(1024).decode(ENCODER)  # Receive and decode message
            if not msg:
                raise ConnectionResetError()  # Treat empty message as disconnection

            username = usernames[clients.index(client)]
            timestamp = datetime.now().strftime("[%H:%M]")
            print(f"{timestamp} {username} says {msg}")

            # Broadcast message to all clients
            broadcast(f"{timestamp} {username}: {msg}\n".encode(ENCODER))
        except:
            # Cleanup on disconnect
            if client in clients:
                index = clients.index(client)
                username = usernames.pop(index)
                clients.remove(client)
                client.close()

                leave_msg = f"{username} has left the chat.\n"
                print(leave_msg.strip())
                broadcast(leave_msg.encode(ENCODER))
            break

# Accepts new client connections
def receive():
    while True:
        client, address = server.accept()  # Accept new client connection
        print(f"Connected with {str(address)}!")

        # Ask for username
        client.send("USER".encode(ENCODER))
        username = client.recv(1024).decode(ENCODER)

        usernames.append(username)
        clients.append(client)

        # Notify all users of the new connection
        broadcast(f"{username} connected to the server!\n".encode(ENCODER))
        print(f"{username} connected.")

        # Start a new thread for the client
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

print("Server running...")
receive()  # Start accepting connections

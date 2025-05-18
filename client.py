# TCP Chatroom Client
import socket
import threading
import tkinter as tk
from tkinter import simpledialog, scrolledtext

# Get local host IP
HOST = socket.gethostbyname(socket.gethostname())
PORT = 9090
ENCODER = 'utf-8'

class Client:
    def __init__(self, host, port):
        # Create and connect the client socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))

        # Prompt for username using a simple dialog
        login = tk.Tk()
        login.withdraw()
        self.username = simpledialog.askstring("Login", "Please choose a valid, unique username", parent=login)

        self.gui_done = False  # GUI not ready yet
        self.running = True    # Main loop control flag

        # Start GUI and receiving threads
        threading.Thread(target=self.gui_loop).start()
        threading.Thread(target=self.receive).start()

    # GUI setup and main loop
    def gui_loop(self):
        self.win = tk.Tk()
        self.win.title("Local TCP Chatroom")
        self.win.configure(bg="lightgray")
        self.win.resizable(False, False)

        tk.Label(self.win, text="Chat:", bg="lightgray", font=('Century Gothic', 15)).pack(padx=20, pady=5)

        self.text_area = scrolledtext.ScrolledText(self.win, state='disabled')
        self.text_area.pack(padx=20, pady=5)

        tk.Label(self.win, text="Message:", bg="lightgray", font=('Century Gothic', 15)).pack(padx=20, pady=5)

        self.input_area = tk.Text(self.win, height=3)
        self.input_area.pack(padx=20, pady=5)

        tk.Button(self.win, text="Send", font=('Century Gothic', 15), command=self.write).pack(padx=20, pady=5)

        self.win.protocol("WM_DELETE_WINDOW", self.stop)  # Graceful shutdown on close
        self.gui_done = True
        self.win.mainloop()

    # Send message to the server
    def write(self):
        msg = self.input_area.get("1.0", "end").strip()
        if msg:
            self.sock.send(msg.encode(ENCODER))
            self.input_area.delete("1.0", "end")

    # Proper shutdown of client socket and GUI
    def stop(self):
        self.running = False
        self.sock.close()
        self.win.quit()

    # Receive messages from the server
    def receive(self):
        while self.running:
            try:
                msg = self.sock.recv(1024).decode(ENCODER)
                if msg == "USER":
                    # Respond to server’s username request
                    self.sock.send(self.username.encode(ENCODER))  
                elif self.gui_done:
                    self.text_area.config(state='normal')
                    self.text_area.insert('end', msg)
                    self.text_area.yview('end')  # Scroll to bottom
                    self.text_area.config(state='disabled')
            except:
                break  # Stop receiving if an error occurs

# Start the client
client = Client(HOST, PORT)
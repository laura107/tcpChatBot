import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox
from tkinter import ttk

# Constants for connection
HOST = #INSERT YOUR IP
PORT = 10002

# Global variables
client = None
nickname = None
users = []

def connect_to_server():
    global client, nickname

    nickname = simpledialog.askstring("Nickname", "Choose a nickname:", parent=window)
    if not nickname:
        window.destroy()
        return

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((HOST, PORT))
        status_label.config(text="Connected", fg="green")
    except Exception as e:
        messagebox.showerror("Connection Error", f"Cannot connect to server: {e}")
        window.destroy()
        return

    # Start threads for receiving messages and sending nickname
    receive_thread = threading.Thread(target=receive)
    receive_thread.start()

def receive():
    while True:
        try:
            message = client.recv(1024).decode('ascii')
            if message == 'NICK':
                client.send(nickname.encode('ascii'))
            elif message.startswith('USERLIST'):
                update_user_list(message)
            else:
                display_message(message)
        except Exception as e:
            display_message("An error occurred! Reconnecting...", 'error')
            status_label.config(text="Disconnected", fg="red")
            client.close()
            reconnect()
            break

def reconnect():
    global client
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST, PORT))
        client.send(nickname.encode('ascii'))
        status_label.config(text="Reconnected", fg="green")
    except Exception as e:
        display_message(f"Reconnection failed: {e}", 'error')
        status_label.config(text="Disconnected", fg="red")

def write():
    message = input_area.get("1.0", tk.END).strip()
    if message:
        client.send(f'{nickname}: {message}'.encode('ascii'))
        display_message(f'{nickname} (You): {message}', 'self')
        input_area.delete('1.0', tk.END)

def display_message(message, tag=None):
    text_area.config(state=tk.NORMAL)
    if tag:
        text_area.insert(tk.END, message + '\n', tag)
    else:
        text_area.insert(tk.END, message + '\n')
    text_area.yview(tk.END)
    text_area.config(state=tk.DISABLED)

def update_user_list(message):
    global users
    users = message.split()[1:]
    user_list.delete(0, tk.END)
    for user in users:
        user_list.insert(tk.END, user)

def on_closing():
    client.close()
    window.destroy()

# Tkinter GUI setup
window = tk.Tk()
window.title("Enhanced Chat Client")

# Connection status
status_label = tk.Label(window, text="Disconnected", fg="red")
status_label.pack(pady=5)

# Chat display area
text_area = scrolledtext.ScrolledText(window, wrap=tk.WORD)
text_area.pack(padx=10, pady=10)
text_area.config(state=tk.DISABLED)
text_area.tag_config('self', foreground='blue')
text_area.tag_config('error', foreground='red')
text_area.tag_config('system', foreground='purple')

# Input area
input_frame = tk.Frame(window)
input_frame.pack(padx=10, pady=10)

input_area = tk.Text(input_frame, height=3, bg='lightyellow', fg='black')
input_area.pack(side=tk.LEFT, padx=5)

# Send button
send_button = tk.Button(input_frame, text="Send", command=write, bg='lightblue')
send_button.pack(side=tk.RIGHT, padx=5)

# User list
user_list_frame = tk.Frame(window)
user_list_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=10)

user_list_label = tk.Label(user_list_frame, text="Users", bg='lightgreen')
user_list_label.pack()

user_list = tk.Listbox(user_list_frame, bg='lightyellow', fg='black')
user_list.pack(fill=tk.Y)

window.protocol("WM_DELETE_WINDOW", on_closing)

# Connect to server
connect_to_server()

window.mainloop()

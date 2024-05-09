import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np
import base64
import json
import requests
import websockets
import asyncio
import webbrowser
import threading
import io
from tkinter import messagebox


class ClientGUI:
    def __init__(self, root, server_url):
        self.root = root
        self.root.title("Distributed Image Processing Application")
        self.root.geometry("600x400")
        self.server_url = server_url
        self.response_image = []
        

        # Background Image
        self.background_image = Image.open("b1.image")  # Change the path to your background image
        self.background_photo = ImageTk.PhotoImage(self.background_image)
        self.background_label = tk.Label(root, image=self.background_photo)
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Header
        header_frame = tk.Frame(self.root, bg="#2c3e50", height=50)
        header_frame.pack(fill="x")

        header_label = tk.Label(header_frame, text="Distributed Image Processing Client", font=("Helvetica", 16), fg="white", bg="#2c3e50")
        header_label.pack(pady=10)

        # Input Frame
        self.input_frame = tk.Frame(self.root, bg="pink",highlightbackground="blue", bd=5)
        self.input_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8, relheight=0.3)

        # Image Selection
        self.image_label = tk.Label(self.input_frame, text="Select an Image:", font=("Helvetica", 12), bg="white")
        self.image_label.grid(row=0, column=0, padx=10, pady=5)

        self.image_path_entry = tk.Entry(self.input_frame, width=40)
        self.image_path_entry.grid(row=0, column=1, padx=10, pady=5)

        self.browse_button = tk.Button(self.input_frame, text="Browse", command=self.select_image)
        self.browse_button.grid(row=0, column=2, padx=10, pady=5)

        # Service Selection
        self.service_label = tk.Label(self.input_frame, text="Select a Service:", font=("Helvetica", 12), bg="white")
        self.service_label.grid(row=1, column=0, padx=10, pady=5)

        self.service_combobox = ttk.Combobox(self.input_frame, width=35)
        self.service_combobox.grid(row=1, column=1, padx=10, pady=5)
        self.service_combobox.bind("<<ComboboxSelected>>", self.update_input_fields)

        # Process Button
        self.process_button = tk.Button(self.input_frame, text="Process", command=self.process_image)
        self.process_button.grid(row=2, columnspan=3, padx=10, pady=10)

        # Dictionary to store additional argument widgets
        self.argument_widgets = {}

        # Create a new menu
        self.create_menu()

    def create_menu(self):
        menu = tk.Menu(self.root, bg="pink", fg="white", activebackground="pink", activeforeground="white")
        self.root.config(menu=menu)

        families = [
            ("Color Manipulation", ["Invert", "Saturate", "RGB to Gray", "Gray to RGB"]),
            ("Fourier Transform Domain", ["Fourier Transform", "Butterworth Lowpass Filter", "Butterworth Highpass Filter", "Apply Highpass Filter"]),
            ("Thresholding", ["Mean Adaptive Threshold", "Gaussian Adaptive Threshold", "Gaussian Threshold", "Otsu Threshold", "Binary Threshold"]),
            ("Edge Detection", ["Harris Corner Detection", "Hough Transform", "Canny Edge Filter"]),
            ("Noise Removal", ["Blur Image", "Sharpen Image", "Remove Gaussian Noise", "Remove Salt Pepper Noise"]),
            ("Special Filters", ["Sobel Filter", "Prewitt Filter", "Roberts Filter"])
        ]

        for family, services in families:
            family_menu = tk.Menu(menu, tearoff=0, bg="pink", fg="white", activebackground="white",
                                  activeforeground="pink")
            menu.add_cascade(label=family, menu=family_menu)
            for service in services:
                family_menu.add_command(label=service, command=lambda s=service: self.service_combobox.set(s))

    def select_image(self):
        image_path = filedialog.askopenfilename()
        self.image_path_entry.delete(0, tk.END)
        self.image_path_entry.insert(0, image_path)

    def update_input_fields(self, event):
        # Clear existing argument widgets
        for widget in self.argument_widgets.values():
            widget.destroy()
        self.argument_widgets = {}

        # Get the selected service
        selected_service = self.service_combobox.get()

        # Dictionary to map services to their arguments
        service_arguments = {
            "Butterworth Lowpass Filter": ["Cutoff Frequency", "Order"],
            "Butterworth Highpass Filter": ["Cutoff Frequency", "Order"],
            # Add other services with their arguments here
        }

        # Add input fields for the selected service's arguments
        if selected_service in service_arguments:
            arguments = service_arguments[selected_service]
            for i, arg in enumerate(arguments):
                label = tk.Label(self.input_frame, text=arg+":", bg="white")
                label.grid(row=i+2, column=0, padx=10, pady=5)
                entry = tk.Entry(self.input_frame)
                entry.grid(row=i+2, column=1, padx=10, pady=5)
                self.argument_widgets[arg] = entry
    def open_link(self,url):
        webbrowser.open(url, new=2)

    def process_image(self):
        image_path = self.image_path_entry.get()
        service = self.service_combobox.get()

        try:
            image = cv2.imread(image_path)
            if image is None:
                raise Exception("Invalid Image")

            # Get additional arguments for the selected service
            additional_arguments = {}
            for arg, widget in self.argument_widgets.items():
                additional_arguments[arg] = widget.get()

            request = {
                'image': image,
                'service': service,
                'arguments': additional_arguments
            }

            # Send request to receiving node
            self.send_request(request)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def send_request(self, request):
        print("Preparing to send request(s) to server")
        image= request['image']
        _, encoded_image = cv2.imencode('.jpg', image)
        encoded_image_as_str = base64.b64encode(encoded_image).decode('utf-8')
        request = {'image': encoded_image_as_str,'service_num': 1, 'arguments': request['arguments']}
        print("Sending request(s) to server")
        response = requests.post(self.server_url, data=json.dumps(request), headers={'Content-Type': 'application/json'})
        print("Received response from server")
        return response.json()

    def display_response(self, image,url):
        response_image_data = base64.b64decode(image)
        response_image = Image.open(io.BytesIO(response_image_data))
        response_window = tk.Toplevel()
        # Get screen size
        screen_width = response_window.winfo_screenwidth()
        screen_height = response_window.winfo_screenheight()

        # If image is larger than screen, resize it
        if response_image.width > screen_width or response_image.height > screen_height:
            response_image = response_image.resize((screen_width-100, screen_height-100))

        self.response_image.append(ImageTk.PhotoImage(response_image)) 
        #response_window = tk.Toplevel()
        response_window.title("Processed Image")

        # Add 50 pixels to the height for the download button
        response_window.geometry(f'{response_image.width}x{response_image.height}')

        response_label = tk.Label(response_window, image=self.response_image[-1])
        response_label.pack()
        download_button = tk.Button(response_window, text="Download Image", command=self.open_link(url))
        messagebox.showinfo("Notification", "The processed image window is now open.")

class WebSocketServer:
    def __init__(self, server_address, client):
        self.server_ip = server_address[0]
        self.server_port = server_address[1]
        self.clientGui = client

    async def echo(self, websocket, path):
        print(f"Server started at ws://{self.server_ip}:{self.server_port}")
        async for message in websocket:
            message = json.loads(message)
            image = message['image']
            url=message['url']
            task_id = message['task_id']
            self.clientGui.display_response(image,url)

    async def server(self):
        start_server = await websockets.serve(self.echo, self.server_ip, self.server_port)
        await start_server.serve_forever()

    def start_server(self):
        asyncio.run(self.server())
if __name__ == "__main__":
    root = tk.Tk()
    client = ClientGUI(root, 'http://localhost:8000')

    server = WebSocketServer(('localhost', 8765),client)
    server_thread = threading.Thread(target=server.start_server)
    server_thread.start()
    root.mainloop()
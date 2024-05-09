import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt
import Services
import requests
import json
import base64
import asyncio
import websockets
import threading

class Client:
    def __init__(self, server_url):
        self.server_url = server_url
        print(f"Client initialized with server URL: {self.server_url}")

    def choose_service(self):
        print("Available services:")
        print("1. Grayscale Conversion")
        print("2. Blur")
        print("3. Median Filter")
        print("4. Gaussian Smoothing")
        print("5. Bilateral Smoothing")
        print("6. Unsharp Mask")
        print("7. Laplacian Sharpening")
        print("8. Color Inversion")
        print("9. Contrast Stretching")
        print("10. Brightening")
        print("11. Darkening")
        print("12. Edge Detection")
        service_num = int(input("Enter the number corresponding to the desired service: "))
        print(f"Service number chosen: {service_num}")
        return service_num

    def upload_image(self):
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(title="Select an image file : ")
        print(f"Image uploaded from path: {file_path}")
        image = cv2.imread(file_path)
        return image

    def send_request(self, requests_list):
        print("Preparing to send request(s) to server")
        requests_data = []
        for service_num, image in requests_list:
            _, encoded_image = cv2.imencode('.jpg', image)
            encoded_image_as_str = base64.b64encode(encoded_image).decode('utf-8')
            request = {'service_num': service_num, 'image': encoded_image_as_str}
            requests_data.append(request)
        print("Sending request(s) to server")
        response = requests.post(self.server_url, data=json.dumps(requests_data))
        print("Received response from server")
        return response.json()

    def display_image(self, result):
        print("Displaying result image(s)")
        for i, res in enumerate(result):
            task_id = res
            print(f"Displaying image for task ID: {task_id}")
    
    async def echo(self,websocket, path):
        async for message in websocket:
            print(f"Received message: {message}")

    async def server(self):
        start_server = await websockets.serve(self.echo, "localhost", 8765)
        await start_server.serve_forever()
    
    def start_server(self):
        asyncio.run(self.server())

    def run(self):
        requests_list = []
        for _ in range(10):
            service_num = self.choose_service()
            #image = self.upload_image()
            requests_list.append((10, cv2.imread('image.png')))
            if len(requests_list) < 10:
                more = input("Do you want to upload more images? (yes/no): ")
                if more.lower() != 'yes':
                    break
        result = self.send_request(requests_list)
        self.display_image(result)


if __name__ == "__main__":
    client = Client('http://localhost:8000')
    client_thread = threading.Thread(target=client.run)
    server_thread = threading.Thread(target=client.start_server)
    client_thread.start()
    server_thread.start()
    client_thread.join()
    server_thread.join()


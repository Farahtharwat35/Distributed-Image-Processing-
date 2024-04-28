from worker_thread import WorkerThread
from http.server import BaseHTTPRequestHandler, HTTPServer
import base64
import cv2
import numpy as np
from request_handler import RequestHandler


class Node:
    def __init__(self, server_address):
        self.server_address = server_address

    def run(self):
        httpd = HTTPServer(self.server_address, RequestHandler)
        print(f"Starting server on {self.server_address}")
        httpd.serve_forever()


if __name__ == "__main__":
    node = Node(('localhost', 8000))
    node.run()

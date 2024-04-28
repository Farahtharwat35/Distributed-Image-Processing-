from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import base64
import cv2
import numpy as np
from worker_thread import WorkerThread

class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        print("Received a POST request")
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        requests_data = json.loads(post_data)

        results = []
        for request_data in requests_data:
            print("Processing a request")
            service_num = request_data['service_num']
            encoded_image_as_str = request_data['image']
            decoded_image = base64.b64decode(encoded_image_as_str)
            nparr = np.frombuffer(decoded_image, np.uint8)
            img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            # Process the image using the requested service
            print(f"Processing image with service number {service_num}")
            worker = WorkerThread(service_num, img_np)
            result_image = worker.process_image(service_num, img_np)

            _, encoded_result_image = cv2.imencode('.jpg', result_image)
            encoded_result_image_as_str = base64.b64encode(encoded_result_image).decode('utf-8')
            result = {'image': encoded_result_image_as_str}
            results.append(result)

        print("Sending response")
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(results).encode())
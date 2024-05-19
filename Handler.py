from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from threading import Thread
import uuid
import Channel
import cloudCredentials
from redis_db import redisDB

class RequestHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, storage, **kwargs):
        self.channel = Channel.Channel()
        self.storage = storage
        super().__init__(*args, **kwargs)

    def do_POST(self):
        print("Received a POST request")
        content_length = int(self.headers['Content-Length'])
        if 'X-Forwarded-For' in self.headers:
            client_address = self.headers['X-Forwarded-For']
        else:
            client_address = self.client_address[0]
        post_data = self.rfile.read(content_length)
        request_data = json.loads(post_data)
        task_id = str(uuid.uuid4())
        service_num = request_data['service_num']
        encoded_image_as_str = request_data['image']
        try:
            self.storage.upload_image(encoded_image_as_str, task_id)
        except Exception as e:
            print(f"Failed to upload image: {e}")
            self.storage.upload_image(encoded_image_as_str, task_id)
        message = {'client_address': client_address, 'task_id': task_id, 'service_num': service_num}
        test_r = None
        # ttl = None
        try:
            redisDB.update_image_status(task_id, {"status": 'Received But Not Processed Yet',
                                                  "link": 'None'})
            test_r = redisDB.pull(task_id)
            print("RECEIVED STATUS TEST : ", test_r)
            # # Check TTL of a key
            # ttl = redisDB.redis_client.ttl(task_id)
            # print("TTL of 'TASK ID is':", ttl)
        except Exception as e:
            print(f"Failed to update status in redis: {e}")
          
        try:
            self.channel.publish('requests', json.dumps(message))
        except Exception as e:
            print(f"Failed to send request to workers: {e}")
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(task_id).encode())
    
    def do_GET(self):
        self.send_response(200)

class Node:
    def __init__(self, server_address, storage):
        self.server_address = server_address
        self.storage = storage

    def run(self):
        httpd = HTTPServer(self.server_address, lambda *args, **kwargs: RequestHandler(*args, storage=self.storage, **kwargs))
        print(f"Starting server on {self.server_address}")
        httpd.serve_forever()

if __name__ == "__main__":
    storage = cloudCredentials.Storage()
    node = Node(('0.0.0.0', 8000), storage)
    # Starting a new thread for handling requests
    # request_thread = Thread(target=node.run)
    # request_thread.start()
    node.run()
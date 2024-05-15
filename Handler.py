from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from threading import Thread
import uuid
import Channel
import cloudCredentials
import asyncio
import cv2
import base64
import websockets

class RequestHandler(BaseHTTPRequestHandler):
  def __init__(self, *args,  storage, **kwargs):
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
    self.storage.upload_image(encoded_image_as_str, task_id)
    message = {'client_address': client_address, 'task_id': task_id, 'service_num': service_num}
    try:
      self.channel.publish('requests', json.dumps(message))
    except Exception as e:
      print(f"Failed to send request to workers: {e}")
    result=task_id
    self.send_response(200)
    self.send_header('Content-type', 'application/json')
    self.end_headers()
    self.wfile.write(json.dumps(result).encode())

class Node:
  def __init__(self, server_address,storage):
      self.server_address = server_address
      self.channel = Channel.Channel()
      self.storage = storage

  def run(self):
      httpd = HTTPServer(('localhost', 8000), lambda *args, **kwargs: RequestHandler(*args, storage=storage, **kwargs))
      print(f"Starting server on {self.server_address}")
      httpd.serve_forever()

  async def send_response(self, message, client_address):
    try:
      async with websockets.connect(f"ws://{client_address}:8765") as websocket:
        await websocket.send(message)
        await websocket.close()
    except Exception as e:
      print(f"Client is not avaliable:{client_address}--> {e}")

  def callback(self, ch, method, properties, body):
    print(" [x] Processing Response %r" % body)
    response = json.loads(body)
    task_id = response['task_id']
    client_address = response['client_address']
    #get the url of the image from the cloud storage
    url = self.storage.create_signed_url(task_id)
    image=storage.get_image(task_id)
    _, encoded_image = cv2.imencode('.jpg', image)
    encoded_image_as_str = base64.b64encode(encoded_image).decode('utf-8')
    asyncio.run(self.send_response(json.dumps({'task_id': task_id, 'url': url,'image':encoded_image_as_str}), client_address))
    self.channel.ack(method)


  def ResponseHandler(self):
    print("Start consuming responses")
    self.channel.consume('responses', self.callback)

if __name__ == "__main__":
  storage = cloudCredentials.Storage()
  node = Node(('localhost', 8000),storage)
  node.run()
      
    


from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from threading import Thread
import uuid
import Channel
import websockets
import cloudCredentials
import asyncio

class RequestHandler(BaseHTTPRequestHandler):
  def __init__(self, *args, channel, storage, **kwargs):
    self.channel = channel
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
    requests_data = json.loads(post_data)
    results = []
    for request in requests_data:
      task_id = str(uuid.uuid4())
      service_num = request['service_num']
      encoded_image_as_str = request['image']
      self.storage.upload_image(encoded_image_as_str, task_id)
      message = {'client_address': client_address, 'task_id': task_id, 'service_num': service_num}
      self.channel.publish('responses', json.dumps(message))
      results.append(task_id)
    self.send_response(200)
    self.send_header('Content-type', 'application/json')
    self.end_headers()
    self.wfile.write(json.dumps(results).encode())

class Node:
  def __init__(self, server_address,channel,storage):
      self.server_address = server_address
      self.channel = channel
      self.storage = storage

  def run(self):
      httpd = HTTPServer(('localhost', 8000), lambda *args, **kwargs: RequestHandler(*args, channel=channel, storage=storage, **kwargs))
      print(f"Starting server on {self.server_address}")
      httpd.serve_forever()

  async def send_response(self, message, client_address):
    async with websockets.connect(f"ws://{client_address}:8765") as websocket:
      await websocket.send(message)
      await websocket.close()

  def callback(self, ch, method, properties, body):
    print(" [x] Received %r" % body)
    response = json.loads(body)
    task_id = response['task_id']
    client_address = response['client_address']
    #get the url of the image from the cloud storage
    url = self.storage.create_signed_url(task_id)
    asyncio.run(self.send_response(json.dumps({'task_id': task_id, 'url': url}), client_address))
    self.channel.ack(method)


  def ResponseHandler(self):
    print("Start consuming responses")
    channel.consume('responses', self.callback)

if __name__ == "__main__":
  channel=Channel.Channel()
  storage = cloudCredentials.Storage()
  node = Node(('localhost', 8000),channel,storage)
  request_thread = Thread(target=node.run)
  response_thread = Thread(target=node.ResponseHandler)
  request_thread.start()
  response_thread.start()
  
      
    


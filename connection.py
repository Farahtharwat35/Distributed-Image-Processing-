import Channel
import subprocess
import json

class Connection:
  def __init__(self):
   self.channel = Channel.Channel()
   self.channel.consume('requests', self.callback)
   print("Listening for requests")

  def callback(self, ch, method, properties, body):
    print(" [x] Processing Request %r" % body)
    request = json.loads(body)
    task_id = request['task_id']
    service_num = request['service_num']
    client_address = request['client_address']
    status = subprocess.run(["mpiexec","-n","5","python", "processing_node.py", f"{task_id}", f"{service_num}"],check=True)
    if status.returncode == 0:
      self.channel.ack(method)
      self.channel.publish('responses', json.dumps({'task_id': task_id, 'client_address': client_address}))
    else:
      print("Task failed")

if __name__ == "__main__":
    status = subprocess.run(
        [
            "mpiexec",
            "-n",
            "5",
            "python",
            "processing_node.py",
            "30b93014-038c-4ba2-bfb1-a5632cae00c4",
            str(12),
        ]
    )
    if status.returncode == 0:
        print("Task completed successfully")
    else:
        print("Task failed")

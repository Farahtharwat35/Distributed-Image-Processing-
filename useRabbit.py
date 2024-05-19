import Channel
import time
import uuid

task_id = str(uuid.uuid1(clock_seq=2))
print(f"Task ID: {task_id}")

# Create a Channel object
channel = Channel.Channel()
channel.publish('requests', 'Hello World!')
channel.publish('requests', 'Hello World again!')
channel.publish('requests', 'Hello World once more!')

# Define a callback function
def callback(ch, method, properties, body):
    print(f" [x] Received {body}")
    time.sleep(100)
    channel.ack(method)

# Consume messages from the 'requests' queue
channel.consume('requests', callback)
channel.close()


import base64
import threading
import time
import random
import json
import requests
from processing_node import ProcessingNode

IMAGE_FILE_PATH = "testttt.png"

def mock_upload(IMAGE_FILE_PATH, service_num):

    with open(IMAGE_FILE_PATH, 'rb') as f:
        image_bytes = f.read()
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
    request = {'image': image_base64, 'service_num': service_num}
    response = requests.post('http://localhost:8000', data=json.dumps(request),
                             headers={'Content-Type': 'application/json'})
    print(f'server response: {response.text}')

def process_task(task_id, service_num):
    start_time = time.time()
    node = ProcessingNode()
    node.run(task_id=task_id, service_num=service_num)
    end_time = time.time()
    return end_time - start_time


def thread_function(service_num, times_list):
    service_num = random.choice(list(range(1, 5)) + list(range(6, 25)))  # Exclude service number 5
    mock_upload(IMAGE_FILE_PATH, service_num)
    #execution_time = process_task(task_id, service_num)
    #times_list.append(execution_time)


if __name__ == "__main__":
    threads = []
    for _ in range(10000):
        thread = threading.Thread(target=thread_function)
        threads.append(thread)
        thread.start()

    times_list = []
    threads = []

    for t in threads:
        t.join()

    average_time = sum(times_list) / len(times_list)
    min_time = min(times_list)
    max_time = max(times_list)

    print(f"Average Execution Time: {average_time}")
    print(f"Minimum Execution Time: {min_time}")
    print(f"Maximum Execution Time: {max_time}")

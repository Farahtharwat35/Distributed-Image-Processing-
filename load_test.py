import base64
import threading
import time
import random
import json
import requests

IMAGE_FILE_PATH = "testttt.png"

def mock_upload(IMAGE_FILE_PATH, service_num):
    start_time = time.time()
    with open(IMAGE_FILE_PATH, 'rb') as f:
        image_bytes = f.read()
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
    request = {'image': image_base64, 'service_num': service_num}
    response = requests.post('http://localhost:8000', data=json.dumps(request),
                             headers={'Content-Type': 'application/json'})
    print(f'server response: {response.text}')
    end_time = time.time()
    return end_time - start_time


def thread_function(times_list):

    service_num = random.choice(list(range(1, 5)) + list(range(6, 25)))  # Exclude service number 5
    execution_time = mock_upload(IMAGE_FILE_PATH, service_num)
    times_list.append(execution_time)


if __name__ == "__main__":
    threads = []
    times_list = []
    for _ in range(10000):
        thread = threading.Thread(target=thread_function)
        threads.append(thread)
        thread.start()


    for t in threads:
        t.join()

    average_time = sum(times_list) / len(times_list)
    min_time = min(times_list)
    max_time = max(times_list)

    print(f"Average Execution Time: {average_time}")
    print(f"Minimum Execution Time: {min_time}")
    print(f"Maximum Execution Time: {max_time}")

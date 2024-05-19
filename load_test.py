import base64
import threading
import time
import random
import json
import requests
from redis_db import redisDB
from concurrent.futures import ThreadPoolExecutor
from multiprocessing.pool import ThreadPool
import multiprocessing.pool


IMAGE_FILE_PATH = r"code\IQ.jpg"

def mock_upload(IMAGE_FILE_PATH, service_num):
    with open(IMAGE_FILE_PATH, 'rb') as f:
        image_bytes = f.read()
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
    request = {'image': image_base64, 'service_num': service_num}
    response = requests.post('http://34.49.63.6:80/', data=json.dumps(request),
                             headers={'Content-Type': 'application/json'})
    print(f'server response: {response.text}')
    return response.text
    
def redis_pull(task_ID):
    print(f"Pulling task {task_ID} from Redis")
    task_ID=task_ID.strip('"')
    while True:
        task_data = redisDB.pull(task_ID)
        if task_data:
            status = task_data.get("status")
            if "Processed"  in status or "processed" in status :
                break
    print(f"Task {task_ID} is processed")



def thread_function(times_list, i):
    print(f"Thread {i} started")
    service_num = random.choice(list(range(1, 5)) + list(range(8, 21))+list(range(23,25))) # Exclude service number 5
    task_ID = mock_upload(IMAGE_FILE_PATH, service_num)
    start_time = time.time()
    redis_process = multiprocessing.Process(target=redis_pull,args=(task_ID,))
    redis_process.start()
    redis_process.join()
    end_time = time.time()
    execution_time = end_time - start_time
    times_list.append(execution_time)
    print("Thread finished")

    

if __name__ == "__main__":
    threads = []
    times_list = []
    # with ThreadPoolExecutor(max_workers=50) as executor:
    #    futures=[executor.submit(thread_function,times_list)]
    # pool = multiprocessing.pool.ThreadPool()
    # pool = multiprocessing.pool.ThreadPool(processes=4)
    # pool=ThreadPool(processes=50)
    # pool.apply_async(thread_function,(times_list))
    # pool.close()
    # pool.join()  

    args = [(times_list, i) for i in range(1000)]  # Create an iterable of tuples
    pool = multiprocessing.pool.ThreadPool(1000)
    pool.map(lambda p: thread_function(*p), args)

    pool.close()
    pool.join()
    
    average_time = sum(times_list) / len(times_list)
    min_time = min(times_list)
    max_time = max(times_list)

    print(f"Average Execution Time: {average_time}")
    print(f"Minimum Execution Time: {min_time}")
    print(f"Maximum Execution Time: {max_time}")

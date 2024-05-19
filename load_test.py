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
    response = requests.post('http://localhost:8000', data=json.dumps(request),
                             headers={'Content-Type': 'application/json'})
    print(f'server response: {response.text}')
    return response.text
    
def redis_pull(task_ID,start_time,times_list):
    task_data = redisDB.pull(task_ID)
    status = task_data.get("status")
    while status != "Processed" or status != "processed":
        task_data = redisDB.pull(task_ID)
        status = task_data.get("status")
        time.sleep(0.03)
    print(f"Task {task_ID} is processed")
    end_time = time.time()
    execution_time = end_time - start_time
    times_list.append(execution_time)



def thread_function(times_list):
    print("Thread started")
    service_num = random.choice(list(range(1, 5)) + list(range(8, 21))+list(range(23,25))) # Exclude service number 5
    task_ID = mock_upload(IMAGE_FILE_PATH, service_num)
    start_time = time.time()
    redis_thread=threading.Thread(target=redis_pull,args=(task_ID,start_time,times_list))
    redis_thread.start()

    

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

    multiprocessing.pool.ThreadPool(50).map(thread_function,range(50))

    
    # for future in futures:
    #     future.result()
    # average_time = sum(times_list) / len(times_list)
    # min_time = min(times_list)
    # max_time = max(times_list)

    # print(f"Average Execution Time: {average_time}")
    # print(f"Minimum Execution Time: {min_time}")
    # print(f"Maximum Execution Time: {max_time}")

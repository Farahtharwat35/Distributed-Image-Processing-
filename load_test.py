import argparse
import threading
import time
import random

from processing_node import ProcessingNode


def process_task(task_id, service_num):
    start_time = time.time()

    node = ProcessingNode()

    node.run(task_id=task_id, service_num=service_num)

    end_time = time.time()
    return end_time - start_time


def thread_function(task_id, service_num, times_list):
    execution_time = process_task(task_id, service_num)
    times_list.append(execution_time)


if __name__ == "__main__":

    times_list = []

    threads = []
    for i in range(100):
        task_id = random.randint(1, 1000000)
        service_num = random.randint(1, 5)
        thread = threading.Thread(target=process_task, args=(task_id, service_num))
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

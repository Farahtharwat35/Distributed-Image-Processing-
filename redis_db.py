import threading
import redis

class RedisDB:
    _lock = threading.Lock()  # Class-level lock
    def __init__(self):
        self.redis_client = redis.Redis(host='68.219.178.213', port=6379, db=0)
    
    def update_image_status(self, task_id, task_info):
        with RedisDB._lock:
            # Storing task info in Redis hash
            for key, value in task_info.items():
                self.redis_client.hset(task_id, key, value)

    def pull(self, key):
        with RedisDB._lock:
            #print("------------Pulling data from Redis for key:-----------", key)
            # Retrieving task info from Redis hash
            stored_task_data = self.redis_client.hgetall(key)
            #print("----------Stored task data:--------------------", stored_task_data)
            # Decoding byte values to strings
            decoded_task_data = {key.decode(): value.decode() for key, value in stored_task_data.items()}
            #print("----------Decoded task data:--------------------", decoded_task_data)
            return decoded_task_data

    def delete(self, key):
        with RedisDB._lock:
            self.redis_client.delete(key)

# Create an instance of the RedisDB class
redisDB = RedisDB()

# # Example usage:
# # Assuming you have some task info to store
# task_id = "ba21c643-738e-4b78-b2ef-d093323c7a3a"
# task_info = {"status": "completed", "result": "success"}

# # Storing task info
# redisDB.update_image_status(task_id, task_info)

# # Retrieving task info
# task_data = redisDB.pull(task_id)
# print("Task data:", task_data)

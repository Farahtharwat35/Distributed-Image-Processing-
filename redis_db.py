import redis

class RedisDB:
    def __init__(self):
        self.redis_client=redis.Redis(host='68.219.178.213', port=6379, db=0)
        self.redis_client.flushdb()

    def update_image_status(self, task_id,task_info):
        # Storing user data in Redis hash
        self.redis_client.hmset(task_id, task_info)

    def pull(self,key):
        # Retrieving user data from Redis hash
        stored_user_data = self.redis_client.hgetall(key)
        # Converting byte values to strings (Redis returns byte values)
        decoded_user_data = {key.decode(): value.decode() for key, value in stored_user_data.items()}
        return decoded_user_data


redisDB= RedisDB()
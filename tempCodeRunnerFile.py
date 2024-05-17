from redis_db import redisDB
task_id = "ba21c643-738e-4b78-b2ef-d093323c7a3a"
task_info = {"status": "completed", "result": "success"}

# Storing task info
redisDB.update_image_status(task_id, task_info)

# Retrieving task info
task_data = redisDB.pull(task_id)
print("Task data:", task_data)
import threading
import time
from redis_db import redisDB
from Gui import main_window

class NotificationSystem():
    def __init__(self,task_id):
        self.task_id_responsibility = task_id
    def poll_task(self):
        while True:
            try:
                # Pulling data from Redis for the given task_id
                task_data = redisDB.pull(self.task_id_responsibility)
            except Exception as e:
                print(f"Failed to pull data from Redis: {e}")
                return {"status": "failed", "link": None}

            # Checking if task_data is not empty
            if task_data:
                # Retrieving status and link from task data
                status = task_data.get("status")
                link = task_data.get("link")

                # Print status and link
                print("Status:", status)
                print("Link:", link)
                
                # ------------------> CALL WHAT SHOWS RESULT HEREE (TODO) <------------------
                main_window.show_result_window(status)
                
                # Check if the status is "processed"
                if status == "processed":
                    main_window.show_result_window(status, link)
                    return {"status": status, "link": link}

            # Sleep for a short interval before polling again
            time.sleep(0.03)  # Adjust the interval as needed
            return status
    


if __name__ == "__main__":
    notification_system = NotificationSystem()
    poll_thread = notification_system.poll_task()

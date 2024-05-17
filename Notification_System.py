import time
from redis_db import redisDB


class NotificationSystem():
    def __init__(self,task_id):
        self.task_id_responsibility = str(task_id).strip('"')  # Remove double quotes from the task_id
    def poll_task(self,main_window):
        print("Polling task started .....")
        print("Task ID recieved in NS:", self.task_id_responsibility)
        old_status = None
        new_status = None  
        link = None  
        task_data=None
        flag=True
        
        while True:
            try:
                # Pulling data from Redis for the given task_id
                task_data = redisDB.pull(self.task_id_responsibility)
                #print("Task data:", task_data)
            except Exception as e:
                print(f"Failed to pull data from Redis: {e}")
                return {"status": "failed", "link": None}

            # Checking if task_data is not empty
            if task_data:
                # Retrieving status and link from task data
                new_status = task_data.get("status")
                link = task_data.get("link")
                
                if (new_status != old_status):
                    old_status = new_status
                    # Check if the status is "processed"
                    if new_status == "Processed":
                        task_data = redisDB.pull(self.task_id_responsibility)
                        link = task_data.get("link")
                        #----------TODO : CALL HERE THE FUNCTION THAT WILL UPDATE THE STATUS (remove TODO and write instead)---------------------
                        #main_window.show_result_window(status, link)
                        main_window.update_progress_bar(new_status, link)
                        print("FROM NS : --- Task completed successfully")
                        print("FROM NS : --- Link to the processed image:", link)
                        return 
                    else:
                        #----------TODO : CALL HERE THE FUNCTION THAT WILL UPDATE THE STATUS (remove TODO and write instead)---------------------
                        main_window.update_progress_bar(new_status)
                        print(f"FROM NS :--- {new_status} ")
                        # Sleep for a short interval before polling again
                    time.sleep(0.03)
                    
            else:
                if flag:
                    flag=False
                    #----------TODO : CALL HERE THE FUNCTION THAT WILL UPDATE THE STATUS (remove TODO and write instead)---------------------
                    main_window.update_progress_bar("Task Not Processed Yet")
                    print("FROM NS :--- Task Not Processed Yet")
                    # Sleep for a short interval before polling again
                    time.sleep(0.03)
            
# if __name__ == "__main__":
    # notification_system = NotificationSystem()
    # poll_thread = notification_system.poll_task()
    # task_data = redisDB.pull("ba21c643-738e-4b78-b2ef-d093323c7a3a")
    # print("Task data:", task_data)
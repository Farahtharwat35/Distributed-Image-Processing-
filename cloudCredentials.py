from google.cloud import storage
import datetime
import numpy as np
import cv2
import base64

class Storage:
  def __init__(self):
    self.client = storage.Client.from_service_account_json('grand-highway-422418-s8-a8fdf54e267c.json')
    self.bucket = self.client.get_bucket('distributed-image-processing-bucket')

  def upload_image(self, image, task_id):
    img_bytes = base64.b64decode(image)
        # Convert the bytes object into a NumPy array
    nparr = np.frombuffer(img_bytes, np.uint8)
        # Decode the NumPy array into an image
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        # Now you can use cv2.imencode
    _, encoded_image = cv2.imencode('.png', img)
    encoded_image_bytes = encoded_image.tobytes()
    # Upload the image
    blob = self.bucket.blob(task_id)
    blob.upload_from_string(encoded_image_bytes)
    blob.content_disposition = 'attachment'
    blob.patch()

  def create_signed_url(self, task_id):
    blob = self.bucket.blob(task_id)
    url = blob.generate_signed_url(
        version="v4",
        # This URL is valid for 15 minutes
        expiration=datetime.timedelta(days=2),
        # Allow GET requests using this URL.
        method="GET",
    )
    return url
    
  def get_image(self, task_id):
    blob = self.bucket.blob(task_id)
    image_data =blob.download_as_string()
    nparr = np.frombuffer(image_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img


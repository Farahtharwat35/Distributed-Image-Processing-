import pika
import pika.delivery_mode

# RabbitMQ server credentials
username ='salma'
password ='7256203'


# Channel class to publish and consume messages
class Channel:
    def __init__(self, host='13.40.98.49', port='5672'):
        credentials = pika.PlainCredentials(username, password)
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, port=port, credentials=credentials))
        self.channel = self.connection.channel()

    def publish(self, queue, message):
        self.channel.queue_declare(queue=queue, durable=True)
        self.channel.basic_publish(exchange='', routing_key=queue, body=message, properties=pika.BasicProperties(delivery_mode=2))    
   
    def consume(self, queue, callback):
        self.channel.queue_declare(queue=queue, durable=True)
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=False)
        self.channel.start_consuming()

    def ack(self, method):
        self.channel.basic_ack(delivery_tag=method.delivery_tag)

    def close(self):
        self.channel.stop_consuming()
        self.connection.close()


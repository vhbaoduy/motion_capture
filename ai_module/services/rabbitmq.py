import pika
import threading
from typing import Union
import json
import traceback


class RabbitMQConnection():
    def __init__(self,
                 username: str,
                 password: str,
                 host: str,
                 port: int,
                 heartbeat: int = 600,
                 blocked_connection_timeout: int = 300,
                 **kwargs):
        self.credentials = pika.PlainCredentials(username=username,
                                                 password=password)

        self.parameters = pika.ConnectionParameters(host=host,
                                                    port=port,
                                                    credentials=self.credentials,
                                                    heartbeat=heartbeat,
                                                    blocked_connection_timeout=blocked_connection_timeout)
        self.connection = pika.BlockingConnection(parameters=self.parameters)
        self.channel = self.connection.channel()

    def get_connection(self):
        return self.channel

    def check_connection(self):
        try:
            self.connection.process_data_events()
            print("RabbitMQ connection is active.")
            return True

        except pika.exceptions.AMQPError as e:
            print("RabbitMQ connection is closed or failed:", str(e))
            return False

    def close_connection(self):
        self.connection.close()
        
        
        
class RabbitMQSubscriber():
    def __init__(self,
                 username: str,
                 password: str,
                 host: str,
                 port: int,
                 heartbeat: int=600,
                 blocked_connection_timeout: int=300,
                 **kwargs):
        self.configs = {
            "username": username,
            "password": password,
            "host": host,
            "port": port,
            "heartbeat": heartbeat,
            "blocked_connection_timeout": blocked_connection_timeout
        }
        self.rabbitmq_connection = RabbitMQConnection(**self.configs)
        self.rabbitmq_connection.check_connection()
        self.channel_connection = self.rabbitmq_connection.get_connection()
        self.message = ""
        self.thread = None
        self.callback_func = None
    
    
    def callback(self, ch, method, properties, body):
        """
            Wrap callback function with rabiit mq
        """
        # def callback(ch, method, properties, body):
        topic_name = method.routing_key
        message = body.decode("utf-8")
        # if message is not None:
        #     message = message.replace("\'", "\"")
        # else:
        #     message = ""         
        return self.callback_func(topic_name, message)

    
    def subscribe(self,
                  topic: str):
        # Declare queue for dev
        self.channel_connection.queue_declare(queue=topic,
                                              durable=True)
        self.channel_connection.basic_consume(queue=topic,
                                              on_message_callback=self.callback,
                                              auto_ack=True)

        
    def start_consuming(self):
        self.thread = threading.Thread(target=self.channel_connection.start_consuming,
                                       name="[SUBCRIBER] {}".format("Listening messages from services"),
                                       daemon=True)
        
        self.thread.start()

    
    def close_connection(self):
        self.rabbitmq_connection.close_connection()
        

class RabbitMQPublisher():
    def __init__(self,
                 username: str,
                 password: str,
                 host: str,
                 port: int,
                 heartbeat: int=600,
                 blocked_connection_timeout: int=300,
                 **kwargs):
        self.configs = {
            "username": username,
            "password": password,
            "host": host,
            "port": port,
            "heartbeat": heartbeat,
            "blocked_connection_timeout": blocked_connection_timeout
        }
        self.rabbitmq_connection = None
        self.channel_connection = None
        self.init_connect()

    def init_connect(self):
        self.rabbitmq_connection = RabbitMQConnection(**self.configs)
        self.rabbitmq_connection.check_connection()
        self.channel_connection = self.rabbitmq_connection.get_connection()
        self.channel_connection.confirm_delivery()

    def publish(self,
                topic: str,
                message: Union[dict, str],
                **kwargs):
        if isinstance(message, dict):
            message_str = json.dumps(message)
        else:
            message_str = message
        # Set delivery_mode to 2 for persistence
        properties = pika.BasicProperties(
            delivery_mode=pika.DeliveryMode.Persistent)

        try:
            # Declare queue for dev
            self.channel_connection.queue_declare(queue=topic,
                                                  durable=True)
            self.channel_connection.basic_publish(exchange="",
                                                  routing_key=topic,
                                                  body=message_str,
                                                  mandatory=True,
                                                  properties=properties)

            print(f"Sent to topic `{topic}`: \n{message_str}")
        except:
            # if self.rabbitmq_connection.check_connection():
            #     self.channel_connection = self.rabbitmq_connection.get_connection()
            print(f"Error when sending to topic `{topic}`")
            traceback.print_exc()
            del self.rabbitmq_connection
            del self.channel_connection
            self.init_connect()
            print("Reconnected to RabbitMQ service ...")
            self.channel_connection.basic_publish(exchange="",
                                                  routing_key=topic,
                                                  body=message_str,
                                                  mandatory=True,
                                                  properties=properties)

    def close_connection(self):
        self.rabbitmq_connection.close_connection()
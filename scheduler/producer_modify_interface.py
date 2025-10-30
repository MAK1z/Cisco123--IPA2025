import pika
import os
from dotenv import load_dotenv

load_dotenv()

def produce_config_change_job(host, body):
    rabbitmq_user = os.getenv("RABBITMQ_DEFAULT_USER")
    rabbitmq_pass = os.getenv("RABBITMQ_DEFAULT_PASS")
    credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_pass)
    connection = pika.BlockingConnection(pika.ConnectionParameters(host, credentials=credentials))
    channel = connection.channel()

    queue_name = "config_change_jobs"
    channel.queue_declare(queue=queue_name)
    channel.basic_publish(exchange="", routing_key=queue_name, body=body)
    #print(f" [x] Sent job to queue '{queue_name}'")
    connection.close()
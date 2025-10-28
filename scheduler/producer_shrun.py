import pika
import os
from dotenv import load_dotenv

load_dotenv()

def produce_config_job(host, body):
    rabbitmq_user = os.getenv("RABBITMQ_DEFAULT_USER")
    rabbitmq_pass = os.getenv("RABBITMQ_DEFAULT_PASS")

    credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_pass)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host, credentials=credentials)
    )
    channel = connection.channel()
    channel.exchange_declare(exchange="jobs", exchange_type="direct")
    queue_name = "config_jobs"
    channel.queue_declare(queue=queue_name)
    routing_key = "get_running_config"
    channel.queue_bind(
        queue=queue_name, exchange="jobs", routing_key=routing_key
    )
    channel.basic_publish(exchange="jobs", routing_key=routing_key, body=body)
    print(f" [x] Sent job with routing key '{routing_key}'")
    connection.close()

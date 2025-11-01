import pika
import os
import time
from .callback import callback


def consume(host):
    user = os.getenv("RABBITMQ_DEFAULT_USER")
    pwd = os.getenv("RABBITMQ_DEFAULT_PASS")

    for attempt in range(10):
        try:
            print(f"Connecting to RabbitMQ (try {attempt})...")
            creds = pika.PlainCredentials(user, pwd)
            conn = pika.BlockingConnection(
                pika.ConnectionParameters(host, credentials=creds)
            )
            break
        except Exception as e:
            print(f"Failed: {e}")
            time.sleep(5)
    else:
        print("Could not connect after 10 attempts")
        exit(1)

    ch = conn.channel()
    queue_name = "router_jobs"
    ch.queue_declare(queue=queue_name)
    ch.basic_qos(prefetch_count=1)
    ch.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

    print(f"Waiting for messages in queue '{queue_name}'.")
    ch.start_consuming()

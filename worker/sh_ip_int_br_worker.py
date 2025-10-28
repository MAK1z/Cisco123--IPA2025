import os
from dotenv import load_dotenv
from sh_ip_int_br_module.consumer import consume

load_dotenv()
print("Starting Interface Worker...")
consume(os.getenv("RABBITMQ_HOST"))
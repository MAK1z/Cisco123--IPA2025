import os
from dotenv import load_dotenv
from sh_ip_int_br_module.consumer import consume

load_dotenv()
consume(os.getenv("RABBITMQ_HOST"))
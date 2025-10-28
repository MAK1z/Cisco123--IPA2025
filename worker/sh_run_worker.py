import os
from dotenv import load_dotenv
from sh_run_module.consumer import consume

load_dotenv()
print("Starting Configuration Worker...")
consume(os.getenv("RABBITMQ_HOST"))
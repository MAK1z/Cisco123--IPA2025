import os
from dotenv import load_dotenv

from modify_interface_module.consumer import consume

load_dotenv()
print("Starting Config-Change Worker...")
consume(os.getenv("RABBITMQ_HOST"))
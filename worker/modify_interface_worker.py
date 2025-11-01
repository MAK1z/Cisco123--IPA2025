import os
from dotenv import load_dotenv

from modify_interface_module.consumer import consume

load_dotenv()
consume(os.getenv("RABBITMQ_HOST"))
import os
from dotenv import load_dotenv
from sh_run_module.consumer import consume

load_dotenv()
consume(os.getenv("RABBITMQ_HOST"))

from pkg_resources import declare_namespace
from logging import basicConfig
from dotenv import load_dotenv
import os

declare_namespace("shtl_ink_api")
load_dotenv()
basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))

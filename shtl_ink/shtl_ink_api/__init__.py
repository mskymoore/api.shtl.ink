from pkg_resources import declare_namespace
from logging import basicConfig, INFO
from dotenv import load_dotenv

basicConfig(level=INFO)
declare_namespace("shtl_ink_api")
load_dotenv()

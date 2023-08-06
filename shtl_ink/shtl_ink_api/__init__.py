from pkg_resources import declare_namespace
from logging import basicConfig, INFO, DEBUG
from dotenv import load_dotenv

basicConfig(level=DEBUG)
declare_namespace("shtl_ink_api")
load_dotenv()

from pkg_resources import declare_namespace
from supertokens_python import init, InputAppInfo, SupertokensConfig
from supertokens_python.recipe import emailpassword, session
from .config import app_name, base_url, frontend_base_url, cookie_domain
from .config import supertokens_conn_uri, supertokens_api_key

declare_namespace("shtl_ink_api")


init(
    app_info=InputAppInfo(
        app_name=app_name,
        api_domain=base_url,
        website_domain=frontend_base_url,
        api_base_path="/auth",
        website_base_path="/auth"
    ),
    supertokens_config=SupertokensConfig(
        # try.supertokens.com is for demo purposes. Replace this with the address of your core instance (sign up on supertokens.com), or self host a core.
        # connection_uri="https://b60ca471ef4011ec8cdeb9c2656574d2-ap-southeast-1.aws.supertokens.io:3570",
        # api_key="TGY0bEa5YQe0k1kUqm=sKPre70GruS"
        connection_uri=supertokens_conn_uri,
        api_key=supertokens_api_key
    ),
    framework='fastapi',
    recipe_list=[
        session.init(cookie_domain=cookie_domain),  # initializes session features
        emailpassword.init()
    ],
    mode='asgi'  # use wsgi if you are running using gunicorn
)

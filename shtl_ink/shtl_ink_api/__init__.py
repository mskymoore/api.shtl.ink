from pkg_resources import declare_namespace
from supertokens_python import init, InputAppInfo, SupertokensConfig
from supertokens_python.recipe import emailpassword, session
declare_namespace("shtl_ink_api")


init(
    app_info=InputAppInfo(
        app_name="shtl.ink",
        api_domain="http://localapi.shtl.ink:8000",
        website_domain="http://shtl.ink:3000",
        api_base_path="/auth",
        website_base_path="/auth"
    ),
    supertokens_config=SupertokensConfig(
        # try.supertokens.com is for demo purposes. Replace this with the address of your core instance (sign up on supertokens.com), or self host a core.
        connection_uri="https://b60ca471ef4011ec8cdeb9c2656574d2-ap-southeast-1.aws.supertokens.io:3570",
        api_key="TGY0bEa5YQe0k1kUqm=sKPre70GruS"
    ),
    framework='fastapi',
    recipe_list=[
        session.init(cookie_domain=".shtl.ink"), # initializes session features
        emailpassword.init()
    ],
    mode='asgi' # use wsgi if you are running using gunicorn
)
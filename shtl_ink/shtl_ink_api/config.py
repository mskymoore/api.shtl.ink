import os

if 'BASE_URL' in os.environ and 'ROOT_REDIRECT_URL' in os.environ:
    base_url = os.environ['BASE_URL']
    root_redirect_url = os.environ['ROOT_REDIRECT_URL']
else:
    base_url = "http://localhost:8000"
    root_redirect_url = "http://localhost:3000"
    print('URL environment variables not set, falling back to demo mode')

if 'DB_HOST' in os.environ:
    db_host = os.environ['DB_HOST']
    db_name = os.environ['DB_NAME']
    db_user = os.environ['DB_USER']
    db_pass = os.environ['DB_PASS']
else:
    db_host, db_name, db_user, db_pass = None, None, None, None
    print('DB environment variables not set, falling back to sqlite')

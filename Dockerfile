FROM python:3.9-slim as shtl_ink
ENV PYTHONUNBUFFERED=1
RUN mkdir -p /opt/url-api/shtl_ink/shtl_ink_api
WORKDIR /opt/url-api/
COPY requirements.txt /opt/url-api/requirements.txt
RUN pip install -r requirements.txt
COPY shtl_ink/shtl_ink_api/* /opt/url-api/shtl_ink/shtl_ink_api/
COPY setup.py /opt/url-api/setup.py
COPY README.md /opt/url-api/README.md
RUN python setup.py install
EXPOSE 8000
ENTRYPOINT [ "uvicorn","--host", "0.0.0.0", "--port", "8000",  "shtl_ink.shtl_ink_api.app:app" ]

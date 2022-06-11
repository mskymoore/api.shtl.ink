FROM python:3.9 as shtl_ink
ENV PYTHONUNBUFFERED=1
RUN mkdir -p /opt/url-api/src
COPY ./src/* /opt/url-api/
COPY requirements.txt /opt/url-api/
WORKDIR /opt/url-api/src
RUN pip install -r ../requirements.txt
RUN python setup.py install
EXPOSE 8000
ENTRYPOINT [ "uvicorn","shtl_ink_api.app:app" ]

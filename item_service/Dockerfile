FROM ubuntu:20.04

WORKDIR /salesync/item_service

COPY . .
COPY ./models ./models

RUN apt-get update -y

RUN apt-get install -y python3
RUN apt-get install -y python3-pip

RUN pip install -r requirements.txt

ENV FLASK_APP=app
ENV FLASK_DEBUG=true
ENV APP_CONFIG_FILE=/item_service/config/development.py
ENV DB_USER=postgres
ENV DB_PASSWORD=password
ENV DB_HOST=dev-salesync.cunzt8irsgv8.ap-northeast-2.rds.amazonaws.com
ENV DB_PORT=5432
ENV DB_NAME=salesync
ENV SECRET_KEY=b'\xa2\xa4A\x84\x9f\x86\x82\x05G\xe2\xb2eD\x18p\x01'
ENV JWT_SECRET_KEY=b'\xb4\xc4\x8b\xfbU\xc1\x8d\x1d\x82\xca\x08^\x0bO\x05I'

RUN flask db init
RUN flask db migrate
RUN flask db update

CMD [ "python", "-m", "flask", "run", "--host=0.0.0.0" ]
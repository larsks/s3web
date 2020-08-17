FROM python:3.8

RUN apt update; apt -y install uwsgi uwsgi-plugin-python3
RUN pip install pipenv

COPY . /src
WORKDIR /src
RUN pipenv lock -r > requirements.txt; pip install -r requirements.txt
RUN pip install .
WORKDIR /

CMD uwsgi --http-socket 0.0.0.0:8080  --plugin python3 --mount /=s3web.app:app \
	--pythonpath /usr/local/lib/python3.8/site-packages

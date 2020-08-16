FROM python:3.8

RUN apt update; apt -y install uwsgi uwsgi-plugin-python3
RUN useradd -c "s3web user" s3web
RUN pip install pipenv

COPY . /src
WORKDIR /src

RUN pipenv install

CMD uwsgi --http-socket 0.0.0.0:8080  --plugin python3 -H $(pipenv --venv) --mount /=s3web.app:app

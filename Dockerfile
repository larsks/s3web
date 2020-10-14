FROM python:3.8

RUN pip install pipenv

COPY . /src
WORKDIR /src
RUN pipenv lock -r > requirements.txt; pip install -r requirements.txt
RUN pip install .
WORKDIR /

COPY docker-start.sh /docker-start.sh
CMD ["sh", "/docker-start.sh"]

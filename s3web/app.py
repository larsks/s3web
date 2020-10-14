import boto3
import logging
import os

from urllib.parse import urlunparse

from botocore.client import Config
from botocore.exceptions import ClientError
from flask import Flask
from flask import render_template

default_region = 'us-east-1'


class S3Proxy:
    def __init__(self, endpoint, access_endpoint, access_key, secret_key,
                 bucket_name, region=None):
        self.access_key = access_key
        self.secret_key = secret_key
        self.endpoint = endpoint
        self.bucket_name = bucket_name

        self.region = region if region else default_region

        self.access_endpoint = access_endpoint if access_endpoint else endpoint

        self.init_s3()

    def init_s3(self):
        self.s3_args = s3_args = dict(
            endpoint_url=self.endpoint,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            config=Config(signature_version='s3v4'),
            region_name=self.region,
        )

        self.s3 = boto3.client('s3', **s3_args)

    def images(self):
        res = self.s3.list_objects(Bucket=self.bucket_name)

        for obj in res.get('Contents', []):
            try:
                tags = self.s3.get_object_tagging(Bucket=self.bucket_name,
                                                  Key=obj['Key'])
            except ClientError:
                tags = {}

            obj['url'] = self.url_for(obj)
            obj['access_url'] = self.access_url_for(obj)
            obj['tags'] = {}

            for tag in tags.get('TagSet', []):
                obj['tags'][tag['Key']] = tag['Value']

            yield(obj)

    def url_for(self, obj):
        return f'{self.endpoint}/{self.bucket_name}/{obj["Key"]}'

    def access_url_for(self, obj):
        return f'{self.access_endpoint}/{self.bucket_name}/{obj["Key"]}'


app = Flask(__name__)

if (aws_access_key_id := os.environ.get('AWS_ACCESS_KEY_ID')) is None:
    raise ValueError('missing AWS_SECRET_ACCESS_KEY')

if (aws_secret_access_key := os.environ.get('AWS_SECRET_ACCESS_KEY')) is None:
    raise ValueError('missing AWS_SECRET_ACCESS_KEY')

if (bucket_name := os.environ.get('BUCKET_NAME')) is None:
    raise ValueError('missing BUCKET_NAME')

if (bucket_endpoint := os.environ.get('BUCKET_ENDPOINT')) is None:

    if (bucket_host := os.environ.get('BUCKET_HOST')) is None:
        raise ValueError('BUCKET_HOST is undefined')

    bucket_port = os.environ.get('BUCKET_PORT', '443')

    if (bucket_scheme := os.environ.get('BUCKET_SCHEME')) is None:
        if bucket_port == '443':
            bucket_scheme = 'https'
        elif bucket_port == '80':
            bucket_scheme = 'http'
        else:
            raise ValueError('unable to determine schema from port number')

    bucket_endpoint = urlunparse([
        bucket_scheme,
        f'{bucket_host}:{bucket_port}',
        '/',
        None,
        None,
        None
    ])

bucket_access_endpoint = os.environ.get('BUCKET_ACCESS_ENDPOINT')

app.logger.warning('using s3 endpoint: %s', bucket_endpoint)
if bucket_access_endpoint:
    app.logger.warning('using access endpoint: %s', bucket_access_endpoint)
app.logger.warning('using bucket: %s', bucket_name)

api = S3Proxy(
    bucket_endpoint,
    bucket_access_endpoint,
    aws_access_key_id,
    aws_secret_access_key,
    bucket_name,
)


@app.route('/')
def index():
    images = api.images()
    return render_template('images.html', images=images)


if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

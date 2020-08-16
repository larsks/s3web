import boto3
import logging
import os

from botocore.client import Config
from flask import Flask
from flask import render_template

LOG = logging.getLogger(__name__)
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

        self.s3 = boto3.resource('s3', **s3_args)
        self.bucket = self.s3.Bucket(self.bucket_name)

    def images(self):
        for obj in self.bucket.objects.all():
            obj.url = self.url_for(obj)
            obj.access_url = self.access_url_for(obj)
            yield(obj)

    def url_for(self, obj):
        return f'{self.endpoint}/{self.bucket.name}/{obj.key}'

    def access_url_for(self, obj):
        return f'{self.access_endpoint}/{self.bucket.name}/{obj.key}'


app = Flask(__name__)
api = S3Proxy(
    os.environ.get('S3_ENDPOINT'),
    os.environ.get('S3_ACCESS_ENDPOINT'),
    os.environ.get('S3_ACCESS_KEY'),
    os.environ.get('S3_SECRET_KEY'),
    os.environ.get('S3_BUCKET'),
)


@app.route('/')
def index():
    images = api.images()
    return render_template('images.html', images=images)

# s3web

Builds a web page with links to objects in an S3 bucket. Optionally
replaces the S3 endpoint you're using for API access with a different
URL.

## Configuration

`s3web` requires the following environment variables:

- `S3_ENDPOINT`
- `S3_ACCESS_KEY`
- `S3_SECRET_KEY`
- `S3_BUCKET`

Optionally, to replace `S3_ENDPOINT` with a different url in generated urls:

- `S3_ACCESS_ENDPOINT`

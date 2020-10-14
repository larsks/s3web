#!/bin/sh

: ${GUNICORN_LOG_LEVEL:=INFO}

exec gunicorn -b 0.0.0.0:8080 \
	--log-level ${GUNICORN_LOG_LEVEL} \
	--access-logfile /dev/stdout \
	s3web.app:app

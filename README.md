[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![MIT License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

# gcs-s3-transfer-service

A simple service to upload files from Google Cloud Storage (GCS) to AWS S3.

The app entrypoint is in [main.py](main.py). Per [App Engine docs](https://cloud.google.com/appengine/docs/standard/python3/runtime#application_startup) putting the app entrypoint there allows you to avoid needing to specify entrypoint manually in the `app.yaml` and will automatically use `gunicorn` as the server without needing to add it to the `requirements.txt`.

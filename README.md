[![CircleCI](https://circleci.com/gh/ENCODE-DCC/gcs-s3-transfer-service.svg?style=svg)](https://circleci.com/gh/ENCODE-DCC/gcs-s3-transfer-service)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![MIT License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

# gcs-s3-transfer-service

A simple Google App Engine service to upload files from Google Cloud Storage (GCS) to AWS S3. It is comprised of a single endpoint `/upload` that accepts `POST` requests with `Content-Type: application/json` headers in the form specified by [the schema](gcs_s3_transfer_service/schemas/upload.json). S3 upload credentials must be passed in the request body, for this reason you should use temporary credentials such as those issued by [AWS STS](https://docs.aws.amazon.com/STS/latest/APIReference/welcome.html). The service must have `storage.objects.get` permission to the GCS objects you are attempting to upload.

The app entrypoint is in [main.py](main.py). Per [App Engine docs](https://cloud.google.com/appengine/docs/standard/python3/runtime#application_startup) putting the app entrypoint there allows you to avoid needing to specify entrypoint manually in the `app.yaml` and will automatically use `gunicorn` as the server without needing to add it to the `requirements.txt`.


## Deployment to App Engine

From the root of the repo, run the following from the root of this repo:

```bash
gcloud app deploy
```

To deploy the `queue.yaml`, run the following from the root of this repo:

```bash
gcloud app deploy queue.yaml
```

It is also recommended to enable logging for the queue via the following:

```
gcloud tasks queues update gcs-s3-transfer --log-sampling-ratio=1.0
```

This will enable you to trigger uploads via a Cloud Tasks queue, instead of raw POSTs to the App Engine endpoint.

*WARNING*: Deploying like this will disable existing queues not specified in the `queue.yaml`

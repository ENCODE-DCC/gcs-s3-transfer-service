import time
from http import HTTPStatus
from typing import Any, Dict, Tuple, Union

import boto3
from flask import request
from google.cloud import storage
from jsonschema import validate
from jsonschema.exceptions import ValidationError

from gcs_s3_transfer_service import app
from gcs_s3_transfer_service.gcs import GcsBlob
from gcs_s3_transfer_service.schemas.load import load_schema


@app.errorhandler(HTTPStatus.NOT_FOUND)
def page_not_found(error) -> Tuple[Dict[str, Dict[str, str]], HTTPStatus]:
    """
    Make a nice JSON response on 404
    """
    return (
        {"error": {"message": "Page not found", "reason": str(error)}},
        HTTPStatus.NOT_FOUND,
    )


@app.route("/upload", methods=["POST"])
def upload() -> Tuple[Dict[str, Union[str, Dict[str, str]]], HTTPStatus]:
    """
    At a high level, uploads the file from GCS to S3 by streaming bytes. As the S3
    client reads chunks they are lazily fetched from GCS.

    There are several possible failure modes here that will return non-200 status codes:
        1. The payload was invalid under the schema
        2. The GCS client could not be initialized due to permissions error
        3. The client does not have permissions to access the bucket specified
           in the payload
        4. `s3.upload_fileobj()` failed

    In more details, obtains STS credentials to upload to the portal file specified
    by `encode_file`, creates a S3 client, and uploads the file corresponding to
    `gs_file` (potentially as multipart). For this to work, the blob must be object that
    has a file-like `read` method. For more details see the `boto3` docs:
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.upload_fileobj

    Extensive testing revealed that for boto3 the default transfer config performed
    satisfactorily, see PIP-745
    """
    schema = load_schema("upload")
    try:
        validate(request.json, schema=schema)
    except ValidationError as validation_error:
        return (
            {
                "error": {
                    "message": "Failed to validate posted JSON.",
                    "reason": validation_error.message,
                }
            },
            HTTPStatus.UNPROCESSABLE_ENTITY,
        )

    s3 = _get_s3_client(request.json)
    s3_bucket = request.json["aws_s3_object"]["bucket"]
    s3_key = request.json["aws_s3_object"]["key"]
    s3_uri = f"s3://{s3_bucket}/{s3_key}"

    try:
        gcs_client = _get_gcs_client()
    except Exception as e:
        app.logger.exception("Missing GCP credentials on server")
        return (
            {
                "error": {
                    "message": "Server is missing GCP credentials",
                    "reason": str(e),
                }
            },
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )

    bucket_from_request = request.json["gcs_blob"]["bucket"]
    try:
        bucket = gcs_client.get_bucket(bucket_from_request)
    except Exception as e:
        app.logger.exception("Could not access bucket %s", bucket_from_request)
        return (
            {
                "error": {
                    "message": f"Could not access bucket {bucket_from_request}",
                    "reason": str(e),
                }
            },
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )

    gcs_blob = GcsBlob(request.json["gcs_blob"]["name"], bucket)
    gcs_uri = f"gs://{gcs_blob.bucket}/{gcs_blob.name}"

    app.logger.info("Uploading file %s to %s", gcs_uri, s3_uri)
    try:
        start = time.perf_counter()
        s3.upload_fileobj(
            gcs_blob, s3_bucket, s3_key,
        )
    except Exception as e:
        app.logger.exception("Failed to upload file %s", gcs_uri)
        return (
            {
                "error": {
                    "message": f"Failed to upload {gcs_uri} to {s3_uri}",
                    "reason": str(e),
                }
            },
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )
    else:
        end = time.perf_counter()
        # Need to reload to get blob size
        gcs_blob.reload()
        elapsed = end - start
        blob_size_mb = gcs_blob.size / 1e6
        upload_speed_mb_s = blob_size_mb / elapsed
        message = f"Successfully uploaded file {gcs_uri} ({blob_size_mb} MB) in {elapsed} seconds, {upload_speed_mb_s} MB/s"
        app.logger.info(message)
        return (
            {"message": message},
            HTTPStatus.OK,
        )


def _get_s3_client(request_json: Dict[str, Any]):
    """
    Will not fail if the passed credentials are invalid.

    Unfortunately it is impossible to provide type annotations for the return value
    since the actual class is created dynamically without using something like
    `boto3-stubs`: https://pypi.org/project/boto3-stubs
    """
    s3 = boto3.client(
        "s3",
        aws_access_key_id=request.json["aws_credentials"]["access_key"],
        aws_secret_access_key=request.json["aws_credentials"]["secret_key"],
        aws_session_token=request.json["aws_credentials"]["session_token"],
    )
    return s3


def _get_gcs_client() -> storage.Client:
    """
    Can potentially fail if credentials are available via file or environment variables.
    """
    return storage.Client()

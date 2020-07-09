from http import HTTPStatus
from typing import Any, Dict

import boto3
from flask import request
from google.cloud import storage
from jsonschema import validate
from jsonschema.exceptions import ValidationError

from gcs_s3_transfer_service import app
from gcs_s3_transfer_service.gcs import GcsBlob
from gcs_s3_transfer_service.schemas.load import load_schema


@app.route("/upload", methods=["POST"])
def upload():
    """
    At a high level, uploads the file from GCS to S3 by streaming bytes. As the S3
    client reads chunks they are lazily fetched from GCS.

    In more details, obtains STS credentials to upload to the portal file specified
    by `encode_file`, creates a S3 client, and uploads the file corresponding to
    `gs_file` (potentially as multipart). For this to work, the blob must be object that
    has a file-like `read` method. For more details see the `boto3` docs:
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.upload_fileobj

    Extensive testing revealed that for the boto3 default transfer config performed
    satisfactorily, see PIP-745
    """
    schema = load_schema("upload")
    try:
        validate(request.json, schema=schema)
    except ValidationError as validation_error:
        return (
            {
                "message": "failed to process request",
                "reason": validation_error.message,
            },
            HTTPStatus.UNPROCESSABLE_ENTITY,
        )

    s3 = _get_s3_client(request.json)
    s3_bucket = request.json["aws_s3_object"]["bucket"]
    s3_key = request.json["aws_s3_object"]["key"]
    s3_uri = f"s3://{s3_bucket}/{s3_key}"

    gcs_client = _get_gcs_client()
    bucket = gcs_client.get_bucket(request.json["gcs_uri"]["bucket"])
    gcs_blob = GcsBlob(request.json["gcs_uri"]["path"], bucket)
    gcs_uri = f"gs://{gcs_blob.bucket}/{gcs_blob.name}"

    app.logger.info("Uploading file %s to %s", gcs_uri, s3_uri)
    s3.upload_fileobj(
        gcs_blob, s3_bucket, s3_key,
    )
    app.logger.info("Finished uploading file %s", gcs_uri)
    return ({"message": f"Successfully uploaded {gcs_uri} to {s3_uri}"}, HTTPStatus.OK)


def _get_s3_client(request_json: Dict[str, Any]):
    """
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
    return storage.Client()

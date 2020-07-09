import boto3
from flask import request
from google.cloud import storage

from gcs_s3_transfer_service import app
from gcs_s3_transfer_service.gcs import GcsBlob


@app.route("/")
def hello() -> str:
    return "Hello World!"


@app.route("/upload", methods=["POST"])
def upload():
    """
    At a high level, uploads the file from GCS to S3 by streaming bytes. As the s3
    client reads chunks they are lazily fetched from GCS.

    In more details, obtains STS credentials to upload to the portal file specified
    by `encode_file`, creates a s3 client, and uploads the file corresponding to
    `gs_file` (potentially as multipart). For this to work, the blob acquired by
    `self.backend.blob_from_filename` must return an object that has a file-like
    `read` method. For more details see the `boto3` docs:
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.upload_fileobj

    Extensive testing revealed that for the boto3 default transfer config performed
    satisfactorily, see PIP-745
    """
    s3 = boto3.client(
        "s3",
        aws_access_key_id=request.json["aws_credentials"]["access_key"],
        aws_secret_access_key=request.json["aws_credentials"]["secret_key"],
        aws_session_token=request.json["aws_credentials"]["session_token"],
    )
    s3_bucket = request.json["aws_s3_object"]["bucket"]
    s3_key = request.json["aws_s3_object"]["key"]
    s3_uri = f"s3://{s3_bucket}/{s3_key}"

    gcs_client = storage.Client()
    bucket = gcs_client.get_bucket(request.json["gcs_uri"]["bucket"])
    gcs_blob = GcsBlob(request.json["gcs_uri"]["path"], bucket)
    gcs_uri = f"gs://{gcs_blob.bucket}/{gcs_blob.name}"

    app.logger.info("Uploading file %s to %s", gcs_uri, s3_uri)
    s3.upload_fileobj(
        gcs_blob, s3_bucket, s3_key,
    )
    app.logger.info("Finished uploading file %s", gcs_uri)

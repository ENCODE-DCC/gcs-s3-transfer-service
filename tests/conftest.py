import pytest

from gcs_s3_transfer_service import app


@pytest.fixture(scope="session")
def client():
    app.testing = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def valid_upload_post_body():
    data = {
        "aws_credentials": {
            "aws_access_key_id": "foo",
            "aws_secret_access_key": "bar",
            "aws_session_token": "baz",
        },
        "aws_s3_object": {"bucket": "s3", "key": "object"},
        "gcs_blob": {"bucket": "cool", "name": "object"},
    }
    return data

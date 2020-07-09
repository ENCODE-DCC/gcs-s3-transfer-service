import pytest
from jsonschema import validate
from jsonschema.exceptions import ValidationError

from gcs_s3_transfer_service.schemas.load import load_schema


@pytest.fixture
def schema():
    return load_schema("upload")


def test_upload_schema_valid(schema):
    data = {
        "aws_credentials": {
            "aws_access_key_id": "foo",
            "aws_secret_key": "bar",
            "aws_session_token": "baz",
        },
        "aws_s3_object": {"bucket": "s3", "key": "object"},
        "gcs_blob": {"bucket": "cool", "name": "object"},
    }
    validate(data, schema=schema)


@pytest.mark.parametrize(
    "data",
    [
        {
            "gcs_blob": {"bucket": "foo", "name": "bar"},
            "aws_credentials": {"aws_access_key_id": "bar"},
            "aws_s3_object": {"bucket": "nice", "key": "object"},
        },
        {
            "gcs_blob": {"bucket": "foo"},
            "aws_credentials": {
                "aws_access_key_id": "bar",
                "aws_secret_key": "bar",
                "aws_session_token": "baz",
            },
            "aws_s3_object": {"bucket": "nice", "key": "object"},
        },
        {
            "gcs_blob": {"bucket": "foo", "name": "blob"},
            "aws_credentials": {
                "aws_access_key_id": "bar",
                "aws_secret_key": "bar",
                "aws_session_token": "baz",
            },
            "aws_s3_object": {"bucket": "nice"},
        },
    ],
)
def test_upload_schema_invalid(schema, data):
    with pytest.raises(ValidationError):
        validate(data, schema=schema)

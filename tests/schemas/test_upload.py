import json
from pathlib import Path

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
        "gcs_uri": "gs://cool-bucket/file",
    }
    validate(data, schema=schema)


@pytest.mark.parametrize(
    "data",
    [
        ({"gcs_uri": "gs://foo/bar", "aws_credentials": {"aws_access_key_id": "bar"}},),
        (
            {
                "gcs_uri": "gs://foo/",
                "aws_credentials": {
                    "aws_access_key_id": "bar",
                    "aws_secret_key": "bar",
                    "aws_session_token": "baz",
                },
            },
        ),
    ],
)
def test_upload_schema_invalid(schema, data):
    with pytest.raises(ValidationError):
        validate(data, schema=schema)

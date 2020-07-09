import pytest

from gcs_s3_transfer_service.gcs import GcsBlob


def stub_download_as_string(start=None, end=None, data=b"abc123"):
    if start is None:
        start = 0
    if end is None or end + 1 >= len(data):
        end = len(data) - 1
    if start > end:
        return data
    return data[start : end + 1]


@pytest.mark.parametrize(
    "start,end,expected",
    [(None, None, b"abc123"), (None, 3, b"abc1"), (3, None, b"123"), (1, 2, b"bc")],
)
def test_stub_download_as_string(start, end, expected):
    """
    In this case, need to test the tests to make sure the implementation of
    download_as_string functions the same as Google cloud, reads are 0-indexed and
    inclusive of endpoints.
    """
    result = stub_download_as_string(start, end)
    assert result == expected


def test_gcs_blob_read(mocker):
    """
    Mocking super() is hard, so we just mock out the whole __init__ and set the values
    that we need, see https://github.com/pytest-dev/pytest-mock/issues/110
    """
    mocker.patch.object(GcsBlob, "__init__", return_value=None)
    blob = GcsBlob("key", "bucket")
    mocker.patch.object(blob, "download_as_string", stub_download_as_string)
    blob.pos = 0
    blob._properties = {"size": 6}
    assert blob.read(3) == b"abc"
    assert blob.read(3) == b"123"
    assert blob.read(3) == b""


def test_gcs_blob_read_none(mocker):
    """
    Mocking super() is hard, so we just mock out the whole __init__ and set the values
    that we need, see https://github.com/pytest-dev/pytest-mock/issues/110
    """
    mocker.patch.object(GcsBlob, "__init__", return_value=None)
    blob = GcsBlob("key", "bucket")
    mocker.patch.object(blob, "download_as_string", stub_download_as_string)
    blob.pos = 0
    blob._properties = {"size": 6}
    assert blob.read() == b"abc123"
    assert blob.read() == b""


def test_gcs_blob_read_amount_then_none(mocker):
    """
    Mocking super() is hard, so we just mock out the whole __init__ and set the values
    that we need, see https://github.com/pytest-dev/pytest-mock/issues/110
    """
    mocker.patch.object(GcsBlob, "__init__", return_value=None)
    blob = GcsBlob("key", "bucket")
    mocker.patch.object(blob, "download_as_string", stub_download_as_string)
    blob.pos = 0
    blob._properties = {"size": 6}
    assert blob.read(3) == b"abc"
    assert blob.read() == b"123"
    assert blob.read() == b""

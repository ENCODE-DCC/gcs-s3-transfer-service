from typing import Optional

from google.cloud import storage


class GcsBlob(storage.blob.Blob):
    """
    Wrapper around GCS blob class to provide a read() interface for in-memory transfer
    to s3. The interface here has been adapted from `accession.backends.GcsBlob`, mostly
    via removal of methods unneeded for the service.
    """

    def __init__(self, *args, **kwargs) -> None:
        """
        Initializes self.pos to 0 for keeping track of number of bytes read from file.
        `args` and `kwargs` are passed to parent class `google.cloud.storage.blob.Blob`
        """
        self.pos = 0
        super().__init__(*args, **kwargs)

    def read(self, num_bytes: Optional[int] = None) -> bytes:
        """
        Method to enable using boto3 for uploading files without downloading to disk.
        `Blob.download_as_string()` takes `start` and `end` kwargs to specify a byte
        range. These are 0-indexed and inclusive of endpoints. If the position is
        greater than or equal to the size of the object then we treat that as EOF and
        return an empty byte string `b''`. As per Python convention, when read() is
        called with no read size then the remainder of the file is returned.

        See https://googleapis.dev/python/storage/latest/blobs.html#google.cloud.storage.blob.Blob.download_as_string
        and https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.upload_fileobj
        """
        if self.pos >= self.size:
            read_bytes = b""
        else:
            if num_bytes is None:
                read_bytes = self.download_as_string(start=self.pos)
                self.pos += len(read_bytes)
            else:
                read_bytes = self.download_as_string(
                    start=self.pos, end=self.pos + num_bytes - 1
                )
                self.pos += num_bytes
        return read_bytes

# Per Flask docs you should put the app in the __init__.py then import it and register
# views in other modules
# https://flask.palletsprojects.com/en/1.1.x/patterns/packages/
from flask import Flask

app = Flask(__name__)
# Must import after app is created!
import gcs_s3_transfer_service.views  # noqa: F401, E402

__title__ = "gcs-s3-transfer-service"
__version__ = "0.1.0"
__description__ = (
    "Flask microservice to upload files from Google Cloud Storage to AWS S3"
)
__url__ = "https://github.com/ENCODE-DCC/gcs-s3-transfer-service"
__uri__ = __url__
__author__ = "Paul Sud"
__email__ = "encode-help@lists.stanford.edu"
__license__ = "MIT"
__copyright__ = "Copyright (c) 2020 ENCODE DCC"

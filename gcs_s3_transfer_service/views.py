from gcs_s3_transfer_service import app


@app.route("/")
def hello() -> str:
    """Return a friendly HTTP greeting."""
    return "Hello World!"

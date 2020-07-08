from gcs_s3_transfer_service import app


def test_index():
    app.testing = True
    client = app.test_client()

    r = client.get("/")
    assert r.status_code == 200
    assert "Hello World" in r.get_data(as_text=True)

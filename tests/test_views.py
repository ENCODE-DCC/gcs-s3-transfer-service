from http import HTTPStatus


def test_index(client):
    response = client.get("/")
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_upload_invalid_data_returns_unprocessable_entity(client):
    response = client.post("/upload", data={})
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.get_json()["reason"]


def test_upload(mocker, client, valid_upload_post_body):
    mocker.patch("gcs_s3_transfer_service.views._get_gcs_client")
    mocker.patch("gcs_s3_transfer_service.views._get_s3_client")
    response = client.post("/upload", data=valid_upload_post_body)
    assert response.status_code == HTTPStatus.OK

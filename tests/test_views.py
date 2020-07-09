from http import HTTPStatus


def test_not_found(client):
    response = client.get("/")
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.get_json()["error"]["message"]


def test_upload_invalid_data_returns_unprocessable_entity(client):
    response = client.post("/upload", json={"invalid": "data"})
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.get_json()["error"]["reason"]


def test_upload_returns_internal_server_error_on_failure_to_initialize_gcs_client(
    mocker, client, valid_upload_post_body
):
    mocker.patch(
        "gcs_s3_transfer_service.views._get_gcs_client", side_effect=Exception("foo")
    )
    mocker.patch("gcs_s3_transfer_service.views._get_s3_client")
    response = client.post("/upload", json=valid_upload_post_body)
    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert response.get_json()["error"]["reason"]


def test_upload_returns_internal_server_error_on_failure_to_access_bucket(
    mocker, client, valid_upload_post_body
):
    mock_client = mocker.MagicMock()
    mock_client.get_bucket = mocker.MagicMock(side_effect=Exception("foo"))
    mocker.patch(
        "gcs_s3_transfer_service.views._get_gcs_client", return_value=mock_client
    )
    mocker.patch("gcs_s3_transfer_service.views._get_s3_client")
    response = client.post("/upload", json=valid_upload_post_body)
    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert response.get_json()["error"]["reason"]


def test_upload(mocker, client, valid_upload_post_body):
    mocker.patch("gcs_s3_transfer_service.views._get_gcs_client")
    mocker.patch("gcs_s3_transfer_service.views._get_s3_client")
    response = client.post("/upload", json=valid_upload_post_body)
    assert response.status_code == HTTPStatus.OK
    assert "Successfully uploaded" in response.get_json()["message"]


def test_upload_returns_internal_server_error_on_upload_fileobj_failure(
    mocker, client, valid_upload_post_body
):
    mocker.patch("gcs_s3_transfer_service.views._get_gcs_client")
    mock_s3_client = mocker.MagicMock()
    mock_s3_client.upload_fileobj = mocker.MagicMock(side_effect=Exception("foo"))
    mocker.patch(
        "gcs_s3_transfer_service.views._get_s3_client", return_value=mock_s3_client
    )
    response = client.post("/upload", json=valid_upload_post_body)
    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert response.get_json()["error"]["reason"]

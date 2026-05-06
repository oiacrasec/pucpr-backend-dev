def test_root_serves_swagger_ui(client):
    response = client.get("/")

    assert response.status_code == 200
    assert "Swagger UI" in response.text


def test_favicon_request_does_not_return_404(client):
    response = client.get("/favicon.ico")

    assert response.status_code == 204
    assert response.content == b""

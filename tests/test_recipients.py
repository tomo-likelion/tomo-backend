from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_get_recipient_returns_registered_profile():
    response = client.get("/api/v1/recipients/tanaka@abc.jp")

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "email": "tanaka@abc.jp",
        "name": "Tanaka",
        "countryCode": "JP",
        "languageCode": "ja",
        "relationship": "PARTNER",
        "organization": "ABC Design",
    }


def test_get_recipient_normalizes_email_case():
    response = client.get("/api/v1/recipients/TANAKA@ABC.JP")

    assert response.status_code == 200
    assert response.json()["email"] == "tanaka@abc.jp"


def test_get_recipient_returns_404_for_unknown_email():
    response = client.get("/api/v1/recipients/unknown@example.com")

    assert response.status_code == 404
    assert response.json() == {
        "code": "RECIPIENT_NOT_FOUND",
        "message": "등록되지 않은 수신자입니다.",
    }

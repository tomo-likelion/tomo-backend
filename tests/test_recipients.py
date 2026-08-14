import pytest
from fastapi.testclient import TestClient

from app.repositories import recipient_repository
from app.main import app


client = TestClient(app)


@pytest.fixture(autouse=True)
def isolate_recipient_data(monkeypatch):
    monkeypatch.setattr(
        recipient_repository,
        "_RECIPIENTS",
        recipient_repository._RECIPIENTS.copy(),
    )


def test_create_recipient_registers_new_profile():
    response = client.post(
        "/api/v1/recipients",
        json={
            "email": "sato@design.jp",
            "name": "Sato",
            "countryCode": "JP",
            "languageCode": "ja",
            "relationship": "PARTNER",
            "organization": "Design JP",
        },
    )

    assert response.status_code == 201
    assert response.json() == {
        "id": 3,
        "email": "sato@design.jp",
        "name": "Sato",
        "countryCode": "JP",
        "languageCode": "ja",
        "relationship": "PARTNER",
        "organization": "Design JP",
    }

    lookup_response = client.get("/api/v1/recipients/sato@design.jp")
    assert lookup_response.status_code == 200
    assert lookup_response.json() == response.json()


def test_create_recipient_returns_409_for_duplicate_email():
    response = client.post(
        "/api/v1/recipients",
        json={
            "email": "TANAKA@ABC.JP",
            "name": "Another Tanaka",
            "countryCode": "JP",
            "languageCode": "ja",
            "relationship": "PARTNER",
            "organization": "Another Company",
        },
    )

    assert response.status_code == 409
    assert response.json() == {
        "code": "RECIPIENT_ALREADY_EXISTS",
        "message": "이미 등록된 수신자입니다.",
    }


def test_create_recipient_returns_422_for_invalid_email():
    response = client.post(
        "/api/v1/recipients",
        json={
            "email": "not-an-email",
            "name": "Invalid Recipient",
            "countryCode": "JP",
            "languageCode": "ja",
            "relationship": "PARTNER",
            "organization": "Invalid Company",
        },
    )

    assert response.status_code == 422


def test_get_recipients_returns_all_profiles_in_id_order():
    response = client.get("/api/v1/recipients")

    assert response.status_code == 200
    assert [recipient["email"] for recipient in response.json()] == [
        "tanaka@abc.jp",
        "alex@example.com",
    ]


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

from fastapi.testclient import TestClient


def test_suppliers_crud_validation_and_email_conflict(
    client: TestClient,
    unique_suffix: str,
) -> None:
    supplier_id = None
    payload = {
        "name": f"ООО ТестПоставка {unique_suffix}",
        "email": f"supplier-{unique_suffix}@example.com",
        "phone": "+7 900 100-20-30",
        "address": "г. Москва, Тестовая ул., 1",
    }

    try:
        invalid_response = client.post(
            "/suppliers",
            json={**payload, "email": "wrong-email"},
        )
        assert invalid_response.status_code == 422

        create_response = client.post("/suppliers", json=payload)
        assert create_response.status_code == 201
        supplier = create_response.json()
        supplier_id = supplier["id"]
        assert supplier["email"] == payload["email"]

        get_response = client.get(f"/suppliers/{supplier_id}")
        assert get_response.status_code == 200
        assert get_response.json()["id"] == supplier_id

        conflict_response = client.post(
            "/suppliers",
            json={**payload, "name": f"Дубль {unique_suffix}"},
        )
        assert conflict_response.status_code == 409

        delete_response = client.delete(f"/suppliers/{supplier_id}")
        assert delete_response.status_code == 204
        supplier_id = None
    finally:
        if supplier_id is not None:
            client.delete(f"/suppliers/{supplier_id}")

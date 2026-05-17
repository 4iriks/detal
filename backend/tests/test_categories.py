from fastapi.testclient import TestClient


def test_categories_crud(client: TestClient, unique_suffix: str) -> None:
    category_id = None
    payload = {
        "name": f"Тестовая категория {unique_suffix}",
        "description": "Категория для автотеста",
    }

    try:
        create_response = client.post("/categories", json=payload)
        assert create_response.status_code == 201
        created = create_response.json()
        category_id = created["id"]
        assert created["name"] == payload["name"]

        list_response = client.get("/categories")
        assert list_response.status_code == 200
        assert any(category["id"] == category_id for category in list_response.json())

        get_response = client.get(f"/categories/{category_id}")
        assert get_response.status_code == 200
        assert get_response.json()["id"] == category_id

        put_payload = {
            "name": f"Обновленная категория {unique_suffix}",
            "description": "Описание после PUT",
        }
        put_response = client.put(f"/categories/{category_id}", json=put_payload)
        assert put_response.status_code == 200
        assert put_response.json()["name"] == put_payload["name"]

        patch_response = client.patch(
            f"/categories/{category_id}",
            json={"description": "Описание после PATCH"},
        )
        assert patch_response.status_code == 200
        assert patch_response.json()["description"] == "Описание после PATCH"

        delete_response = client.delete(f"/categories/{category_id}")
        assert delete_response.status_code == 204
        category_id = None

        missing_response = client.get(f"/categories/{created['id']}")
        assert missing_response.status_code == 404
    finally:
        if category_id is not None:
            client.delete(f"/categories/{category_id}")


def test_category_name_unique_conflict(
    client: TestClient,
    unique_suffix: str,
) -> None:
    category_id = None
    payload = {
        "name": f"Уникальная категория {unique_suffix}",
        "description": "Проверка уникальности",
    }

    try:
        create_response = client.post("/categories", json=payload)
        assert create_response.status_code == 201
        category_id = create_response.json()["id"]

        conflict_response = client.post("/categories", json=payload)
        assert conflict_response.status_code == 409
    finally:
        if category_id is not None:
            client.delete(f"/categories/{category_id}")

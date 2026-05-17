from fastapi.testclient import TestClient


def test_warehouses_create_and_get_by_id(
    client: TestClient,
    unique_suffix: str,
) -> None:
    warehouse_id = None
    payload = {
        "name": f"Тестовый склад {unique_suffix}",
        "address": "г. Москва, Проверочная ул., 5",
        "responsible_person": "Тестов Тест Тестович",
    }

    try:
        create_response = client.post("/warehouses", json=payload)
        assert create_response.status_code == 201
        warehouse = create_response.json()
        warehouse_id = warehouse["id"]
        assert warehouse["name"] == payload["name"]

        get_response = client.get(f"/warehouses/{warehouse_id}")
        assert get_response.status_code == 200
        assert get_response.json()["id"] == warehouse_id
    finally:
        if warehouse_id is not None:
            client.delete(f"/warehouses/{warehouse_id}")

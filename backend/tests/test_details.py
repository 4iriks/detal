from fastapi.testclient import TestClient


def create_category(client: TestClient, suffix: str) -> int:
    response = client.post(
        "/categories",
        json={
            "name": f"Детали категория {suffix}",
            "description": "Категория для теста деталей",
        },
    )
    assert response.status_code == 201
    return int(response.json()["id"])


def create_supplier(client: TestClient, suffix: str) -> int:
    response = client.post(
        "/suppliers",
        json={
            "name": f"Детали поставщик {suffix}",
            "email": f"details-supplier-{suffix}@example.com",
            "phone": "+7 900 111-22-33",
            "address": "г. Москва, Детальная ул., 2",
        },
    )
    assert response.status_code == 201
    return int(response.json()["id"])


def create_warehouse(client: TestClient, suffix: str) -> int:
    response = client.post(
        "/warehouses",
        json={
            "name": f"Детали склад {suffix}",
            "address": "г. Москва, Складская тестовая ул., 9",
            "responsible_person": "Складов Семен Семенович",
        },
    )
    assert response.status_code == 201
    return int(response.json()["id"])


def test_details_crud_filters_low_stock_and_quantity(
    client: TestClient,
    unique_suffix: str,
) -> None:
    category_id = None
    supplier_id = None
    warehouse_id = None
    detail_id = None

    try:
        category_id = create_category(client, unique_suffix)
        supplier_id = create_supplier(client, unique_suffix)
        warehouse_id = create_warehouse(client, unique_suffix)

        detail_payload = {
            "name": f"Тестовый болт {unique_suffix}",
            "article": f"TEST-BOLT-{unique_suffix}",
            "material": "Сталь",
            "weight": 0.035,
            "price": 12.5,
            "quantity": 7,
            "category_id": category_id,
            "supplier_id": supplier_id,
            "warehouse_id": warehouse_id,
        }

        create_response = client.post("/details", json=detail_payload)
        assert create_response.status_code == 201
        detail = create_response.json()
        detail_id = detail["id"]
        assert detail["article"] == detail_payload["article"]
        assert detail["category"]["id"] == category_id

        list_response = client.get("/details")
        assert list_response.status_code == 200
        assert any(item["id"] == detail_id for item in list_response.json())

        search_response = client.get("/details", params={"search": unique_suffix})
        assert search_response.status_code == 200
        assert any(item["id"] == detail_id for item in search_response.json())

        quantity_response = client.patch(
            f"/details/{detail_id}/quantity",
            json={"quantity": 2},
        )
        assert quantity_response.status_code == 200
        assert quantity_response.json()["quantity"] == 2

        low_stock_response = client.get(
            "/details/low-stock",
            params={"threshold": 3},
        )
        assert low_stock_response.status_code == 200
        assert any(item["id"] == detail_id for item in low_stock_response.json())

        delete_response = client.delete(f"/details/{detail_id}")
        assert delete_response.status_code == 204
        detail_id = None
    finally:
        if detail_id is not None:
            client.delete(f"/details/{detail_id}")
        if category_id is not None:
            client.delete(f"/categories/{category_id}")
        if supplier_id is not None:
            client.delete(f"/suppliers/{supplier_id}")
        if warehouse_id is not None:
            client.delete(f"/warehouses/{warehouse_id}")

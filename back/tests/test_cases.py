import re


def payload(**overrides):
    data = {
        "project": "Project1",
        "product": "Product1",
        "technology": "Technology1",
        "fail_type": "",
        "fail_model": "Mode A",
    }
    data.update(overrides)
    return data


def create_case(client, **overrides):
    return client.post("/api/v1/cases", json=payload(**overrides))


def test_create_generates_sequential_case_ids_and_allows_empty_fail_type(client):
    first = create_case(client, case_id="ignored-by-server")
    second = create_case(client)
    assert first.status_code == 201
    assert second.status_code == 201
    first_data = first.get_json()["data"]
    second_data = second.get_json()["data"]
    assert re.fullmatch(r"FA\d{8}001", first_data["case_id"])
    assert second_data["case_id"] == f"{first_data['case_id'][:-3]}002"
    assert first_data["fail_type"] is None


def test_create_validates_required_fields(client):
    response = create_case(client, fail_model=" ")
    assert response.status_code == 400
    assert response.get_json()["message"] == "fail_model is required"


def test_get_and_update_case_preserve_case_id(client):
    created = create_case(client).get_json()["data"]
    response = client.put(
        f"/api/v1/cases/{created['id']}",
        json=payload(case_id="FA19990101001", product="Product2", fail_type="Visual"),
    )
    assert response.status_code == 200
    updated = response.get_json()["data"]
    assert updated["case_id"] == created["case_id"]
    assert updated["product"] == "Product2"
    assert updated["fail_type"] == "Visual"
    assert client.get(f"/api/v1/cases/{created['id']}").get_json()["data"] == updated


def test_options_endpoint_returns_requirement_defaults(client):
    response = client.get("/api/v1/cases/options")
    assert response.status_code == 200
    assert response.get_json()["data"] == {
        "projects": ["Project1", "Project2", "Project3"],
        "products": ["Product1", "Product2", "Product3"],
        "technologies": ["Technology1", "Technology2", "Technology3"],
    }


def test_list_search_and_batch_delete(client):
    first = create_case(client, project="Project1").get_json()["data"]
    second = create_case(client, project="Project2").get_json()["data"]
    result = client.get("/api/v1/cases?keyword=Project2").get_json()["data"]
    assert result["pagination"]["total"] == 1
    assert result["items"][0]["id"] == second["id"]
    deleted = client.post("/api/v1/cases/batch-delete", json={"ids": [first["id"], second["id"]]})
    assert deleted.status_code == 200
    assert deleted.get_json()["data"]["deleted"] == 2

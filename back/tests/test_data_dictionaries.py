def test_list_seeds_default_dictionaries(client):
    response = client.get("/api/v1/data-dictionaries")
    assert response.status_code == 200
    data = response.get_json()["data"]
    assert [item["value"] for item in data["project"]] == ["Project1", "Project2", "Project3"]
    assert [item["value"] for item in data["product"]] == ["Product1", "Product2", "Product3"]
    assert [item["value"] for item in data["technology"]] == ["Technology1", "Technology2", "Technology3"]


def test_replace_dictionary_updates_case_options(client):
    response = client.put(
        "/api/v1/data-dictionaries/project",
        json={"options": ["Phoenix", "Orion", "Atlas"]},
    )
    assert response.status_code == 200
    assert [item["value"] for item in response.get_json()["data"]] == ["Phoenix", "Orion", "Atlas"]
    case_options = client.get("/api/v1/cases/options").get_json()["data"]
    assert case_options["projects"] == ["Phoenix", "Orion", "Atlas"]


def test_replace_dictionary_validates_type_values_and_duplicates(client):
    assert client.put("/api/v1/data-dictionaries/unknown", json={"options": ["A"]}).status_code == 400
    assert client.put("/api/v1/data-dictionaries/project", json={"options": ["A", "A"]}).status_code == 400
    assert client.put("/api/v1/data-dictionaries/project", json={"options": [""]}).status_code == 400


def test_dictionary_can_be_cleared(client):
    response = client.put("/api/v1/data-dictionaries/project", json={"options": []})
    assert response.status_code == 200
    assert response.get_json()["data"] == []
    assert client.get("/api/v1/cases/options").get_json()["data"]["projects"] == []

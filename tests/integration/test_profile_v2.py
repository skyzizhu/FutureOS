from sqlalchemy.orm import Session

from infra.db import Profile
from tests.integration.test_m4_reports import account, profile


def test_extended_industries_and_country_catalog_are_public_and_consistent(runtime):
    client, _, _ = runtime
    entries = client.get("/api/v1/taxonomies/industries").json()["entries"]
    parents = {e["code"] for e in entries if e["level"] == 1}
    children = [e for e in entries if e["level"] == 2]
    assert len(parents) == 23 and len(children) == 261
    assert len({e["code"] for e in entries}) == len(entries)
    assert all(e["parent_code"] in parents for e in children)
    assert {"agriculture", "mining", "construction", "commerce", "transport", "culture"} <= parents
    assert any(e["code"] == "software" and e["parent_code"] == "technology" for e in children)
    assert all(
        any(e["code"] == parent + "_other" for e in children)
        for parent in parents - {"not_applicable"}
    )
    assert next(e for e in entries if e["code"] == "technology")["label"] == "互联网与信息技术"
    assert next(e for e in entries if e["code"] == "not_applicable")["label"] == (
        "暂不按职业分类（学生／退休等）"
    )
    for code, label in [
        ("technology_product_management", "产品经理"),
        ("technology_ui_design", "UI设计师"),
    ]:
        assert any(
            e["code"] == code and e["label"] == label and e["parent_code"] == "technology"
            for e in children
        )
    countries = client.get("/api/v1/taxonomies/countries")
    assert countries.status_code == 200
    codes = {entry["code"] for entry in countries.json()["entries"]}
    assert len(codes) == 258 and {"CN", "US", "GB", "CA", "JP"} <= codes
    headers, _, _ = account(client)
    assert (
        client.put(
            "/api/v1/me/profile",
            headers=headers,
            json={"industry_l1_code": "agriculture", "industry_l2_code": "software"},
        ).status_code
        == 422
    )
    assert (
        client.put(
            "/api/v1/me/profile",
            headers=headers,
            json={"industry_l1_code": "agriculture", "industry_l2_code": "agriculture_other"},
        ).status_code
        == 422
    )
    for code in ["technology_product_management", "technology_ui_design", "software"]:
        response = client.put(
            "/api/v1/me/profile",
            headers=headers,
            json={
                "industry_l1_code": "technology",
                "industry_l2_code": code,
            },
        )
        assert response.status_code == 200, response.text
        assert (
            client.get("/api/v1/me/profile", headers=headers).json()["profile"]["industry_l2_code"]
            == code
        )
    saved = client.put(
        "/api/v1/me/profile",
        headers=headers,
        json={
            "industry_l1_code": "agriculture",
            "industry_l2_code": "agriculture_other",
            "industry_detail": "设施农业机器人运营",
        },
    )
    assert saved.status_code == 200, saved.text
    snapshot = client.post("/api/v1/me/profile/snapshots", headers=headers).json()
    assert snapshot["profile"]["industry_detail"] == "设施农业机器人运营"


def test_optional_demographics_encrypted_but_excluded_from_research_snapshots(runtime):
    client, engine, _ = runtime
    headers, state, _ = account(client)
    saved = profile(
        client,
        headers,
        country_code="US",
        subdivision="Private-state-California",
        gender="female",
        age=33,
        occupation_text="开发",
        goals=["职业发展"],
        tasks=["编码"],
        use_optional_fields=True,
    )
    assert saved["profile"]["age"] == 33
    assert saved["profile"]["gender"] == "female"
    assert saved["profile"]["country_code"] == "US"
    snapshot = client.post("/api/v1/me/profile/snapshots", headers=headers).json()
    assert snapshot["profile"]["age"] is None and snapshot["profile"]["gender"] is None
    assert snapshot["profile"]["country_code"] == "US"
    assert snapshot["profile"]["subdivision"] == "Private-state-California"
    from uuid import UUID

    with Session(engine) as session:
        row = session.get(Profile, UUID(state["identity"]["user_id"]))
        assert "Private-state-California" not in row.ciphertext
    profile(
        client,
        headers,
        country_code="US",
        subdivision="Private-state-California",
        gender="female",
        age=33,
        use_optional_fields=False,
    )
    minimal = client.post("/api/v1/me/profile/snapshots", headers=headers).json()["profile"]
    assert minimal["country_code"] == "" and minimal["subdivision"] == ""
    assert minimal["age"] is None and minimal["gender"] is None
    # Current optional information remains editable; withdrawing use does not silently erase it.
    current = client.get("/api/v1/me/profile", headers=headers).json()["profile"]
    assert current["age"] == 33 and current["subdivision"] == "Private-state-California"
    exported = client.get("/api/v1/me/export", headers=headers)
    assert exported.status_code == 200 and exported.json()["profile"]["profile"]["age"] == 33


def test_optional_profile_validation_and_legacy_compatibility(runtime):
    client, _, _ = runtime
    headers, _, _ = account(client)
    original = profile(client, headers, region="原地区文本")
    for change in [
        {"age": 0},
        {"age": 121},
        {"age": 22.5},
        {"age": "22"},
        {"gender": "invalid"},
        {"country_code": "XX"},
        {"subdivision": "California"},
    ]:
        result = client.put(
            "/api/v1/me/profile",
            headers=headers,
            json={"industry_l1_code": "technology", "industry_l2_code": "software", **change},
        )
        assert result.status_code == 422, (change, result.text)
    current = client.get("/api/v1/me/profile", headers=headers).json()
    assert current == original and current["profile"]["region"] == "原地区文本"
    assert current["profile"]["age"] is None and current["profile"]["country_code"] == ""

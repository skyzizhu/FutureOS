from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from infra.community_seed import catalog_id
from infra.db import (
    CommunityActivity,
    CommunityIndustry,
    CommunityLike,
    ConsumerPreference,
    IndustryTracking,
)
from tests.integration.test_m4_reports import account, complete_report, profile


def public_report(runtime):
    client, _, _ = runtime
    owner, _, _ = account(client)
    reader, _, _ = account(client)
    profile(client, owner)
    _, report = complete_report(runtime, owner)
    result = client.post(
        f"/api/v1/me/community/reports/{report['report_id']}/publish",
        headers=owner,
        json={
            "industry_id": str(catalog_id("ai")),
            "report_version_id": report["report_version_id"],
            "confirm_public": True,
        },
    )
    assert result.status_code == 200, result.text
    return owner, reader, result.json()["id"]


def test_copy_public_industries_is_owned_independent_idempotent_and_supports_multiple(runtime):
    client, engine, _ = runtime
    owner, _, _ = account(client)
    other, _, _ = account(client)
    copies = []
    for code in ["ai", "energy"]:
        url = f"/api/v1/me/community/industries/{catalog_id(code)}/add"
        first = client.put(url, headers=owner)
        assert first.status_code == 200, first.text
        item = first.json()
        assert item["owned"] and item["source_industry_id"] == str(catalog_id(code))
        assert item["id"] != str(catalog_id(code)) and item["public"] is False
        assert client.put(url, headers=owner).json()["id"] == item["id"]
        copies.append(item)
    assert len(client.get("/api/v1/me/community/industries", headers=owner).json()) == 2
    first = copies[0]
    edit = client.put(
        f"/api/v1/me/community/industries/{first['id']}",
        headers=owner,
        json={"name": "我的独立行业", "description": "我的观察角度", "domain": "technology"},
    )
    assert edit.status_code == 200
    assert (
        client.get(f"/api/v1/community/industries/{catalog_id('ai')}").json()["name"] == "人工智能"
    )
    assert (
        client.get(f"/api/v1/me/community/industries/{first['id']}", headers=other).status_code
        == 404
    )
    settings = {"monitor_enabled": True, "prediction_enabled": True, "email_enabled": True}
    for item in copies:
        response = client.put(
            f"/api/v1/me/community/industries/{item['id']}/tracking", headers=owner, json=settings
        )
        assert response.status_code == 200, response.text
        assert response.json()["status"] == "waiting_rules"
        assert (
            client.get(
                f"/api/v1/me/community/industries/{item['id']}/tracking", headers=owner
            ).json()["email_enabled"]
            is True
        )
    assert (
        client.put(
            f"/api/v1/me/community/industries/{copies[0]['id']}/tracking",
            headers=other,
            json=settings,
        ).status_code
        == 404
    )
    with Session(engine) as session:
        assert session.scalar(select(func.count()).select_from(IndustryTracking)) == 2
        assert session.get(CommunityIndustry, UUID(first["id"])).name == "我的独立行业"


def test_like_bookmark_author_inbox_dedup_read_and_download_visibility(runtime):
    client, engine, _ = runtime
    owner, reader, identifier = public_report(runtime)
    like = f"/api/v1/me/community/reports/{identifier}/like"
    save = f"/api/v1/me/community/reports/{identifier}/bookmark"
    assert client.put(like).status_code == 401
    for _ in range(2):
        assert client.put(like, headers=reader).status_code == 200
        assert (
            client.put(
                save, headers=reader, json={"industry_id": str(catalog_id("ai"))}
            ).status_code
            == 200
        )
    public = client.get(f"/api/v1/community/reports/{identifier}")
    assert public.json()["likes_count"] == 1 and public.json()["bookmarks_count"] == 1
    inbox = client.get("/api/v1/me/community/notifications", headers=owner)
    assert inbox.status_code == 200, inbox.text
    assert len(inbox.json()) == 2 and {n["kind"] for n in inbox.json()} == {"like", "bookmark"}
    note = inbox.json()[0]["id"]
    assert (
        client.post(f"/api/v1/me/community/notifications/{note}/read", headers=reader).status_code
        == 404
    )
    assert (
        client.post(f"/api/v1/me/community/notifications/{note}/read", headers=owner).status_code
        == 200
    )
    assert client.delete(like, headers=reader).status_code == 200
    assert client.put(like, headers=reader).status_code == 200
    assert len(client.get("/api/v1/me/community/notifications", headers=owner).json()) == 2
    assert client.put(like, headers=owner).status_code == 200
    assert len(client.get("/api/v1/me/community/notifications", headers=owner).json()) == 2
    url = f"/api/v1/me/community/reports/{identifier}/download"
    assert client.get(url).status_code == 401
    downloaded = client.get(url, headers=reader)
    assert (
        downloaded.status_code == 200 and "attachment" in downloaded.headers["content-disposition"]
    )
    assert "text/markdown" in downloaded.headers["content-type"]
    assert "行业观察" in downloaded.text and "画像" not in downloaded.text.replace("个人画像", "")
    assert (
        client.delete(f"/api/v1/me/community/publications/{identifier}", headers=owner).status_code
        == 200
    )
    assert client.get(url, headers=reader).status_code == 404
    assert client.put(like, headers=reader).status_code == 404
    with Session(engine) as session:
        assert session.scalar(select(func.count()).select_from(CommunityActivity)) == 2
        assert session.scalar(select(func.count()).select_from(CommunityLike)) == 2


def test_theme_default_account_persistence_and_private_erasure(runtime):
    client, engine, _ = runtime
    owner, reader, identifier = public_report(runtime)
    assert client.get("/api/v1/me/preferences", headers=reader).json()["theme"] == "system"
    assert (
        client.put("/api/v1/me/preferences", headers=reader, json={"theme": "dark"}).status_code
        == 200
    )
    assert client.get("/api/v1/me/preferences", headers=reader).json()["theme"] == "dark"
    assert client.get("/api/v1/me/preferences", headers=owner).json()["theme"] == "system"
    assert (
        client.put("/api/v1/me/preferences", headers=reader, json={"theme": "invalid"}).status_code
        == 422
    )
    assert (
        client.put(f"/api/v1/me/community/reports/{identifier}/like", headers=reader).status_code
        == 200
    )
    export = client.get("/api/v1/me/export", headers=reader)
    assert export.status_code == 200, export.text
    assert export.json()["appearance"][0]["theme"] == "dark"
    erased = client.request(
        "DELETE",
        "/api/v1/me/data",
        headers=reader,
        json={"password": "Local-test-password-123!", "confirmation": "DELETE MY DATA"},
    )
    assert erased.status_code == 200, erased.text
    with Session(engine) as session:
        assert session.scalar(select(func.count()).select_from(ConsumerPreference)) == 0
        assert session.scalar(select(func.count()).select_from(CommunityActivity)) == 0
        assert session.scalar(select(func.count()).select_from(CommunityLike)) == 0


def test_public_reads_are_durable_daily_deduplicated_and_withdrawal_safe(runtime, monkeypatch):
    from concurrent.futures import ThreadPoolExecutor
    from datetime import timedelta
    from uuid import uuid4

    from infra.db import CommunityReportMetric, CommunityReportRead, utcnow

    client, engine, _ = runtime
    owner, _, identifier = public_report(runtime)
    visitor = uuid4()
    endpoint = f"/api/v1/community/reports/{identifier}/read"

    def read(who):
        response = client.post(endpoint, json={"visitor_id": str(who)})
        assert response.status_code == 200, response.text
        return response.json()["views_count"]

    assert read(visitor) == 1
    assert read(visitor) == 1
    others = [uuid4() for _ in range(8)]
    if engine.dialect.name == "postgresql":
        with ThreadPoolExecutor(max_workers=4) as pool:
            list(pool.map(read, [visitor] * 4 + others))
    else:
        for who in others:
            read(who)
    assert client.get(f"/api/v1/community/reports/{identifier}").json()["views_count"] == 9
    feed = client.get("/api/v1/community/reports").json()
    assert next(row for row in feed if row["id"] == identifier)["views_count"] == 9
    now = utcnow()
    monkeypatch.setattr("infra.consumer_social.utcnow", lambda: now + timedelta(days=3))
    assert read(visitor) == 10
    with Session(engine) as session:
        assert session.get(CommunityReportMetric, UUID(identifier)).views_count == 10
        reads = list(session.scalars(select(CommunityReportRead)))
        assert len(reads) == 1
        assert len(reads[0].visitor_hash) == 64 and reads[0].visitor_hash != str(visitor)
    assert (
        client.delete(f"/api/v1/me/community/publications/{identifier}", headers=owner).status_code
        == 200
    )
    assert client.post(endpoint, json={"visitor_id": str(uuid4())}).status_code == 404

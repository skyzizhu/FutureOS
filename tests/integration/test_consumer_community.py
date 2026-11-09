from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from infra.community_seed import catalog_id
from infra.db import CommunityBookmark, ResearchConversation
from tests.integration.test_m4_reports import account, complete_report, profile
from workers.research.main import run_once


def test_public_discovery_has_no_private_identity_and_filters(runtime):
    client, _, _ = runtime
    industries = client.get("/api/v1/community/industries")
    assert industries.status_code == 200, industries.text
    assert len(industries.json()) == 5
    reports = client.get("/api/v1/community/reports").json()
    assert len(reports) == 3 and all(r["sample"] and r["label"] == "DEMO" for r in reports)
    assert all("user_id" not in r and "report_id" not in r for r in reports)
    filtered = client.get(
        "/api/v1/community/reports", params={"industry_id": str(catalog_id("ai"))}
    )
    assert len(filtered.json()) == 2
    assert client.get("/api/v1/community/reports?offset=-1").status_code == 422
    assert client.get("/api/v1/me/community/industries").status_code == 401


def test_private_industry_public_sharing_membership_and_owner_edit(runtime):
    client, _, _ = runtime
    owner, _, _ = account(client)
    other, _, _ = account(client)
    created = client.post(
        "/api/v1/me/community/industries",
        headers=owner,
        json={"name": "关注的测试行业", "description": "我关心的变化", "domain": "technology"},
    )
    assert created.status_code == 201, created.text
    identifier = created.json()["id"]
    url = f"/api/v1/me/community/industries/{identifier}"
    assert client.get(f"/api/v1/community/industries/{identifier}").status_code == 404
    assert client.get(url, headers=other).status_code == 404
    assert client.put(url + "/visibility", headers=owner, json={"public": True}).status_code == 200
    assert client.get(f"/api/v1/community/industries/{identifier}").status_code == 200
    assert client.put(url + "/membership", headers=other).status_code == 200
    assert client.put(url + "/membership", headers=other).status_code == 200
    assert len(client.get("/api/v1/me/community/industries", headers=other).json()) == 1
    assert client.put(url + "/visibility", headers=other, json={"public": False}).status_code == 404
    assert client.put(url + "/visibility", headers=owner, json={"public": False}).status_code == 200
    assert client.get(f"/api/v1/community/industries/{identifier}").status_code == 404
    # Existing members retain their own collection; new visitors cannot discover it.
    assert client.get(url, headers=other).status_code == 200
    assert client.delete(url + "/membership", headers=other).status_code == 200
    assert client.get(url, headers=other).status_code == 404


def test_report_snapshot_excludes_personal_data_and_withdrawal_hides_saved_copy(runtime):
    client, engine, _ = runtime
    owner, _, _ = account(client)
    other, _, _ = account(client)
    profile(
        client, owner, occupation_text="PRIVATE_OCCUPATION_NEVER_SHARE", use_optional_fields=True
    )
    _, report = complete_report(runtime, owner)
    payload = {
        "industry_id": str(catalog_id("ai")),
        "report_version_id": report["report_version_id"],
        "confirm_public": True,
    }
    url = f"/api/v1/me/community/reports/{report['report_id']}"
    assert client.post(url + "/preview", headers=other, json=payload).status_code == 404
    preview = client.post(url + "/preview", headers=owner, json=payload)
    assert preview.status_code == 200, preview.text
    assert "PRIVATE_OCCUPATION" not in preview.text and "profile_snapshot_id" not in preview.text
    assert "primary_impacts" not in preview.text and "recommendations" not in preview.text
    rejected = client.post(
        url + "/publish", headers=owner, json={**payload, "confirm_public": False}
    )
    assert rejected.status_code == 422
    publication = client.post(url + "/publish", headers=owner, json=payload)
    assert publication.status_code == 200, publication.text
    identifier = publication.json()["id"]
    public = f"/api/v1/community/reports/{identifier}"
    assert client.get(public).status_code == 200
    bookmark = f"/api/v1/me/community/reports/{identifier}/bookmark"
    assert (
        client.put(
            bookmark, headers=other, json={"industry_id": str(catalog_id("energy"))}
        ).status_code
        == 200
    )
    saved = client.get("/api/v1/me/community/bookmarks", headers=other).json()
    assert saved[0]["saved_industry_id"] == str(catalog_id("energy"))
    assert (
        client.delete(f"/api/v1/me/community/publications/{identifier}", headers=other).status_code
        == 404
    )
    assert (
        client.delete(f"/api/v1/me/community/publications/{identifier}", headers=owner).status_code
        == 200
    )
    assert client.get(public).status_code == 404
    assert client.get("/api/v1/me/community/bookmarks", headers=other).json() == []
    assert client.get(f"/api/v1/reports/{report['report_id']}", headers=owner).status_code == 200
    assert client.delete(bookmark, headers=other).status_code == 200
    with Session(engine) as session:
        assert session.scalar(select(CommunityBookmark)) is None


def test_personalized_feed_uses_profile_and_followed_industry(runtime):
    client, _, _ = runtime
    headers, _, _ = account(client)
    profile(client, headers, industry_l1_code="energy", industry_l2_code="storage")
    feed = client.get("/api/v1/me/community/feed", headers=headers)
    assert feed.status_code == 200, feed.text
    assert feed.json()[0]["industry_id"] == str(catalog_id("energy"))
    assert "画像" in feed.json()[0]["reason"]


def test_conversations_encrypted_idempotent_owner_only_and_durable_job(runtime):
    client, engine, config = runtime
    owner, _, _ = account(client)
    other, _, _ = account(client)
    profile(client, owner)
    payload = {
        "industry_id": str(catalog_id("ai")),
        "question": "PRIVATE_CHAT_我想看软件开发的变化",
        "client_id": str(uuid4()),
    }
    created = client.post("/api/v1/me/conversations", headers=owner, json=payload)
    assert created.status_code == 201, created.text
    identifier = created.json()["id"]
    url = f"/api/v1/me/conversations/{identifier}"
    assert (
        client.post("/api/v1/me/conversations", headers=owner, json=payload).json()["id"]
        == identifier
    )
    assert (
        client.post(
            "/api/v1/me/conversations", headers=owner, json={**payload, "question": "换个问题"}
        ).status_code
        == 409
    )
    assert client.get(url, headers=other).status_code == 404
    message = {"text": "重点看国内未来一年", "client_id": str(uuid4())}
    first = client.post(url + "/messages", headers=owner, json=message)
    assert first.status_code == 200, first.text
    assert len(client.post(url + "/messages", headers=owner, json=message).json()["messages"]) == 4
    with Session(engine) as session:
        row = session.get(ResearchConversation, UUID(identifier))
        assert "PRIVATE_CHAT" not in row.ciphertext and "国内" not in row.ciphertext
    assert (
        client.post(url + "/start", headers=owner, json={"confirm_demo_reuse": False}).status_code
        == 422
    )
    started = client.post(url + "/start", headers=owner, json={"confirm_demo_reuse": True})
    assert started.status_code == 200, started.text
    assert started.json()["job_status"] == "queued"
    assert (
        client.post(url + "/start", headers=owner, json={"confirm_demo_reuse": True}).json()[
            "job_id"
        ]
        == started.json()["job_id"]
    )
    assert run_once(engine, config)
    done = client.get(url, headers=owner)
    assert done.status_code == 200, done.text
    assert done.json()["job_status"] == "succeeded" and done.json()["report_id"]
    assert client.delete(url, headers=other).status_code == 404
    assert client.delete(url, headers=owner).status_code == 200
    assert client.get(url, headers=owner).status_code == 404
    assert (
        client.get(f"/api/v1/reports/{done.json()['report_id']}", headers=owner).status_code == 200
    )


def test_private_report_folder_and_account_erasure_remove_community_graph(runtime):
    client, engine, _ = runtime
    owner, _, _ = account(client)
    other, _, _ = account(client)
    profile(client, owner)
    _, report = complete_report(runtime, owner)
    report_id = report["report_id"]
    folder = f"/api/v1/me/community/private-reports/{report_id}"
    body = {"industry_id": str(catalog_id("ai"))}
    assert client.put(folder, headers=other, json=body).status_code == 404
    assert client.put(folder, headers=owner, json=body).status_code == 200
    publication = client.post(
        f"/api/v1/me/community/reports/{report_id}/publish",
        headers=owner,
        json={**body, "report_version_id": report["report_version_id"], "confirm_public": True},
    ).json()
    assert (
        client.put(
            f"/api/v1/me/community/reports/{publication['id']}/bookmark", headers=other, json=body
        ).status_code
        == 200
    )
    chat = client.post(
        "/api/v1/me/conversations",
        headers=owner,
        json={**body, "question": "我的私人研究问题", "client_id": str(uuid4())},
    ).json()
    exported = client.get("/api/v1/me/export", headers=owner)
    assert exported.status_code == 200, exported.text
    assert exported.json()["conversations"][0]["id"] == chat["id"]
    erased = client.request(
        "DELETE",
        "/api/v1/me/data",
        headers=owner,
        json={"password": "Local-test-password-123!", "confirmation": "DELETE MY DATA"},
    )
    assert erased.status_code == 200, erased.text
    assert client.get(f"/api/v1/community/reports/{publication['id']}").status_code == 404
    assert client.get("/api/v1/me/community/bookmarks", headers=other).json() == []
    with Session(engine) as session:
        assert session.scalar(select(ResearchConversation)) is None
        assert session.scalar(select(CommunityBookmark)) is None


def test_search_and_sort_happen_before_pagination(runtime):
    from datetime import timedelta

    from infra.db import CommunityPublication, utcnow

    client, engine, _ = runtime
    with Session(engine) as session:
        template = session.scalar(select(CommunityPublication))
        body = dict(template.body)
        now = utcnow()
        for index in range(30):
            session.add(
                CommunityPublication(
                    id=uuid4(),
                    industry_id=catalog_id("ai"),
                    public=True,
                    created_at=now - timedelta(days=index + 1),
                    body={
                        **body,
                        "title": "分页关键字" if index == 29 else f"分页阅读示例 {index}",
                    },
                )
            )
        session.commit()
    url = "/api/v1/community/reports"
    filtered = client.get(url, params={"q": "分页关键字"})
    assert filtered.status_code == 200, filtered.text
    assert len(filtered.json()) == 1 and filtered.json()[0]["title"] == "分页关键字"
    first = client.get(url).json()
    second = client.get(url, params={"offset": 24}).json()
    assert len(first) == 24 and len(second) == 9
    assert not {row["id"] for row in first} & {row["id"] for row in second}
    oldest = client.get(url, params={"sort": "oldest"}).json()
    assert oldest[0]["title"] == "分页关键字"
    assert client.get(url, params={"q": "x" * 101}).status_code == 422


def test_standalone_publication_keeps_industry_private_and_can_be_withdrawn(runtime):
    client, _, _ = runtime
    owner, _, _ = account(client)
    reader, _, _ = account(client)
    profile(client, owner, occupation_text="PRIVATE_OCCUPATION_NEVER_SHARE")
    _, report = complete_report(runtime, owner)
    private_industry = client.get("/api/v1/me/community/industries", headers=owner).json()[0]
    endpoint = f"/api/v1/me/community/reports/{report['report_id']}"
    data = {
        "report_version_id": report["report_version_id"],
        "industry_id": None,
        "confirm_public": True,
    }
    assert (
        client.post(
            endpoint + "/publish",
            headers=owner,
            json={**data, "industry_id": private_industry["id"]},
        ).status_code
        == 409
    )
    response = client.post(endpoint + "/publish", headers=owner, json=data)
    assert response.status_code == 200, response.text
    result = response.json()
    identifier = result["id"]
    assert result["industry_id"] is None
    assert "PRIVATE_OCCUPATION" not in response.text
    assert private_industry["id"] not in response.text
    assert client.get("/api/v1/community/industries/" + private_industry["id"]).status_code == 404
    assert client.get("/api/v1/community/reports/" + identifier).status_code == 200
    feed = client.get("/api/v1/community/reports?standalone=true&limit=1").json()
    assert [item["id"] for item in feed] == [identifier]
    linked = client.get("/api/v1/community/reports", params={"industry_id": str(catalog_id("ai"))})
    assert identifier not in {item["id"] for item in linked.json()}
    download = client.get(f"/api/v1/me/community/reports/{identifier}/download", headers=reader)
    assert download.status_code == 200 and "独立公开报告" in download.text
    assert (
        client.delete(f"/api/v1/me/community/publications/{identifier}", headers=owner).status_code
        == 200
    )
    assert client.get("/api/v1/community/reports/" + identifier).status_code == 404
    assert client.get("/api/v1/community/reports?standalone=true").json() == []

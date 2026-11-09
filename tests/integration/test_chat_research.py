from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from infra.community_seed import catalog_id
from infra.db import ChatIndustryResearch, Job
from tests.integration.test_m4_reports import account
from workers.research.main import run_once

CHAT = "/api/v1/me/conversations"


def create_chat(client, headers):
    response = client.post(
        CHAT,
        headers=headers,
        json={"client_id": str(uuid4()), "question": "人工智能未来会有哪些变化？"},
    )
    assert response.status_code == 201, response.text
    return CHAT + "/" + response.json()["id"]


def test_worker_research_persists_private_progress_and_result(runtime):
    client, engine, config = runtime
    owner, _, _ = account(client)
    other, _, _ = account(client)
    chat = create_chat(client, owner)
    another = create_chat(client, owner)
    endpoint = chat + "/industry-research"
    request = {
        "client_id": str(uuid4()),
        "industry_id": str(catalog_id("ai")),
        "horizon_days": 365,
        "confirm_demo": True,
    }
    queued = client.post(endpoint, headers=owner, json=request)
    assert queued.status_code == 202, queued.text
    run_id = queued.json()["id"]
    assert queued.json()["status"] == "queued"
    assert client.post(endpoint, headers=owner, json=request).json()["id"] == run_id
    assert (
        client.post(endpoint, headers=owner, json={**request, "horizon_days": 180}).status_code
        == 409
    )
    assert (
        client.post(
            endpoint, headers=owner, json={**request, "client_id": str(uuid4())}
        ).status_code
        == 409
    )
    assert client.get(f"{endpoint}/{run_id}", headers=other).status_code == 404
    assert client.get(f"{another}/industry-research/{run_id}", headers=owner).status_code == 404
    assert run_once(engine, config)
    response = client.get(f"{endpoint}/{run_id}", headers=owner)
    assert response.status_code == 200, response.text
    finished = response.json()
    assert finished["status"] == "succeeded"
    assert [step["stage"] for step in finished["stages"]] == ["search", "analysis", "report"]
    result = finished["result"]
    assert result["scope"]["label"] == "DEMO" and result["scope"]["horizon_days"] == 365
    assert result["report"]["forecasts"] and result["sources"]
    with Session(engine) as session:
        run = session.get(ChatIndustryResearch, UUID(run_id))
        assert run and "人工智能" not in run.scope_ciphertext
        assert run.result_ciphertext and result["report"]["forecasts"][0]["statement"] not in (
            run.result_ciphertext
        )
        job = session.get(Job, UUID(run_id))
        assert job and job.result == {"label": "DEMO"}
    assert client.get("/api/v1/jobs/" + run_id, headers=owner).json()["result"] is None

    request["client_id"] = str(uuid4())
    next_run = client.post(endpoint, headers=owner, json=request)
    assert next_run.status_code == 202, next_run.text
    pending = next_run.json()["id"]
    assert client.post(f"{endpoint}/{pending}/cancel", headers=owner).status_code == 200
    assert client.get(f"{endpoint}/{pending}", headers=owner).json()["status"] == "cancelled"
    assert client.delete(chat, headers=owner).status_code == 200
    with Session(engine) as session:
        assert session.get(ChatIndustryResearch, UUID(run_id)) is None
        assert session.get(ChatIndustryResearch, UUID(pending)) is None

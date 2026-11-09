from datetime import timedelta
from uuid import UUID

from prediction_engine.contracts.models import M2DraftV1, ResearchNarrativeV1, ResearchSnapshotV1
from prediction_engine.forecasting.workflow import (
    build_forecast_draft,
    mock_narrative,
    narrative_messages,
)
from sqlalchemy import func, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from infra.db import ModelCall, ResearchRun, User, utcnow
from infra.providers.deepseek import DeepSeekRequestError
from infra.providers.deepseek_llm import DeepSeekLLMProvider
from infra.research_repository import engine_code_hash
from infra.settings import Settings


async def execute_m2(engine: Engine, run_id: UUID, config: Settings) -> M2DraftV1:
    with Session(engine, expire_on_commit=False) as session:
        run = session.get(ResearchRun, run_id)
        if run is None:
            raise ValueError("RESEARCH_RUN_NOT_FOUND")
        snapshot = ResearchSnapshotV1.model_validate(run.snapshot)
        if run.engine_code_hash != engine_code_hash():
            raise ValueError("REPLAY_ENGINE_VERSION_MISMATCH")
        model_id = run.model_id
        if run.provider == "mock":
            narrative = mock_narrative(snapshot)
        else:
            if not config.live_research_enabled or config.deepseek_api_key is None:
                raise ValueError("LIVE_RESEARCH_DISABLED")
            session.scalar(select(User).where(User.id == run.creator_id).with_for_update())
            call = session.get(ModelCall, run_id)
            if call is not None:
                if call.status != "completed" or call.response is None:
                    raise ValueError("MODEL_CALL_UNCERTAIN_REQUIRES_REVIEW")
                narrative = ResearchNarrativeV1.model_validate(call.response)
                model_id = call.model_id
                session.commit()
            else:
                if sum(map(len, narrative_messages(snapshot))) > 50_000:
                    raise ValueError("RESEARCH_MODEL_BUDGET_EXCEEDED")
                count = session.scalar(
                    select(func.count())
                    .select_from(ModelCall)
                    .where(
                        ModelCall.user_id == run.creator_id,
                        ModelCall.started_at >= utcnow() - timedelta(days=1),
                    )
                )
                if (count or 0) >= 5:
                    raise ValueError("RESEARCH_MODEL_DAILY_BUDGET_EXCEEDED")
                call = ModelCall(
                    run_id=run_id, user_id=run.creator_id, status="started", model_id=model_id
                )
                session.add(call)
                session.commit()
                provider = DeepSeekLLMProvider(config.deepseek_api_key, model_id)
                try:
                    narrative = await provider.generate_structured(
                        ResearchNarrativeV1,
                        narrative_messages(snapshot),
                        budget=4096,
                        trace_context=str(run_id),
                    )
                    call.response = narrative.model_dump(mode="json")
                    call.model_id = provider.actual_model_id
                    call.usage = provider.usage
                    call.status = "completed"
                    call.finished_at = utcnow()
                    session.commit()
                    model_id = call.model_id
                except DeepSeekRequestError as exc:
                    call.status, call.error_code, call.finished_at = "failed", exc.code, utcnow()
                    session.commit()
                    raise ValueError(exc.code) from None
    return build_forecast_draft(run_id, snapshot, narrative, model_id)

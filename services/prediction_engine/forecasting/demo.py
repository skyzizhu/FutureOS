"""M0 wiring demonstration only; does not run real research or publish forecasts."""

from datetime import datetime
from hashlib import sha256

from prediction_engine.contracts.models import DemoResearchResultV1
from prediction_engine.contracts.providers import LLMProvider, SearchProvider


async def research_demo(
    question: str, as_of: datetime, trace_id: str, search: SearchProvider, llm: LLMProvider
) -> DemoResearchResultV1:
    sources = await search.search(question, as_of=as_of, max_results=3)
    if not sources:
        raise ValueError("EVIDENCE_UNVERIFIED")
    if any(s.label != "DEMO" or s.published_at is None or s.published_at > as_of for s in sources):
        raise ValueError("EVIDENCE_UNVERIFIED")
    result = await llm.generate_structured(
        DemoResearchResultV1, (question,), budget=1, trace_context=trace_id
    )
    # Domain attaches validated source IDs, never trusts invented model citations.
    return DemoResearchResultV1.model_validate(
        {
            **result.model_dump(),
            "source_ids": tuple(s.hit_id for s in sources),
            "research_as_of": as_of,
            "prompt_hash": sha256(question.encode()).hexdigest(),
        }
    )

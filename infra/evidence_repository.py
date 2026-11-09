"""M1 persistence/application boundary. Core contains deterministic rules and DTOs only."""

import json
from datetime import datetime
from typing import Any, Literal
from uuid import NAMESPACE_URL, UUID, uuid5

from prediction_engine.contracts.models import (
    EvidenceClaimV1,
    HistoricalCaseImportV1,
    HistoricalCaseViewV1,
    IndicatorDefinitionV1,
    IndicatorImportV1,
    ObservationImportV1,
    ObservationV1,
    SignalImportV1,
    SignalV1,
    SourceImportV1,
    SourceIngestedV1,
    SourceVersionV1,
)
from prediction_engine.evidence.temporal import known_by, utc
from prediction_engine.ingestion.normalize import canonical_url, content_hash, likely_reprint
from prediction_engine.signal_detection.rules import candidate_domains
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.orm import Session

from infra.db import (
    Base,
    EvidenceClaim,
    HistoricalCase,
    HistoricalCaseEvent,
    Indicator,
    ObservationVintage,
    Signal,
    SignalSource,
    SourceDocument,
    SourceGroup,
    SourceVersion,
    utcnow,
)


class EvidenceError(Exception):
    def __init__(self, code: str, message: str, status: int = 422) -> None:
        self.code, self.message, self.status = code, message, status
        super().__init__(code)


def stable_id(value: str) -> UUID:
    return uuid5(NAMESPACE_URL, "futureos:m1:" + value)


def digest(value: Any) -> str:
    return content_hash(json.dumps(value, ensure_ascii=False, sort_keys=True, default=str))


def columns(row: Base) -> dict[str, Any]:
    result = {column.name: getattr(row, column.name) for column in row.__table__.columns}
    return {
        key: utc(value) if isinstance(value, datetime) else value for key, value in result.items()
    }


class EvidenceRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def ensure(self, model: type[Base], values: dict[str, Any]) -> None:
        insert = (
            pg_insert
            if self.session.bind is not None and self.session.bind.dialect.name == "postgresql"
            else sqlite_insert
        )
        # Source groups derive both unique keys from the same identity. Concurrent
        # inserts can hit either unique index before the winning transaction commits.
        conflict_target = None if model is SourceGroup else ["id"]
        self.session.execute(
            insert(model).values(**values).on_conflict_do_nothing(index_elements=conflict_target)
        )

    def version(self, row: SourceVersion) -> SourceVersionV1:
        source = self.session.get(SourceDocument, row.source_id)
        assert source is not None
        return SourceVersionV1.model_validate(
            {**columns(row), "source_version_id": row.id, "url": source.canonical_url},
            extra="ignore",
        )

    def claim(self, row: EvidenceClaim) -> EvidenceClaimV1:
        version = self.session.get(SourceVersion, row.source_version_id)
        assert version is not None
        return EvidenceClaimV1.model_validate(
            {**columns(row), "claim_id": row.id, "source_group_id": version.source_group_id},
            extra="ignore",
        )

    def ingest(self, data: SourceImportV1, actor_id: UUID) -> SourceIngestedV1:
        now = utcnow()
        try:
            url = canonical_url(data.url)
            original = canonical_url(data.original_source_url) if data.original_source_url else url
        except ValueError:
            raise EvidenceError(
                "SOURCE_URL_INVALID", "来源必须使用有效且不含账号密码的 HTTP(S) URL"
            ) from None
        snapshot = {**data.model_dump(mode="json"), "url": url, "original_source_url": original}
        fingerprint = digest(snapshot)
        source_id = stable_id(data.label + ":url:" + url)
        version_id = stable_id(str(source_id) + ":" + fingerprint)
        previous = self.session.get(SourceVersion, version_id)
        if previous is not None:
            return SourceIngestedV1(
                version=self.version(previous),
                duplicate=True,
                claim_ids=tuple(
                    self.session.scalars(
                        select(EvidenceClaim.id).where(
                            EvidenceClaim.source_version_id == version_id
                        )
                    )
                ),
            )
        available = now if data.availability_basis == "observed_now" else data.available_at
        if (available and available > now) or (data.published_at and data.published_at > now):
            raise EvidenceError("SOURCE_TIME_IN_FUTURE", "不能导入尚未公开或未来才可获取的资料")
        if data.revised_at and (available is None or data.revised_at > available):
            raise EvidenceError("SOURCE_REVISION_TIME_INVALID", "修订时间不得晚于该版本可获取时间")
        if data.published_at and available and available < data.published_at:
            raise EvidenceError("SOURCE_TIME_INVALID", "可获取时间早于发布时间")
        for claim in data.claims:
            if claim.quote not in data.content:
                raise EvidenceError("CLAIM_QUOTE_NOT_FOUND", "引用片段不在保留的原文中")
            if claim.verification_status == "verified" and available is None:
                raise EvidenceError(
                    "SOURCE_AVAILABILITY_UNKNOWN", "未知可获取时间的资料不能作为已核实证据"
                )
        group_id = stable_id(data.label + ":origin:" + original)
        method = "declared_original" if data.original_source_url else "canonical_url"
        if data.content:
            candidates = self.session.scalars(
                select(SourceVersion)
                .where(SourceVersion.label == data.label)
                .order_by(SourceVersion.ingested_at.desc())
                .limit(1000)
            )
            for candidate in candidates:
                if likely_reprint(data.content, candidate.content):
                    group_id = candidate.source_group_id
                    method = (
                        "content_hash"
                        if content_hash(data.content) == candidate.content_hash
                        else "text_similarity"
                    )
                    break
        self.ensure(
            SourceGroup, {"id": group_id, "fingerprint": digest(str(group_id)), "label": data.label}
        )
        self.ensure(
            SourceDocument,
            {
                "id": source_id,
                "canonical_url": url,
                "url_hash": content_hash(url),
                "label": data.label,
                "ingested_at": now,
            },
        )
        values = {
            key: value
            for key, value in data.model_dump(exclude={"schema_version"}).items()
            if key not in {"url", "original_source_url", "claims", "domain_tags"}
        }
        values.update(
            id=version_id,
            source_id=source_id,
            source_group_id=group_id,
            version_label="sha256:" + fingerprint[:16],
            snapshot_hash=fingerprint,
            content_hash=content_hash(data.content),
            ingested_at=now,
            available_at=available,
            dedup_method=method,
            original_source_url=original if data.original_source_url else None,
            domain_tags=[tag.value for tag in data.domain_tags],
        )
        self.ensure(SourceVersion, values)
        claim_ids = []
        for item in data.claims:
            claim_id = stable_id(str(version_id) + ":claim:" + digest(item.model_dump(mode="json")))
            self.ensure(
                EvidenceClaim,
                {
                    **item.model_dump(exclude={"schema_version"}),
                    "id": claim_id,
                    "source_version_id": version_id,
                    "known_at": available,
                    "verified_by": actor_id if item.verification_status == "verified" else None,
                    "verified_at": now if item.verification_status == "verified" else None,
                    "label": data.label,
                },
            )
            claim_ids.append(claim_id)
            if item.claim_kind == "fact" and item.verification_status == "verified":
                domains = candidate_domains(item.claim_text)
                if domains:
                    self.create_signal(
                        SignalImportV1(
                            headline=item.claim_text,
                            claim_ids=(claim_id,),
                            domain_tags=tuple(dict.fromkeys((*data.domain_tags, *domains))),
                            mechanism_tags=("keyword_candidate_v1",),
                        ),
                        commit=False,
                    )
        self.session.commit()
        row = self.session.get(SourceVersion, version_id)
        assert row is not None
        return SourceIngestedV1(
            version=self.version(row), claim_ids=tuple(claim_ids), duplicate=False
        )

    def sources(
        self, as_of: datetime | None = None, label: str | None = None
    ) -> list[SourceVersionV1]:
        query = select(SourceVersion).order_by(SourceVersion.ingested_at.desc(), SourceVersion.id)
        if label:
            query = query.where(SourceVersion.label == label)
        if as_of:
            query = query.where(SourceVersion.available_at <= as_of)
        return [self.version(row) for row in self.session.scalars(query.limit(200))]

    def evidence(self, as_of: datetime, label: str | None = None) -> list[EvidenceClaimV1]:
        query = (
            select(EvidenceClaim)
            .join(SourceVersion)
            .where(
                EvidenceClaim.known_at <= as_of,
                SourceVersion.available_at <= as_of,
                EvidenceClaim.verification_status == "verified",
            )
        )
        if label:
            query = query.where(EvidenceClaim.label == label)
        return [
            self.claim(row)
            for row in self.session.scalars(query.order_by(EvidenceClaim.id).limit(500))
        ]

    def indicator(self, data: IndicatorImportV1) -> IndicatorDefinitionV1:
        identifier = stable_id(
            "indicator:"
            + digest(
                [data.code, data.provider, data.geo_scope, data.definition_version, data.label]
            )
        )
        existing = self.session.get(Indicator, identifier)
        if existing is not None:
            if any(
                getattr(existing, key) != value
                for key, value in data.model_dump(exclude={"schema_version"}).items()
            ):
                raise EvidenceError(
                    "INDICATOR_DEFINITION_CONFLICT", "指标定义已存在，请创建新定义版本", 409
                )
        else:
            self.ensure(
                Indicator, {**data.model_dump(exclude={"schema_version"}), "id": identifier}
            )
            self.session.commit()
        return IndicatorDefinitionV1(
            indicator_id=identifier, **data.model_dump(exclude={"schema_version"})
        )

    def observation(self, indicator_id: UUID, data: ObservationImportV1) -> ObservationV1:
        indicator = self.session.scalar(
            select(Indicator).where(Indicator.id == indicator_id).with_for_update()
        )
        source = self.session.get(SourceVersion, data.source_version_id)
        if indicator is None:
            raise EvidenceError("INDICATOR_NOT_FOUND", "指标不存在", 404)
        if source is None:
            raise EvidenceError("SOURCE_NOT_FOUND", "指标必须引用存在的来源版本", 404)
        if source.label != indicator.label or (data.quality_flag == "DEMO_DATA") != (
            indicator.label == "DEMO"
        ):
            raise EvidenceError("DATASET_LABEL_MISMATCH", "DEMO 与真实数据不得混用")
        if not known_by(source.available_at, data.available_at):
            raise EvidenceError(
                "OBSERVATION_SOURCE_NOT_AVAILABLE", "指标可获取时间不得早于引用来源版本"
            )
        if data.available_at > utcnow():
            raise EvidenceError("OBSERVATION_TIME_IN_FUTURE", "不能导入未来才可获取的指标")
        if data.quality_flag == "VERIFIED" and not self.session.scalar(
            select(EvidenceClaim.id)
            .where(
                EvidenceClaim.source_version_id == source.id,
                EvidenceClaim.verification_status == "verified",
                EvidenceClaim.claim_kind == "fact",
            )
            .limit(1)
        ):
            raise EvidenceError("OBSERVATION_EVIDENCE_UNVERIFIED", "正式指标需要已核实事实主张")
        identifier = stable_id(
            "observation:"
            + digest(
                [
                    str(indicator_id),
                    utc(data.period_start).isoformat(),
                    utc(data.period_end).isoformat(),
                    data.revision_number,
                ]
            )
        )
        prior = self.session.get(ObservationVintage, identifier)
        if prior is not None:
            if any(
                columns(prior)[key] != value
                for key, value in data.model_dump(exclude={"schema_version"}).items()
            ):
                raise EvidenceError(
                    "OBSERVATION_REVISION_CONFLICT", "同一修订版本不可覆盖；请追加修订号", 409
                )
            return self.observation_view(prior)
        revisions = self.session.scalars(
            select(ObservationVintage).where(
                ObservationVintage.indicator_id == indicator_id,
                ObservationVintage.period_start == data.period_start,
                ObservationVintage.period_end == data.period_end,
            )
        )
        for revision in revisions:
            if (
                revision.revision_number < data.revision_number
                and utc(revision.available_at) >= data.available_at
            ) or (
                revision.revision_number > data.revision_number
                and utc(revision.available_at) <= data.available_at
            ):
                raise EvidenceError("OBSERVATION_REVISION_ORDER", "新修订必须有更晚的可获取时间")
        self.ensure(
            ObservationVintage,
            {
                **data.model_dump(exclude={"schema_version"}),
                "id": identifier,
                "indicator_id": indicator_id,
                "label": indicator.label,
            },
        )
        self.session.commit()
        row = self.session.get(ObservationVintage, identifier)
        assert row is not None
        return self.observation_view(row)

    @staticmethod
    def observation_view(row: ObservationVintage) -> ObservationV1:
        return ObservationV1.model_validate(
            {**columns(row), "observation_id": row.id}, extra="ignore"
        )

    def series(
        self,
        indicator_id: UUID,
        as_of: datetime,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> list[ObservationV1]:
        if self.session.get(Indicator, indicator_id) is None:
            raise EvidenceError("INDICATOR_NOT_FOUND", "指标不存在", 404)
        query = (
            select(ObservationVintage)
            .join(SourceVersion)
            .where(
                ObservationVintage.indicator_id == indicator_id,
                ObservationVintage.available_at <= as_of,
                SourceVersion.available_at <= as_of,
                ObservationVintage.quality_flag != "UNVERIFIED",
            )
        )
        if start:
            query = query.where(ObservationVintage.period_start >= start)
        if end:
            query = query.where(ObservationVintage.period_end <= end)
        rows = self.session.scalars(
            query.order_by(
                ObservationVintage.available_at.desc(), ObservationVintage.revision_number.desc()
            )
        )
        latest: dict[tuple[datetime, datetime], ObservationV1] = {}
        for row in rows:
            key = (utc(row.period_start), utc(row.period_end))
            latest.setdefault(key, self.observation_view(row))
        return [latest[key] for key in sorted(latest)]

    def create_signal(self, data: SignalImportV1, *, commit: bool = True) -> SignalV1:
        claims = [
            self.session.get(EvidenceClaim, identifier)
            for identifier in dict.fromkeys(data.claim_ids)
        ]
        if any(claim is None for claim in claims):
            raise EvidenceError("SIGNAL_SOURCE_MISSING", "信号必须关联存在的证据主张", 404)
        labels = set()
        for claim in claims:
            assert claim is not None
            source = self.session.get(SourceVersion, claim.source_version_id)
            if (
                source is None
                or claim.claim_kind != "fact"
                or claim.verification_status != "verified"
                or not known_by(source.available_at, utcnow())
            ):
                raise EvidenceError(
                    "SIGNAL_EVIDENCE_UNVERIFIED", "仅已核实、时间有效的事实可生成信号候选"
                )
            labels.add(claim.label)
        if len(labels) != 1:
            raise EvidenceError("DATASET_LABEL_MISMATCH", "DEMO 与真实信号证据不得混用")
        identifier = stable_id("signal:" + digest(data.model_dump(mode="json")))
        self.ensure(
            Signal,
            {
                "id": identifier,
                "headline": data.headline,
                "lifecycle_stage": data.lifecycle_stage.value,
                "mechanism_tags": list(data.mechanism_tags),
                "domain_tags": [x.value for x in data.domain_tags],
                "label": next(iter(labels)),
                "detected_at": utcnow(),
            },
        )
        for claim in claims:
            assert claim is not None
            source = self.session.get(SourceVersion, claim.source_version_id)
            assert source is not None
            if self.session.get(SignalSource, (identifier, claim.id)) is None:
                self.session.add(
                    SignalSource(
                        signal_id=identifier,
                        evidence_claim_id=claim.id,
                        source_version_id=source.id,
                        source_group_id=source.source_group_id,
                    )
                )
        self.session.flush()
        if commit:
            self.session.commit()
        signal = self.session.get(Signal, identifier)
        assert signal is not None
        return self.signal_view(signal)

    def signal_view(self, row: Signal) -> SignalV1:
        links = list(
            self.session.scalars(select(SignalSource).where(SignalSource.signal_id == row.id))
        )
        groups = tuple(sorted({link.source_group_id for link in links}, key=str))
        return SignalV1.model_validate(
            {
                **columns(row),
                "signal_id": row.id,
                "claim_ids": tuple(link.evidence_claim_id for link in links),
                "source_group_ids": groups,
                "independent_source_count": len(groups),
            },
            extra="ignore",
        )

    def signals(self, as_of: datetime | None = None, label: str | None = None) -> list[SignalV1]:
        query = select(Signal).order_by(Signal.detected_at.desc()).limit(200)
        if label:
            query = query.where(Signal.label == label)
        output = []
        for signal in self.session.scalars(query):
            view = self.signal_view(signal)
            if as_of is not None:
                claims = [
                    self.session.get(EvidenceClaim, identifier) for identifier in view.claim_ids
                ]
                if any(claim is None or not known_by(claim.known_at, as_of) for claim in claims):
                    continue
            output.append(view)
        return output

    def historical_case(self, data: HistoricalCaseImportV1) -> UUID:
        if data.cutoff_at > utcnow() or any(event.known_at > utcnow() for event in data.events):
            raise EvidenceError("CASE_TIME_IN_FUTURE", "历史案例不能包含未来才发生或公开的结果")
        for event in data.events:
            source = self.session.get(SourceVersion, event.source_version_id)
            if source is None:
                raise EvidenceError("SOURCE_NOT_FOUND", "历史案例需要有效来源", 404)
            if source.label != data.label:
                raise EvidenceError("DATASET_LABEL_MISMATCH", "案例和来源标签不一致")
            if not known_by(source.available_at, event.known_at):
                raise EvidenceError(
                    "CASE_SOURCE_NOT_AVAILABLE", "案例使用了当时尚不可获取的来源版本"
                )
            if (event.data_role == "contemporaneous" and event.known_at > data.cutoff_at) or (
                event.data_role == "outcome" and event.known_at <= data.cutoff_at
            ):
                raise EvidenceError("CASE_ROLE_TIME_INVALID", "当时事实和事后结果的时间边界无效")
        identifier = stable_id("case:" + digest(data.model_dump(mode="json")))
        self.ensure(
            HistoricalCase,
            {
                key: value
                for key, value in {
                    **data.model_dump(exclude={"schema_version"}),
                    "id": identifier,
                    "domain_tags": [tag.value for tag in data.domain_tags],
                    "mechanism_tags": list(data.mechanism_tags),
                    "limitations": list(data.limitations),
                }.items()
                if key != "events"
            },
        )
        for event in data.events:
            self.ensure(
                HistoricalCaseEvent,
                {
                    **event.model_dump(exclude={"schema_version"}),
                    "id": stable_id(str(identifier) + digest(event.model_dump(mode="json"))),
                    "case_id": identifier,
                },
            )
        self.session.commit()
        return identifier

    def case_view(self, identifier: UUID, as_of: datetime) -> HistoricalCaseViewV1:
        row = self.session.get(HistoricalCase, identifier)
        if row is None:
            raise EvidenceError("HISTORICAL_CASE_NOT_FOUND", "历史案例不存在", 404)
        if as_of < utc(row.cutoff_at):
            raise EvidenceError(
                "AS_OF_PRECEDES_CASE_CUTOFF", "该案例背景只能从指定 cutoff 时点查看"
            )
        entries: dict[Literal["contemporaneous", "outcomes"], list[dict[str, Any]]] = {
            "contemporaneous": [],
            "outcomes": [],
        }
        for event in self.session.scalars(
            select(HistoricalCaseEvent).where(
                HistoricalCaseEvent.case_id == identifier, HistoricalCaseEvent.known_at <= as_of
            )
        ):
            source = self.session.get(SourceVersion, event.source_version_id)
            if source is not None and known_by(source.available_at, as_of):
                entries["outcomes" if event.data_role == "outcome" else "contemporaneous"].append(
                    {
                        key: value
                        for key, value in columns(event).items()
                        if key not in {"id", "case_id"}
                    }
                )
        return HistoricalCaseViewV1.model_validate(
            {**columns(row), "case_id": row.id, "as_of": as_of, **entries}, extra="ignore"
        )

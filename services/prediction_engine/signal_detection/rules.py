"""M1 conservative candidate tagging, never a forecast or confidence score."""

from prediction_engine.contracts.models import DomainTag

RULE_VERSION = "signals-keywords-v1"
RULES: dict[DomainTag, tuple[str, ...]] = {
    DomainTag.TECHNOLOGY: ("技术", "可靠性", "agent", "technology"),
    DomainTag.WORKFORCE: ("招聘", "岗位", "就业", "job", "hiring"),
    DomainTag.CONSUMPTION: ("消费", "价格", "成本", "price", "cost"),
    DomainTag.EDUCATION: ("学习", "教育", "技能", "learning"),
    DomainTag.ENERGY: ("能源", "电池", "energy"),
}


def candidate_domains(text: str) -> tuple[DomainTag, ...]:
    lowered = text.casefold()
    return tuple(
        domain for domain, keywords in RULES.items() if any(word in lowered for word in keywords)
    )

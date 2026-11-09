"""Product-owned starter industries and conspicuously synthetic reading examples."""

from uuid import NAMESPACE_URL, UUID, uuid5

from sqlalchemy.orm import Session

from infra.db import CommunityIndustry, CommunityPublication

CATALOG = (
    ("ai", "人工智能", "从技术进展，到工作与生活的改变。", "technology"),
    ("energy", "新能源", "关注能源技术、应用场景与产业变化。", "energy"),
    ("health", "医疗健康", "理解医疗服务与健康技术的发展边界。", "healthcare"),
    ("manufacturing", "先进制造", "观察生产方式、自动化与产业协作。", "manufacturing"),
    ("learning", "教育与学习", "探索学习方式与未来能力的变化。", "education"),
)


def catalog_id(code: str) -> UUID:
    return uuid5(NAMESPACE_URL, "futureos:consumer:industry:" + code)


def seed_community(session: Session) -> None:
    for code, name, description, domain in CATALOG:
        if session.get(CommunityIndustry, catalog_id(code)) is None:
            session.add(
                CommunityIndustry(
                    id=catalog_id(code),
                    name=name,
                    description=description,
                    domain=domain,
                    public=True,
                )
            )
    session.flush()
    examples = (
        (
            "code",
            "ai",
            "AI 编程，会怎样改变软件开发？",
            "从工具、任务和协作方式出发，学习如何阅读一份行业研究报告。",
            "report-code.webp",
        ),
        (
            "learning",
            "ai",
            "大模型走进日常，哪些能力值得关注？",
            "把技术能力、采用条件与个人选择分开看，保留判断中的不确定性。",
            "report-learning.webp",
        ),
        (
            "energy",
            "energy",
            "理解新能源变化，可以从哪些问题开始？",
            "从技术、需求与应用条件三个角度，建立自己的观察清单。",
            "industry-energy.webp",
        ),
    )
    for code, industry, title, summary, image in examples:
        identifier = uuid5(NAMESPACE_URL, "futureos:consumer:example:" + code)
        if session.get(CommunityPublication, identifier) is not None:
            continue
        session.add(
            CommunityPublication(
                id=identifier,
                industry_id=catalog_id(industry),
                public=True,
                body={
                    "title": title,
                    "summary": summary,
                    "label": "DEMO",
                    "sample": True,
                    "image": image,
                    "sections": [
                        {
                            "heading": "这是一份阅读示例",
                            "text": (
                                "用于展示报告的阅读、收藏与行业归档方式，不是已执"
                                "行的联网研究，也不代表现实预测。"
                            ),
                        },
                        {
                            "heading": "先明确问题，再判断变化",
                            "text": "明确范围、地区与时间，区分事实、假设与待验证判断。",
                        },
                        {
                            "heading": "把证据和不确定性放在一起",
                            "text": (
                                "正式报告应包含可核查来源、适用条件和反例。示例没"
                                "有真实证据，不提供行动建议。"
                            ),
                        },
                    ],
                },
            )
        )

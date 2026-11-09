import json
from pathlib import Path

from prediction_engine.contracts.models import DomainTag
from prediction_engine.ingestion.normalize import canonical_url, likely_reprint
from prediction_engine.signal_detection.rules import candidate_domains


def test_url_canonicalization_preserves_meaningful_parameters():
    assert (
        canonical_url("https://EXAMPLE.org:443/a?b=2&utm_source=x&a=1#top")
        == "https://example.org/a?a=1&b=2"
    )
    assert canonical_url("https://example.org/a?version=2") != canonical_url(
        "https://example.org/a?version=1"
    )


def test_conservative_reprint_similarity():
    body = "An independently documented synthetic pilot about reliability and deployment cost. " * 5
    assert likely_reprint(body, body + " Reprinted.")
    assert not likely_reprint("short", "short but unrelated")
    assert not likely_reprint(body, "A different measurement with different data. " * 10)


def test_rules_and_taxonomy_are_explicit_not_forecasts():
    taxonomy = json.loads(Path("packages/taxonomies/domains.v1.json").read_text())
    assert {item["code"] for item in taxonomy["domains"]} == {item.value for item in DomainTag}
    assert DomainTag.WORKFORCE in candidate_domains("DEMO hiring jobs")
    assert candidate_domains("An unrelated neutral phrase") == ()


def test_positive_and_negative_fixture_has_neutral_early_view():
    cases = json.loads(Path("fixtures/m1/historical_cases.v1.json").read_text())
    assert cases["label"] == "DEMO"
    assert {case["outcome"]["category"] for case in cases["cases"]} == {"success", "failure"}
    for case in cases["cases"]:
        assert case["contemporaneous"]["known_at"] < case["cutoff_at"] < case["outcome"]["known_at"]
        assert "success" not in case["title"] and "failure" not in case["title"]

from src.news_reasoning_auditor.config import Settings
from src.news_reasoning_auditor.source_registry import SourceRegistry


def test_registry_match() -> None:
    registry = SourceRegistry(Settings())
    match = registry.match("www.foxnews.com")
    assert match is not None
    assert match.source_leaning == "right"


def test_registry_unknown() -> None:
    registry = SourceRegistry(Settings())
    assert registry.leaning_for("nonexistent-example-site.test") == "unknown"

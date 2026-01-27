"""Tests for the collector module."""

import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import pytest

from src.collector import Collector
from src.models import PipelineState


class TestURLDeduplication:
    """Tests for URL deduplication logic."""

    def test_url_hash_consistency(self):
        """Same URL should produce same hash."""
        collector = self._create_collector()

        url = "https://example.com/article/123"
        hash1 = collector._url_hash(url)
        hash2 = collector._url_hash(url)

        assert hash1 == hash2

    def test_url_hash_different_urls(self):
        """Different URLs should produce different hashes."""
        collector = self._create_collector()

        hash1 = collector._url_hash("https://example.com/article/1")
        hash2 = collector._url_hash("https://example.com/article/2")

        assert hash1 != hash2

    def test_deduplicate_removes_duplicates(self):
        """Deduplication should remove items with same URL."""
        collector = self._create_collector()

        from src.models import Item, ItemStatus

        items = [
            Item(
                id="abc123",
                title="Article 1",
                url="https://example.com/article",
                source="Test",
                group="test",
                status=ItemStatus.PENDING,
            ),
            Item(
                id="abc123",  # Same ID = same URL hash
                title="Article 1 Duplicate",
                url="https://example.com/article",
                source="Test",
                group="test",
                status=ItemStatus.PENDING,
            ),
            Item(
                id="def456",
                title="Article 2",
                url="https://example.com/article-2",
                source="Test",
                group="test",
                status=ItemStatus.PENDING,
            ),
        ]

        result = collector._deduplicate(items)

        assert len(result) == 2
        assert result[0].title == "Article 1"
        assert result[1].title == "Article 2"

    def _create_collector(self) -> Collector:
        """Create a collector with temporary paths."""
        with tempfile.TemporaryDirectory() as tmpdir:
            return Collector(
                sources_path=Path(tmpdir) / "sources.yaml",
                state_path=Path(tmpdir) / "state.json",
            )


class TestDateFiltering:
    """Tests for date-based filtering."""

    def test_filter_old_items(self):
        """Items older than lookback window should be filtered."""
        from datetime import timedelta

        from src.models import Item, ItemStatus

        with tempfile.TemporaryDirectory() as tmpdir:
            collector = Collector(
                sources_path=Path(tmpdir) / "sources.yaml",
                state_path=Path(tmpdir) / "state.json",
                lookback_days=7,
            )

            old_date = datetime.now(timezone.utc) - timedelta(days=10)
            new_date = datetime.now(timezone.utc) - timedelta(days=1)

            items = [
                Item(
                    id="old123",
                    title="Old Article",
                    url="https://example.com/old",
                    published_at=old_date,
                    source="Test",
                    group="test",
                    status=ItemStatus.PENDING,
                ),
                Item(
                    id="new456",
                    title="New Article",
                    url="https://example.com/new",
                    published_at=new_date,
                    source="Test",
                    group="test",
                    status=ItemStatus.PENDING,
                ),
            ]

            result = collector._filter_new(items)

            assert len(result) == 1
            assert result[0].title == "New Article"

    def test_filter_processed_urls(self):
        """Already processed URLs should be filtered."""
        from src.models import Item, ItemStatus

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"

            # Create state with processed URL
            state = PipelineState(
                processed_urls={"https://example.com/processed"}
            )
            state_path.write_text(
                json.dumps({
                    "last_run": None,
                    "processed_urls": list(state.processed_urls),
                    "processed_dates": [],
                })
            )

            collector = Collector(
                sources_path=Path(tmpdir) / "sources.yaml",
                state_path=state_path,
            )

            items = [
                Item(
                    id="proc123",
                    title="Processed Article",
                    url="https://example.com/processed",
                    source="Test",
                    group="test",
                    status=ItemStatus.PENDING,
                ),
                Item(
                    id="new456",
                    title="New Article",
                    url="https://example.com/new",
                    source="Test",
                    group="test",
                    status=ItemStatus.PENDING,
                ),
            ]

            result = collector._filter_new(items)

            assert len(result) == 1
            assert result[0].title == "New Article"


class TestStateManagement:
    """Tests for state persistence."""

    def test_save_and_load_state(self):
        """State should persist correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"

            collector = Collector(
                sources_path=Path(tmpdir) / "sources.yaml",
                state_path=state_path,
            )

            # Add URLs to state
            collector.state.add_url("https://example.com/1")
            collector.state.add_url("https://example.com/2")
            collector.save_state()

            # Create new collector instance
            collector2 = Collector(
                sources_path=Path(tmpdir) / "sources.yaml",
                state_path=state_path,
            )

            assert collector2.state.is_processed("https://example.com/1")
            assert collector2.state.is_processed("https://example.com/2")
            assert not collector2.state.is_processed("https://example.com/3")

"""Tests for the renderer module."""

import tempfile
from datetime import datetime, timezone
from pathlib import Path

import pytest

from src.models import Article, Citation, Item, ItemStatus, Synthesis
from src.renderer import Renderer


class TestPageRendering:
    """Tests for page rendering output format."""

    def test_daily_page_format(self):
        """Daily page should have correct structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            docs_dir = Path(tmpdir) / "docs"
            renderer = Renderer(docs_dir=docs_dir)

            items = [
                Item(
                    id="test1",
                    title="Test Article",
                    url="https://example.com/test",
                    source="Test Source",
                    group="microsoft",
                    snippet="Test snippet content",
                    status=ItemStatus.EXTRACTED,
                )
            ]

            articles = [
                Article(
                    url="https://example.com/test",
                    slug="test",
                    title="Test Article",
                    extracted_text="Full extracted content here for testing purposes.",
                    success=True,
                )
            ]

            synthesis = Synthesis(
                digest_md="- Test digest item",
                blog_md="Test blog analysis",
                citations=[
                    Citation(
                        url="https://example.com/test",
                        title="Test Article",
                        source="Test Source",
                        group="microsoft",
                    )
                ],
            )

            page_path = renderer.render_daily_page(
                date="2026-01-27",
                items=items,
                articles=articles,
                synthesis=synthesis,
            )

            assert page_path.exists()

            content = page_path.read_text()

            # Check structure
            assert "2026-01-27" in content
            assert "Quick Digest" in content
            assert "Today's Highlights" in content
            assert "Deep Analysis" in content
            assert "Sources" in content

            # Check content
            assert "Test Article" in content
            assert "Test Source" in content
            assert "https://example.com/test" in content

    def test_archive_index_format(self):
        """Archive index should list dates correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            docs_dir = Path(tmpdir) / "docs"
            renderer = Renderer(docs_dir=docs_dir)

            dates = ["2026-01-25", "2026-01-26", "2026-01-27"]

            index_path = renderer.update_archive_index(dates)

            assert index_path.exists()

            content = index_path.read_text()

            # Dates should be in descending order
            assert "2026-01-27" in content
            assert "2026-01-26" in content
            assert "2026-01-25" in content

            # Should have links
            assert "2026-01-27.md" in content

    def test_home_page_links_to_latest(self):
        """Home page should link to latest report."""
        with tempfile.TemporaryDirectory() as tmpdir:
            docs_dir = Path(tmpdir) / "docs"
            renderer = Renderer(docs_dir=docs_dir)

            home_path = renderer.update_home_page("2026-01-27")

            assert home_path.exists()

            content = home_path.read_text()

            assert "2026-01-27" in content
            assert "daily/2026-01-27.md" in content


class TestExistingDates:
    """Tests for date detection logic."""

    def test_get_existing_dates(self):
        """Should find existing daily pages."""
        with tempfile.TemporaryDirectory() as tmpdir:
            docs_dir = Path(tmpdir) / "docs"
            daily_dir = docs_dir / "daily"
            daily_dir.mkdir(parents=True)

            # Create some daily pages
            (daily_dir / "2026-01-25.md").write_text("content")
            (daily_dir / "2026-01-26.md").write_text("content")
            (daily_dir / "index.md").write_text("content")  # Should be ignored
            (daily_dir / "EXAMPLE.md").write_text("content")  # Should be ignored

            renderer = Renderer(docs_dir=docs_dir)
            dates = renderer.get_existing_dates()

            assert len(dates) == 2
            assert "2026-01-25" in dates
            assert "2026-01-26" in dates

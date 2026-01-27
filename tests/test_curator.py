"""Tests for the curator module."""

import tempfile
from pathlib import Path

import pytest
import yaml

from src.curator import Curator
from src.models import CurationConfig, Item, ItemStatus


class TestCurationFilters:
    """Tests for curation filtering logic."""

    def test_denylist_filters_items(self):
        """Items matching denylist should be excluded."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "curation.yaml"
            config_path.write_text(
                yaml.dump({
                    "top_per_group": 10,
                    "denylist": ["sponsored", "advertisement"],
                    "allowlist": [],
                })
            )

            curator = Curator(config_path=config_path)

            items = [
                Item(
                    id="1",
                    title="Sponsored: Great Product",
                    url="https://example.com/sponsored",
                    source="Test",
                    group="test",
                    snippet="",
                    status=ItemStatus.PENDING,
                ),
                Item(
                    id="2",
                    title="Real News Article",
                    url="https://example.com/real",
                    source="Test",
                    group="test",
                    snippet="",
                    status=ItemStatus.PENDING,
                ),
            ]

            result = curator.curate(items)

            assert len(result) == 1
            assert result[0].title == "Real News Article"

    def test_allowlist_prioritizes_items(self):
        """Items matching allowlist should be included."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "curation.yaml"
            config_path.write_text(
                yaml.dump({
                    "top_per_group": 10,
                    "denylist": [],
                    "allowlist": ["power bi", "databricks"],
                })
            )

            curator = Curator(config_path=config_path)

            items = [
                Item(
                    id="1",
                    title="Power BI Updates",
                    url="https://example.com/pbi",
                    source="Test",
                    group="test",
                    snippet="",
                    status=ItemStatus.PENDING,
                ),
                Item(
                    id="2",
                    title="Random Topic",
                    url="https://example.com/random",
                    source="Test",
                    group="test",
                    snippet="",
                    status=ItemStatus.PENDING,
                ),
            ]

            result = curator.curate(items)

            assert len(result) == 1
            assert result[0].title == "Power BI Updates"

    def test_min_title_length(self):
        """Items with short titles should be excluded."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "curation.yaml"
            config_path.write_text(
                yaml.dump({
                    "top_per_group": 10,
                    "min_title_length": 10,
                    "denylist": [],
                    "allowlist": [],
                })
            )

            curator = Curator(config_path=config_path)

            items = [
                Item(
                    id="1",
                    title="Short",
                    url="https://example.com/short",
                    source="Test",
                    group="test",
                    snippet="",
                    status=ItemStatus.PENDING,
                ),
                Item(
                    id="2",
                    title="This is a longer title",
                    url="https://example.com/long",
                    source="Test",
                    group="test",
                    snippet="",
                    status=ItemStatus.PENDING,
                ),
            ]

            result = curator.curate(items)

            assert len(result) == 1
            assert result[0].title == "This is a longer title"


class TestGroupSelection:
    """Tests for top-N per group selection."""

    def test_top_per_group_limit(self):
        """Should select only top N items per group."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "curation.yaml"
            config_path.write_text(
                yaml.dump({
                    "top_per_group": 2,
                    "denylist": [],
                    "allowlist": [],
                })
            )

            curator = Curator(config_path=config_path)

            items = [
                Item(
                    id=str(i),
                    title=f"Article {i} about topic",
                    url=f"https://example.com/{i}",
                    source="Test",
                    group="microsoft",
                    snippet="",
                    status=ItemStatus.PENDING,
                )
                for i in range(5)
            ]

            result = curator.curate(items)

            assert len(result) == 2

    def test_multiple_groups(self):
        """Should select top N from each group independently."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "curation.yaml"
            config_path.write_text(
                yaml.dump({
                    "top_per_group": 2,
                    "denylist": [],
                    "allowlist": [],
                })
            )

            curator = Curator(config_path=config_path)

            items = [
                Item(
                    id="ms1",
                    title="Microsoft Article 1",
                    url="https://example.com/ms1",
                    source="Test",
                    group="microsoft",
                    snippet="",
                    status=ItemStatus.PENDING,
                ),
                Item(
                    id="ms2",
                    title="Microsoft Article 2",
                    url="https://example.com/ms2",
                    source="Test",
                    group="microsoft",
                    snippet="",
                    status=ItemStatus.PENDING,
                ),
                Item(
                    id="ms3",
                    title="Microsoft Article 3",
                    url="https://example.com/ms3",
                    source="Test",
                    group="microsoft",
                    snippet="",
                    status=ItemStatus.PENDING,
                ),
                Item(
                    id="db1",
                    title="Databricks Article 1",
                    url="https://example.com/db1",
                    source="Test",
                    group="data_platform",
                    snippet="",
                    status=ItemStatus.PENDING,
                ),
                Item(
                    id="db2",
                    title="Databricks Article 2",
                    url="https://example.com/db2",
                    source="Test",
                    group="data_platform",
                    snippet="",
                    status=ItemStatus.PENDING,
                ),
            ]

            result = curator.curate(items)

            # 2 from microsoft + 2 from data_platform
            assert len(result) == 4

            microsoft_items = [i for i in result if i.group == "microsoft"]
            data_platform_items = [i for i in result if i.group == "data_platform"]

            assert len(microsoft_items) == 2
            assert len(data_platform_items) == 2

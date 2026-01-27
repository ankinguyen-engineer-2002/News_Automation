"""Curator module - Filters and selects items for processing."""

import logging
import re
from pathlib import Path
from typing import Optional

import yaml

from .models import CurationConfig, Item

logger = logging.getLogger(__name__)


class Curator:
    """Curates and filters news items based on configurable rules."""

    def __init__(self, config_path: Path):
        """
        Initialize the curator.

        Args:
            config_path: Path to curation.yaml configuration
        """
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> CurationConfig:
        """Load curation configuration from YAML."""
        if not self.config_path.exists():
            logger.warning(f"Curation config not found: {self.config_path}")
            return CurationConfig()

        with open(self.config_path) as f:
            data = yaml.safe_load(f) or {}
            return CurationConfig(**data)

    def curate(self, items: list[Item]) -> list[Item]:
        """
        Curate items based on configuration rules.

        Args:
            items: List of discovered items

        Returns:
            List of selected items for further processing
        """
        logger.info(f"Curating {len(items)} items")

        # Step 1: Apply filters
        filtered = self._apply_filters(items)
        logger.info(f"After filtering: {len(filtered)} items")

        # Step 2: Score and rank
        scored = self._score_items(filtered)

        # Step 3: Select top N per group
        selected = self._select_top_per_group(scored)
        logger.info(f"Selected: {len(selected)} items")

        return selected

    def _apply_filters(self, items: list[Item]) -> list[Item]:
        """Apply allowlist/denylist filters."""
        filtered: list[Item] = []

        for item in items:
            # Check minimum title length
            if len(item.title) < self.config.min_title_length:
                continue

            # Check denylist
            if self._matches_denylist(item):
                continue

            # If allowlist is specified, item must match
            if self.config.allowlist and not self._matches_allowlist(item):
                continue

            filtered.append(item)

        return filtered

    def _matches_allowlist(self, item: Item) -> bool:
        """Check if item matches any allowlist pattern."""
        text = f"{item.title} {item.snippet}".lower()

        for pattern in self.config.allowlist:
            if pattern.lower() in text:
                return True

        return False

    def _matches_denylist(self, item: Item) -> bool:
        """Check if item matches any denylist pattern."""
        text = f"{item.title} {item.snippet}".lower()

        for pattern in self.config.denylist:
            if pattern.lower() in text:
                return True

        return False

    def _score_items(self, items: list[Item]) -> list[tuple[Item, float]]:
        """
        Score items for ranking.

        Returns list of (item, score) tuples sorted by score descending.
        """
        scored: list[tuple[Item, float]] = []

        for item in items:
            score = 0.0

            # Base score from priority (if available from source)
            # Higher priority sources get higher base score

            # Boost for matching more allowlist keywords
            text = f"{item.title} {item.snippet}".lower()
            for pattern in self.config.allowlist:
                if pattern.lower() in text:
                    score += 1.0

            # Boost for recency (newer is better)
            if item.published_at:
                from datetime import datetime, timezone

                age_hours = (
                    datetime.now(timezone.utc) - item.published_at
                ).total_seconds() / 3600
                recency_score = max(0, 24 - age_hours) / 24  # 0-1 based on age
                score += recency_score * 2

            # Boost for longer snippets (more context)
            if len(item.snippet) > 100:
                score += 0.5

            scored.append((item, score))

        # Sort by score descending
        scored.sort(key=lambda x: x[1], reverse=True)

        return scored

    def _select_top_per_group(
        self, scored_items: list[tuple[Item, float]]
    ) -> list[Item]:
        """Select top N items per group."""
        group_counts: dict[str, int] = {}
        selected: list[Item] = []

        for item, score in scored_items:
            count = group_counts.get(item.group, 0)

            if count < self.config.top_per_group:
                selected.append(item)
                group_counts[item.group] = count + 1

        return selected

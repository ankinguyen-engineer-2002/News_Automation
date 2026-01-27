"""Collector module - Fetches and normalizes news items from various sources."""

import hashlib
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

import feedparser
import requests
import yaml
from dateutil import parser as date_parser

from .models import Item, ItemStatus, PipelineState, Source, SourceType

logger = logging.getLogger(__name__)

# Default user agent for requests
USER_AGENT = (
    "Mozilla/5.0 (compatible; DailyEngineeringIntelligence/1.0; "
    "+https://github.com/your-repo)"
)


class Collector:
    """Collects news items from configured sources."""

    def __init__(
        self,
        sources_path: Path,
        state_path: Path,
        lookback_days: int = 7,
    ):
        """
        Initialize the collector.

        Args:
            sources_path: Path to sources.yaml configuration
            state_path: Path to state.json for deduplication
            lookback_days: How many days back to consider items
        """
        self.sources_path = sources_path
        self.state_path = state_path
        self.lookback_days = lookback_days
        self.state = self._load_state()
        self.sources_config = self._load_sources()

    def _load_state(self) -> PipelineState:
        """Load pipeline state from disk."""
        if self.state_path.exists():
            try:
                import json

                data = json.loads(self.state_path.read_text())
                # Convert processed_urls list back to set
                if "processed_urls" in data and isinstance(data["processed_urls"], list):
                    data["processed_urls"] = set(data["processed_urls"])
                return PipelineState(**data)
            except Exception as e:
                logger.warning(f"Failed to load state: {e}")
        return PipelineState()

    def save_state(self) -> None:
        """Save pipeline state to disk."""
        import json

        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        # Convert set to list for JSON serialization
        data = self.state.model_dump()
        data["processed_urls"] = list(data["processed_urls"])
        self.state_path.write_text(json.dumps(data, indent=2, default=str))

    def _load_sources(self) -> dict:
        """Load sources configuration from YAML."""
        if not self.sources_path.exists():
            logger.warning(f"Sources file not found: {self.sources_path}")
            return {"groups": {}}

        with open(self.sources_path) as f:
            return yaml.safe_load(f) or {"groups": {}}

    def collect(self) -> list[Item]:
        """
        Collect items from all configured sources.

        Returns:
            List of discovered items (deduplicated)
        """
        all_items: list[Item] = []

        for group_name, sources in self.sources_config.get("groups", {}).items():
            logger.info(f"Processing group: {group_name}")

            for source_config in sources:
                source = Source(**source_config)
                if not source.enabled:
                    continue

                try:
                    items = self._fetch_source(source, group_name)
                    all_items.extend(items)
                    logger.info(f"  {source.name}: {len(items)} items")
                except Exception as e:
                    logger.error(f"  {source.name}: Error - {e}")

        # Deduplicate and filter
        unique_items = self._deduplicate(all_items)
        new_items = self._filter_new(unique_items)

        logger.info(
            f"Collected {len(all_items)} total, "
            f"{len(unique_items)} unique, "
            f"{len(new_items)} new"
        )

        return new_items

    def _fetch_source(self, source: Source, group_name: str) -> list[Item]:
        """Fetch items from a single source."""
        if source.type == SourceType.RSS:
            return self._fetch_rss(source, group_name)
        elif source.type == SourceType.API:
            return self._fetch_api(source, group_name)
        elif source.type == SourceType.SCRAPE:
            return self._fetch_scrape(source, group_name)
        else:
            logger.warning(f"Unknown source type: {source.type}")
            return []

    def _fetch_rss(self, source: Source, group_name: str) -> list[Item]:
        """Fetch items from an RSS/Atom feed."""
        items: list[Item] = []

        try:
            feed = feedparser.parse(
                source.url,
                agent=USER_AGENT,
            )

            if feed.bozo and feed.bozo_exception:
                logger.warning(f"Feed parse warning: {feed.bozo_exception}")

            for entry in feed.entries:
                # Parse published date
                published_at = None
                for date_field in ["published_parsed", "updated_parsed", "created_parsed"]:
                    if hasattr(entry, date_field) and getattr(entry, date_field):
                        try:
                            time_tuple = getattr(entry, date_field)
                            published_at = datetime(*time_tuple[:6], tzinfo=timezone.utc)
                            break
                        except Exception:
                            pass

                # If no parsed date, try string parsing
                if not published_at:
                    for date_field in ["published", "updated", "created"]:
                        if hasattr(entry, date_field) and getattr(entry, date_field):
                            try:
                                published_at = date_parser.parse(getattr(entry, date_field))
                                break
                            except Exception:
                                pass

                # Get snippet/summary
                snippet = ""
                if hasattr(entry, "summary"):
                    snippet = self._clean_html(entry.summary)[:500]
                elif hasattr(entry, "description"):
                    snippet = self._clean_html(entry.description)[:500]

                # Create item
                url = entry.get("link", "")
                if not url:
                    continue

                item = Item(
                    id=self._url_hash(url),
                    title=entry.get("title", "Untitled"),
                    url=url,
                    published_at=published_at,
                    source=source.name,
                    snippet=snippet,
                    tags=source.tags.copy(),
                    group=group_name,
                    status=ItemStatus.PENDING,
                )
                items.append(item)

        except Exception as e:
            logger.error(f"RSS fetch error for {source.name}: {e}")

        return items

    def _fetch_api(self, source: Source, group_name: str) -> list[Item]:
        """Fetch items from an API endpoint."""
        # Placeholder for API fetching - can be extended
        logger.info(f"API fetching not yet implemented for {source.name}")
        return []

    def _fetch_scrape(self, source: Source, group_name: str) -> list[Item]:
        """Fetch items by scraping a webpage."""
        # Placeholder for web scraping - can be extended
        logger.info(f"Scraping not yet implemented for {source.name}")
        return []

    def _url_hash(self, url: str) -> str:
        """Generate a hash of a URL for deduplication."""
        return hashlib.md5(url.encode()).hexdigest()[:12]

    def _clean_html(self, html: str) -> str:
        """Remove HTML tags from a string."""
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, "html.parser")
        return soup.get_text(separator=" ", strip=True)

    def _deduplicate(self, items: list[Item]) -> list[Item]:
        """Remove duplicate items based on URL hash."""
        seen: set[str] = set()
        unique: list[Item] = []

        for item in items:
            if item.id not in seen:
                seen.add(item.id)
                unique.append(item)

        return unique

    def _filter_new(self, items: list[Item]) -> list[Item]:
        """Filter out items that have already been processed."""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=self.lookback_days)
        new_items: list[Item] = []

        for item in items:
            # Skip if already processed
            if self.state.is_processed(item.url):
                continue

            # Skip if too old
            if item.published_at and item.published_at < cutoff_date:
                continue

            new_items.append(item)

        return new_items

    def mark_processed(self, items: list[Item]) -> None:
        """Mark items as processed in the state."""
        for item in items:
            self.state.add_url(item.url)
        self.state.last_run = datetime.now(timezone.utc)

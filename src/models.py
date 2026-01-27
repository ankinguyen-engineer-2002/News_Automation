"""Pydantic models for the Daily Engineering Intelligence pipeline."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_serializer


class ItemStatus(str, Enum):
    """Status of an item in the pipeline."""

    PENDING = "pending"
    SELECTED = "selected"
    EXTRACTED = "extracted"
    EXTRACT_FAILED = "extract_failed"
    SYNTHESIZED = "synthesized"


class SourceType(str, Enum):
    """Type of news source."""

    RSS = "rss"
    API = "api"
    SCRAPE = "scrape"


class Source(BaseModel):
    """Configuration for a news source."""

    name: str
    type: SourceType
    url: str
    tags: list[str] = Field(default_factory=list)
    priority: int = Field(default=1, ge=1, le=10)
    enabled: bool = True


class SourceGroup(BaseModel):
    """A group of related sources."""

    name: str
    sources: list[Source] = Field(default_factory=list)


class Item(BaseModel):
    """A discovered news item."""

    id: str = Field(description="Unique identifier (URL hash)")
    title: str
    url: str
    published_at: Optional[datetime] = None
    source: str = Field(description="Source name")
    snippet: str = Field(default="", description="Short description or summary")
    tags: list[str] = Field(default_factory=list)
    group: str = Field(description="Source group name")
    status: ItemStatus = ItemStatus.PENDING

    def url_hash(self) -> str:
        """Generate a hash of the URL for deduplication."""
        import hashlib

        return hashlib.md5(self.url.encode()).hexdigest()[:12]


class Article(BaseModel):
    """Extracted article content."""

    url: str
    slug: str = Field(description="URL slug for file naming")
    title: str = ""
    extracted_text: str = ""
    extracted_at: Optional[datetime] = None
    success: bool = False
    error: Optional[str] = None
    word_count: int = 0

    @classmethod
    def from_item(cls, item: Item) -> "Article":
        """Create an Article from an Item."""
        import re
        from urllib.parse import urlparse

        # Generate slug from URL
        parsed = urlparse(item.url)
        path = parsed.path.strip("/").replace("/", "-")
        slug = re.sub(r"[^a-z0-9-]", "", path.lower())[:50] or item.url_hash()

        return cls(url=item.url, slug=slug, title=item.title)


class Citation(BaseModel):
    """A citation reference for synthesized content."""

    url: str
    title: str
    source: str
    group: str


class Synthesis(BaseModel):
    """Synthesized content output."""

    digest_md: str = Field(description="Short daily digest in markdown")
    blog_md: str = Field(description="Deep blog post in markdown")
    citations: list[Citation] = Field(default_factory=list)
    generated_at: Optional[datetime] = None
    adapter_used: str = "nollm"


class PipelineState(BaseModel):
    """Persistent state for the pipeline."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    last_run: Optional[datetime] = None
    processed_urls: set[str] = Field(default_factory=set)
    processed_dates: list[str] = Field(default_factory=list)

    @field_serializer("processed_urls")
    def serialize_urls(self, urls: set[str]) -> list[str]:
        """Serialize set to list for JSON compatibility."""
        return list(urls)

    def add_url(self, url: str) -> None:
        """Mark a URL as processed."""
        self.processed_urls.add(url)

    def is_processed(self, url: str) -> bool:
        """Check if a URL has been processed."""
        return url in self.processed_urls


class CurationConfig(BaseModel):
    """Configuration for content curation."""

    top_per_group: int = Field(default=5, ge=1, le=20)
    allowlist: list[str] = Field(default_factory=list)
    denylist: list[str] = Field(default_factory=list)
    min_title_length: int = Field(default=10)
    max_age_days: int = Field(default=7)


class DailyRun(BaseModel):
    """Summary of a daily pipeline run."""

    date: str = Field(description="Run date YYYY-MM-DD")
    items_discovered: int = 0
    items_selected: int = 0
    items_extracted: int = 0
    items_failed: int = 0
    digest_generated: bool = False
    blog_generated: bool = False
    pages_rendered: bool = False
    notification_sent: bool = False
    run_started: Optional[datetime] = None
    run_completed: Optional[datetime] = None
    errors: list[str] = Field(default_factory=list)

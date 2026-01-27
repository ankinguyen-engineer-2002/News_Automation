"""Astro Renderer - Generates content for Astro site."""

import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from .models import Article, Item, Synthesis

logger = logging.getLogger(__name__)


class AstroRenderer:
    """Renders MDX content files for Astro site."""

    # Topic slug mapping
    TOPIC_MAPPING = {
        "microsoft": "microsoft",
        "data_platform": "data-platform",
        "analytics_engineering": "analytics-engineering",
        "ai_agents": "ai-agents",
        "ai_llm": "ai-agents",
        "automation": "automation",
        "github": "github",
    }

    def __init__(self, astro_dir: Path):
        """
        Initialize renderer.

        Args:
            astro_dir: Path to astro-site directory
        """
        self.astro_dir = astro_dir
        self.articles_dir = astro_dir / "src" / "content" / "articles"
        self.dailies_dir = astro_dir / "src" / "content" / "dailies"
        self.articles_dir.mkdir(parents=True, exist_ok=True)
        self.dailies_dir.mkdir(parents=True, exist_ok=True)

        # Track article numbers per topic
        self._topic_counters: dict[str, int] = {}

    def _get_topic_slug(self, group: str) -> str:
        """Convert group name to topic slug."""
        return self.TOPIC_MAPPING.get(group, "github")

    def _get_next_number(self, topic: str) -> int:
        """Get next article number for a topic."""
        if topic not in self._topic_counters:
            # Count existing articles for this topic
            existing = list(self.articles_dir.glob("*.mdx"))
            count = sum(
                1 for f in existing
                if self._read_topic_from_file(f) == topic
            )
            self._topic_counters[topic] = count
        
        self._topic_counters[topic] += 1
        return self._topic_counters[topic]

    def _read_topic_from_file(self, path: Path) -> Optional[str]:
        """Read topic from existing MDX file frontmatter."""
        try:
            content = path.read_text(encoding="utf-8")
            match = re.search(r'^topic:\s*["\']?([^"\'\n]+)', content, re.MULTILINE)
            return match.group(1).strip() if match else None
        except:
            return None

    def _make_slug(self, date: str, title: str) -> str:
        """Create URL-safe slug from date and title."""
        # Clean title
        slug = title.lower()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[\s_]+', '-', slug)
        slug = slug[:50].rstrip('-')
        return f"{date}-{slug}"

    def _escape_yaml(self, text: str) -> str:
        """Escape text for YAML frontmatter."""
        if not text:
            return ""
        # Escape quotes and newlines
        text = text.replace('\\', '\\\\')
        text = text.replace('"', '\\"')
        text = text.replace('\n', ' ')
        return text.strip()

    def _extract_excerpt(self, text: str, max_length: int = 200) -> str:
        """Extract excerpt from article text."""
        if not text:
            return ""
        
        # Remove markdown headers and formatting
        text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
        
        # Get first meaningful paragraph
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        for para in paragraphs:
            if len(para) < 30:
                continue
            if para.startswith(('*', '-', '|', '[', '!')):
                continue
            para = para.replace('\n', ' ').strip()
            if len(para) > max_length:
                return para[:max_length].rsplit(' ', 1)[0] + '...'
            return para
        
        return text[:max_length] + '...' if len(text) > max_length else text

    def render_articles(
        self,
        date: str,
        items: list[Item],
        articles: list[Article],
        synthesis: Optional[Synthesis] = None,
    ) -> list[Path]:
        """
        Render article MDX files.

        Args:
            date: Date string (YYYY-MM-DD)
            items: Curated items
            articles: Extracted articles
            synthesis: Optional synthesis (unused for now)

        Returns:
            List of paths to generated files
        """
        article_map = {a.url: a for a in articles}
        generated = []

        for item in items:
            topic = self._get_topic_slug(item.group)
            number = self._get_next_number(topic)
            article = article_map.get(item.url)
            
            # Get content
            if article and article.success and article.extracted_text:
                content = article.extracted_text
                excerpt = self._extract_excerpt(content)
            else:
                content = item.snippet or ""
                excerpt = item.snippet or ""

            slug = self._make_slug(date, item.title)
            
            # Build MDX content
            mdx = f'''---
title: "{self._escape_yaml(item.title)}"
source: "{self._escape_yaml(item.source)}"
url: "{item.url}"
topic: "{topic}"
date: "{date}"
excerpt: "{self._escape_yaml(excerpt)}"
number: {number}
publishDate: "{date}T00:00:00Z"
---

{content}
'''
            
            # Write file - use .md instead of .mdx to avoid expression parsing issues
            file_path = self.articles_dir / f"{slug}.md"
            file_path.write_text(mdx, encoding="utf-8")
            generated.append(file_path)
            logger.info(f"Generated article: {file_path.name}")

        logger.info(f"Rendered {len(generated)} articles for {date}")
        return generated

    def render_daily_summary(
        self,
        date: str,
        items: list[Item],
    ) -> Path:
        """
        Render daily summary MDX file.

        Args:
            date: Date string (YYYY-MM-DD)
            items: Curated items

        Returns:
            Path to generated file
        """
        # Count by topic
        topic_counts: dict[str, int] = {}
        for item in items:
            topic = self._get_topic_slug(item.group)
            topic_counts[topic] = topic_counts.get(topic, 0) + 1

        # Format date
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        formatted = date_obj.strftime("%B %d, %Y")

        # Build summary content
        mdx = f'''---
date: "{date}"
title: "{formatted}"
articleCount: {len(items)}
topicCounts:
{chr(10).join(f'  {k}: {v}' for k, v in sorted(topic_counts.items()))}
publishDate: "{date}T00:00:00Z"
---

# Daily Summary for {formatted}

**{len(items)}** articles curated across **{len(topic_counts)}** topics.
'''

        file_path = self.dailies_dir / f"{date}.md"
        file_path.write_text(mdx, encoding="utf-8")
        logger.info(f"Generated daily summary: {file_path.name}")

        return file_path

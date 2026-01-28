"""Astro Renderer - Generates content for Astro site with AI translation support."""

import logging
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from .models import Article, Item, Synthesis

logger = logging.getLogger(__name__)


class AstroRenderer:
    """Renders MD content files for Astro site with Vietnamese translation."""

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

    def __init__(self, astro_dir: Path, use_ai: bool = False):
        """
        Initialize renderer.

        Args:
            astro_dir: Path to astro-site directory
            use_ai: Whether to use AI for translation/summarization
        """
        self.astro_dir = astro_dir
        self.articles_dir = astro_dir / "src" / "content" / "articles"
        self.dailies_dir = astro_dir / "src" / "content" / "dailies"
        self.articles_dir.mkdir(parents=True, exist_ok=True)
        self.dailies_dir.mkdir(parents=True, exist_ok=True)

        # Track article numbers per topic
        self._topic_counters: dict[str, int] = {}
        
        # AI adapter for translation
        self.gemini = None
        if use_ai:
            try:
                from .gemini_adapter import GeminiAdapter
                self.gemini = GeminiAdapter()
                logger.info("Gemini adapter initialized for translations")
            except Exception as e:
                logger.warning(f"Could not initialize Gemini: {e}")

    def _get_topic_slug(self, group: str) -> str:
        """Convert group name to topic slug."""
        return self.TOPIC_MAPPING.get(group, "github")

    def _get_next_number(self, topic: str) -> int:
        """Get next article number for a topic."""
        if topic not in self._topic_counters:
            # Count existing articles for this topic
            existing = list(self.articles_dir.glob("*.md"))
            count = sum(
                1 for f in existing
                if self._read_topic_from_file(f) == topic
            )
            self._topic_counters[topic] = count
        
        self._topic_counters[topic] += 1
        return self._topic_counters[topic]

    def _read_topic_from_file(self, path: Path) -> Optional[str]:
        """Read topic from existing MD file frontmatter."""
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

    def _translate(self, text: str) -> str:
        """Translate text to Vietnamese using Gemini if available."""
        if not self.gemini or not text:
            return ""
        try:
            return self.gemini.translate_to_vietnamese(text)
        except Exception as e:
            logger.warning(f"Translation failed: {e}")
            return ""
    
    def _is_content_poor(self, content: str) -> bool:
        """Check if content is too short or poor quality."""
        if not content:
            return True
        
        # Count actual content (excluding markdown formatting)
        text_only = re.sub(r'[#*\[\]!`]', '', content)
        word_count = len(text_only.split())
        
        # Consider poor if less than 150 words
        return word_count < 150
    
    def _enrich_content(self, title: str, url: str, current_content: str) -> str:
        """Use AI to generate richer content for articles with poor content."""
        if not self.gemini:
            return current_content
        
        try:
            prompt = f"""Based on the following article title and available content, 
write a comprehensive technical summary (300-500 words) for an engineering audience.

Title: {title}
URL: {url}
Available content: {current_content[:1000]}

Write in English, focusing on:
1. Key technical concepts and innovations
2. Practical implications for engineers
3. Notable insights or takeaways

Format with markdown headers and bullet points where appropriate."""
            
            response = self.gemini.model.generate_content(prompt)
            enriched = response.text.strip()
            
            # Append attribution
            enriched += f"\n\n---\n*AI-generated summary based on [original article]({url})*"
            
            logger.info(f"Enriched content for: {title[:40]}...")
            return enriched
            
        except Exception as e:
            logger.warning(f"Content enrichment failed: {e}")
            return current_content

    def render_articles(
        self,
        date: str,
        items: list[Item],
        articles: list[Article],
        synthesis: Optional[Synthesis] = None,
    ) -> list[Path]:
        """
        Render article MD files with optional Vietnamese translation.

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
            
            # Enrich poor content with AI if available
            if self.gemini and self._is_content_poor(content):
                logger.info(f"Content too short, enriching: {item.title[:40]}...")
                content = self._enrich_content(item.title, item.url, content)
                excerpt = self._extract_excerpt(content)

            slug = self._make_slug(date, item.title)
            
            # Generate Vietnamese translations if AI is available
            title_vi = ""
            excerpt_vi = ""
            if self.gemini:
                logger.info(f"Translating: {item.title[:50]}...")
                title_vi = self._translate(item.title)
                excerpt_vi = self._translate(excerpt)
            
            # Build MD content with bilingual support
            md = f'''---
title: "{self._escape_yaml(item.title)}"
title_vi: "{self._escape_yaml(title_vi)}"
source: "{self._escape_yaml(item.source)}"
url: "{item.url}"
topic: "{topic}"
date: "{date}"
excerpt: "{self._escape_yaml(excerpt)}"
excerpt_vi: "{self._escape_yaml(excerpt_vi)}"
number: {number}
publishDate: "{date}T00:00:00Z"
---

{content}
'''
            
            # Write file
            file_path = self.articles_dir / f"{slug}.md"
            file_path.write_text(md, encoding="utf-8")
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
        Render daily summary MD file.

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
        md = f'''---
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
        file_path.write_text(md, encoding="utf-8")
        logger.info(f"Generated daily summary: {file_path.name}")

        return file_path
